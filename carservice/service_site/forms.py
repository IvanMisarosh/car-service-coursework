from django.forms import ModelForm
from . import models
from django import forms
from django.urls import reverse_lazy
from django.utils import timezone

class CarForm(forms.ModelForm):
    class Meta:
        model = models.Car
        fields = ['vin', 'manufacture_year', 'car_model', 'customer', 'color', "mileage"]
        widgets = {
            'vin': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'manufacture_year': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'car_model': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'customer': forms.HiddenInput(),
            'color': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'vin': 'VIN-код',
            'manufacture_year': 'Рік випуску',
            'car_model': 'Модель авто',
            'color': 'Колір',
            'mileage': 'Пробіг',
        }
        help_texts = {
            'vin': 'Ідентифікаційний номер транспортного засобу',
        }

    def __init__(self, *args, **kwargs):
        customer_id = kwargs.pop('customer_id', None)
        super(CarForm, self).__init__(*args, **kwargs)
        
        if customer_id:
            self.fields['customer'].initial = customer_id

        self.fields['car_model'].required = True
        self.fields['car_model'].queryset = models.CarModel.objects.select_related('car_brand').all()

class StationForm(forms.ModelForm):
    class Meta:
        model = models.Station
        fields = ['address', 'phone_number']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Адреса станції',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Номер телефону',
            }),
        }

class PartForm(forms.ModelForm):
    class Meta:
        model = models.Part
        fields = ['part_name', 'part_brand', 'part_type', 'weight', 'dimensions', 
                  'description', 'quantity_per_package', 'price_per_package']
        widgets = {
            'part_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'part_brand': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'part_type': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'quantity_per_package': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'price_per_package': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
        }
        labels = {
            'part_name': 'Назва запчастини',
            'part_brand': 'Бренд',
            'part_type': 'Тип запчастини',
            'weight': 'Вага (кг)',
            'dimensions': 'Розміри',
            'description': 'Опис',
            'quantity_per_package': 'Кількість в упаковці',
            'price_per_package': 'Ціна за упаковку (₴)',
        }
        help_texts = {
            'weight': 'Вкажіть вагу в кілограмах',
            'dimensions': 'Наприклад: 10x20x5 см',
            'quantity_per_package': 'Скільки одиниць у кожній упаковці',
        }

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
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Розміри (наприклад: довжина x ширина x висота)'
            }),
            'car_brand': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'body_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'engine_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'transmission_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'drive_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
            'suspension_type': forms.Select(attrs={'class': 'form-select form-select-sm mt-1'}),
        }
        labels = {
            'model_name': 'Назва моделі',
            'car_brand': 'Бренд авто',
            'body_type': 'Тип кузова',
            'engine_type': 'Тип двигуна',
            'transmission_type': 'Тип трансмісії',
            'drive_type': 'Тип приводу',
            'suspension_type': 'Тип підвіски',
            'dimensions': 'Габарити',
        }
        help_texts = {
            'model_name': 'Введіть назву моделі авто',
            'dimensions': 'Наприклад: 4500 x 1800 x 1400 мм',
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
        labels = {
            'supplier_name': 'Назва постачальника',
            'email': 'Електронна пошта',
            'phone_number': 'Номер телефону',
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['email', 'first_name', 'last_name', 'phone_number']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'email': 'Електронна пошта',
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'phone_number': 'Номер телефону',
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
        labels = {
            'order_date': 'Дата замовлення',
            'supplier': 'Постачальник',
            'procurement_status': 'Статус замовлення',
            'employee': 'Працівник, відповідальний за замовлення',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

                # Правильний формат для HTML5 datetime-local
        dt_fields = ["order_date"]
        for field in dt_fields:
            value = self.initial.get(field) or self.instance.__dict__.get(field)
            if value:
                self.initial[field] = timezone.localtime(value).strftime('%Y-%m-%d')

class VisitForm(ModelForm):
    class Meta:
        model = models.Visit
        fields = ['visit_date', 'visit_status', 'car', 'employee', 'payment_status',
                   'details', 'planned_end_date', 'actual_end_date', 'payment_date']
        labels = {
            'visit_date': 'Дата візиту',
            'visit_status': 'Статус візиту',
            'car': 'Авто',
            'employee': 'Працівник',
            'payment_status': 'Статус оплати',
            'details': 'Details',
            'planned_end_date': 'Орієнтовна дата закінчення',
            'actual_end_date': 'Фактична дата закінчення',
            'payment_date': 'Дата оплати',
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

                # Правильний формат для HTML5 datetime-local
        dt_fields = ['visit_date', 'planned_end_date', 'actual_end_date', 'payment_date']
        for field in dt_fields:
            value = self.initial.get(field) or self.instance.__dict__.get(field)
            if value:
                self.initial[field] = timezone.localtime(value).strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        visit_status = cleaned_data.get('visit_status')
        
        # Assume we have a COMPLETED status with ID=2 (adjust as needed)
        COMPLETED_STATUS_ID = 2  # Replace with your actual completed status ID
        print(visit_status, visit_status.pk)
        # Check if the status is being changed to completed
        if visit_status and visit_status.pk == COMPLETED_STATUS_ID:
            # If it's a new visit being created as completed, skip validation
            if not self.instance.pk:
                raise forms.ValidationError("Не можна завершити візит без послуг.")
                
            # Get all services for this visit
            visit_services = self.instance.visit_services.all()
            print(visit_services)
            
            if not visit_services:
                # If no services are associated with this visit, raise validation error
                raise forms.ValidationError("Не можна завершити візит без послуг.")
            
            # Check if each service has an associated provided service
            missing_services = []
            for visit_service in visit_services:
                try:
                    # Try to get the related provided service
                    provided_service = visit_service.provided_service
                    if not provided_service:
                        missing_services.append(visit_service.service)
                except models.ProvidedService.DoesNotExist:
                    missing_services.append(visit_service.service)
            
            if missing_services:
                service_names = ', '.join([str(service) for service in missing_services])
                raise forms.ValidationError(
                    f"Не можна завершити візит. Наступні послуги не були виконані: {service_names}"
                )
                
            # Ensure actual_end_date is set when completing a visit
            if not cleaned_data.get('actual_end_date'):
                # self.add_error('actual_end_date', 'Фактична дата закінчення повинна бути встановлена для завершеного візиту.')
                cleaned_data['actual_end_date'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        
        return cleaned_data