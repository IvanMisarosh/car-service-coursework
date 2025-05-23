from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Count, Max
from .. import models
from ..forms import SupplierForm
from .. import views_utils
from ..domain import suppliers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError
from django.contrib import messages


class SuppliersView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_supplier']
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get("page", 1)
        items_per_page = int(request.GET.get("items_per_page", 10))
        search_query = request.GET.get("search", '')

        search_terms = search_query.split()
        query = Q()

        for term in search_terms:
            query |= Q(supplier_name__icontains=term) | Q(
                email__icontains=term) | Q(
                phone_number__icontains=term)

        # Get suppliers with annotations for items supplied count and last order date
        suppliers = models.Supplier.objects.annotate(
            items_supplied=Count('procurementorder__units'),
            last_order_date=Max('procurementorder__order_date')
        ).filter(query).order_by('supplier_name')


        paginator = Paginator(suppliers, items_per_page)
        page_obj = paginator.get_page(page_number)

        context = {
            "suppliers": page_obj,
        }

        return views_utils.render_htmx(request, "service_site/supplier/suppliers.html", "service_site/supplier/_supplier_list.html", context)
    
@login_required
@require_http_methods(["GET", "POST"])
@permission_required(['service_site.change_supplier'], raise_exception=True) 
def get_supplier_edit_row(request, pk):
    if request.method == 'GET':
        supplier = views_utils.get_supplier_with_stats(pk)

        context = {
            'supplier': supplier,
        }
        return views_utils.render_htmx(request, None, "service_site/supplier/_supplier_edit_row.html", context)
    elif request.method == "POST":
        data = request.POST
        supplier = suppliers.update_supplier(views_utils.get_supplier_with_stats(pk),
                                             supplier_name=data.get('supplier_name'),
                                             email=data.get('email'),
                                             phone=data.get('phone_number'))

        context = {
            'supplier': supplier,
        }
        return views_utils.render_htmx(request, None, "service_site/supplier/_supplier_list_row.html", context)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_supplier'], raise_exception=True) 
def get_supplier_row(request, pk):
    supplier = views_utils.get_supplier_with_stats(pk)

    context = {
        'supplier': supplier,
    }
    return views_utils.render_htmx(request, None, "service_site/supplier/_supplier_list_row.html", context)


@method_decorator(csrf_exempt, name='dispatch')
class SupplierView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.change_supplier', 'service_site.add_supplier']
    login_url = '/login/'
    
    def get(self, request):
        form = SupplierForm()
        return views_utils.render_htmx(request, None, "service_site/supplier/_add_supplier_form.html", {"form": form})

    def post(self, request):
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            # Render the new row for the supplier table
            return views_utils.render_htmx(request, None, "service_site/supplier/_supplier_list_row.html", {"supplier": supplier, "request": request})
        return views_utils.render_htmx(request, None, "service_site/supplier/_add_supplier_form.html", {"form": form})
    
    def delete(self, request, supplier_id):
        supplier = views_utils.get_supplier_with_stats(supplier_id)
        try:
            supplier_name = supplier.supplier_name
            supplier.delete()
            messages.success(request, f"Постачальника {supplier_name} успішно видалено")
            return HttpResponse("", status=200)
        except ProtectedError:
            messages.error(request, f"Неможливо видалити постачальника '{supplier.supplier_name}' оскільки він має посилання на закупки.")
            
            context = {
                'supplier': supplier,
            }
            return render(request, "service_site/supplier/_supplier_list_row.html", context)
        except Exception:
            pass
