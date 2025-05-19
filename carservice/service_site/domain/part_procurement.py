from .. import models
from ..enums import ProcurementStatusEnum
from .. import exceptions
from django.db import transaction


def remove_part_placement(placement_id):
    placement = models.StoragePlacement.objects.select_related('part_in_station', 'procurement_unit').prefetch_related(
        'procurement_unit__procurement_order__procurement_status').get(pk=placement_id)

    order = placement.procurement_unit.procurement_order 
    if order.procurement_status.status_name == ProcurementStatusEnum.DELIVERED:
        raise exceptions.ProcurementIsCompletedError("Cannot delete placement from completed order")
    
    if placement.part_in_station.quantity < placement.quantity:
        raise exceptions.NotEnoughPartsError("Cannot delete placement. Parts have been used")

    with transaction.atomic():
        placement.part_in_station.remove_parts(placement.quantity)
        placement.delete()