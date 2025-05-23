from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from . import models
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import timedelta


def group_required(group_name):
    def in_group(user):
        return user.is_authenticated and user.groups.filter(name=group_name).exists()
    return user_passes_test(in_group)

def render_htmx(request, template_full, template_partial, context):
    if request.htmx:
        return render(request, template_partial, context)
    else:
        return render(request, template_full, context)
    
def get_visit_service_data(pk):
    return models.VisitService.objects.select_related(
            'service', 'service__service_type', 'provided_service', 
            'provided_service__employee', 'visit'
        ).prefetch_related('provided_service__required_parts').get(pk=pk)

def get_visit_service_with_part_search_context(request, visit_service_id):
    visit_service = get_visit_service_data(pk=visit_service_id)
    part_brands = models.PartBrand.objects.all()
    part_types = models.PartType.objects.all()

    context = {
        "visit_service": visit_service,
        'part_brands': part_brands,
        'part_types': part_types,
    }

    if f'staged_parts_{visit_service_id}' in request.session:
        del request.session[f'staged_parts_{visit_service_id}']
        request.session.modified = True

    return context

def get_order_search_query(search_query):
    query = Q()
    if search_query:
        search_terms = search_query.split()
        for term in search_terms:
            query |= Q(order_number__icontains=term) | Q(
                employee__first_name__icontains=term) | Q(
                employee__last_name__icontains=term) | Q(
                supplier__supplier_name__icontains=term)
    return query

def calculate_station_stats(station):
    """Helper function to calculate station statistics"""
    one_month_ago = timezone.now() - timedelta(days=60)
    
    # Get unique customers who visited this station in the last month
    unique_customers = models.Customer.objects.filter(
        cars__visits__employee__station=station,
        cars__visits__visit_date__gte=one_month_ago
    ).distinct().count()
    
    # Get total services completed in the last month
    completed_services = models.ProvidedService.objects.filter(
        employee__station=station,
        provided_date__gte=one_month_ago
    ).count()
    
    # Calculate average visit price for this station in the last month
    avg_visit_price = models.Visit.objects.filter(
        employee__station=station,
        visit_date__gte=one_month_ago,
        price__isnull=False
    ).aggregate(avg_price=Avg('price'))['avg_price'] or 0
    
    # Format the average price to two decimal places
    avg_visit_price = round(float(avg_visit_price), 2)
    
    return {
        "unique_customers": unique_customers,
        "completed_services": completed_services,
        "avg_visit_price": avg_visit_price
    }

def get_supplier_with_stats(supplier_id):
    supplier = get_object_or_404(models.Supplier, pk=supplier_id)
    supplier.items_supplied = models.ProcurementUnit.items_supplied_by_supplier(supplier)
    supplier.last_order_date = models.ProcurementOrder.supplier_last_order_date(supplier)

    return supplier
    