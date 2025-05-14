from django.core.paginator import Paginator
from .. import models
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..filters import VisitFilter
from django.db.models import Q
from ..views_utils import render_htmx
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .. import models, resources, filters
from django.contrib.auth.decorators import login_required
from datetime import datetime

class Visits(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_customer']
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get("page", 1)
        items_per_page = int(request.GET.get("items_per_page", 10))
        search_query = request.GET.get("search", '')

        search_terms = search_query.split()
        query = Q()

        for term in search_terms:
            query |= Q(car__car_model__car_brand__brand_name__icontains=term) | Q(
                car__car_model__model_name__icontains=term) | Q(
                car__customer__first_name__icontains=term) | Q(
                car__customer__last_name__icontains=term) | Q(
                visit_number__icontains=term) | Q(
                employee__first_name__icontains=term) | Q(
                employee__last_name__icontains=term) | Q(
                visit_status__status_name__icontains=term) | Q(
                payment_status__payment_name__icontains=term) | Q(
                car__customer__phone_number__icontains=term)
            
        if request.user.is_authenticated and request.user.groups.filter(name='mechanic').exists():
            query &= Q(employee__station=request.user.employee.station)

        visits = models.Visit.objects.all().select_related(
            'visit_status', 'car', 'car__customer', 'car__car_model', 'employee', 'payment_status').filter(query).order_by('-visit_date')

        visit_filter = VisitFilter(request.GET, queryset=visits)
        visits_qs = visit_filter.qs

        paginator = Paginator(visits_qs, items_per_page)
        page_obj = paginator.get_page(page_number)

        context = {
            "visits": page_obj,
            "filter_form": visit_filter.form,
        }

        return render_htmx(request, "service_site/visits/visits.html", "service_site/visits/_visit_list.html", context)
    
    def delete(self, request, visit_id):
        visit = get_object_or_404(models.Visit, pk=visit_id)
        try:
            visit_number = visit.visit_number
            visit.delete()
            messages.success(request, f"Візит №{visit_number} успішно видалено.")
        except ProtectedError:
            messages.error(
                request,
                f"Неможливо видалити візит №{visit.visit_number}, оскільки він має послуги."
            )
        except Exception:
            messages.error(request, "Сталася невідома помилка під час видалення візиту.")
        finally:
            return self.get(request)


@login_required
def export_visits(request):
    """
    Export visit data with customer, car, employee, and station details.
    Supported formats: csv, json
    """
    format = request.GET.get('format', 'csv')
    
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})
    
    sorting_method = request.GET.get("sorting_method", "visit_date")
    search_query = request.GET.get("search", '')
    query = Q()
    search_terms = search_query.split()
    qs = None
    
    if request.GET.get('export_selection') == 'true':
        # Export filtered results
        for term in search_terms:
            query |= (
                Q(car__customer__first_name__icontains=term) | 
                Q(car__customer__last_name__icontains=term) | 
                Q(car__vin__icontains=term) | 
                Q(employee__first_name__icontains=term) | 
                Q(employee__last_name__icontains=term) |
                Q(visit_number__icontains=term)
            )
        visits = models.Visit.objects.all().filter(query).order_by(sorting_method)
        visit_filter = filters.VisitFilter(request.GET, visits)
        qs = visit_filter.qs
    else:
        # Export all visits
        visits = models.Visit.objects.all().order_by(sorting_method)
        qs = visits
    
    resource = resources.VisitResource()
    dataset = resource.export(qs)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'visits_{timestamp}'
    
    if format == 'csv':
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    elif format == 'json':
        response = HttpResponse(dataset.json, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
    else:
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    return response