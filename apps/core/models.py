import os

import pandas as pd
from django.db import models

from datetime import datetime
from uuid import uuid4
from apps.users.models import User
from apps.utils.enums import ProcessingStatus

class Core(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    process_status = models.CharField(
        max_length=30,
        blank=False,
        null=False,
        choices=[(status.value, ProcessingStatus.get_status_name(status.value)) for status in ProcessingStatus],
        default=ProcessingStatus.AWAITING_PROCESSING.value,
        verbose_name="Status do Processamento"
    )
    start_processing = models.DateTimeField(
        blank=True,
        null=True,
        auto_now=False,
        verbose_name="Incio do Processamento"
    )
    ending_processing = models.DateTimeField(
        blank=True,
        null=True,
        auto_now=False,
        verbose_name="Fim do Processamento"
    )

    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)

class CoreTable(Core):
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT, # is_active = False is the pattern used, but this is one more layer protection
        null=True,
        blank=False,
        related_name='%(app_label)s_%(class)s_created',
        verbose_name="Criado Por"
    )
    mail_sent = models.BooleanField(
        default=False,
        verbose_name="Email do lote enviado",
        blank=False,
        null=False
    )
    class Meta:
        abstract = True

    @staticmethod
    def _prepare_dataframe(df, column_mapping):
        # Rename colunas
        df.rename(columns=column_mapping, inplace=True)

        # fill NaN e change bools
        df = df.fillna("")
        df = df.replace({True: "Sim", False: "Não"})
        # replace numerical status for description
        status_col = "Status do Processamento"
        if status_col in df.columns:
            df[status_col] = df[status_col].astype(str).map(lambda x: ProcessingStatus.get_status_name(x))

        # Processa cada coluna para tratar datas
        for col in df.columns:
            processed_values = []

            # datetime columns - treating our models datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                # Remove fuso horário de todas as entradas
                df[col] = df[col].dt.tz_localize(None)
                continue  # Pula para próxima coluna


            # ensures download independently - treating entry data wrong date formats
            for value in df[col]:
                try:
                    # Tenta converter para datetime (UTC)
                    dt = pd.to_datetime(value, errors="coerce", utc=True)

                    if pd.isna(dt):  # Se falhou, mantém o original
                        processed_values.append(value)
                    else:  # Se OK, remove fuso horário
                        processed_values.append(dt.tz_localize(None))
                except Exception as e:
                    # Fallback para erros inesperados
                    print(f"Erro ao processar valor {value}: {e}")
                    processed_values.append(value)

            # update with treated values
            df[col] = processed_values

        return df

    def generate_excel(self, temp_dir: str, lines, column_mapping, file_prefix: str) -> str or None:
        if not lines.exists():
            return None

        data_for_worksheet = list(lines.values())
        df = pd.DataFrame(data_for_worksheet)

        if 'data' in df.columns:
            df_data_normalized = pd.json_normalize(df['data'].dropna())
            df = df.drop(columns=['data']).reset_index(drop=True)
            df_data_normalized = df_data_normalized.reindex(df.index, fill_value=None)
            df = pd.concat([df, df_data_normalized], axis=1)

        df = self._prepare_dataframe(df, column_mapping)

        file_name = os.path.join(temp_dir, f"{file_prefix}_{self.id}.xlsx")
        df.to_excel(file_name, index=False)
        return file_name

class CoreLines(Core):
    details = models.CharField(default="",max_length=255, blank=True, null=True, verbose_name="Detalhes do Processamento")
    data = models.JSONField()

    class Meta:
        abstract = True
