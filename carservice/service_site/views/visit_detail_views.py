from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
import uuid
from .. import forms


class VisitDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_customer']
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        visit_id = kwargs.get('visit_id')

        if not visit_id:
            return render(request, "service_site/visits/visit_details.html", {
                "visit_form": forms.VisitForm(),
            })
        
        visit = models.Visit.objects.select_related(
            'visit_status', 'car', 'car__customer', 'car__car_model', 'employee',
              'employee__employee_position', 'payment_status').prefetch_related('visit_services',
               'visit_services__provided_service', 'visit_services__provided_service__employee',
                'visit_services__provided_service__required_parts', "visit_services__service", 
                 'visit_services__service__service_type').get(pk=visit_id)
        
        context = {
            "visit": visit,
            "visit_services": visit.visit_services.all(),
            "visit_car": visit.car,
            "visit_customer": visit.car.customer,
            "visit_form": forms.VisitForm(instance=visit),
        }

        return render(request, "service_site/visits/visit_details.html", context)
    
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

            car = getattr(form.instance, 'car', None)
            visit_services = getattr(form.instance, 'visit_services', None)
            
            context = {
                "visit_form": form,
                "visit_car": form.instance.car if car else None,
                "visit_customer": form.instance.car.customer if car else None, 
                "visit": form.instance if form.instance.pk else None,
                "visit_services": visit_services.all() if form.instance.pk else None,
            }
            print(context)
            return render(request, "service_site/visits/visit_details.html", context)

class VisitServiceView(View):
    def get_object(self, visit_service_id):
        return models.VisitService.objects.select_related(
            'service', 'service__service_type', 'provided_service', 
            'provided_service__employee', 'visit'
        ).prefetch_related('provided_service__required_parts').get(pk=visit_service_id)

    def post(self, request, visit_service_id):
        visit_service = self.get_object(visit_service_id)

        qty = int(request.POST.get('quantity', 1))
        if qty > 0:
            visit_service.quantity = qty
            visit_service.save()

        context = {
            "v_service": visit_service,
            "v_price": float(visit_service.visit.price)
        }

        # TODO: find a way to update the visit price after adding/deleting a service without refreshing the page
        response = render(request, "service_site/visits/_visit_service.html", context)
        response["HX-Refresh"] = "true" 
        return response

    def delete(self, request, visit_service_id):
        visit_service = get_object_or_404(models.VisitService, pk=visit_service_id)
        visit_service.delete()
        # TODO: find a way to update the visit price after adding/deleting a service without refreshing the page
        response = HttpResponse("")
        response["HX-Refresh"] = "true"
        return response

# Create your views here.
@login_required()
def index(request):
    return render(request, 'service_site/index.html', {
        'title': 'Home',
    })

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
    
    return render(request, "service_site/visits/_car_search_result.html", {
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
    
    return render(request, "service_site/visits/_service_search_result.html", {
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

    return render(request, "service_site/visits/_visit_car_details.html", context)

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

    return render(request, "service_site/visits/_car_details.html", context)

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

    return render(request, "service_site/visits/_staged_visit_service.html", context)

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
    
    print(visit_services)
    return render(request, 'service_site/visits/_visit_services.html', 
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