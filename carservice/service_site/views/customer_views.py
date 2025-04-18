from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .. import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from .. import filters


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


def render_htmx(request, template_full, template_partial, context):
    if request.htmx:
        return render(request, template_partial, context)
    else:
        return render(request, template_full, context)
