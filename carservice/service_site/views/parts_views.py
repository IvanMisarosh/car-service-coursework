from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .. import models
from .. import forms
from ..views_utils import render_htmx
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
import uuid
from datetime import datetime
from django.core.paginator import Paginator
import json
from django.db.models import ProtectedError
from django.template.loader import render_to_string



class PartsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_part']
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get("page", 1)
        items_per_page = int(request.GET.get("items_per_page", 10))
        search_query = request.GET.get("search", '')

        search_terms = search_query.split()
        query = Q()

        for term in search_terms:
            query |= Q(part_name__icontains=term) | Q(
                description__icontains=term) | Q(
                part_brand__brand_name__icontains=term) | Q(
                part_type__part_type_name__icontains=term)

        parts = models.Part.objects.filter(query).select_related('part_brand', 'part_type').order_by('part_name')

        paginator = Paginator(parts, items_per_page)
        page_obj = paginator.get_page(page_number)

        part_types = models.PartType.objects.all().order_by('part_type_name')
        part_brands = models.PartBrand.objects.all().order_by('brand_name')

        context = {
            "parts": page_obj,
            "part_types": part_types,
            "part_brands": part_brands,
        }

        return render_htmx(request, "part/parts.html", "part/_part_list.html", context)

@login_required
def part_availability(request, part_id):
    """
    View to return part availability across different stations.
    This is designed to be loaded via HTMX.
    """
    part = get_object_or_404(models.Part, pk=part_id)
    part_in_stations = models.PartInStation.objects.filter(part=part).select_related('station')
    
    # Get all stations, including those without this part
    all_stations = models.Station.objects.all()
    
    # Create a dictionary of station_id: quantity for quick lookups
    availability_dict = {pis.station_id: pis.quantity for pis in part_in_stations}
    
    # Create a list of station availability info
    stations_availability = []
    for station in all_stations:
        stations_availability.append({
            'station': station,
            'quantity': availability_dict.get(station.station_id, 0),
            'is_available': station.station_id in availability_dict
        })
    
    context = {
        'part': part,
        'stations_availability': stations_availability
    }
    
    return render(request, 'part/_part_availability.html', context)


class PartFormView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.add_part']
    login_url = '/login/'

    def get(self, request):
        form = forms.PartForm()
        part_types = models.PartType.objects.all().order_by('part_type_name')
        part_brands = models.PartBrand.objects.all().order_by('brand_name')
        
        context = {
            "form": form,
            "part_types": part_types,
            "part_brands": part_brands,
        }
        return render_htmx(request, None, "part/_add_part_form.html", context)

    def post(self, request):
        form = forms.PartForm(request.POST)
        if form.is_valid():
            part = form.save()
            # Get part types and brands for the template
            part_types = models.PartType.objects.all().order_by('part_type_name')
            part_brands = models.PartBrand.objects.all().order_by('brand_name')
            
            # Render the new row for the part table
            return render_htmx(request, None, "part/_part_list_row.html", {
                "part": part, 
                "part_types": part_types,
                "part_brands": part_brands
            })
        
        print(form.errors)

        return HttpResponseBadRequest("")
    
def delete_part(request, part_id):
    part = get_object_or_404(models.Part, pk=part_id)
    try:
        part_name = part.part_name
        part.delete()
        messages.success(request, f"Запчастину '{part_name}' успішно видалено.")
        return HttpResponse("", status=200)
    except ProtectedError:
        messages.error(request, f"Неможливо видалити запчастину '{part.part_name}', оскільки вона використовується у послугах.")
        context = {'part': part}
        return render(request, "part/_part_list_row.html", context)


class PartEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.change_part']
    login_url = '/login/'

    def get(self, request, part_id):
        part = get_object_or_404(models.Part, pk=part_id)
        part_types = models.PartType.objects.all().order_by('part_type_name')
        part_brands = models.PartBrand.objects.all().order_by('brand_name')
        
        context = {
            "part": part,
            "part_types": part_types,
            "part_brands": part_brands,
        }
        return render_htmx(request, None, "part/_part_edit_form_row.html", context)
    
    def post(self, request, part_id):
        part = get_object_or_404(models.Part, pk=part_id)
        print(f"Request Body: {request.POST}") 
        data = request.POST

        # Update the part with the data from HTMX
        part.part_name = data.get('part_name', part.part_name)
        part.weight = float(data.get('weight', part.weight))
        part.dimensions = data.get('dimensions', part.dimensions) or None
        part.description = data.get('description', part.description) or None
        part.quantity_per_package = int(data.get('quantity_per_package', part.quantity_per_package))
        part.price_per_package = float(data.get('price_per_package', part.price_per_package))
        
        # Handle foreign keys
        brand_id = data.get('part_brand')
        if brand_id:
            part.part_brand_id = brand_id
        else:
            part.part_brand = None
            
        type_id = data.get('part_type')
        if type_id:
            part.part_type_id = type_id
        else:
            part.part_type = None
        
        # Save the part object after updating it
        part.save()

        # Prepare the context for the updated part
        context = {
            'part': part,
        }
        
        # Return the updated part row as HTMX response
        return render_htmx(request, None, "part/_part_list_row.html", context)


class PartRowView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_part']
    login_url = '/login/'
    
    def get(self, request, part_id):
        part = get_object_or_404(models.Part, pk=part_id)
        part_types = models.PartType.objects.all().order_by('part_type_name')
        part_brands = models.PartBrand.objects.all().order_by('brand_name')
        
        context = {
            'part': part,
            'part_types': part_types,
            'part_brands': part_brands,
        }
        return render_htmx(request, None, "part/_part_list_row.html", context)

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
    return render(request, "service_site/part_procurement/_unit_part_select.html", {'parts': parts})

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
        'avaliable_units': part_in_station.quantity,
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
            print(part['avaliable_units'])
            if quantity > part['avaliable_units']:
                messages.error(request, f"Кількість перевищує доступну ({part['avaliable_units']}).")
                return HttpResponse("")
            elif  quantity < 0:
                messages.error(request, f"Кількість запчастин має бути більшою за 0.")
                return HttpResponse("")
            else:
                part['quantity'] = quantity
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

    if models.ProvidedService.objects.filter(visit_service=visit_service).exists():
        provided_service = models.ProvidedService.objects.get(visit_service=visit_service)
    else:
        provided_service = models.ProvidedService.objects.create(
            visit_service=visit_service,
            employee=employee,
            provided_date=datetime.now(),
        )

    for staged in staged_parts:
        part_in_station = models.PartInStation.objects.select_related("part").get(pk=staged['part_id'])
        if part_in_station.quantity < staged['quantity']:
            messages.error(request, f'При збереженні запчастини ({part_in_station.part.part_name}) для використання сталась помилка (в наявності: {part_in_station.quantity}, ви запросили: {staged['quantity']}). Додавання цієї запчастини пропущено') 
        else:
            models.RequiredPart.objects.create(
                provided_service=provided_service,
                part_in_station=part_in_station,
                quantity=staged['quantity']
            )
            part_in_station.quantity -= staged['quantity']
            part_in_station.save()

    if f'staged_parts_{v_service_id}' in request.session:
        del request.session[f'staged_parts_{v_service_id}']
        request.session.modified = True

    context = get_visit_service_with_part_search_context(request, v_service_id)
    rendered = render_to_string("service_site/visits/_required_parts_search_widget.html", context, request=request)
    response = HttpResponse(rendered)
    response['HX-Trigger'] = 'update-visit-services'
    messages.success(request, "Дані послуги оновлені.")
    return response

def delete_required_part(request, required_part_id):
    required_part = get_object_or_404(models.RequiredPart.objects.select_related("provided_service__visit_service", "part_in_station"), pk=required_part_id)
    try:
        part_in_station = required_part.part_in_station
        qty = required_part.quantity
        required_part.delete()
        part_in_station.quantity += qty
        part_in_station.save()
        context = get_visit_service_with_part_search_context(request, required_part.provided_service.visit_service.pk)
        rendered = render_to_string("service_site/visits/_required_parts_search_widget.html", context, request=request)
        response = HttpResponse(rendered)
        response['HX-Trigger'] = 'update-visit-services'
        messages.success(request, "Запчастину успішно видалено.")
        return response 
    except Exception as e:
        print(e)
        messages.error(request, "Сталася помилка при видаленні.")
        return HttpResponseBadRequest()
    

def get_visit_service_data(pk):
    return models.VisitService.objects.select_related(
            'service', 'service__service_type', 'provided_service', 
            'provided_service__employee', 'visit'
        ).prefetch_related('provided_service__required_parts').get(pk=pk)


def get_visit_service_with_part_search_context(request, visit_service_id):
    visit_service = get_visit_service_data(pk=visit_service_id)
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

    return context