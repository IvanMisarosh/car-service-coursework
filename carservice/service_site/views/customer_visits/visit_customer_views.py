from django.shortcuts import render
from django.db.models import Q
from .. import models
from django.contrib.auth.decorators import permission_required, login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_car'], raise_exception=True)
def car_search(request):
    search_query = request.GET.get("search", "")
    
    search_terms = search_query.split()
    query = Q()
    
    for term in search_terms:
        query |= Q(car_model__car_brand__brand_name__icontains=term) | \
                 Q(car_model__model_name__icontains=term) | \
                 Q(customer__first_name__icontains=term) | \
                 Q(customer__last_name__icontains=term) | \
                 Q(customer__phone_number__icontains=term)
    
    cars = models.Car.objects.select_related(
        'car_model', 'car_model__car_brand', 'customer'
    ).filter(query).distinct()
    
    return render(request, "service_site/visits/_car_search_result.html", {
        "car_selection": cars,
    })

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visit'], raise_exception=True)
def update_visit_car(request):
    car_id = request.POST.get('selected_car_id')
    car = models.Car.objects.select_related(
        'customer', 'color', 'car_model', 'car_model__car_brand', 'car_model__suspension_type', 'car_model__engine_type',
        'car_model__transmission_type', 'car_model__drive_type', 'car_model__body_type'
    ).get(pk=car_id)

    context = {
        "visit_car": car,
        "visit_customer": car.customer,
    }

    return render(request, "service_site/visits/_visit_car_details.html", context)

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_visit'], raise_exception=True)
def select_car_from_search(request):
    car_id = request.POST.get('car_id')
    car = models.Car.objects.select_related(
        'customer', 'color', 'car_model', 'car_model__car_brand', 'car_model__suspension_type', 'car_model__engine_type',
        'car_model__transmission_type', 'car_model__drive_type', 'car_model__body_type'
    ).get(pk=car_id)

    context = {
        "visit_car": car,
        "visit_customer": car.customer,
    }

    return render(request, "service_site/visits/_car_details.html", context)

@login_required
@require_http_methods(["GET"])
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
@require_http_methods(["GET"])
@permission_required('service_site.change_visit', raise_exception=True)
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

@login_required
@require_http_methods(["GET"])
@permission_required('service_site.view_customer', raise_exception=True)
def get_customer_search(request):
    return render(request, "service_site/visits/_customer_search.html")