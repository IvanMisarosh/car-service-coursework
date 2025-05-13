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
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'employee_position', 'station')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('employee_position', 'station')
    ordering = ('last_name', 'first_name')

@admin.register(models.ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('service_type_name',)
    search_fields = ('service_type_name',)
    ordering = ('service_type_name',)


@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'service_type', 'price')
    list_filter = ('service_type',)
    search_fields = ('service_name',)
    ordering = ('service_name',)


@admin.register(models.VisitStatus)
class VisitStatusAdmin(admin.ModelAdmin):
    list_display = ('status_name', )
    search_fields = ('status_name',)
    ordering = ('status_name',)


@admin.register(models.PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('payment_name', )
    search_fields = ('payment_name',)
    ordering = ('payment_name',)