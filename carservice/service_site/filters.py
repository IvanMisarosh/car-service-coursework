import django_filters
from django import forms
from .models import Customer

class CustomerFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        lookup_expr="startswith",
        label="First Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"})
    )
    
    last_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Last Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"})
    )

    email = django_filters.CharFilter(
        lookup_expr="startswith",
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )

    phone_number = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Phone Number",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number",})
    )

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone_number"]
