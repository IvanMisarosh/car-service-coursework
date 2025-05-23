from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from .. import models
from ...domain import part_procurement
from ... import exceptions
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.views.generic import View 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_procurementorder', 'service_site.view_procurementunit', 'service_site.view_storageplacement'], raise_exception=True)
def procurement_order_items(request, order_id):
    order = models.ProcurementOrder.objects.prefetch_related("units", "units__part", "units__part__part_type", "units__part__part_brand").get(pk=order_id)
    return render(request, 'service_site/part_procurement/_order_details.html', {
        'order': order
    })
    
class AddOrderUnitView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_procurementunit', 'service_site.add_procurementunit']
    login_url = '/login/'

    def get(self, request, order_id):
        parts = models.Part.objects.select_related('part_brand').all()
        part_brands = models.PartBrand.objects.all()
        part_types = models.PartType.objects.all()

        context = {
            'parts': parts,
            'part_brands': part_brands,
            'part_types': part_types,
            'order_id': order_id
        }
        return render(request, 'service_site/part_procurement/_add_order_unit.html', context)

    def post(self, request, order_id):
        try:
            order_unit = part_procurement.add_order_unit(order_id, 
                                                         request.POST.get('part_id'), 
                                                         request.POST.get('quantity'), 
                                                         request.POST.get('price_per_unit'))
        except exceptions.InvalidProcurementUnitData as e:
            messages.error(request, str(e))
            return HttpResponse(status=400)
        except  ObjectDoesNotExist as e:
            messages.error(request, str(e))
            return HttpResponse(status=400)
        except (TypeError, ValueError) as e:
            messages.error(request, str(e))
            return HttpResponse(status=400)

        return render(request, 'service_site/part_procurement/_unit_row_with_placement.html', 
                      {'unit': order_unit, "placed_count": order_unit.get_placed_count})
    
@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_procurementunit',
                      'service_site.view_procurementunit'], raise_exception=True)
def delete_procurement_unit(request, unit_id):
    unit = get_object_or_404(models.ProcurementUnit, pk=unit_id)

    try:
        part_procurement.delete_procurement_unit(unit)
    except exceptions.UnitHasPlacementsError as e:
        messages.error(request, str(e))
        rendered = render_to_string('service_site/part_procurement/_unit_row.html', {
            'unit': unit,
            'placed_count': unit.get_placed_count()
        }, request=request)
        return HttpResponse(rendered, status=400)
    else:
        messages.success(request, f"Одиницю закупівлі успішно видалено")
        return HttpResponse("", status=200)

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_procurementunit',
                      'service_site.view_procurementunit'], raise_exception=True)
def edit_unit(request, unit_id):
    unit = get_object_or_404(models.ProcurementUnit, pk=unit_id)
    try:
        part_procurement.update_procurement_unit(unit, 
                                                request.POST.get("quantity"),
                                                request.POST.get("price"))
    except exceptions.InvalidProcurementUnitData as e:
        messages.error(request, str(e))
        status = 400
    except (ValueError, TypeError):
        messages.error(request, "Невірні дані для ціни або кількості")
        status = 400
    else:
        messages.success(request, "Одиницю успішно оновлено")
        status = 200

    placed_count = unit.get_placed_count()
    rendered_row = render_to_string("service_site/part_procurement/_unit_row.html", {
        "unit": unit,
        "placed_count": placed_count
    }, request=request)
    return HttpResponse(rendered_row, status)

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.change_procurementunit'], raise_exception=True)
def update_row(request, unit_id):
    unit = get_object_or_404(models.ProcurementUnit, procurement_unit_id=unit_id)
    unit.refresh_from_db()
    placed_count = unit.get_placed_count()

    return render(request, "service_site/part_procurement/_unit_row.html", {
        "unit": unit,
        "placed_count": placed_count
    })

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_part'], raise_exception=True) 
def part_search_for_unit(request):
    brand_id = request.GET.get("part_brand", None)
    part_type_id = request.GET.get("part_type", None)

    search_query = Q()

    parts = models.Part.objects.prefetch_related('part_brand', 'part_type')
        
    if brand_id:
        search_query &= Q(part_brand__part_brand_id=brand_id)
    if part_type_id:
        search_query &= Q(part_type__part_type_id=part_type_id)
        
    parts = parts.filter(search_query).distinct()
    return render(request, "service_site/part_procurement/_unit_part_select.html", {'parts': parts})