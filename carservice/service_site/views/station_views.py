from django.views import View
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..views_utils import render_htmx
from .. import models
from .. import forms
from .. import views_utils 
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import ProtectedError

class StationsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_station']
    login_url = '/login/'
    
    def get(self, request, *args, **kwargs):
        page_number = request.GET.get("page", 1)
        items_per_page = int(request.GET.get("items_per_page", 12))
        search_query = request.GET.get("search", '')
        
        search_terms = search_query.split()
        query = Q()
        
        for term in search_terms:
            query |= Q(address__icontains=term) | \
                    Q(phone_number__icontains=term)
        
        # Get stations with employee count
        stations = models.Station.objects.annotate(
            employee_count=Count('employee')
        ).filter(query).order_by('address')
        
        # Add statistics to each station before pagination
        stations_with_stats = []
        for station in stations:
            stats = views_utils.calculate_station_stats(station)
            station.unique_customers = stats["unique_customers"]
            station.completed_services = stats["completed_services"]
            station.avg_visit_price = stats["avg_visit_price"]
            stations_with_stats.append(station)
        
        paginator = Paginator(stations_with_stats, items_per_page)
        page_obj = paginator.get_page(page_number)
        
        context = {
            "stations": page_obj,
        }
        
        return render_htmx(request, "service_site/station/stations.html", "service_site/station/_station_list.html", context)

@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_station'], raise_exception=True) 
def delete_station(request, station_id):
    station = get_object_or_404(models.Station, pk=station_id)
    try:
        station_address = station.address
        station.delete()
        messages.success(request, f"Станцію за адресою {station_address} успішно видалено.")
        return HttpResponse("", status=200)
    except ProtectedError:
        messages.error(request, f"Неможливо видалити станцію '{station.address}', оскільки вона має працівників та\або запчастини на складі склад.")
        return view_station(request, station_id)

@login_required
@require_http_methods(["GET", "POST"])
@permission_required(['service_site.add_station'], raise_exception=True) 
def add_station(request):
    if request.method == "GET":
        context = {
            "form": forms.StationForm()
        }
        return render(request, 'service_site/station/_station_add_form.html', context)
    elif request.method == "POST":
        form = forms.StationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stations')
        else:
            context = {
                "form": form
            }
            return render(request, 'service_site/station/_station_add_form.html', context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_station'], raise_exception=True) 
def view_station(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    
    # Get employees and parts for this station
    employees = models.Employee.objects.filter(station=station).select_related('employee_position')
    parts_in_station = models.PartInStation.objects.filter(station=station).select_related('part', 'part__part_brand', 'part__part_type')
    
    active_tab = request.GET.get('tab', 'summary')
    stats = views_utils.calculate_station_stats(station)
    station.unique_customers = stats["unique_customers"]
    station.completed_services = stats["completed_services"]
    station.avg_visit_price = stats["avg_visit_price"]
    station.employee_count = employees.count()
    
    context = {
        "station": station,
        "employees": employees,
        "parts_in_station": parts_in_station,
        "active_tab": active_tab,
    }
    return render(request, "service_site/station/_station_card.html", context)

@login_required
@require_http_methods(["GET", "POST"])
@permission_required(['service_site.view_station', 'service_site.change_station'], raise_exception=True) 
def edit_station(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    if request.method == "POST":
        form = forms.StationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            return redirect('view-station', pk=station.station_id)
    elif request.method == "GET":
        form = forms.StationForm(instance=station)
        return render(request, 'service_site/station/_station_form.html', {'form': form, 'station': station})

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_station'], raise_exception=True) 
def station_employees(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    employees = models.Employee.objects.filter(station=station).select_related('employee_position')
    
    context = {
        "station": station,
        "employees": employees,
        "active_tab": "employees"
    }
    return render(request, "service_site/station/_station_employees_tab.html", context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_station'], raise_exception=True) 
def station_equipment(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    parts_in_station = models.PartInStation.objects.filter(station=station).select_related('part', 'part__part_brand', 'part__part_type')
    
    context = {
        "station": station,
        "parts_in_station": parts_in_station,
        "active_tab": "equipment"
    }
    return render(request, "service_site/station/_station_equipment_tab.html", context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_station'], raise_exception=True) 
def station_empty(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    
    # Calculate statistics for the station
    stats = views_utils.calculate_station_stats(station)
    station.unique_customers = stats["unique_customers"]
    station.completed_services = stats["completed_services"]
    station.avg_visit_price = stats["avg_visit_price"]
    
    context = {
        "station": station,
        "active_tab": "summary",
    }
    
    return render(request, "service_site/station/_station_summary_tab.html", context)