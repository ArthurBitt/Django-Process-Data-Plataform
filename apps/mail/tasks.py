import os
from datetime import datetime

from celery import shared_task
from apps.mail.views import send_mail

from apps.utils.enums import ProcessingStatus
from apps.worksheets.models import Worksheet
from apps.core.logs import log
from config.settings import DIRECTORY, EMAIL_TO


@shared_task(
    name="task_send_mail_report",
    queue="queue_send_mail_report",
)
def task_send_mail_report():
    """
    Here configs query with business rules to consider or not consider status.
    .
    """
    worksheets_processed = Worksheet.objects.filter(
        mail_sent=False,
        is_active=True,
        process_status__in=[
            ProcessingStatus.ERROR_PROCESSING.value,
            ProcessingStatus.PROCESSED_SUCCESSFULLY.value,
            ProcessingStatus.PROCESSED.value,
        ],
    ).all()

    for worksheet in worksheets_processed:
        if worksheet.mail_sent:
            log.log_with_delay(f"E-mail já foi enviado anteriormente para a planilha {worksheet.id}.")
            return

        try:
            report = worksheet.generate_excel(
                temp_dir=DIRECTORY,
            )
            if not report:
                log.log_with_delay(f"Nenhum dado encontrado na planilha {worksheet.id}.")
                return
        except Exception as e:
            log.log_with_delay(f"Erro ao gerar o arquivo Excel: {e}")
            return

        if report:
            message_context = f"Finalizado em: {datetime.now().strftime('%d/%m/%Y')} às {worksheet.ending_processing.strftime('%H:%M')}"
            message_status = ""

            if worksheet.process_status == ProcessingStatus.ERROR_PROCESSING.value:
                message_status = f"com Erro!:"
            elif worksheet.process_status == ProcessingStatus.PROCESSED_SUCCESSFULLY.value:
                message_status = f"com Sucesso!:"
            else:
                message_status = ""

            send_mail(
                subject=f"Worksheet {worksheet.id} - Processamento finalizado {message_status}",
                recipient=EMAIL_TO,
                template="completed_worksheet",
                context={
                    "%date%": message_context
                },
                document=report
            )
            worksheet.mail_sent = True
            worksheet.save()

        log.log_with_delay('E-mail enviado com sucesso!')
        try:
            os.remove(report)
            log.log_with_delay(f"Arquivo {report} removido com sucesso!")
        except Exception as e:
            print(f"Erro ao remover o arquivo: {e}")