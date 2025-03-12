from django.shortcuts import render
from django.core.paginator import Paginator
from . import models
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required()
def index(request):
    return render(request, 'base.html', {
        'title': 'Home',
    })

@login_required
@permission_required('service_site.view_customer', raise_exception=True)
def customer_list(request):
    search_query = request.GET.get("search", "")
    page_number = request.GET.get("page", 1)

    customers = models.Customer.objects.all().order_by("last_name", "first_name")
    if search_query:
        customers = customers.filter(first_name__icontains=search_query) | customers.filter(last_name__icontains=search_query)

    paginator = Paginator(customers, 10)  # Show 10 customers per page
    page_obj = paginator.get_page(page_number)

    if request.htmx:
        return render(request, "service_site/customers_list.html", {"customers": page_obj})
    return render(request, "service_site/customers.html", {"customers": page_obj})