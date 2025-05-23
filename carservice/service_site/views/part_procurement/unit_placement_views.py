from django.shortcuts import render, get_object_or_404
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

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.view_storageplacement'], raise_exception=True)
def unit_placements(request, pk):
    unit = get_object_or_404(models.ProcurementUnit.objects.prefetch_related('placements__part_in_station__station'), pk=pk)
    return render(request, 'service_site/part_procurement/_unit_placements.html', {'unit': unit})

class AddPlacementView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['service_site.view_procurementunit', 'service_site.add_storageplacement']
    login_url = '/login/'

    def get(self, request, unit_id):
        unit = get_object_or_404(models.ProcurementUnit, procurement_unit_id=unit_id)
        stations = models.Station.objects.all()
        context = {
            'unit': unit,
            'stations': stations
        }
        return render(request, 'service_site/part_procurement/_placement_form.html', context)

    def post(self, request, unit_id):
        unit = get_object_or_404(models.ProcurementUnit, procurement_unit_id=unit_id)

        try:
            part_procurement.add_part_placement(unit, 
                                                request.POST.get('station_id'),
                                                request.POST.get('quantity'))
        except exceptions.InvalidPlacementError as e:
            messages.error(request, str(e))
        except models.Station.DoesNotExist:
            messages.error(request, "Станцію не знайдено.")
        except (TypeError, ValueError):
            messages.error(request, "Некоректна кількість для розміщення або станція.")
            return HttpResponse(status=400)
        else:
            messages.success(request, "Розміщення успішно додано.")

        unit.refresh_from_db()
        placed_count = unit.get_placed_count()
        rendered_row = render_to_string("service_site/part_procurement/_unit_row.html", {
            "unit": unit,
            "placed_count": placed_count
        }, request=request)
        return HttpResponse(rendered_row)
    
@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.delete_storageplacement',
                      'service_site.view_procurementunit'], raise_exception=True)
def remove_placement(request, placement_id):
    placement = get_object_or_404(
        models.StoragePlacement.objects.select_related('procurement_unit', 'part_in_station__station'),
        pk=placement_id
    )
    unit = placement.procurement_unit

    try:
        part_procurement.remove_part_placement(placement_id)
    except exceptions.ProcurementIsCompletedError as e:
        messages.error(request, str(e))
        status = 400
    except exceptions.NotEnoughPartsError as e:
        messages.error(request, str(e))
        status = 400
    else:
        messages.success(request, "Розміщення успішно видалене")
        status = 200
        unit.refresh_from_db()

    rendered = render_to_string('service_site/part_procurement/_unit_placements.html', {'unit': unit}, request=request)
    response = HttpResponse(rendered, status=status)
    response['HX-Trigger'] = 'placementRemoved'
    return response