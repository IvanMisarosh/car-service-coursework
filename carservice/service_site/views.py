from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from . import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
import uuid
from . import filters
from . import forms

class Visits(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_customer']
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get("page", 1)
        items_per_page = int(request.GET.get("items_per_page", 10))

        visits = models.Visit.objects.all().select_related(
            'visit_status', 'car', 'car__customer', 'car__car_model', 'employee', 'payment_status').order_by('-visit_date')


        paginator = Paginator(visits, items_per_page)
        page_obj = paginator.get_page(page_number)

        context = {
            "visits": page_obj,
        }

        return render_htmx(request, "service_site/visits.html", "service_site/includes/visit_list.html", context)
    
class VisitDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_customer']
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        visit_id = kwargs.get('visit_id')

        if not visit_id:
            return render(request, "service_site/visit_details.html", {
                "visit_form": forms.VisitForm(),
            })
        
        visit = models.Visit.objects.select_related(
            'visit_status', 'car', 'car__customer', 'car__car_model', 'employee',
              'employee__employee_position', 'payment_status').prefetch_related('visit_services',
               'visit_services__provided_service', "visit_services__service", 'visit_services__service__service_type').get(pk=visit_id)
        
        context = {
            "visit": visit,
            "visit_services": visit.visit_services.all(),
            "visit_car": visit.car,
            "visit_customer": visit.car.customer,
            "visit_form": forms.VisitForm(instance=visit),
        }
        self.save_visit_data_in_session(request, visit)

        return render(request, "service_site/visit_details.html", context)
    
    def post(self, request, *args, **kwargs):
        visit_id = kwargs.get('visit_id')

        if not visit_id:
            visit_id = request.POST.get('visit_id', None)

        if visit_id:
            visit = models.Visit.objects.get(pk=visit_id)
            form = forms.VisitForm(request.POST, instance=visit)
        else:
            form = forms.VisitForm(request.POST)
            form.instance.visit_number = models.Visit.generate_visit_number()

        if form.is_valid():
            visit = form.save()
            return redirect('visit-detail', visit_id=visit.pk)
        else:
            print("Form is not valid")
            print(form.errors)
            print(form.instance)
            # If form is not valid, re-render the page with errors
            print(form.instance.visit_services.all())
            return render(request, "service_site/visit_details.html", {
                "visit_form": form,
                "visit_car": form.instance.car,
                "visit_customer": form.instance.car.customer, 
                "visit": form.instance,
                "visit_services": form.instance.visit_services.all(),
            })

    def save_visit_data_in_session(self, request, visit):
        request.session['visit_id'] = visit.pk
    

# Create your views here.
@login_required()
def index(request):
    return render(request, 'service_site/index.html', {
        'title': 'Home',
    })

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

    return render(request, "service_site/includes/selected_customer_details.html", context)


@login_required
@permission_required('service_site.view_customer', raise_exception=True)
def customer_list(request):
    page_number = request.GET.get("page", 1)
    items_per_page = int(request.GET.get("items_per_page", 10))
    sorting_method = request.GET.get("sorting_method", "first_name")

    customers = models.Customer.objects.all().order_by(sorting_method)

    customer_filter = filters.CustomerFilter(request.GET, customers)

    paginator = Paginator(customer_filter.qs, items_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        "customers": page_obj,
        "form": customer_filter.form,
    }

    return render_htmx(request, "service_site/customers.html", "service_site/includes/customers_list.html", context)

def car_search(request):
    search_query = request.GET.get("search", "")
    
    search_terms = search_query.split()
    query = Q()
    
    for term in search_terms:
        query |= Q(car_model__car_brand__brand_name__icontains=term) | \
                 Q(car_model__model_name__icontains=term) | \
                 Q(customer__first_name__icontains=term) | \
                 Q(customer__last_name__icontains=term) | \
                 Q(customer__phone_number__icontains=term)
    
    cars = models.Car.objects.select_related(
        'car_model', 'car_model__car_brand', 'customer'
    ).filter(query).distinct()
    
    return render(request, "service_site/includes/car_search_result.html", {
        "car_selection": cars,
    })

def service_search(request):
    search_query = request.GET.get("search", "")
    
    search_terms = search_query.split()
    query = Q()
    
    for term in search_terms:
        query |= Q(service_name__icontains=term) | \
                 Q(service_type__service_type_name__icontains=term)
    
    services = models.Service.objects.select_related('service_type').filter(query).distinct().order_by('service_name')
    
    return render(request, "service_site/includes/service_search_result.html", {
        "service_selection": services,
    })

def update_visit_car(request):
    car_id = request.POST.get('selected_car_id')
    car = models.Car.objects.select_related(
        'customer', 'color', 'car_model', 'car_model__car_brand', 'car_model__suspension_type', 'car_model__engine_type',
        'car_model__transmission_type', 'car_model__drive_type', 'car_model__body_type'
    ).get(pk=car_id)

    context = {
        "visit_car": car,
        "visit_customer": car.customer,
    }

    return render(request, "service_site/includes/visit_car_details.html", context)

def select_car_in_car_search_modal(request):
    car_id = request.POST.get('car_id')
    car = models.Car.objects.select_related(
        'customer', 'color', 'car_model', 'car_model__car_brand', 'car_model__suspension_type', 'car_model__engine_type',
        'car_model__transmission_type', 'car_model__drive_type', 'car_model__body_type'
    ).get(pk=car_id)

    context = {
        "visit_car": car,
        "visit_customer": car.customer,
    }

    return render(request, "service_site/includes/car_details.html", context)

def add_staged_service(request):
    service_id = request.POST.get('service_id')
    visit_id = request.POST.get('visit_id')
    
    service = models.Service.objects.get(pk=service_id)
    
    # Create a unique ID for this staged service
    temp_id = str(uuid.uuid4())
    
    # Get or initialize the staged services list in session
    staged_services = request.session.get(f'staged_services_{visit_id}', [])
    
    # Add the new staged service to the list
    staged_service = {
        'temp_id': temp_id,
        'service_id': service_id,
        'service_name': service.service_name,
        'service_type_name': service.service_type.service_type_name,
        'price': float(service.price),
        'quantity': 1,
        'description': service.description
    }
    
    staged_services.append(staged_service)
    
    # Save back to session
    request.session[f'staged_services_{visit_id}'] = staged_services
    request.session.modified = True
    
    context = {
        "staged_service": staged_service,
        "visit_id": visit_id
    }

    return render(request, "service_site/includes/staged_visit_service.html", context)

def update_staged_service(request):
    temp_id = request.POST.get('temp_id')
    visit_id = request.POST.get('visit_id')
    quantity = int(request.POST.get('quantity', 1))
    
    # Get the staged services from session
    staged_services = request.session.get(f'staged_services_{visit_id}', [])
    
    # Update the service with matching temp_id
    for service in staged_services:
        if service['temp_id'] == temp_id:
            service['quantity'] = quantity
            break
    
    # Save back to session
    request.session[f'staged_services_{visit_id}'] = staged_services
    request.session.modified = True
    
    return HttpResponse("")  

def remove_staged_service(request):
    temp_id = request.POST.get('temp_id')
    visit_id = request.POST.get('visit_id')
    
    # Get the staged services from session
    staged_services = request.session.get(f'staged_services_{visit_id}', [])
    
    # Remove the service with matching temp_id
    staged_services = [s for s in staged_services if s['temp_id'] != temp_id]
    
    # Save back to session
    request.session[f'staged_services_{visit_id}'] = staged_services
    request.session.modified = True
    
    return HttpResponse("")  

def save_staged_services(request):
    visit_id = request.POST.get('visit_id')
    visit = models.Visit.objects.get(pk=visit_id)
    # Get the staged services from session
    staged_services = request.session.get(f'staged_services_{visit_id}', [])
    
    # Create actual database records
    for staged in staged_services:
        service = models.Service.objects.get(pk=staged['service_id'])
        v_s = models.VisitService.objects.create(
            visit=visit,
            service=service,
            quantity=staged['quantity'],
        )
    
    # Clear the session data
    if f'staged_services_{visit_id}' in request.session:
        del request.session[f'staged_services_{visit_id}']
        request.session.modified = True
    
    visit_services = models.VisitService.objects.filter(visit=visit).select_related(
        'service', 'service__service_type', 'provided_service').order_by('-provided_service__provided_date')
    
    return render(request, 'service_site/includes/visit_services.html', 
        {
            'visit_services': visit_services,
        }
    )

def clear_staged_services(request):
    visit_id = request.POST.get('visit_id')
    
    # Clear the staged services for this visit from the session
    if f'staged_services_{visit_id}' in request.session:
        del request.session[f'staged_services_{visit_id}']
        request.session.modified = True
    
    # Return an empty response or a success message
    return redirect('visit-detail', visit_id=visit_id)

def delete_visit_service(request, visit_service_id):
    
    # Get the VisitService object and delete it
    visit_service = models.VisitService.objects.get(pk=visit_service_id)
    visit_service.delete()
    
    return HttpResponse("") 



def render_htmx(request, template_full, template_partial, context):
    if request.htmx:
        return render(request, template_partial, context)
    else:
        return render(request, template_full, context)
