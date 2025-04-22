from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .. import models
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..filters import VisitFilter
from django.db.models import Q


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


def render_htmx(request, template_full, template_partial, context):
    if request.htmx:
        return render(request, template_partial, context)
    else:
        return render(request, template_full, context)
