from django.contrib import admin
from .models import (
    Worksheet,
    WorksheetLine,
)


@admin.register(Worksheet)
class WorksheetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_by',
        'created_at',
        'updated_at',
        'process_status',
        'start_processing',
        'ending_processing',
        'is_active',
    )
    search_fields = (
        'id',
        'created_by__email'
    )
    list_filter = (
        'process_status',
        'created_at',
        'updated_at',
        'start_processing',
        'ending_processing'
    )
    readonly_fields = ('id','created_by','is_active')
    ordering = ('created_at',)
    list_display_links = ('id',)

@admin.register(WorksheetLine)
class WorksheetLineAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'worksheet_id',
        'process_status',
        'start_processing',
        'ending_processing',
        'is_active'
    )
    search_fields = (
        'id',
        'worksheet_id__id',
        'process_status'
    )
    list_filter = (
        'worksheet_id',
        'process_status',
        'start_processing',
        'ending_processing'
    )
    # readonly_fields = ('id','is_active', 'worksheet_id')
    ordering = ('created_at',)
    list_display_links = ('id',)


