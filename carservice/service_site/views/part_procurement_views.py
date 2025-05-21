from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .. import models
from .. import filters
from .. import forms
from .. import resources
from ..domain import part_procurement
from .. import exceptions
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from datetime import datetime
from django.template.loader import render_to_string
from django.db.models import ProtectedError
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_procurementorder'], raise_exception=True)
def procurement_orders(request):
    """View for displaying all procurement orders with filtering and pagination."""
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    items_per_page = int(request.GET.get('items_per_page', 10))

    queryset = models.ProcurementOrder.objects.select_related(
        'employee', 'employee__employee_position', 'supplier', 'procurement_status'
    ).order_by("-order_date")
    
    query = Q()
    if search_query:
        search_terms = search_query.split()
        for term in search_terms:
            query |= Q(order_number__icontains=term) | Q(
                employee__first_name__icontains=term) | Q(
                employee__last_name__icontains=term) | Q(
                supplier__supplier_name__icontains=term)
       
    qs = queryset.filter(query)
    filter = filters.ProcurementOrderFilter(request.GET, queryset=qs)

    paginator = Paginator(filter.qs, items_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'procurement_orders': page_obj,
        'filter_form': filter.form,
    }
    
    # Check if request is HTMX
    if request.headers.get('HX-Request'):
        return render(request, 'service_site/part_procurement/_procurement_order_list.html', context)
    
    return render(request, 'service_site/part_procurement/procurement_orders.html', context)


@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_procurementorder'], raise_exception=True)
def export_procurement_orders(request):
    """
    Export procurement orders data to various formats.
    Supported formats: csv, json
    """
    format = request.GET.get('format', 'csv')
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})
    
    search_query = request.GET.get('search', '')

    queryset = models.ProcurementOrder.objects.select_related(
        'employee', 'employee__employee_position', 'supplier', 'procurement_status'
    ).order_by("-order_date")

    query = Q()
    if search_query:
        search_terms = search_query.split()
        for term in search_terms:
            query |= Q(order_number__icontains=term) | Q(
                employee__first_name__icontains=term) | Q(
                employee__last_name__icontains=term) | Q(
                supplier__supplier_name__icontains=term)
       
    qs = queryset.filter(query)
    filter = filters.ProcurementOrderFilter(request.GET, queryset=qs)
    filtered_qs = filter.qs
    
    resource = resources.ProcurementOrderResource()
    dataset = resource.export(filtered_qs)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'procurement_orders_{timestamp}'
    
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
@require_http_methods(["GET", "POST"])
@permission_required(['service_site.add_procurementorder'], raise_exception=True)
def add_order(request):
    if request.method == "GET":
        form = forms.ProcurementOrderInfoForm()
        return render(request, 'service_site/part_procurement/_add_order_form.html', {'form': form})
    if request.method == 'POST':
        # TODO: Refactor this to avoid using model forms
        form = forms.ProcurementOrderInfoForm(request.POST)
        
        if form.is_valid():
            form.instance.order_number = models.ProcurementOrder.generate_order_number()
            form.instance.total_price = 0
            order = form.save()
            messages.success(request, f'Замовлення №{order.order_number} успішно додано')
            return render(request, "service_site/part_procurement/_order_row_expandable.html", {"order": order})

    return render(request, 'service_site/part_procurement/_add_order_form.html', {'form': form}, status=400)

@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_procurementorder'], raise_exception=True)
def delete_procurement_order(request, order_id):
    try:
        order_number = part_procurement.delete_procurement_order(order_id)
        messages.success(request, f"Замовлення {order_number} успішно видалено")
    except ProtectedError:
        messages.error(request, "Неможливо видалити замовлення, оскільки воно має позиції.")
        return HttpResponse(status=400)
    except ObjectDoesNotExist:
        messages.error(request, "Неможливо видалити замовлення, оскільки воно не існує")
        return HttpResponse(status=400)
    else:
        response = HttpResponse()
        response['HX-Redirect'] = reverse('procurement-orders', kwargs={})
        return response

@login_required
@require_http_methods(["GET", 'POST'])
@permission_required(['service_site.view_procurementorder'], raise_exception=True)
def order_info(request, pk):
    order = get_object_or_404(models.ProcurementOrder, pk=pk)
    return render(request, 'service_site/part_procurement/_order_info_fields.html', {'order': order})

@login_required
@require_http_methods(["GET", "POST"])
@permission_required(['service_site.change_procurementorder'], raise_exception=True)
def edit_order_info(request, pk):
    order = get_object_or_404(models.ProcurementOrder, pk=pk)
    if request.method == 'POST':
        # TODO: Refactor this to avoid using model forms
        form = forms.ProcurementOrderInfoForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return order_info(request, pk)  # Rerender view mode
    else:
        form = forms.ProcurementOrderInfoForm(instance=order)
    return render(request, 'service_site/part_procurement/_edit_order_info_form.html', {'form': form, 'order': order})

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_procurementorder', 'service_site.view_procurementunit', 'service_site.view_storageplacement'], raise_exception=True)
def procurement_order_items(request, order_id):
    order = models.ProcurementOrder.objects.prefetch_related("units", "units__part", "units__part__part_type", "units__part__part_brand").get(pk=order_id)
    return render(request, 'service_site/part_procurement/_order_details.html', {
        'order': order
    })
    
class AddOrderUnitView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_procurementunit', 'service_site.add_procurementunit']
    login_url = '/login/'

    def get(self, request, order_id):
        parts = models.Part.objects.select_related('part_brand').all()
        part_brands = models.PartBrand.objects.all()
        part_types = models.PartType.objects.all()

        context = {
            'parts': parts,
            'part_brands': part_brands,
            'part_types': part_types,
            'order_id': order_id
        }
        return render(request, 'service_site/part_procurement/_add_order_unit.html', context)

    def post(self, request, order_id):
        try:
            order_unit = part_procurement.add_order_unit(order_id, 
                                                         request.POST.get('part_id'), 
                                                         request.POST.get('quantity'), 
                                                         request.POST.get('price_per_unit'))
        except exceptions.InvalidProcurementUnitData as e:
            messages.error(request, str(e))
            return HttpResponse(status=400)
        except  ObjectDoesNotExist as e:
            messages.error(request, str(e))
            return HttpResponse(status=400)
        except (TypeError, ValueError) as e:
            messages.error(request, str(e))
            return HttpResponse(status=400)

        return render(request, 'service_site/part_procurement/_unit_row_with_placement.html', 
                      {'unit': order_unit, "placed_count": order_unit.get_placed_count})
    
@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_procurementunit',
                      'service_site.view_procurementunit'], raise_exception=True)
def delete_procurement_unit(request, unit_id):
    unit = get_object_or_404(models.ProcurementUnit, pk=unit_id)

    try:
        part_procurement.delete_procurement_unit(unit)
    except exceptions.UnitHasPlacementsError as e:
        messages.error(request, str(e))
        rendered = render_to_string('service_site/part_procurement/_unit_row.html', {
            'unit': unit,
            'placed_count': unit.get_placed_count()
        }, request=request)
        return HttpResponse(rendered, status=400)
    else:
        messages.success(request, f"Одиницю закупівлі успішно видалено")
        return HttpResponse("", status=200)

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_procurementunit',
                      'service_site.view_procurementunit'], raise_exception=True)
def edit_unit(request, unit_id):
    unit = get_object_or_404(models.ProcurementUnit, pk=unit_id)
    try:
        part_procurement.update_procurement_unit(unit, 
                                                request.POST.get("quantity"),
                                                request.POST.get("price"))
    except exceptions.InvalidProcurementUnitData as e:
        messages.error(request, str(e))
        status = 400
    except (ValueError, TypeError):
        messages.error(request, "Невірні дані для ціни або кількості")
        status = 400
    else:
        messages.success(request, "Одиницю успішно оновлено")
        status = 200

    return render(request, 'service_site/part_procurement/_unit_row.html', {
        'unit': unit, 
        "placed_count": unit.get_placed_count
        }, status=status)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_storageplacement'], raise_exception=True)
def unit_placements(request, pk):
    unit = get_object_or_404(models.ProcurementUnit.objects.prefetch_related('placements__part_in_station__station'), pk=pk)
    return render(request, 'service_site/part_procurement/_unit_placements.html', {'unit': unit})

class AddPlacementView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_procurementunit', 'service_site.add_storageplacement']
    login_url = '/login/'

    def get(self, request, unit_id):
        unit = get_object_or_404(models.ProcurementUnit, procurement_unit_id=unit_id)
        stations = models.Station.objects.all()
        context = {
            'unit': unit,
            'stations': stations
        }
        return render(request, 'service_site/part_procurement/_placement_form.html', context)

    def post(self, request, unit_id):
        unit = get_object_or_404(models.ProcurementUnit, procurement_unit_id=unit_id)

        try:
            part_procurement.add_part_placement(unit, 
                                                request.POST.get('station_id'),
                                                request.POST.get('quantity'))
        except exceptions.InvalidPlacementError as e:
            messages.error(request, str(e))
        except models.Station.DoesNotExist:
            messages.error(request, "Станцію не знайдено.")
        except (TypeError, ValueError):
            messages.error(request, "Некоректна кількість для розміщення або станція.")
            return HttpResponse(status=400)
        else:
            messages.success(request, "Розміщення успішно додано.")

        unit.refresh_from_db()
        placed_count = unit.get_placed_count()
        rendered_row = render_to_string("service_site/part_procurement/_unit_row.html", {
            "unit": unit,
            "placed_count": placed_count
        }, request=request)
        return HttpResponse(rendered_row)
    
@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.delete_storageplacement',
                      'service_site.view_procurementunit'], raise_exception=True)
def remove_placement(request, placement_id):
    placement = get_object_or_404(
        models.StoragePlacement.objects.select_related('procurement_unit', 'part_in_station__station'),
        pk=placement_id
    )
    unit = placement.procurement_unit

    try:
        part_procurement.remove_part_placement(placement_id)
    except exceptions.ProcurementIsCompletedError as e:
        messages.error(request, str(e))
        status = 400
    except exceptions.NotEnoughPartsError as e:
        messages.error(request, str(e))
        status = 400
    else:
        messages.success(request, "Розміщення успішно видалене")
        status = 200
        unit.refresh_from_db()

    rendered = render_to_string('service_site/part_procurement/_unit_placements.html', {'unit': unit}, request=request)
    response = HttpResponse(rendered, status=status)
    response['HX-Trigger'] = 'placementRemoved'
    return response

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.change_procurementunit'], raise_exception=True)
def update_row(request, unit_id):
    unit = get_object_or_404(models.ProcurementUnit, procurement_unit_id=unit_id)
    unit.refresh_from_db()
    placed_count = unit.get_placed_count()

    return render(request, "service_site/part_procurement/_unit_row.html", {
        "unit": unit,
        "placed_count": placed_count
    })

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_procurementorder'], raise_exception=True)
def update_order_row(request, order_id):
    order = get_object_or_404(models.ProcurementOrder, pk=order_id)

    return render(request, "service_site/part_procurement/_order_row.html", {
        "order": order,
    })