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


@admin.register(models.DriveType)
class DriveTypeAdmin(admin.ModelAdmin):
    list_display = ('drive_type_name',)
    fields = ('drive_type_name',)
    search_fields = ('drive_type_name',)
    ordering = ('drive_type_name',)

@admin.register(models.CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('brand_name',)
    fields = ('brand_name',)
    search_fields = ('brand_name',)
    ordering = ('brand_name',)

@admin.register(models.SuspensionType)
class SuspensionTypeAdmin(admin.ModelAdmin):
    list_display = ('suspension_type_name',)
    fields = ('suspension_type_name',)
    search_fields = ('suspension_type_name',)
    ordering = ('suspension_type_name',)

@admin.register(models.TransmissionType)
class TransmissionTypeAdmin(admin.ModelAdmin):
    list_display = ('transmission_type_name',)
    fields = ('transmission_type_name',)
    search_fields = ('transmission_type_name',)
    ordering = ('transmission_type_name',)

@admin.register(models.EngineType)
class EngineTypeAdmin(admin.ModelAdmin):
    list_display = ('engine_type_name',)
    fields = ('engine_type_name',)
    search_fields = ('engine_type_name',)
    ordering = ('engine_type_name',)

@admin.register(models.BodyType)
class BodyTypeAdmin(admin.ModelAdmin):
    list_display = ('body_type_name',)
    fields = ('body_type_name',)
    search_fields = ('body_type_name',)
    ordering = ('body_type_name',)

@admin.register(models.PartType)
class PartTypeAdmin(admin.ModelAdmin):
    list_display = ('part_type_name',)
    fields = ('part_type_name',)
    search_fields = ('part_type_name',)

@admin.register(models.PartBrand)
class PartBrandAdmin(admin.ModelAdmin):
    list_display = ('brand_name',)
    fields = ('brand_name',)
    search_fields = ('brand_name',)

@admin.register(models.EmployeePosition)
class EmployeePositionAdmin(admin.ModelAdmin):
    list_display = ('position_name',)
    fields = ('position_name',)
    search_fields = ('position_name',)

@admin.register(models.Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('address', "phone_number")  # або як в тебе називається поле
    search_fields = ('address',)

@admin.register(models.Part)
class PartAdmin(admin.ModelAdmin):
    list_display = (
        'part_name',
        'part_brand',
        'part_type',
        'weight',
        'quantity_per_package',
        'price_per_package'
    )
    search_fields = ('part_name',)
    list_filter = ('part_brand', 'part_type')
    autocomplete_fields = ('part_brand', 'part_type')

@admin.register(models.PartInStation)
class PartInStationAdmin(admin.ModelAdmin):
    list_display = ('station', 'part', 'get_part_type', 'get_part_brand', 'quantity')
    list_filter = ('station', 'part__part_type', 'part__part_brand')
    search_fields = ('part__part_name', 'station__address')
    autocomplete_fields = ('station', 'part')
    ordering = ('station', 'part')

    @admin.display(description='Part Type')
    def get_part_type(self, obj):
        return obj.part.part_type.part_type_name if obj.part and obj.part.part_type else '-'

    @admin.display(description='Part Brand')
    def get_part_brand(self, obj):
        return obj.part.part_brand.brand_name if obj.part and obj.part.part_brand else '-'