from django.shortcuts import render
from django.core.paginator import Paginator
from .. import models
from .. import filters
from ..views_utils import render_htmx
from .. import resources
from .. import forms
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.db.models.deletion import ProtectedError

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_customer'], raise_exception=True) 
def export_customers(request):
    """
    Export customer data with their cars to various formats.
    Supported formats: csv, xlsx, json
    """
    format = request.GET.get('format', 'csv')
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})
    
    sorting_method = request.GET.get("sorting_method", "first_name")
    search_query = request.GET.get("search", '')
    query = Q()

    search_terms = search_query.split()
    qs = None
    if request.GET.get('export_selection') == 'true':
        for term in search_terms:
            query |= Q(first_name__icontains=term) | Q(
                email__icontains=term) | Q(
                phone_number__icontains=term) | Q(
                last_name__icontains=term)
        customers = models.Customer.objects.all().filter(query).order_by(sorting_method)
        customer_filter = filters.CustomerFilter(request.GET, customers)
        qs = customer_filter.qs
    else:
        customers = models.Customer.objects.all().order_by(sorting_method)
        qs = customers

    resource = resources.CustomerResource()
    dataset = resource.export(qs)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'customers_with_cars_{timestamp}'
    
    if format == 'csv':
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    elif format == 'json':
        response = HttpResponse(dataset.json, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
    else:
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    return response

@login_required
@require_http_methods(["GET"])
@permission_required('service_site.view_customer', raise_exception=True)
def customer_details(request):
    customer_id = request.GET.get("customer_id", None)
    customer = models.Customer.objects.get(pk=customer_id)

    context = {
        'customer': customer,
        'customer_cars': customer.get_cars(),
        'customer_visits': customer.get_visits()
    }

    return render(request, "service_site/customers/_selected_customer_details.html", context)


@login_required
@require_http_methods(["GET"])
@permission_required('service_site.view_customer', raise_exception=True)
def customer_list(request):
    page_number = request.GET.get("page", 1)
    items_per_page = int(request.GET.get("items_per_page", 10))
    sorting_method = request.GET.get("sorting_method", "first_name")
    search_query = request.GET.get("search", '')

    search_terms = search_query.split()
    query = Q()

    for term in search_terms:
        query |= Q(first_name__icontains=term) | Q(
            email__icontains=term) | Q(
            phone_number__icontains=term) | Q(
            last_name__icontains=term)

    customers = models.Customer.objects.all().filter(query).order_by(sorting_method)

    customer_filter = filters.CustomerFilter(request.GET, customers)

    paginator = Paginator(customer_filter.qs, items_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        "customers": page_obj,
        "form": customer_filter.form,
    }

    return render_htmx(request, "service_site/customers/customers.html", "service_site/customers/_customers_list.html", context)

@login_required
@require_http_methods(["GET", "POST"])
@permission_required(['service_site.change_customer'], raise_exception=True) 
def get_customer_edit_row(request, pk):
    """
    Handle GET request to display the customer edit form
    Handle POST request to save the edited customer data
    """
    if request.method == 'GET':
        customer = get_object_or_404(models.Customer, pk=pk)
        
        # Get customer's last visit if it exists
        last_visit = models.Visit.objects.filter(car__customer=customer).order_by('-visit_date').first()
        if last_visit:
            customer.last_visit = last_visit
        
        context = {
            'customer': customer,
        }
        return render_htmx(request, None, "service_site/customers/_customer_edit_row.html", context)
    
    elif request.method == "POST":
        data = request.POST
        customer = get_object_or_404(models.Customer, pk=pk)
        
        # Update customer fields from form data
        customer.email = data.get('email', customer.email)
        customer.first_name = data.get('first_name', customer.first_name)
        customer.last_name = data.get('last_name', customer.last_name)
        customer.phone_number = data.get('phone_number', customer.phone_number)
        customer.save()
        
        # Get customer's last visit if it exists
        last_visit = models.Visit.objects.filter(car__customer=customer).order_by('-visit_date').first()
        if last_visit:
            customer.last_visit = last_visit
        
        context = {
            'customer': customer,
        }
        return render_htmx(request, None, "service_site/customers/_customer_list_row.html", context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_customer'], raise_exception=True) 
def get_customer_row(request, pk):
    """
    Return the normal display row for a customer (used for canceling edits)
    """
    customer = get_object_or_404(models.Customer, pk=pk)
    
    # Get customer's last visit if it exists
    last_visit = models.Visit.objects.filter(car__customer=customer).order_by('-visit_date').first()
    if last_visit:
        customer.last_visit = last_visit
    
    context = {
        'customer': customer,
    }
    return render_htmx(request, None, "service_site/customers/_customer_list_row.html", context)

@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_customer'], raise_exception=True) 
def delete_customer(request, customer_id):
    customer = get_object_or_404(models.Customer, pk=customer_id)
    try:
        customer_name = f"{customer.first_name} {customer.last_name}"
        customer.delete()
        messages.success(request, f"Клієнта {customer_name} успішно видалено")
        return HttpResponse("", status=200)
    except ProtectedError:
        messages.error(request, f"Неможливо видалити клієнта '{customer_name}', його авто мають записи про обслуговування.")
        context = {'customer': customer}
        return render(request, "customer/_customer_list_row.html", context)
    except Exception:
        messages.error(request, f"Сталася помилка при видаленні клієнта. Спробуйте пізніше.")
        context = {'customer': customer}
        return render(request, "service_site/customers/_customer_list_row.html", context)

class CustomerAddView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.change_customer', 'service_site.add_customer']
    login_url = '/login/'
    
    def get(self, request):
        form = forms.CustomerForm()
        return render_htmx(request, None, "service_site/customers/_add_customer_form.html", {"form": form})

    def post(self, request):
        form = forms.CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            
            # Render the new row for the customer table
            return render_htmx(request, None, "service_site/customers/_customer_list_row.html", {"customer": customer})
        return render_htmx(request, None, "service_site/customers/_add_customer_form.html", {"form": form})

@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_car'], raise_exception=True) 
def delete_car(request, car_id):
    car = get_object_or_404(models.Car, pk=car_id)
    try:
        vin = car.vin
        car.delete()
        messages.success(request, f"Автомобіль з VIN {vin} успішно видалено")
        return HttpResponse("", status=200)
    except ProtectedError:
        messages.error(request, f"Неможливо видалити авто '{car.vin}', оскільки є пов’язані записи.")
        context = {
            'car': car,
        }
        return render(request, "service_site/customers/_car_list_row.html", context)
    except Exception:
        return HttpResponse("Помилка під час видалення", status=500)    

class CarAddView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.change_car', 'service_site.add_car']
    login_url = '/login/'
    
    def get(self, request):
        customer_id = request.GET.get('customer_id')
        car_id = request.GET.get('car_id')
        if car_id:
            # Edit existing car
            car = get_object_or_404(models.Car, pk=car_id)
            form = forms.CarForm(instance=car)
            customer_id = car.customer_id
        else:
            # Add new car
            form = forms.CarForm(customer_id=customer_id) if customer_id else forms.CarForm()
        context = {
            "form": form,
            "customer": models.Customer.objects.get(pk=customer_id)
        }
        
        return render(request, "service_site/customers/_add_car_form.html", context)

    def post(self, request):
        car_id = request.POST.get('car_id')
        customer_id = request.POST.get('customer_id')
        
        if car_id:
            # Edit existing car
            car = get_object_or_404(models.Car, pk=car_id)
            form = forms.CarForm(request.POST, instance=car)
        else:
            # Add new car
            form = forms.CarForm(request.POST)
        
        if form.is_valid():
            car = form.save()   
            response = HttpResponse("")
            if car_id:
                response['HX-Trigger'] = f'update-car-{car.pk}'
            else:
                response['HX-Trigger'] = 'update-selected-customer-car-list'
            message = f'Авто {car.vin} успішно додано' if not car_id else f"Дані про авто {car.vin} успішно оновлені"
            messages.success(request, message)
            return response
        
        # If form is invalid, return the form with errors
        messages.error(request, "Додавання/збереження не вдалось, виправіть помилки на формі")
        context = {
            "form": form,
            "customer": models.Customer.objects.get(pk=customer_id) if customer_id else None
        }
        return render_htmx(request, None, "service_site/customers/_add_car_form.html", context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_customer'], raise_exception=True) 
def selected_customer_car_list_row(request, car_id):
    car = get_object_or_404(models.Car.objects.select_related(
        'customer', 'car_model__car_brand', 'car_model__body_type',
        'car_model__drive_type', 'car_model__suspension_type',
        'car_model__transmission_type', 'car_model__engine_type',
        'color'
    ), pk=car_id)
    
    return render(request, "service_site/customers/_selected_customer_car_list_row.html", {"car": car})

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_customer'], raise_exception=True) 
def selected_customer_car_list(request, customer_id):
    cars = models.Car.objects.select_related(
        'customer', 'car_model__car_brand', 'car_model__body_type',
        'car_model__drive_type', 'car_model__suspension_type',
        'car_model__transmission_type', 'car_model__engine_type',
        'color'
    ).filter(customer__customer_id = customer_id)
    
    return render(request, "service_site/customers/_selected_customer_car_list.html", {"customer_cars": cars, "customer": cars[0].customer})