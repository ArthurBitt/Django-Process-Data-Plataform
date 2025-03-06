from apps.core.models import CoreLines, CoreTable

from django.db import models

from apps.worksheets import constants

"""
Generic Pattern for Worksheet Models - Uploaded and Processed Data
note: same uploaded data are processed and monitored optimizing the storage with only one table 
for worksheet and lines
"""

class Worksheet(CoreTable):
    class Meta:
        verbose_name = "Planilha"
        verbose_name_plural = "Planilhas"


    def generate_excel(self, temp_dir: str, *args) -> str or None:
        lines = WorksheetLine.objects.filter(worksheet_id=self)
        return super().generate_excel(
            temp_dir,
            lines,
            constants.WorksheetsColumnMappings.get('report'),
            "worksheet"
        )

class WorksheetLine(CoreLines):
    worksheet_id = models.ForeignKey(Worksheet, db_column='worksheet_id',on_delete=models.CASCADE, related_name='worksheet_lines')
    class Meta:
        verbose_name = "Linha"
        verbose_name_plural = "Linhas"