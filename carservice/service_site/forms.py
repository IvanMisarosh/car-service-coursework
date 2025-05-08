from django.forms import ModelForm
from . import models
from django import forms
from django.urls import reverse_lazy

class CarModelForm(forms.ModelForm):
    class Meta:
        model = models.CarModel
        fields = [
            'model_name', 'car_brand', 'body_type', 'engine_type',
            'transmission_type', 'drive_type', 'suspension_type', 'dimensions'
        ]
        widgets = {
            'model_name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Назва моделі',
                'hx-get': reverse_lazy('check-model-name'),
                'hx-trigger': 'keyup',
                'hx-target': '#div_id_model_name',
                'hx-swap': 'outerHTML'
                },),
            'dimensions': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Розміри'}),
            'car_brand': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'body_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'engine_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'transmission_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'drive_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'suspension_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
        }

        def clean_model_name(self):
            model_name = self.clean_data["model_name"]
            if models.CarModel.objects.exists(model_name=model_name):
                return forms.ValidationError("Назва моделі має бути унікальна")
            return model_name

class SupplierForm(forms.ModelForm):
    class Meta:
        model = models.Supplier
        fields = ['supplier_name', 'email', 'phone_number']
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }

class ProcurementOrderInfoForm(forms.ModelForm):
    class Meta:
        model = models.ProcurementOrder
        fields = ['order_date', 'supplier', 'procurement_status', 'employee']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'supplier': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'procurement_status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'employee': forms.Select(attrs={'class': 'form-select form-select-sm', 'id': 'employee-select'}),
        }

class VisitForm(ModelForm):
    class Meta:
        model = models.Visit
        fields = ['visit_date', 'visit_status', 'car', 'employee', 'payment_status',
                   'details', 'planned_end_date', 'actual_end_date', 'payment_date']
        labels = {
            'visit_date': 'Visit Date',
            'visit_status': 'Visit Status',
            'car': 'Car',
            'employee': 'Employee',
            'payment_status': 'Payment Status',
            'details': 'Details',
            'planned_end_date': 'Planned End Date',
            'actual_end_date': 'Actual End Date',
            'payment_date': 'Payment Date',
        }
        widgets = {
            'visit_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
            'visit_status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'car': forms.HiddenInput(attrs={'class': 'form-select', 'id': 'car-hidden-input'}),
            'employee': forms.Select(attrs={'class': 'form-select select2'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'planned_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
            'actual_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = models.Employee.objects.order_by('first_name', 'last_name')