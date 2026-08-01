from django.contrib import admin

from . import content
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'service_label', 'created_at']
    search_fields = ['name', 'email', 'company']
    list_filter = ['service_interest', 'created_at']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'

    @admin.display(description='servicio de interés')
    def service_label(self, obj):
        return dict(content.service_choices()).get(obj.service_interest, obj.service_interest)
