from django.shortcuts import render, redirect
from django.urls import reverse
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from .. import forms
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_visit'], raise_exception=True)
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
        "visit_car": visit.car,
        "visit_customer": visit.car.customer,
        "visit_price": visit.price,
    }
    
    return render(request, "service_site/visits/_info.html", context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_visit'], raise_exception=True)
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

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.change_visit'], raise_exception=True)
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

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visit'], raise_exception=True)
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
        response = HttpResponse()
        response['HX-Redirect'] = reverse('visit-detail', kwargs={'visit_id': visit.pk})
        return response
    else:
        car = getattr(form.instance, 'car', None)
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