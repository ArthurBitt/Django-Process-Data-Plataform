from .views import UploadView, DownloadReportView, ListProcessDataView, ListWorksheetsLines, ReprocessWorksheet
from django.urls import path

urlpatterns = [
    path('list-worksheets-service/', ListProcessDataView.as_view(), name='list-data'),
    path('upload-service/', UploadView.as_view(), name='upload-data'),
    path('download-excel-report-service/<str:worksheet_id>/', DownloadReportView.as_view(), name='download-data'),
    path('reprocess-worksheet-service/<str:worksheet_id>/', ReprocessWorksheet.as_view(), name='reprocess-worksheet'),
    path('list-worksheet-lines-service/<str:worksheet_id>/', ListWorksheetsLines.as_view(), name='list-worksheet-lines'),
]

