from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Count, Max, F
from ..models import Supplier, ProcurementOrder, ProcurementUnit
from ..forms import SupplierForm
from ..views_utils import render_htmx
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
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
        suppliers = Supplier.objects.annotate(
            items_supplied=Count('procurementorder__units'),
            last_order_date=Max('procurementorder__order_date')
        ).filter(query).order_by('supplier_name')


        paginator = Paginator(suppliers, items_per_page)
        page_obj = paginator.get_page(page_number)

        context = {
            "suppliers": page_obj,
        }

        return render_htmx(request, "supplier/suppliers.html", "supplier/_supplier_list.html", context)
    

def get_supplier_edit_row(request, pk):
    if request.method == 'GET':
        supplier = get_object_or_404(Supplier, pk=pk)
        items_supplied = ProcurementUnit.objects.filter(procurement_order__supplier=supplier).count()
        last_order_date = ProcurementOrder.objects.filter(supplier=supplier).aggregate(Max('order_date'))['order_date__max']

        supplier.items_supplied = items_supplied
        supplier.last_order_date = last_order_date
        context = {
            'supplier': supplier,
        }
        return render_htmx(request, None, "supplier/_supplier_edit_row.html", context)
    elif request.method == "POST":
        data = request.POST
        print(data)
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.supplier_name = data.get('supplier_name', supplier.supplier_name)
        supplier.email = data.get('email', supplier.email)
        supplier.phone_number = data.get('phone_number', supplier.phone_number)
        supplier.save()

        # Recalculate items_supplied and last_order_date for this supplier
        items_supplied = ProcurementUnit.objects.filter(procurement_order__supplier=supplier).count()
        last_order_date = ProcurementOrder.objects.filter(supplier=supplier).aggregate(Max('order_date'))['order_date__max']

        supplier.items_supplied = items_supplied
        supplier.last_order_date = last_order_date

        context = {
            'supplier': supplier,
        }
        return render_htmx(request, None, "supplier/_supplier_list_row.html", context)

def get_supplier_row(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    items_supplied = ProcurementUnit.objects.filter(procurement_order__supplier=supplier).count()
    last_order_date = ProcurementOrder.objects.filter(supplier=supplier).aggregate(Max('order_date'))['order_date__max']

    supplier.items_supplied = items_supplied
    supplier.last_order_date = last_order_date

    context = {
        'supplier': supplier,
    }
    return render_htmx(request, None, "supplier/_supplier_list_row.html", context)


@method_decorator(csrf_exempt, name='dispatch')
class SupplierView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.change_supplier', 'service_site.add_supplier']
    login_url = '/login/'
    
    def get(self, request):
        form = SupplierForm()
        return render_htmx(request, None, "supplier/_add_supplier_form.html", {"form": form})

    def post(self, request):
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            # Render the new row for the supplier table
            return render_htmx(request, None, "supplier/_supplier_list_row.html", {"supplier": supplier, "request": request})
        return render_htmx(request, None, "supplier/_add_supplier_form.html", {"form": form})
    
    def delete(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        try:
            supplier_name = supplier.supplier_name
            supplier.delete()
            messages.success(request, f"Постачальника {supplier_name} успішно видалено")
            return HttpResponse("", status=200)
        except ProtectedError:
            messages.error(request, f"Неможливо видалити постачальника '{supplier.supplier_name}' оскільки він має посилання на закупки.")
            
            items_supplied = ProcurementUnit.objects.filter(procurement_order__supplier=supplier).count()
            last_order_date = ProcurementOrder.objects.filter(supplier=supplier).aggregate(Max('order_date'))['order_date__max']
            
            supplier.items_supplied = items_supplied
            supplier.last_order_date = last_order_date
            
            context = {
                'supplier': supplier,
            }
            return render(request, "supplier/_supplier_list_row.html", context)
        except Exception:
            pass

    
