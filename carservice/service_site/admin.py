# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class CustomUserAdmin(UserAdmin):
    model = models.CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('employee',)}),
    )

admin.site.register(models.CustomUser, CustomUserAdmin)
@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'phone_number', 'employee_position', 'station')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('employee_position', 'station')
    ordering = ('last_name', 'first_name')