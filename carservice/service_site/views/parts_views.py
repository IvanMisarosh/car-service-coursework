from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .. import models
from .. import forms
from ..views_utils import render_htmx
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import ProtectedError



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

        return render_htmx(request, "service_site/part/parts.html", "service_site/part/_part_list.html", context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_partinstation'], raise_exception=True) 
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
    
    return render(request, 'service_site/part/_part_availability.html', context)


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
        return render_htmx(request, None, "service_site/part/_add_part_form.html", context)

    def post(self, request):
        form = forms.PartForm(request.POST)
        if form.is_valid():
            part = form.save()
            # Get part types and brands for the template
            part_types = models.PartType.objects.all().order_by('part_type_name')
            part_brands = models.PartBrand.objects.all().order_by('brand_name')
            
            # Render the new row for the part table
            return render_htmx(request, None, "service_site/part/_part_list_row.html", {
                "part": part, 
                "part_types": part_types,
                "part_brands": part_brands
            })

        return HttpResponseBadRequest("")

@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_part'], raise_exception=True)  
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
        return render(request, "service_site/part/_part_list_row.html", context)


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
        return render_htmx(request, None, "service_site/part/_part_edit_form_row.html", context)
    
    def post(self, request, part_id):
        part = get_object_or_404(models.Part, pk=part_id)
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
        return render_htmx(request, None, "service_site/part/_part_list_row.html", context)


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
        return render_htmx(request, None, "service_site/part/_part_list_row.html", context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_part'], raise_exception=True) 
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