from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from .. import filters
from django.db.models import Q
from ..views_utils import render_htmx
from .. import resources
from datetime import datetime
from django.http import HttpResponse

@login_required
def export_customers(request):
    """
    Export customer data with their cars to various formats.
    Supported formats: csv, xlsx, json
    """
    format = request.GET.get('format', 'csv')
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})
    
    customers = models.Customer.objects.all()
    customer_filter = filters.CustomerFilter(request.GET, customers)

    resource = resources.CustomerResource()
    dataset = resource.export(customer_filter.qs)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'customers_with_cars_{timestamp}'
    
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
@permission_required('service_site.view_customer', raise_exception=True)
def customer_details(request):
    customer_id = request.GET.get("customer_id", None)
    customer = models.Customer.objects.get(pk=customer_id)

    context = {
        'customer': customer,
        'customer_cars': customer.get_cars(),
        'customer_visits': customer.get_visits()
    }

    return render(request, "service_site/customers/_selected_customer_details.html", context)


@login_required
@permission_required('service_site.view_customer', raise_exception=True)
def customer_list(request):
    page_number = request.GET.get("page", 1)
    items_per_page = int(request.GET.get("items_per_page", 10))
    sorting_method = request.GET.get("sorting_method", "first_name")

    customers = models.Customer.objects.all().order_by(sorting_method)

    customer_filter = filters.CustomerFilter(request.GET, customers)

    paginator = Paginator(customer_filter.qs, items_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        "customers": page_obj,
        "form": customer_filter.form,
    }

    return render_htmx(request, "service_site/customers/customers.html", "service_site/customers/_customers_list.html", context)

@login_required
@permission_required('service_site.view_customer', raise_exception=True)
def customer_search(request):
    search = request.GET.get("search", '')
    search_terms = search.split()
    search_query = Q()

    for term in search_terms:
        search_query |= Q(first_name__icontains=term) | \
                Q(last_name__icontains=term) | \
                Q(email__icontains=term) | \
                Q(phone_number__icontains=term)

    customers = models.Customer.objects.prefetch_related('cars').filter(search_query).distinct()
    return render(request, "service_site/visits/_customer_search_result.html", 
                  {"customers": customers})

@login_required
@permission_required('service_site.view_customer', raise_exception=True)
def select_visit_customer(request):
    customer_id = request.GET.get("customer_id", None)
    customer = models.Customer.objects.prefetch_related(
        'cars__car_model', 'cars__car_model__car_brand', 'cars__car_model__suspension_type', 'cars__car_model__engine_type',
        'cars__car_model__transmission_type', 'cars__car_model__drive_type', 'cars__car_model__body_type'
    ).get(pk=customer_id)

    context = {
        'visit_customer': customer,
    }

    return render(request, "service_site/visits/_visit_customer_details.html", context)


def get_customer_search(request):
    return render(request, "service_site/visits/_customer_search.html")




