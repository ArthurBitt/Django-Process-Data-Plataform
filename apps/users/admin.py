from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class UsersAdmin(UserAdmin):

    list_display = ('id','email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'last_login')

    list_filter = ('is_active', 'is_staff', 'is_superuser')

    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('id','username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    ordering = ('first_name',)

    readonly_fields = ('id', 'last_login', 'date_joined')

admin.site.register(User, UsersAdmin)