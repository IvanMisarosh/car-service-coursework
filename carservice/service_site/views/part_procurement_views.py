from django.core.paginator import Paginator
from django.db.models import Q, F
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .. import models
from .. import filters
from .. import forms
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.template.loader import render_to_string
import json

@login_required
def procurement_orders(request):
    """View for displaying all procurement orders with filtering and pagination."""
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    items_per_page = int(request.GET.get('items_per_page', 10))

    queryset = models.ProcurementOrder.objects.select_related(
        'employee', 'employee__employee_position', 'supplier', 'procurement_status'
    ).order_by("-order_date")

    if search_query:
        queryset = queryset.filter(
            Q(order_number__icontains=search_query) |
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(supplier__supplier_name__icontains=search_query)
        )

    filter = filters.ProcurementOrderFilter(request.GET, queryset=queryset)
    filtered_qs = filter.qs

    paginator = Paginator(filtered_qs, items_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'procurement_orders': page_obj,
        'filter_form': filter.form,
    }
    
    # Check if request is HTMX
    if request.headers.get('HX-Request'):
        return render(request, 'part_procurement/_procurement_order_list.html', context)
    
    return render(request, 'part_procurement/procurement_orders.html', context)

def add_order(request):
    if request.method == "GET":
        form = forms.ProcurementOrderInfoForm()
        # messages.add_message(request, *(messages.SUCCESS, "Congratulations! You did it."))
        # messages.error(request, 'words')
        return render(request, 'part_procurement/_add_order_form.html', {'form': form})
    if request.method == 'POST':
        form = forms.ProcurementOrderInfoForm(request.POST)
        
        if form.is_valid():
            form.instance.order_number = models.ProcurementOrder.generate_order_number()
            form.instance.total_price = 0
            order = form.save()
            # messages.error(request, 'words')
            return render(request, "part_procurement/_order_row_expandable.html", {"order": order})
    # messages.error(request, 'words')
    return render(request, 'part_procurement/_add_order_form.html', {'form': form}, status=400)
    
def order_info(request, pk):
    order = get_object_or_404(models.ProcurementOrder, pk=pk)
    return render(request, 'part_procurement/_order_info_fields.html', {'order': order})

def edit_order_info(request, pk):
    order = get_object_or_404(models.ProcurementOrder, pk=pk)
    if request.method == 'POST':
        form = forms.ProcurementOrderInfoForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return order_info(request, pk)  # Rerender view mode
    else:
        form = forms.ProcurementOrderInfoForm(instance=order)
    return render(request, 'part_procurement/_edit_order_info_form.html', {'form': form, 'order': order})

def procurement_order_items(request, order_id):
    order = models.ProcurementOrder.objects.prefetch_related("units", "units__part", "units__part__part_type", "units__part__part_brand").get(pk=order_id)
    return render(request, 'part_procurement/_order_details.html', {
        'order': order
    })

def add_order_unit(request, order_id):

    if request.method == "GET":
        parts = models.Part.objects.select_related('part_brand').all()
        part_brands = models.PartBrand.objects.all()
        part_types = models.PartType.objects.all()
        context = {
            'parts' : parts,
            'part_brands' : part_brands,
            "part_types" : part_types,
            'order_id' : order_id 
        }
        return render(request, 'part_procurement/_add_order_unit.html', context)
    elif request.method == 'POST':
        #TODO: add validation
        part_id = request.POST.get('part_id', None)
        quantity = int(request.POST.get('quantity', 1))
        price_per_unit = float(request.POST.get('price_per_unit', 1))
        part = get_object_or_404(models.Part, pk=part_id)
        order = models.ProcurementOrder.objects.get(pk=order_id)
        order_unit = models.ProcurementUnit.objects.create(
            procurement_order=order,
            quantity=quantity,
            price_per_unit=price_per_unit,
            part=part
        )
        # messages.error(request, "Quantity must be greater than 0.")
        return render(request, 'part_procurement/_unit_row_with_placement.html', 
                      {'unit': order_unit, "placed_count": order_unit.get_placed_count})

def edit_unit(request, unit_id):
    unit = get_object_or_404(models.ProcurementUnit, pk=unit_id)
    # print(request.POST)
    price = float(request.POST.get("price", unit.price_per_unit))
    quantity = int(request.POST.get("quantity", unit.quantity))

    # TODO: validate input

    unit.quantity = quantity
    unit.price_per_unit = price
    unit.save()

    return render(request, 'part_procurement/_unit_row.html', {'unit': unit, "placed_count": unit.get_placed_count})

def unit_placements(request, pk):
    unit = get_object_or_404(models.ProcurementUnit.objects.prefetch_related('placements__part_in_station__station'), pk=pk)
    return render(request, 'part_procurement/_unit_placements.html', {'unit': unit})

def add_placement(request, unit_id):
    print(request.method)
    unit = get_object_or_404(models.ProcurementUnit, procurement_unit_id=unit_id)
    if request.method == "GET":
        
        stations = models.Station.objects.all()
        context = {
            'unit': unit,
            'stations': stations
        }
        return render(request, 'part_procurement/_placement_form.html', context)
    elif request.method == "POST":
        station_id = request.POST.get('station_id')
        quantity = int(request.POST.get('quantity', 0))

        placed_count = unit.get_placed_count()
        available_quantity = unit.quantity - placed_count

        if quantity <= 0 or quantity > available_quantity:
            return HttpResponse("Неправильна кількість", status=400)

        station = get_object_or_404(models.Station, station_id=station_id)

        part_in_station, created = models.PartInStation.objects.get_or_create(
            station=station,
            part=unit.part,
            defaults={'quantity': 0}
        )

        part_in_station.quantity += quantity
        part_in_station.save()

        models.StoragePlacement.objects.create(
            procurement_unit=unit,
            part_in_station=part_in_station,
            quantity=quantity,
            placement_date=datetime.now()
        )

        # Refresh the unit instance and re-fetch placed_count
        unit.refresh_from_db()
        placed_count = unit.get_placed_count()

        # Render only this updated row
        rendered_row = render_to_string("part_procurement/_unit_row.html", {
            "unit": unit,
            "placed_count": placed_count
        }, request=request)

        return HttpResponse(rendered_row)
    
def remove_placement(request, placement_id):
    placement = get_object_or_404(models.StoragePlacement, pk=placement_id)
    unit_id=placement.procurement_unit.pk
    placement.delete()
    return redirect("update-unit", unit_id)


def update_row(request, unit_id):
    unit = get_object_or_404(models.ProcurementUnit, procurement_unit_id=unit_id)
    unit.refresh_from_db()
    placed_count = unit.get_placed_count()

    return render(request, "part_procurement/_unit_row.html", {
        "unit": unit,
        "placed_count": placed_count
    })

def update_order_row(request, order_id):
    order = get_object_or_404(models.ProcurementOrder, pk=order_id)

    return render(request, "part_procurement/_order_row.html", {
        "order": order,
    })