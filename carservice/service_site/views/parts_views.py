from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
import uuid
from datetime import datetime

def part_search(request):
    search = request.GET.get("search", '')
    brand_id = request.GET.get("part_brand", None)
    part_type_id = request.GET.get("part_type", None)
    station_id = request.GET.get("station_id", None)
    search_terms = search.split()
    search_query = Q()

    if not station_id:
        return HttpResponse("Station ID is required.", status=400)

    station_parts = models.PartInStation.objects.prefetch_related(
        'part', 'part__part_brand', 'part__part_type'
    ).filter(station__station_id=station_id)

    for term in search_terms:
        search_query |= Q(part__part_brand__brand_name__icontains=term) | \
                       Q(part__part_type__part_type_name__icontains=term) | \
                       Q(part__part_name__icontains=term)
        
    if brand_id:
        search_query &= Q(part__part_brand__part_brand_id=brand_id)
    if part_type_id:
        search_query &= Q(part__part_type__part_type_id=part_type_id)
        
    parts = station_parts.filter(search_query).distinct()
    return render(request, "service_site/visits/_part_search_result.html", {'part_selection': parts})

def part_search_for_unit(request):
    brand_id = request.GET.get("part_brand", None)
    part_type_id = request.GET.get("part_type", None)

    search_query = Q()

    parts = models.Part.objects.prefetch_related('part_brand', 'part_type')
        
    if brand_id:
        search_query &= Q(part_brand__part_brand_id=brand_id)
    if part_type_id:
        search_query &= Q(part_type__part_type_id=part_type_id)
        
    parts = parts.filter(search_query).distinct()
    return render(request, "part_procurement/_unit_part_select.html", {'parts': parts})

def add_staged_part(request):
    part_id = request.POST.get('part_id')
    v_service_id = request.POST.get('visit_service_id')

    part_in_station = models.PartInStation.objects.select_related('part', 'part__part_brand', 'part__part_type').get(pk=part_id)
    part = part_in_station.part

    temp_id = str(uuid.uuid4())

    staged_parts = request.session.get(f'staged_parts_{v_service_id}', [])

    staged_part = {
        'temp_id': temp_id,
        'part_id': part_id,
        'part_name': part.part_name,
        'part_brand_name': part.part_brand.brand_name if part.part_brand else 'Unknown',
        'part_type_name': part.part_type.part_type_name if part.part_type else 'Unknown',
        'quantity_per_package': part.quantity_per_package,
        'avaliable_units': part.quantity_per_package * part_in_station.quantity,
        'price_per_package': float(part.price_per_package),
        'description': part.description,
        'quantity': 1,
        'price_per_unit': float(part.get_price_per_unit()),
    }

    staged_parts.append(staged_part)
    request.session[f'staged_parts_{v_service_id}'] = staged_parts
    request.session.modified = True

    context = {
        "staged_part": staged_part,
    }

    return render(request, "service_site/visits/_staged_required_part.html", context)

def update_staged_part(request):
    temp_id = request.POST.get('temp_id')
    v_service_id = request.POST.get('visit_service_id')
    quantity = int(request.POST.get('quantity', 1))

    staged_parts = request.session.get(f'staged_parts_{v_service_id}', [])

    for part in staged_parts:
        if part['temp_id'] == temp_id:
            # Check if quantity is greater than available units
            if quantity > part['avaliable_units']:
                # messages.error(request, f"Quantity exceeds available units ({part['avaliable_units']}).")
                # return HttpResponse("")
                part['quantity'] = part['avaliable_units']
            else:
                part['quantity'] = max(1, quantity)
            
            break

    request.session[f'staged_parts_{v_service_id}'] = staged_parts
    request.session.modified = True

    return HttpResponse("")

def remove_staged_part(request):
    temp_id = request.POST.get('temp_id')
    v_service_id = request.POST.get('visit_service_id')

    staged_parts = request.session.get(f'staged_parts_{v_service_id}', [])
    staged_parts = [p for p in staged_parts if p['temp_id'] != temp_id]

    request.session[f'staged_parts_{v_service_id}'] = staged_parts
    request.session.modified = True

    return HttpResponse("")

def save_staged_parts(request):
    v_service_id = request.POST.get('visit_service_id')
    staged_parts = request.session.get(f'staged_parts_{v_service_id}', [])
    visit_service = models.VisitService.objects.get(pk=v_service_id)
    employee = request.user.employee
    error = False

    if len(staged_parts) == 0:
        messages.error(request, "No parts staged.")
        error = True
        
    if models.ProvidedService.objects.filter(visit_service=visit_service).exists():
        
        messages.error(request, "This service has already been provided.")
        error = True

    if error:
        # TODO: figure out why hx-target-error doesn't work when status is 400
        response = render(request, "service_site/visits/_toast.html", status=200)
        return response

    provided_service = models.ProvidedService.objects.create(
        visit_service=visit_service,
        employee=employee,
        provided_date=datetime.now(),
    )

    for staged in staged_parts:
        part_in_station = models.PartInStation.objects.get(pk=staged['part_id'])
        models.RequiredPart.objects.create(
            provided_service=provided_service,
            part_in_station=part_in_station,
            quantity=staged['quantity']
        )

    if f'staged_parts_{v_service_id}' in request.session:
        del request.session[f'staged_parts_{v_service_id}']
        request.session.modified = True

    # return redirect('visit-services', visit_id=visit_id)
    response = HttpResponse("")
    response['HX-Refresh'] = 'true'
    return response

