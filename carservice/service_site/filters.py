import django_filters
from django import forms
from .models import Customer, Visit, CarBrand
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

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


class VisitFilter(django_filters.FilterSet):
    visit_date__gte = django_filters.DateFilter(
        field_name='visit_date', lookup_expr='gte', label='Visit Date From',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    visit_date__lte = django_filters.DateFilter(
        field_name='visit_date', lookup_expr='lte', label='Visit Date To',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    planned_end_date__gte = django_filters.DateFilter(
        field_name='planned_end_date', lookup_expr='gte', label='Planned End From',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    planned_end_date__lte = django_filters.DateFilter(
        field_name='planned_end_date', lookup_expr='lte', label='Planned End To',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    actual_end_date__gte = django_filters.DateFilter(
        field_name='actual_end_date', lookup_expr='gte', label='Actual End From',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    actual_end_date__lte = django_filters.DateFilter(
        field_name='actual_end_date', lookup_expr='lte', label='Actual End To',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    payment_date__gte = django_filters.DateFilter(
        field_name='payment_date', lookup_expr='gte', label='Payment Date From',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    payment_date__lte = django_filters.DateFilter(
        field_name='payment_date', lookup_expr='lte', label='Payment Date To',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )

    visit_status = django_filters.ModelChoiceFilter(
        queryset=Visit.visit_status.field.related_model.objects.all(),
        label='Visit Status',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    customer = django_filters.ModelChoiceFilter(
        field_name='car__customer',
        queryset=Customer.objects.all(),
        label='Customer',
        widget=forms.Select(attrs={'class': 'form-select select2'})
    )

    car_brand = django_filters.ModelChoiceFilter(
        field_name="car__car_model__car_brand",
        queryset=CarBrand.objects.all(),
        label='Car Brand',
        widget=forms.Select(attrs={'class': 'form-select select2'})
    )

    employee = django_filters.ModelChoiceFilter(
        queryset=Visit.employee.field.related_model.objects.all(),
        label='Employee',
        widget=forms.Select(attrs={'class': 'form-select select2'})
    )

    payment_status = django_filters.ModelChoiceFilter(
        queryset=Visit.payment_status.field.related_model.objects.all(),
        label='Payment Status',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    price__gte = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte', label='Min Price',
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'})
    )
    price__lte = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte', label='Max Price',
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'})
    )

    class Meta:
        model = Visit
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.form.helper = FormHelper()
        self.form.helper.form_method = 'get'
        self.form.helper.form_id = 'visit-filter-form'
        self.form.helper.layout = Layout(
            Row(
                Column('visit_date__gte', css_class='form-group col-md-6 mb-0 mt-2'),
                Column('visit_date__lte', css_class='form-group col-md-6 mb-0 mt-2')
            ),
            Row(
                Column('planned_end_date__gte', css_class='form-group col-md-6 mb-0'),
                Column('planned_end_date__lte', css_class='form-group col-md-6 mb-0')
            ),
            Row(
                Column('actual_end_date__gte', css_class='form-group col-md-6 mb-0'),
                Column('actual_end_date__lte', css_class='form-group col-md-6 mb-0')
            ),
            Row(
                Column('payment_date__gte', css_class='form-group col-md-6 mb-0'),
                Column('payment_date__lte', css_class='form-group col-md-6 mb-0')
            ),
            Row(
                Column('visit_status', css_class='form-group col-md-6 mb-0'),
                Column('payment_status', css_class='form-group col-md-6 mb-0')
            ),
            "customer",  
            "car_brand", 
            'employee',   
            Row(
                Column('price__gte', css_class='form-group col-md-6 mb-0'),
                Column('price__lte', css_class='form-group col-md-6 mb-0')
            ),
            Submit('submit', 'Search', css_class='btn btn-primary')
        )
