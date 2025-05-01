from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from .. import models
from ..filters import ProcurementOrderFilter  

def procurement_order_list(request):
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    items_per_page = int(request.GET.get('items_per_page', 10))

    queryset = models.ProcurementOrder.objects.select_related(
        'employee', 'supplier', 'procurement_status'
    ).prefetch_related('procurementunit_set__part__part_type')

    if search_query:
        queryset = queryset.filter(
            Q(order_number__icontains=search_query) |
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(supplier__supplier_name__icontains=search_query)
        )

    filter = ProcurementOrderFilter(request.GET, queryset=queryset)
    filtered_qs = filter.qs

    paginator = Paginator(filtered_qs, items_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'procurement_orders': page_obj,
        'filter_form': filter.form,
    }

    if request.htmx:
        html = render_to_string('part_procurement/procurement_order_list.html', context, request=request)
        return HttpResponse(html)

    return render(request, 'part_procurement/procurement_orders.html', context)
