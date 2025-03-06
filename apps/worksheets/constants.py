class RequiredColumns:
    __upload_required_columns = {
        'sheet_model_1': {
            '1': 'a',
            '2': 'b',
            '3': 'c',
            '4': 'd',
            '5': 'e'
        },
        'sheet_model_2': {
            '1': 'f',
            '2': 'g',
            '3': 'h',
            '4': 'i',
            '5': 'j'
        },
    }

    @classmethod
    def get(cls, upload_type):
        return {key: value.lower() for key, value in cls.__upload_required_columns.get(upload_type, {}).items()}

class WorksheetsColumnMappings:
    # Dicionário privado com os mapeamentos
    __COLUMN_MAPPINGS = {
        'report': {
            'id': 'Linha',
            'worksheet_id_id': 'Planilha',
            'process_status': 'Status do Processamento',
            'start_processing': 'Início do Processamento',
            'ending_processing': 'Fim do Processamento',
            'is_active': 'Esta ativo',
            'created_at': 'Foi criado em',
            'updated_at': 'Foi atualizado em',
            # insert here specif columns
        }
    }

    @classmethod
    def get(cls, mapping_type: str) -> dict:
        """Retorna uma cópia do mapeamento solicitado ou dicionário vazio se não existir"""
        return cls.__COLUMN_MAPPINGS.get(mapping_type.lower(), {}).copy()