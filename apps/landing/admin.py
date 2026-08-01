from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'service_interest', 'created_at']
    search_fields = ['name', 'email', 'company']
    list_filter = ['service_interest', 'created_at']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
