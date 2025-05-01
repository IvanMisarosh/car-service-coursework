from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from .. import models
from ..filters import ProcurementOrderFilter 
from ..forms import ProcurementOrderForm 

def procurement_order_list(request):
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    items_per_page = int(request.GET.get('items_per_page', 10))

    queryset = models.ProcurementOrder.objects.select_related(
        'employee', 'supplier', 'procurement_status'
    ).prefetch_related('procurementunit_set__part__part_type').order_by("-order_date")

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
        html = render_to_string('part_procurement/_procurement_order_list.html', context, request=request)
        return HttpResponse(html)

    return render(request, 'part_procurement/procurement_orders.html', context)

def create_procurement_order(request):
    if request.method == 'POST':
        print(request.POST)
        form = ProcurementOrderForm(request.POST)
        if form.is_valid():
            form.instance.order_number = models.ProcurementOrder.generate_order_number()
            form.save()
            response = HttpResponse("")
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = ProcurementOrderForm()

    return render(request, 'part_procurement/_order_form.html', 
                  {'form': form,
                   'employees': models.Employee.objects.all(),
                   })

def employee_info(request):
    employee_id = request.GET.get('employee')
    employee = get_object_or_404(models.Employee, pk=employee_id)
    return render(request, 'part_procurement/_employee_info_card.html', {'employee': employee})

