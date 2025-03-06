from config.settings import (
    ID_TEMPLATE_COMPLETED_WORKSHEET,
    ENDPOINT_SQAD_MAIL,
    SQAD_MAIL_TOKEN,
)

import requests
import json


def send_mail(
    subject: str,
    recipient: list,
    template: str,
    context: dict,
    document=None,
    email: str = "noreply@squadytecnologia.com.br",
):
    try:
        url = f"{ENDPOINT_SQAD_MAIL}/send/"

        templates = {
            "completed_worksheet": {
                "id": ID_TEMPLATE_COMPLETED_WORKSHEET,
            }
        }

        if not templates.get(template):
            """Caso o parâmetro template não exista no
            dicionário 'templates', um erro é retornado"""

            return "ERROR: Parâmetro 'template' não\
             existe nos templates cadastrados"

        headers = {
            "Authorization": f"Bearer {SQAD_MAIL_TOKEN}",
        }

        file = None
        if document:
            with open(document, "rb") as document_file:
                content = document_file.read()

            file = {
                "attach": (
                    str(document).split("/")[-1],
                    content,
                    "application/xlsx",
                )
            }

        payload = {
            "data": json.dumps(
                {
                    "subject": subject,
                    "from_email": email,
                    "recipient_list": recipient,
                    "template_id": templates[template]["id"],
                    "context_template": context,
                }
            )
        }

        r = requests.post(
            url, files=file, data=payload, headers=headers, timeout=60
        )

        return r
    except Exception as e:
        print(
            f"""
        Função: apps.mail.views.send_mail
        tipo erro: {type(e)}
        mensagem: {e}
        """
        )
        return str(e)
