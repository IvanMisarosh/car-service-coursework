from .. import models, exceptions
from django.db import transaction

def update_visit_service_quantity(visit_service, quantity):
    if quantity < 1:
        raise exceptions.InvalidVisitServiceData("Кількість має бути вищою за 0.")
    visit_service.set_quantity(quantity)

def delete_visit_service(visit_service):
    visit_service.delete()

def delete_required_part(required_part):
    part_in_station = required_part.part_in_station
    qty = required_part.quantity

    with transaction.atomic():
        required_part.delete()
        part_in_station.add_parts(qty)

