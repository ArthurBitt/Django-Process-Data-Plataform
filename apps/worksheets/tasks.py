from datetime import datetime
from celery import shared_task
from .models import Worksheet, WorksheetLine
from apps.utils.enums import ProcessingStatus
from apps.core.logs import log


@shared_task(
    name="task_validate_worksheet_status",
    queue="queue_validate_worksheet_status",
)
def task_validate_worksheet_status():

    def get_worksheet_lines(worksheet_id):
        return WorksheetLine.objects.filter(worksheet_id=worksheet_id, is_active=True).order_by("start_processing")

    def update_status(worksheet):
        worksheet_id = worksheet.id

        lines = get_worksheet_lines(worksheet_id).exclude(start_processing=None)
        if worksheet.start_processing is None and lines.exists():
                line = lines.first()
                worksheet.process_status = ProcessingStatus.PROCESSING.value
                worksheet.start_processing = line.start_processing
                worksheet.save()

        total_lines_count = get_worksheet_lines(worksheet_id).count()

        total_lines_processed_with_success_count = get_worksheet_lines(worksheet_id).filter(
            process_status__in=[
                ProcessingStatus.PROCESSED_SUCCESSFULLY.value,
            ]
        ).count()

        if total_lines_processed_with_success_count == total_lines_count:
            worksheet.process_status = ProcessingStatus.PROCESSED_SUCCESSFULLY.value
            worksheet.ending_processing = datetime.now()
            worksheet.save()

        else:
            total_lines_with_error_count = get_worksheet_lines(worksheet_id).filter(
                process_status__in=[
                    ProcessingStatus.ERROR_PROCESSING.value
                ]
            ).count()
            if total_lines_with_error_count == total_lines_count:
                worksheet.process_status = ProcessingStatus.ERROR_PROCESSING.value
                worksheet.ending_processing = datetime.now()
                worksheet.save()

            elif (total_lines_with_error_count + total_lines_processed_with_success_count) == total_lines_count:
                worksheet.process_status = ProcessingStatus.PROCESSED.value
                worksheet.ending_processing = datetime.now()
                worksheet.save()
            else:
                # not processed yet
                pass

    worksheets_to_process = Worksheet.objects.filter(
        process_status__in=[
            ProcessingStatus.AWAITING_PROCESSING.value,
            ProcessingStatus.PROCESSING.value
        ],
        is_active=True
    ).order_by("id")

    if not worksheets_to_process.exists():
        log.log_with_delay("There no worksheets to update status.")
        return

    for worksheet in worksheets_to_process:
        update_status(worksheet)

    log.log_with_delay("Ending task worksheet update status..")