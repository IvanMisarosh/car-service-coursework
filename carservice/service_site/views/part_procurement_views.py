from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .. import models
from .. import filters
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_date

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

def procurement_order_items(request, order_id):
    order = models.ProcurementOrder.objects.prefetch_related("units", "units__part", "units__part__part_type", "units__part__part_brand").get(pk=order_id)
    return render(request, 'part_procurement/_order_details.html', {
        'order': order
    })
