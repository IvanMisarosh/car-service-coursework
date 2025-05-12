from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from .. import filters
from django.db.models import Q
from ..views_utils import render_htmx
from .. import resources
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .. import forms
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.template.loader import render_to_string
import json
from django.contrib import messages

@login_required
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
    print(request.GET.get('export_selection'))
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
        # Default to CSV if format not recognized
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    return response

@login_required
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
@permission_required('service_site.view_customer', raise_exception=True)
def customer_search(request):
    search = request.GET.get("search", '')
    search_terms = search.split()
    search_query = Q()

    for term in search_terms:
        search_query |= Q(first_name__icontains=term) | \
                Q(last_name__icontains=term) | \
                Q(email__icontains=term) | \
                Q(phone_number__icontains=term)

    customers = models.Customer.objects.prefetch_related('cars').filter(search_query).distinct()
    return render(request, "service_site/visits/_customer_search_result.html", 
                  {"customers": customers})

@login_required
@permission_required('service_site.view_customer', raise_exception=True)
def select_visit_customer(request):
    customer_id = request.GET.get("customer_id", None)
    customer = models.Customer.objects.prefetch_related(
        'cars__car_model', 'cars__car_model__car_brand', 'cars__car_model__suspension_type', 'cars__car_model__engine_type',
        'cars__car_model__transmission_type', 'cars__car_model__drive_type', 'cars__car_model__body_type'
    ).get(pk=customer_id)

    context = {
        'visit_customer': customer,
    }

    return render(request, "service_site/visits/_visit_customer_details.html", context)


def get_customer_search(request):
    return render(request, "service_site/visits/_customer_search.html")


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
            customer = car.customer
            
            # Fetch updated data for selected_customer_details
            customer_cars = models.Car.objects.filter(customer=customer)
            customer_visits = models.Visit.objects.filter(car__customer=customer).order_by('-visit_date')
            
            context = {
                "customer": customer,
                "customer_cars": customer_cars,
                "customer_visits": customer_visits
            }
            print(context)
            
            # Return both success message and updated customer details
            success_message = f'<div class="alert alert-success">Автомобіль {car} успішно збережено. ' \
                            f'<button type="button" class="btn-close float-end" ' \
                            f'onclick="document.getElementById(\'add-car-form-container\').innerHTML = \'\';"></button></div>'
            
            customer_details_html = render_to_string('service_site/customers/_selected_customer_details.html', context)
            
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'showMessage': success_message,
                'updateCustomerDetails': customer_details_html
            })
            return response
        
        # If form is invalid, return the form with errors
        context = {
            "form": form,
            "customer": models.Customer.objects.get(pk=customer_id) if customer_id else None
        }
        return render_htmx(request, None, "service_site/customers/_add_car_form.html", context)