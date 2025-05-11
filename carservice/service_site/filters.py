import django_filters
from django import forms
from .models import Customer, Visit, CarBrand, ProcurementOrder, Supplier, ProcurementStatus, BodyType, DriveType, EngineType
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

class ProcurementOrderFilter(django_filters.FilterSet):
    class Meta:
        model = ProcurementOrder
        fields = {}
    
    order_date__gte = django_filters.DateFilter(
        field_name='order_date', lookup_expr='gte', label='Дата замовлення з',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    order_date__lte = django_filters.DateFilter(
        field_name='order_date', lookup_expr='lte', label='Дата замовлення до',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )

    procurement_status = django_filters.ModelChoiceFilter(
        field_name='procurement_status__status_name',
        queryset=ProcurementStatus.objects.all(),
        label='Статус замовлення',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    supplier = django_filters.ModelMultipleChoiceFilter(
        field_name='supplier__supplier_name',
        queryset=Supplier.objects.all(),
        label='Постачальник',
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2'})
    )

class CustomerFilter(django_filters.FilterSet):
    car_brand = django_filters.ModelMultipleChoiceFilter(
        field_name="cars__car_model__car_brand",
        queryset=CarBrand.objects.all(),
        label="Бренд авто",
        widget=forms.SelectMultiple(attrs={"class": "form-select select2"})
    )

    body_type = django_filters.ModelMultipleChoiceFilter(
        field_name="cars__car_model__body_type",
        queryset=BodyType.objects.all(),
        label="Тип кузову",
        widget=forms.SelectMultiple(attrs={"class": "form-select select2"})
    )

    drive_type = django_filters.ModelChoiceFilter(
        field_name="cars__car_model__drive_type",
        queryset=DriveType.objects.all(),
        label="Тип приводу",
        widget=forms.Select(attrs={"class": "form-select select2"})
    )

    engine_type = django_filters.ModelChoiceFilter(
        field_name="cars__car_model__engine_type",
        queryset=EngineType.objects.all(),
        label="Тип двигуна",
        widget=forms.Select(attrs={"class": "form-select select2"})
    )

    visit_date_from = django_filters.DateFilter(
        field_name="cars__visits__visit_date",
        lookup_expr="gte",
        label="Візит з",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    visit_date_to = django_filters.DateFilter(
        field_name="cars__visits__visit_date",
        lookup_expr="lte",
        label="Візит до",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = Customer
        fields = []



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

    car_brand = django_filters.ModelMultipleChoiceFilter(
        field_name="car__car_model__car_brand",
        queryset=CarBrand.objects.all(),
        label='Car Brand',
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2'})
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
