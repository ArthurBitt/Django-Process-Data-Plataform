from django.utils import timezone
from rest_framework.exceptions import APIException

from apps.worksheets.constants import RequiredColumns
from apps.utils.enums import ProcessingStatus
from apps.worksheets.models import (
    Worksheet,
    WorksheetLine
)

from django.db import transaction
from rest_framework import serializers

from io import BytesIO
import pandas as pd
import tempfile
import io

from django.db.models import Count

class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    upload_type = serializers.CharField()

    @staticmethod
    def validate_file(value):
        valid_extensions = ['.xlsx']
        if not value.name.lower().endswith(tuple(valid_extensions)):
            raise serializers.ValidationError("Formato de arquivo inválido. Envie um arquivo .xlsx")
        return value

    def create(self, validated_data):
        file = validated_data['file']
        upload_type = validated_data['upload_type']
        file_io = BytesIO(file.read())
        return self.process_xlsx(file_io, upload_type, self.context['request'].user)

    @staticmethod
    def process_xlsx(file_io, upload_type, user):
        with transaction.atomic():
            try:
                df = pd.read_excel(file_io)
                df = df.fillna('').astype(str)
                df.columns = df.columns.str.strip().str.lower().str.replace(r'\n', '', regex=True)

                # validate columns before processing entry data to database
                required_columns = set(RequiredColumns.get(upload_type).values())

                processed_columns = set(
                    col.strip().lower().replace('\n', '') for col in df.columns
                )

                if required_columns != processed_columns:
                    missing = required_columns - processed_columns
                    extra = processed_columns - required_columns

                    error_message = []
                    if missing:
                        error_message.append(f"Colunas faltantes: {', '.join(missing)}")
                    if extra:
                        error_message.append(f"Colunas extras: {', '.join(extra)}")

                    raise serializers.ValidationError(" ".join(error_message))

                worksheet = Worksheet.objects.create(created_by=user)

                for _, row in df.iterrows():
                    row_data = row.to_dict()
                    WorksheetLine.objects.create(
                        worksheet_id=worksheet,
                        data=row_data
                    )
                return worksheet
            except Exception as e:
                raise serializers.ValidationError(f"Fail to process XLSX: {str(e)}")

class DownloadReportSerializer(serializers.Serializer):
    worksheet_id = serializers.UUIDField(required=True)

    def validate_worksheet_id(self, value):
        try:
            worksheet = Worksheet.objects.get(id=value)
        except Worksheet.DoesNotExist:
            raise serializers.ValidationError("Worksheet not found")
        try:
            worksheet_lines = WorksheetLine.objects.filter(worksheet_id=worksheet).all()
        except:
            raise serializers.ValidationError("Fail to get Worksheet Lines")

        if not worksheet_lines.exists():
            raise serializers.ValidationError("Empty Worksheet")

        self.context['worksheet'] = worksheet

        return value

    @staticmethod
    def create_excel_file(worksheet):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = worksheet.generate_excel(temp_dir)

            if not file_path:
                raise serializers.ValidationError("Worksheet empty or not found")

            with open(file_path, 'rb') as excel_file:
                excel_buffer = io.BytesIO(excel_file.read())

            excel_buffer.seek(0)
            return excel_buffer

class ProcessDataStatusCountSerializer(serializers.Serializer):
    status_name = serializers.CharField()
    total = serializers.IntegerField()

class ListProcessDataSerializer(serializers.Serializer):
    worksheet_id = serializers.UUIDField()
    total_lines = serializers.IntegerField()
    status_counts = ProcessDataStatusCountSerializer(many=True)
    status_4_percentage = serializers.FloatField()
    status_5_percentage = serializers.FloatField()
    created_by = serializers.CharField()
    processing_start_date = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        required=False,
        allow_null=True
    )
    processing_end_date = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        required=False,
        allow_null=True
    )

    @staticmethod
    def get_status_counts(worksheet):
        status_counts = {
            ProcessingStatus.get_status_name(status.value): 0
            for status in ProcessingStatus
        }

        # Query the database for process_status counts
        process_status_counts = WorksheetLine.objects.filter(worksheet_id=worksheet).values(
            "process_status"
        ).annotate(total=Count("id"))

        # Atualiza status_counts com os valores do banco de dados
        for item in process_status_counts:
            status_name = ProcessingStatus.get_status_name(item["process_status"])
            status_counts[status_name] = item["total"]

        # Converte o dicionário para uma lista de dicionários
        return [{"status_name": name, "total": total} for name, total in status_counts.items()]

    @staticmethod
    def get_status_4_percentage(worksheet):
        total_lines = WorksheetLine.objects.filter(worksheet_id=worksheet).count()
        if total_lines == 0:
            return 0.0

        status_4_lines = WorksheetLine.objects.filter(worksheet_id=worksheet, process_status=4).count()
        percentage = (status_4_lines / total_lines) * 100
        return round(percentage, 1)

    @staticmethod
    def get_status_5_percentage(worksheet):
        total_lines = WorksheetLine.objects.filter(worksheet_id=worksheet).count()
        if total_lines == 0:
            return 0.0

        status_5_lines = WorksheetLine.objects.filter(worksheet_id=worksheet, process_status=5).count()
        percentage = (status_5_lines / total_lines) * 100
        return round(percentage, 1)

    @staticmethod
    def get_created_by(instance):
        user = instance.created_by
        return user.email

    def to_representation(cls, instance):
        worksheet_total_lines = WorksheetLine.objects.filter(worksheet_id=instance).count()

        # Converte o process_status (string) para o nome do status
        worksheet_status = ProcessingStatus.get_status_name(instance.process_status)

        worksheet_processing_start_date = instance.start_processing.strftime(
            '%Y-%m-%d %H:%M:%S') if instance.start_processing else None
        worksheet_processing_end_date = instance.ending_processing.strftime(
            '%Y-%m-%d %H:%M:%S') if instance.ending_processing else None
        lines_status_counts = cls.get_status_counts(instance)
        lines_status_4_percentage = cls.get_status_4_percentage(instance)
        lines_status_5_percentage = cls.get_status_5_percentage(instance)
        worksheet_create_at = instance.created_at.strftime('%Y-%m-%d %H:%M:%S') if instance.created_at else None
        created_by = cls.get_created_by(instance)

        return {
            "worksheet_id": instance.id,
            "worksheet_status": worksheet_status,
            "worksheet_total_lines": worksheet_total_lines,
            "worksheet_processing_start_date": worksheet_processing_start_date,
            "worksheet_processing_end_date": worksheet_processing_end_date,
            "worksheet_create_at": worksheet_create_at,
            "worksheet_created_by": created_by,
            "lines_sucess_percentage": lines_status_4_percentage,
            "lines_error_percentage": lines_status_5_percentage,
            "lines_status_counts": lines_status_counts,
        }

class ListWorksheetLinesSerializer(serializers.Serializer):
    worksheet_id = serializers.UUIDField(required=True)
    process_status = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    @staticmethod
    def validate_worksheet_id(value):
        try:
            Worksheet.objects.get(id=value)
        except Worksheet.DoesNotExist:
            raise serializers.ValidationError("worksheet not found")
        return value

    @staticmethod
    def validate_process_status(value):
        if value is not None:
            value = str(value)
            valid_status = [status.value for status in ProcessingStatus]
            if value not in valid_status:
                raise serializers.ValidationError("Status are between 1 and 5")
        return value

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "process_status": ProcessingStatus.get_status_name(instance.process_status)
        }

class ReprocessWorksheetSerializer(serializers.Serializer):
    worksheet_id = serializers.UUIDField(required=True)

    def validate_worksheet_id(self, value):
        try:
            worksheet = Worksheet.objects.get(
                id=value,
                is_active=True,
                process_status__in=['5', '6']
            )

            lines_to_process = WorksheetLine.objects.filter(
                worksheet_id=worksheet,
                is_active=True,
                process_status=5
            )

            if not lines_to_process.exists():
                raise serializers.ValidationError("There are no lines to reprocess")

            self.context['worksheet'] = worksheet
            self.context['lines_to_process'] = lines_to_process
            return value

        except Worksheet.DoesNotExist:
            raise serializers.ValidationError("Worksheet not found or not ready to reprocess")
        except Exception as e:
            raise serializers.ValidationError(f"Fail to get Worksheet: {str(e)}")

    def reprocess_worksheet(self):
        worksheet = self.context['worksheet']
        request = self.context.get('request')
        lines_to_reprocess = self.context['lines_to_process']

        try:
            # Atualiza as linhas
            lines_to_reprocess.update(
                process_status=1,
                details=f"Put to Reprocess by {request.user} in {timezone.now().strftime('%d/%m/%Y %H:%M')}",
                updated_at=timezone.now()
            )

            # Atualiza a worksheet
            worksheet.process_status = 3
            worksheet.updated_at = timezone.now()
            worksheet.save()

        except Exception as e:
            error_msg = f"Error during reprocessing: {str(e)}"

            # Reverte o status em caso de erro
            lines_to_reprocess.update(
                process_status=5,
                detail=error_msg,
                updated=timezone.now()
            )
            worksheet.process_status = 5
            worksheet.detail = error_msg
            worksheet.updated = timezone.now()
            worksheet.save()

            raise APIException(error_msg)

class ReprocessWorksheetLineSerializer(serializers.Serializer):

    worksheet_id = serializers.UUIDField(required=True)

    @staticmethod
    def validate_reprocess(value):
        try:
            worksheet = Worksheet.objects.get(id=value)
        except Worksheet.DoesNotExist:
            raise serializers.ValidationError("Worksheet not found")

        try:
            worksheet_lines = WorksheetLine.objects.filter(worksheet_id=worksheet,process_status=5).all()
            if worksheet_lines.exists():
                return worksheet
            else:
                raise serializers.ValidationError("There are no lines to reprocess")

        except:
            raise serializers.ValidationError("Fail to get Worksheet Lines")

