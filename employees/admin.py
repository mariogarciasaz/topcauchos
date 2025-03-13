from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'position', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Posición', {'fields': ('position',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Posición', {'fields': ('position',)}),
    )