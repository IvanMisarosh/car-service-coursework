from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.urls import reverse
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
import uuid
from .. import forms
from ..views_utils import group_required
from .. import resources
from datetime import datetime
from django.http import HttpResponse

@login_required
def export_visit_services(request, visit_id):
    """
    Export visit services data to various formats.
    Supported formats: csv, json
    """
    format = request.GET.get('format', 'csv')
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})
    
    visit_services = models.VisitService.objects.all().select_related(
        'visit', 'service', 'visit__car', 
        'visit__visit_status', 'visit__payment_status'
    ).filter(visit__visit_id = visit_id)
    
    resource = resources.VisitServiceResource()
    dataset = resource.export(visit_services)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'visit_services_{timestamp}'
    
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

def visit_info(request, visit_id):
    visit = models.Visit.objects.select_related(
        'visit_status', 'car', 'car__customer', 'car__car_model', 'employee',
            'employee__employee_position', 'payment_status').prefetch_related('visit_services',
            'visit_services__provided_service', 'visit_services__provided_service__employee',
            'visit_services__provided_service__required_parts', "visit_services__service", 
                'visit_services__service__service_type').get(pk=visit_id)
    
    context = {
        "visit": visit,
        "visit_id": visit.pk,
        # "visit_services": visit.visit_services.all(),
        "visit_car": visit.car,
        "visit_customer": visit.car.customer,
        "visit_price": visit.price,
    }
    
    return render(request, "service_site/visits/_info.html", context)

def visit_details(request, visit_id):
    visit = models.Visit.objects.select_related(
        'visit_status', 'car', 'car__customer', 'car__car_model', 'employee',
            'employee__employee_position', 'payment_status').prefetch_related('visit_services',
            'visit_services__provided_service', 'visit_services__provided_service__employee',
            'visit_services__provided_service__required_parts', "visit_services__service", 
                'visit_services__service__service_type').get(pk=visit_id)
    
    context = {
        "visit": visit,
        "visit_id": visit.pk,
        "visit_services": visit.visit_services.all(),
        "visit_car": visit.car,
        "visit_customer": visit.car.customer,
        "visit_price": visit.price,
    }

    if request.user.is_authenticated and request.user.groups.filter(name='mechanic').exists():
        return render(request, "service_site/visits/visit_details_mechanic.html", context)
    
    return render(request, "service_site/visits/visit_details_manager.html", context)

def get_visit_form(request):
    visit_id = request.GET.get('visit_id', None)

    context = {}
    if not visit_id:
        context["visit_form"] = forms.VisitForm()
        return render(request, "service_site/visits/visit_details_manager.html", context)
    else:
        visit = models.Visit.objects.select_related(
            'visit_status', 'car', 'car__customer', 'car__car_model', 'employee',
              'employee__employee_position', 'payment_status').prefetch_related('visit_services',
               'visit_services__provided_service', 'visit_services__provided_service__employee',
                'visit_services__provided_service__required_parts', "visit_services__service", 
                 'visit_services__service__service_type').get(pk=visit_id)
        v_form = forms.VisitForm(instance=models.Visit.objects.get(pk=visit_id))
        context["visit_car"] = visit.car
        context["visit_customer"] = visit.car.customer
        context["visit"] = visit
        context["visit_price"] = visit.price
        context['visit_form'] = v_form
        context["visit_id"] = visit_id
        return render(request, "service_site/visits/_form.html", context)


def save_visit_form(request):
    visit_id = request.POST.get('visit_id')
    
    if visit_id:
        visit = models.Visit.objects.get(pk=visit_id)
        form = forms.VisitForm(request.POST, instance=visit)
    else:
        form = forms.VisitForm(request.POST)
        form.instance.visit_number = models.Visit.generate_visit_number()

    if form.is_valid():
        visit = form.save()
        messages.success(request, f"Візит №{visit.visit_number} був успішно збережений.")
        print("coocked")
        response = HttpResponse()
        response['HX-Redirect'] = reverse('visit-detail', kwargs={'visit_id': visit.pk})
        return response
    else:
        car = getattr(form.instance, 'car', None)
        print("not coocked")
        visit_services = getattr(form.instance, 'visit_services', None)
        context = {
            "visit_form": form,
            "visit_car": form.instance.car if car else None,
            "visit_customer": form.instance.car.customer if car else None,
            "visit": form.instance if form.instance.pk else None,
            "visit_services": visit_services.all() if form.instance.pk else None,
            "visit_price": form.instance.price if form.instance.pk else None,
            "is_edit_form": True,
        }
        return render(request, "service_site/visits/_form.html", context)


class VisitDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_customer']
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        visit_id = kwargs.get('visit_id')

        if not visit_id:
            return render(request, "service_site/visits/visit_details_manager.html", {
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
            "visit_id": visit.pk,
            "visit_services": visit.visit_services.all(),
            "visit_car": visit.car,
            "visit_customer": visit.car.customer,
            "visit_price": visit.price,
        }

        if request.user.is_authenticated and request.user.groups.filter(name='mechanic').exists():
            return render(request, "service_site/visits/visit_details_mechanic.html", context)
        
        # context['visit_form'] = forms.VisitForm(instance=visit)
        return render(request, "service_site/visits/visit_details_manager.html", context)
    
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
            messages.success(request, f"Візит №{visit.visit_number} був успішно збережений.")
            print("coocked")
            return redirect('visit-detail', visit_id=visit.pk)
        else:
            car = getattr(form.instance, 'car', None)
            print("not coocked")
            visit_services = getattr(form.instance, 'visit_services', None)
            context = {
                "visit_form": form,
                "visit_car": form.instance.car if car else None,
                "visit_customer": form.instance.car.customer if car else None,
                "visit": form.instance if form.instance.pk else None,
                "visit_services": visit_services.all() if form.instance.pk else None,
                "visit_price": form.instance.price if form.instance.pk else None,
                "is_edit_form": True,
            }
            return render(request, "service_site/visits/visit_details_manager.html", context)
        
class VisitServiceView(View):
    def get_object(self, visit_service_id):
        return models.VisitService.objects.select_related(
            'service', 'service__service_type', 'provided_service', 
            'provided_service__employee', 'visit'
        ).prefetch_related('provided_service__required_parts').get(pk=visit_service_id)
    
    def get(self, request, visit_service_id):
        visit_service = self.get_object(visit_service_id)
        context = {
            "visit_service": visit_service,
            "visit": visit_service.visit,
            "visit_price": visit_service.visit.price,
        }
        return render(request, "service_site/visits/_selected_visit_service.html", context)

    def post(self, request, visit_service_id):
        visit_service = self.get_object(visit_service_id)

        qty = int(request.POST.get('quantity', 1))
        if qty > 0:
            visit_service.quantity = qty
            visit_service.save()
            messages.success(request, f"Послуга була успішно збережена.")
        else:
            messages.error(request, "Кількість має бути вищою за 0.")
        return visit_services(request, visit_service.visit.pk)

    def delete(self, request, visit_service_id):
        visit_service = get_object_or_404(models.VisitService, pk=visit_service_id)
        visit_service.delete()
        return redirect('visit-services', visit_id=visit_service.visit.pk)

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

    temp_id = str(uuid.uuid4())

    staged_services = request.session.get(f'staged_services_{visit_id}', [])
    
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
    
    staged_services = request.session.get(f'staged_services_{visit_id}', [])

    for service in staged_services:
        if service['temp_id'] == temp_id:
            service['quantity'] = quantity
            break

    request.session[f'staged_services_{visit_id}'] = staged_services
    request.session.modified = True
    
    return HttpResponse("")  

def remove_staged_service(request):
    temp_id = request.POST.get('temp_id')
    visit_id = request.POST.get('visit_id')
    
    staged_services = request.session.get(f'staged_services_{visit_id}', [])
    
    staged_services = [s for s in staged_services if s['temp_id'] != temp_id]
    
    request.session[f'staged_services_{visit_id}'] = staged_services
    request.session.modified = True
    
    return HttpResponse("")  

def save_staged_services(request):
    visit_id = request.POST.get('visit_id')
    visit = models.Visit.objects.get(pk=visit_id)
    staged_services = request.session.get(f'staged_services_{visit_id}', [])
    
    for staged in staged_services:
        service = models.Service.objects.get(pk=staged['service_id'])
        v_s = models.VisitService.objects.create(
            visit=visit,
            service=service,
            quantity=staged['quantity'],
        )
    
    if f'staged_services_{visit_id}' in request.session:
        del request.session[f'staged_services_{visit_id}']
        request.session.modified = True

    return redirect('visit-services', visit_id=visit_id)

def visit_services(request, visit_id):
    visit = models.Visit.objects.get(pk=visit_id)
    
    visit_services = models.VisitService.objects.filter(visit=visit).select_related(
        'service', 'service__service_type', 'provided_service').order_by('-provided_service__provided_date')

    return render(request, 'service_site/visits/_visit_services.html', 
        {   
            'visit': visit,
            'visit_services': visit_services,
            "visit_price": models.Visit.objects.get(pk=visit_id).price,
        }
    )

def clear_staged_services(request):
    visit_id = request.POST.get('visit_id')
    
    if f'staged_services_{visit_id}' in request.session:
        del request.session[f'staged_services_{visit_id}']
        request.session.modified = True
    
    return HttpResponse("")

def visit_service_with_part_search(request, visit_service_id):
    visit_service = models.VisitService.objects.get(pk=visit_service_id)
    part_brands = models.PartBrand.objects.all()
    part_types = models.PartType.objects.all()

    context = {
        "visit_service": visit_service,
        'part_brands': part_brands,
        'part_types': part_types,
    }

    if f'staged_parts_{visit_service_id}' in request.session:
        del request.session[f'staged_parts_{visit_service_id}']
        request.session.modified = True

    return render(request, "service_site/visits/_required_parts_search_widget.html", context)