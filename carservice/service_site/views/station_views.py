from django.views import View
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..views_utils import render_htmx
from .. import models
from .. import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from crispy_forms.templatetags.crispy_forms_filters import as_crispy_field
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

def calculate_station_stats(station):
    """Helper function to calculate station statistics"""
    one_month_ago = timezone.now() - timedelta(days=60)
    
    # Get unique customers who visited this station in the last month
    unique_customers = models.Customer.objects.filter(
        cars__visits__employee__station=station,
        cars__visits__visit_date__gte=one_month_ago
    ).distinct().count()
    
    # Get total services completed in the last month
    completed_services = models.ProvidedService.objects.filter(
        employee__station=station,
        provided_date__gte=one_month_ago
    ).count()
    
    # Calculate average visit price for this station in the last month
    avg_visit_price = models.Visit.objects.filter(
        employee__station=station,
        visit_date__gte=one_month_ago,
        price__isnull=False
    ).aggregate(avg_price=Avg('price'))['avg_price'] or 0
    
    # Format the average price to two decimal places
    avg_visit_price = round(float(avg_visit_price), 2)
    
    return {
        "unique_customers": unique_customers,
        "completed_services": completed_services,
        "avg_visit_price": avg_visit_price
    }

class StationsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = []
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
            stats = calculate_station_stats(station)
            station.unique_customers = stats["unique_customers"]
            station.completed_services = stats["completed_services"]
            station.avg_visit_price = stats["avg_visit_price"]
            stations_with_stats.append(station)
        
        paginator = Paginator(stations_with_stats, items_per_page)
        page_obj = paginator.get_page(page_number)
        
        context = {
            "stations": page_obj,
        }
        
        return render_htmx(request, "station/stations.html", "station/_station_list.html", context)
    
def add_station(request):
    if request.method == "GET":
        context = {
            "form": forms.StationForm()
        }
        return render(request, 'station/_station_add_form.html', context)
    elif request.method == "POST":
        form = forms.StationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stations')
        else:
            context = {
                "form": form
            }
            return render(request, 'station/_station_add_form.html', context)
    
def view_station(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    
    # Get employees and parts for this station
    employees = models.Employee.objects.filter(station=station).select_related('employee_position')
    parts_in_station = models.PartInStation.objects.filter(station=station).select_related('part', 'part__part_brand', 'part__part_type')
    
    active_tab = request.GET.get('tab', 'employees')
    
    context = {
        "station": station,
        "employees": employees,
        "parts_in_station": parts_in_station,
        "active_tab": active_tab,
        "employee_count": employees.count()
    }
    return render(request, "station/_station_card.html", context)

def edit_station(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    if request.method == "POST":
        form = forms.StationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            return redirect('view-station', pk=station.station_id)
    elif request.method == "GET":
        form = forms.StationForm(instance=station)
        return render(request, 'station/_station_form.html', {'form': form, 'station': station})

def station_employees(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    employees = models.Employee.objects.filter(station=station).select_related('employee_position')
    
    context = {
        "station": station,
        "employees": employees,
        "active_tab": "employees"
    }
    return render(request, "station/_station_employees_tab.html", context)

def station_equipment(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    parts_in_station = models.PartInStation.objects.filter(station=station).select_related('part', 'part__part_brand', 'part__part_type')
    
    context = {
        "station": station,
        "parts_in_station": parts_in_station,
        "active_tab": "equipment"
    }
    return render(request, "station/_station_equipment_tab.html", context)

def station_empty(request, pk):
    station = get_object_or_404(models.Station, pk=pk)
    
    # Calculate statistics for the station
    stats = calculate_station_stats(station)
    station.unique_customers = stats["unique_customers"]
    station.completed_services = stats["completed_services"]
    station.avg_visit_price = stats["avg_visit_price"]
    
    context = {
        "station": station,
        "active_tab": "summary",
    }
    
    return render(request, "station/_station_summary_tab.html", context)