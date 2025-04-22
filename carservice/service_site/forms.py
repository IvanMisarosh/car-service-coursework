from django.forms import ModelForm
from . import models
from django import forms

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
            'visit_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'visit_status': forms.Select(attrs={'class': 'form-select'}),
            'car': forms.HiddenInput(attrs={'class': 'form-select', 'id': 'car-hidden-input'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'planned_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'actual_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = models.Employee.objects.order_by('first_name', 'last_name')