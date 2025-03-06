from rest_framework.exceptions import APIException

from apps.worksheets.models import Worksheet, WorksheetLine
from apps.worksheets.serializers import (
    UploadSerializer,
    DownloadReportSerializer,
    ListProcessDataSerializer,
    ListWorksheetLinesSerializer,
    ReprocessWorksheetSerializer,
)

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.http import HttpResponse


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow staff or admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser

class UploadView(APIView):
    """
    View for uploading XLSX files.
    :param file: XLSX file (required)
    :param upload_type: Type of upload (required)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    @staticmethod
    def post(request, *args, **kwargs):
        serializer = UploadSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            worksheet = serializer.save()
            return Response({
                "message": "Dados XLSX processados com sucesso!",
                "table_id": worksheet.id
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DownloadReportView(APIView):
    """
    View for downloading processed/processing spreadsheets.
    :param worksheet_id: UUID of the worksheet (required)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    @staticmethod
    def get(request, worksheet_id):
        serializer = DownloadReportSerializer(
            data={'worksheet_id': worksheet_id},
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            excel_buffer = serializer.create_excel_file(serializer.context['worksheet'])
            response = HttpResponse(
                excel_buffer.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = f'attachment; filename="planilha_{worksheet_id}.xlsx"'
            return response

        except Exception as e:
            return Response(
                {"error": f"Fail to genarete report: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ListProcessDataView(APIView):
    """
    View for listing processed data.
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    @staticmethod
    def get(request):
        worksheets = Worksheet.objects.all()

        if not worksheets.exists():
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(worksheets, request)

        serializer = ListProcessDataSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class ListWorksheetsLines(APIView):
    """
    View for listing worksheet lines.
    :param worksheet_id: UUID of the worksheet (required)
    :param status: Process status (optional, values between 1-5)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    serializer_class = ListWorksheetLinesSerializer
    pagination_class = PageNumberPagination

    def get(self, request, worksheet_id, *args, **kwargs):

        process_status = request.query_params.get('status')

        data = {
            'worksheet_id': worksheet_id,
            'process_status': process_status
        }

        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        queryset = WorksheetLine.objects.filter(
            worksheet_id=validated_data['worksheet_id']
        )

        if validated_data.get('process_status') is not None:
            queryset = queryset.filter(
                process_status=validated_data['process_status']
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = self.serializer_class(page if page is not None else queryset, many=True)

        return paginator.get_paginated_response(serializer.data) if page else Response(serializer.data)

class ReprocessWorksheet(APIView):
    """
    View for reprocessing a worksheet.
    :param worksheet_id: UUID of the worksheet (required)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    @staticmethod
    def post(request, worksheet_id):
        serializer = ReprocessWorksheetSerializer(
            data={'worksheet_id': worksheet_id},  # Passe o worksheet_id como dado
            context={
                'request': request,
                'worksheet_id': worksheet_id
            }
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.reprocess_worksheet()
            return Response(
                {"message": "Lines successfully queued for reprocessing"},
                status=status.HTTP_200_OK
            )

        except APIException as e:
            return Response(
                {"error": str(e.detail)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ReprocessLine(APIView):
    ...