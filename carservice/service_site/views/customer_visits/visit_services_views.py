from django.shortcuts import render, redirect, get_object_or_404
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .. import resources
from ...domain import visit_services as visit_domain
from ... import exceptions
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import ProtectedError

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_visit'], raise_exception=True)
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


@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visitservice', 'service_site.view_visitservice'], raise_exception=True)
def edit_visit_service(request, visit_service_id):
    visit_service = get_object_or_404(models.VisitService, pk=visit_service_id)
    try:
        qty = int(request.POST.get('quantity', 1))
        visit_domain.update_visit_service_quantity(visit_service, qty)
    except (ValueError, TypeError):
        messages.error(request, "Невірний формат кількості.")
        return HttpResponse(status=400)
    except exceptions.InvalidVisitServiceData as e:
        messages.error(request, str(e))
        return HttpResponse(status=400)
    else:
        messages.success(request, "Послуга була успішно збережена.")

    return redirect('visit-services', visit_id=visit_service.visit.pk)

@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_visitservice', 'service_site.view_visitservice'], raise_exception=True)
def delete_visit_service(request, visit_service_id):
    visit_service = get_object_or_404(models.VisitService, pk=visit_service_id)
    visit_id = visit_service.visit.pk
    try:
        visit_domain.delete_visit_service(visit_service)
    except ProtectedError:
        messages.error(request, "Неможливо видалити виконану послугу.")
        return HttpResponse(status=400)
    else:
        messages.success(request, "Послугу успішно видалено")
    return redirect('visit-services', visit_id=visit_id)

@login_required
@require_http_methods(["GET", "POST", "DELETE"])
@permission_required(['service_site.view_visitservice'], raise_exception=True)
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


