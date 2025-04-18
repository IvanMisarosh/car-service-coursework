from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .. import models
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class Visits(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_customer']
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get("page", 1)
        items_per_page = int(request.GET.get("items_per_page", 10))

        visits = models.Visit.objects.all().select_related(
            'visit_status', 'car', 'car__customer', 'car__car_model', 'employee', 'payment_status').order_by('-visit_date')


        paginator = Paginator(visits, items_per_page)
        page_obj = paginator.get_page(page_number)

        context = {
            "visits": page_obj,
        }

        return render_htmx(request, "service_site/visits/visits.html", "service_site/visits/_visit_list.html", context)


def render_htmx(request, template_full, template_partial, context):
    if request.htmx:
        return render(request, template_partial, context)
    else:
        return render(request, template_full, context)
