from django.shortcuts import render, redirect
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import uuid
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q


@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visit'], raise_exception=True)
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

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visit'], raise_exception=True)
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

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visit'], raise_exception=True)
def remove_staged_service(request):
    temp_id = request.POST.get('temp_id')
    visit_id = request.POST.get('visit_id')
    
    staged_services = request.session.get(f'staged_services_{visit_id}', [])
    
    staged_services = [s for s in staged_services if s['temp_id'] != temp_id]
    
    request.session[f'staged_services_{visit_id}'] = staged_services
    request.session.modified = True
    
    return HttpResponse("")  

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visit'], raise_exception=True)
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

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visit'], raise_exception=True)
def clear_staged_services(request):
    visit_id = request.POST.get('visit_id')
    
    if f'staged_services_{visit_id}' in request.session:
        del request.session[f'staged_services_{visit_id}']
        request.session.modified = True
    
    return HttpResponse("")

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_visitservice'], raise_exception=True)
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