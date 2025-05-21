from .. import models
from ..enums import ProcurementStatusEnum
from .. import exceptions
from django.db import transaction
from datetime import datetime

def delete_procurement_order(order_id):
    order = models.ProcurementOrder.objects.get(pk=order_id)
    order_number = order.order_number
    order.delete()
    return order_number

def add_order_unit(order_id, part_id, quantity, price_per_unit):
    part_id = int(part_id)
    quantity = int(quantity)
    price_per_unit = float(price_per_unit)

    if quantity < 1:
        raise exceptions.InvalidProcurementUnitData("Кількість має бути більше 0.")
    if price_per_unit <= 0:
        raise exceptions.InvalidProcurementUnitData("Ціна має бути більше 0.")

    part = models.Part.objects.get(pk=part_id)
    order = models.ProcurementOrder.objects.get(pk=order_id)

    return models.ProcurementUnit.objects.create(
        procurement_order=order,
        quantity=quantity,
        price_per_unit=price_per_unit,
        part=part
    )

def delete_procurement_unit(unit):
    placed_count = unit.get_placed_count()
    if placed_count > 0:
        raise exceptions.UnitHasPlacementsError(f"Неможливо видалити, оскільки {placed_count} одиниці вже розміщені.")
    
    unit.delete()

def update_procurement_unit(unit, quantity, price):
    placed = unit.get_placed_count()
    price = float(price)
    quantity = int(quantity)

    if quantity < 1:
        raise exceptions.InvalidProcurementUnitData("Кількість одиниць має бути вищою за 0")
    if quantity < placed:
        raise exceptions.InvalidProcurementUnitData(f"Кількість ({quantity}) менша за вже розміщені одиниці ({placed})")
    if price <= 0:
        raise exceptions.InvalidProcurementUnitData("Ціна за одиницю має бути вищою за 0")

    unit.quantity = quantity
    unit.price_per_unit = price
    unit.save()

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


def add_part_placement(unit, station_id, quantity):
    quantity = int(quantity)
    station_id = int(station_id)

    if quantity <= 0:
        raise exceptions.InvalidPlacementError("Кількість для розміщення має бути більшою за 0.")

    placed_count = unit.get_placed_count()
    available_quantity = unit.quantity - placed_count

    if quantity > available_quantity:
        raise exceptions.InvalidPlacementError(
            f"Кількість для розміщення має бути в діапазоні від 1 до {available_quantity}"
        )

    station = models.Station.objects.get(station_id=station_id)

    with transaction.atomic():
        part_in_station, _ = models.PartInStation.objects.get_or_create(
            station=station,
            part=unit.part,
            defaults={'quantity': 0}
        )
        part_in_station.quantity += quantity
        part_in_station.save()

        models.StoragePlacement.objects.create(
            procurement_unit=unit,
            part_in_station=part_in_station,
            quantity=quantity,
            placement_date=datetime.now()
        )