from enum import Enum

class ProcessingStatus(Enum):
    AWAITING_PROCESSING = "1"
    QUEUED_FOR_PROCESSING = "2"
    PROCESSING = "3"
    PROCESSED_SUCCESSFULLY = "4"
    ERROR_PROCESSING = "5"
    PROCESSED = '6'

    @staticmethod
    def get_status_name(value):
        # Convert value to string to handle both string and integer inputs
        value = str(value)
        return {
            "1": "aguardando processamento",
            "2": "em fila para processamento",
            "3": "processando",
            "4": "processado com sucesso",
            "5": "erro ao processar",
            "6": "processamento finalizado"
        }.get(value, "status desconhecido")

    @staticmethod
    def get_status_value(status_name):
        # Converte o nome do status (string) de volta para o valor do enum
        return {
            "aguardando processamento": "1",
            "em fila para processamento": "2",
            "processando": "3",
            "processado com sucesso": "4",
            "erro ao processar": "5",
            "processamento finalizado":"6"
        }.get(status_name, None)

class AutomationErrorStatus(Enum):
    OBJECT_CANNOT_BE_FOUND = "tag não pode ser encontrada: "
    OBJECT_CANNOT_BE_CLICKED = "tag não pode ser clicada: "
    OBJECT_CANNOT_BE_FILLED = "tag não pode ser preenchida: "
    OBJECT_CANNOT_BE_SUBMITTED = "tag não pode ser confirmada: "
    OBJECT_CANNOT_BE_SWITCHED = "iframe não pode ser trocado: "
    OBJECT_CANNOT_BE_SELECTED = "tag não pode ser selecionada: "

    @staticmethod
    def return_error(moment, problematic_field, status):
        error_message = (
            f"ETAPA:{moment} ERRO: "
             f"{status} "
             f"id({problematic_field})"
        )
        return error_message
