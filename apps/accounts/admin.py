from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import LoginAttempt, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_staff', 'date_joined']
    search_fields = ['username', 'email']
    list_filter = ['is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil', {'fields': ('bio',)}),
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Solo lectura y borrado: las filas las escribe la señal de login fallido.

    Sirve para dos cosas: ver si alguien está probando contraseñas y desbloquear
    una IP (incluida la propia) borrando sus intentos.
    """

    list_display = ['created_at', 'ip_address', 'username']
    list_filter = ['created_at']
    search_fields = ['ip_address', 'username']
    date_hierarchy = 'created_at'
    readonly_fields = ['ip_address', 'username', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
