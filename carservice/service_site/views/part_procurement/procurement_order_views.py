from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .. import models
from .. import filters
from .. import forms
from .. import resources
from ... import views_utils
from ...domain import part_procurement
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from datetime import datetime
from django.db.models import ProtectedError
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_procurementorder'], raise_exception=True)
def procurement_orders(request):
    """View for displaying all procurement orders with filtering and pagination."""
    page_number = request.GET.get('page', 1)
    items_per_page = int(request.GET.get('items_per_page', 10))

    search_query = views_utils.get_order_search_query(request.GET.get('search', ''))

    queryset = models.ProcurementOrder.objects.select_related(
        'employee', 'employee__employee_position', 'supplier', 'procurement_status'
    ).order_by("-order_date")
       
    qs = queryset.filter(search_query)
    filter = filters.ProcurementOrderFilter(request.GET, queryset=qs)

    paginator = Paginator(filter.qs, items_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'procurement_orders': page_obj,
        'filter_form': filter.form,
    }
    
    return views_utils.render_htmx(request, 
                                   template_full='service_site/part_procurement/procurement_orders.html',
                                   template_partial='service_site/part_procurement/_procurement_order_list.html',
                                   context=context)

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
    
    search_query = views_utils.get_order_search_query(request.GET.get('search', ''))

    queryset = models.ProcurementOrder.objects.select_related(
        'employee', 'employee__employee_position', 'supplier', 'procurement_status'
    ).order_by("-order_date")
       
    qs = queryset.filter(search_query)
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
@permission_required(['service_site.view_procurementorder'], raise_exception=True)
def update_order_row(request, order_id):
    order = get_object_or_404(models.ProcurementOrder, pk=order_id)

    return render(request, "service_site/part_procurement/_order_row.html", {
        "order": order,
    })