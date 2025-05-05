# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models import Sum
from django.utils import timezone
import random
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    employee = models.OneToOneField('Employee', null=True, blank=True, on_delete=models.CASCADE, db_column='EmployeeID')


class DriveType(models.Model):
    drive_type_id = models.AutoField(primary_key=True, db_column='DriveTypeID')
    drive_type_name = models.CharField(max_length=50, unique=True, db_column='DriveTypeName')

    class Meta:
        db_table = 'DriveType'   
    
    def __str__(self):
        return self.drive_type_name

class CarBrand(models.Model):
    car_brand_id = models.AutoField(primary_key=True, db_column='CarBrandID')
    brand_name = models.CharField(max_length=100, unique=True, db_column='BrandName')
    
    class Meta:
        db_table = 'CarBrand'  
    
    def __str__(self):
        return self.brand_name

class SuspensionType(models.Model):
    suspension_type_id = models.AutoField(primary_key=True, db_column='SuspensionTypeID')
    suspension_type_name = models.CharField(max_length=50, unique=True, db_column='SuspensionTypeName')
    
    class Meta:
        db_table = 'SuspensionType' 
    
    def __str__(self):
        return self.suspension_type_name

class TransmissionType(models.Model):
    transmission_type_id = models.AutoField(primary_key=True, db_column='TransmissionTypeID')
    transmission_type_name = models.CharField(max_length=50, unique=True, db_column='TransmissionTypeName')
    
    class Meta:
        db_table = 'TransmissionType' 
    
    def __str__(self):
        return self.transmission_type_name

class EngineType(models.Model):
    engine_type_id = models.AutoField(primary_key=True, db_column='EngineTypeID')
    engine_type_name = models.CharField(max_length=50, unique=True, db_column='EngineTypeName')
    
    class Meta:
        db_table = 'EngineType'
    
    def __str__(self):
        return self.engine_type_name

class BodyType(models.Model):
    body_type_id = models.AutoField(primary_key=True, db_column='BodyTypeID')
    body_type_name = models.CharField(max_length=50, unique=True, db_column='BodyTypeName')
    
    class Meta:
        db_table = 'BodyType'
    
    def __str__(self):
        return self.body_type_name

class CarModel(models.Model):
    car_model_id = models.AutoField(primary_key=True, db_column='CarModelID')
    model_name = models.CharField(max_length=100, unique=True, db_column='ModelName')
    dimensions = models.CharField(max_length=35, null=True, blank=True, db_column='Dimensions')
    drive_type = models.ForeignKey(DriveType, null=True, blank=True, on_delete=models.CASCADE, db_column='DriveTypeID')
    car_brand = models.ForeignKey(CarBrand, null=True, blank=True, on_delete=models.CASCADE, db_column='CarBrandID')
    suspension_type = models.ForeignKey(SuspensionType, null=True, blank=True, on_delete=models.CASCADE, db_column='SuspensionTypeID')
    transmission_type = models.ForeignKey(TransmissionType, null=True, blank=True, on_delete=models.CASCADE, db_column='TransmissionTypeID')
    engine_type = models.ForeignKey(EngineType, null=True, blank=True, on_delete=models.CASCADE, db_column='EngineTypeID')
    body_type = models.ForeignKey(BodyType, null=True, blank=True, on_delete=models.CASCADE, db_column='BodyTypeID')
    
    class Meta:
        db_table = 'CarModel'
    
    def __str__(self):
        return self.model_name

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True, db_column='CustomerID')
    email = models.CharField(max_length=100, null=True, blank=True, db_column='Email')
    first_name = models.CharField(max_length=50, db_column='FirstName')
    last_name = models.CharField(max_length=50, db_column='LastName')
    phone_number = models.CharField(max_length=15, db_column='PhoneNumber')
    
    class Meta:
        db_table = 'Customer'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_cars(self):
        cars = Car.objects.filter(customer=self.customer_id)
        return cars
    
    def get_car_num(self):
        cars = self.get_cars()
        return len(cars)
    
    def get_visits(self):
        return Visit.objects.filter(car__customer=self).order_by('-visit_date')
    
    def last_visit(self):
        """Returns the most recent visit for this customer."""
        return Visit.objects.filter(car__customer=self).order_by('-visit_date').first()
    
    def last_visit_date(self):
        return self.last_visit().visit_date


class Color(models.Model):
    color_id = models.AutoField(primary_key=True, db_column='ColorID')
    color_name = models.CharField(max_length=70, unique=True, db_column='ColorName')
    
    class Meta:
        db_table = 'Color'
    
    def __str__(self):
        return self.color_name

class Car(models.Model):
    car_id = models.AutoField(primary_key=True, db_column='CarID')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='CustomerID', related_name='cars')
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, db_column='CarModelID')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, db_column='ColorID')
    manufacture_year = models.IntegerField(null=True, blank=True, db_column='ManufactureYear')
    note = models.CharField(max_length=255, null=True, blank=True, db_column='Note')
    vin = models.CharField(max_length=17, unique=True, null=True, blank=True, db_column='VIN')
    mileage = models.IntegerField(null=True, blank=True, db_column='Mileage')
    
    class Meta:
        db_table = 'Car' 
    
    def __str__(self):
        return f"{self.car_model} ({self.vin})"

class PartType(models.Model):
    part_type_id = models.AutoField(primary_key=True, db_column='PartTypeID')
    part_type_name = models.CharField(max_length=100, unique=True, db_column='PartTypeName')
    
    class Meta:
        db_table = 'PartType'   
    
    def __str__(self):
        return self.parttype_name

class PartBrand(models.Model):
    part_brand_id = models.AutoField(primary_key=True, db_column='PartBrandID')
    brand_name = models.CharField(max_length=100, unique=True, db_column='BrandName')
    
    class Meta:
        db_table = 'PartBrand'
    
    def __str__(self):
        return self.brand_name

class Part(models.Model):
    part_id = models.AutoField(primary_key=True, db_column='PartID')
    part_brand = models.ForeignKey(PartBrand, null=True, blank=True, on_delete=models.SET_NULL, db_column='PartBrandID')
    part_type = models.ForeignKey(PartType, null=True, blank=True, on_delete=models.SET_NULL, db_column='PartTypeID')
    part_name = models.CharField(max_length=100, db_column='PartName')
    weight = models.DecimalField(max_digits=10, decimal_places=2, db_column='Weight')
    dimensions = models.CharField(max_length=100, null=True, blank=True, db_column='Dimensions')
    description = models.CharField(max_length=250, null=True, blank=True, db_column='Description')
    quantity_per_package = models.IntegerField(db_column='QuantityPerPackage')
    price_per_package = models.DecimalField(max_digits=10, decimal_places=2, db_column='PricePerPackage')
    
    class Meta:
        db_table = 'Part'
    
    def __str__(self):
        return self.part_name
    
    def get_price_per_unit(self):
        """Calculates the price per unit of the part."""
        return round(self.price_per_package / self.quantity_per_package, 2)

class Station(models.Model):
    station_id = models.AutoField(primary_key=True, db_column='StationID')
    address = models.CharField(max_length=100, db_column='Address')
    phone_number = models.CharField(max_length=25, db_column='PhoneNumber')
    
    class Meta:
        db_table = 'Station'
    
    def __str__(self):
        return self.address

class PartInStation(models.Model):
    part_in_station_id = models.AutoField(primary_key=True, db_column='PartInStationID')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, db_column='StationID')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, db_column='PartID')
    quantity = models.IntegerField(db_column='Quantity')
    
    class Meta:
        db_table = 'PartInStation'
        unique_together = ('station', 'part')   
    
    def __str__(self):
        return f"{self.part} at {self.station}"

class EmployeePosition(models.Model):
    employee_position_id = models.AutoField(primary_key=True, db_column='EmployeePositionID')
    position_name = models.CharField(max_length=100, unique=True, db_column='PositionName')
    
    class Meta:
        db_table = 'EmployeePosition'
    
    def __str__(self):
        return self.position_name

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True, db_column='EmployeeID')
    employee_position = models.ForeignKey(EmployeePosition, null=True, blank=True, on_delete=models.SET_NULL, db_column='EmployeePositionID')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, db_column='StationID')
    first_name = models.CharField(max_length=50, db_column='FirstName')
    last_name = models.CharField(max_length=50, db_column='LastName')
    email = models.CharField(max_length=100, null=True, blank=True, db_column='Email')
    phone_number = models.CharField(max_length=15, db_column='PhoneNumber')
    address = models.CharField(max_length=100, null=True, blank=True, db_column='Address')
    
    class Meta:
        db_table = 'Employee'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ServiceType(models.Model):
    service_type_id = models.AutoField(primary_key=True, db_column='ServiceTypeID')
    service_type_name = models.CharField(max_length=100, unique=True, db_column='ServiceTypeName')
    
    class Meta:
        db_table = 'ServiceType'
    
    def __str__(self):
        return self.service_type_name

class Service(models.Model):
    service_id = models.AutoField(primary_key=True, db_column='ServiceID')
    service_type = models.ForeignKey(ServiceType, null=True, blank=True, on_delete=models.SET_NULL, db_column='ServiceTypeID')
    service_name = models.CharField(max_length=100, unique=True, db_column='ServiceName')
    description = models.CharField(max_length=255, null=True, blank=True, db_column='Description')
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='Price')
    
    class Meta:
        db_table = 'Service'
    
    def __str__(self):
        return self.service_name

class VisitStatus(models.Model):
    visit_status_id = models.AutoField(primary_key=True, db_column='VisitStatusID')
    status_name = models.CharField(max_length=70, unique=True, db_column='StatusName')
    
    class Meta:
        db_table = 'VisitStatus'    
    
    def __str__(self):
        return self.status_name

class PaymentStatus(models.Model):
    payment_status_id = models.AutoField(primary_key=True, db_column='PaymentStatusID')
    payment_name = models.CharField(max_length=70, unique=True, db_column='PaymentName')
    
    class Meta:
        db_table = 'PaymentStatus'
        
    
    def __str__(self):
        return self.payment_name

class Visit(models.Model):
    visit_id = models.AutoField(primary_key=True, db_column='VisitID')
    visit_status = models.ForeignKey(VisitStatus, on_delete=models.CASCADE, db_column='VisitStatusID')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, db_column='CarID', related_name='visits')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmployeeID')
    payment_status = models.ForeignKey(PaymentStatus, null=True, blank=True, on_delete=models.SET_NULL, db_column='PaymentStatusID')
    visit_date = models.DateTimeField(default=timezone.now, db_column='VisitDate')
    planned_end_date = models.DateTimeField(null=True, blank=True, db_column='PlannedEndDate')
    actual_end_date = models.DateTimeField(null=True, blank=True, db_column='ActualEndDate')
    details = models.CharField(max_length=500, null=True, blank=True, db_column='Details')
    visit_number = models.IntegerField(db_column='VisitNumber')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='Price')
    payment_date = models.DateTimeField(null=True, blank=True, db_column='PaymentDate')
    
    class Meta:
        db_table = 'Visit'
    
    def __str__(self):
        return f"Visit {self.visit_number} - {self.car}"
    
    def visit_service_count(self):
        services = VisitService.objects.filter(visit=self.visit_id)
        return len(services)
    
    @staticmethod
    def generate_visit_number():
        """Generates a unique visit number."""
        while True:
            visit_number = random.randint(1000, 999999999)
            if not Visit.objects.filter(visit_number=visit_number).exists():
                break
        return visit_number
        

class VisitService(models.Model):
    visit_service_id = models.AutoField(primary_key=True, db_column='VisitServiceID')
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, db_column='VisitID', related_name='visit_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, db_column='ServiceID')
    quantity = models.IntegerField(db_column='Quantity')
    
    class Meta:
        db_table = 'VisitService'
    
    def __str__(self):
        return f"{self.service} for {self.visit}"
    
    def get_total_price(self):
        """Calculates the total price for this service."""
        return self.service.price * self.quantity

class ProvidedService(models.Model):
    provided_service_id = models.AutoField(primary_key=True, db_column='ProvidedServiceID')
    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, db_column='EmployeeID')
    visit_service = models.OneToOneField(VisitService, on_delete=models.CASCADE, db_column='VisitServiceID', related_name='provided_service')
    provided_date = models.DateTimeField(null=True, blank=True, db_column='ProvidedDate')
    
    class Meta:
        db_table = 'ProvidedService'  
    
    def __str__(self):
        return f"Service provided: {self.visitservice}"
    
    def get_total_price(self):
        """Calculates the total price for this provided service."""
        required_parts_price = 0
        for r_part in self.required_parts.all():
            required_parts_price += r_part.get_total_price()
            
        return self.visit_service.get_total_price() + required_parts_price

class RequiredPart(models.Model):
    required_part_id = models.AutoField(primary_key=True, db_column='RequiredPartID')
    part_in_station = models.ForeignKey(PartInStation, on_delete=models.CASCADE, db_column='PartInStationID')
    provided_service = models.ForeignKey(ProvidedService, on_delete=models.CASCADE, db_column='ProvidedServiceID', related_name='required_parts')
    quantity = models.IntegerField(db_column='Quantity')
    
    class Meta:
        db_table = 'RequiredPart'   
    
    def __str__(self):
        return f"{self.quantity} of {self.partinstation.part} for {self.providedservice}"
    
    def get_part_price(self):
        """Calculates the price for this required part."""
        return round(self.part_in_station.part.price_per_package / self.part_in_station.part.quantity_per_package, 2)
    
    def get_total_price(self):
        """Calculates the total price for this required part record."""
        return round(self.get_part_price() * self.quantity, 2)

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True, db_column='SupplierID')
    email = models.CharField(max_length=100, null=True, blank=True, db_column='Email')
    phone_number = models.CharField(max_length=15, null=True, blank=True, db_column='PhoneNumber')
    supplier_name = models.CharField(max_length=100, null=True, blank=True, db_column='SupplierName')
    
    class Meta:
        db_table = 'Supplier'   
    
    def __str__(self):
        return self.supplier_name

class ProcurementStatus(models.Model):
    procurement_status_id = models.AutoField(primary_key=True, db_column='ProcurementStatusID')
    status_name = models.CharField(max_length=50, null=True, blank=True, db_column='StatusName')
    
    class Meta:
        db_table = 'ProcurementStatus'  
    
    def __str__(self):
        return self.status_name

class ProcurementOrder(models.Model):
    procurement_order_id = models.AutoField(primary_key=True, db_column='ProcurementOrderID')
    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, db_column='EmployeeID')
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL, db_column='SupplierID')
    procurement_status = models.ForeignKey(ProcurementStatus, null=True, blank=True, on_delete=models.SET_NULL, db_column='ProcurementStatusID')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='TotalPrice')
    order_date = models.DateTimeField(null=True, blank=True, db_column='OrderDate')
    order_number = models.CharField(max_length=50, null=True, blank=True, db_column='OrderNumber')
    
    class Meta:
        db_table = 'ProcurementOrder'   
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    @staticmethod
    def generate_order_number():
        """Generates a unique visit number."""
        while True:
            order_number = random.randint(1, 999999999)
            if not ProcurementOrder.objects.filter(order_number=order_number).exists():
                break
        return order_number

class ProcurementUnit(models.Model):
    procurement_unit_id = models.AutoField(primary_key=True, db_column='ProcurementUnitID')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, db_column='PartID')
    quantity = models.IntegerField(db_column='Quantity')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='PricePerUnit')
    procurement_order = models.ForeignKey(ProcurementOrder, null=True, blank=True, on_delete=models.SET_NULL, db_column='ProcurementOrderID', related_name='units')
    
    class Meta:
        db_table = 'ProcurementUnit'  
    
    def __str__(self):
        return f"{self.quantity} of {self.part}"
    
    def get_total_price(self):
        return self.quantity * self.price_per_unit
    
    def get_placed_count(self):
        result = self.placements.aggregate(total_placed=Sum('quantity'))
        return result['total_placed'] or 0

class StoragePlacement(models.Model):
    storage_placement_id = models.AutoField(primary_key=True, db_column='StoragePlacementID')
    procurement_unit = models.ForeignKey(ProcurementUnit, on_delete=models.CASCADE, db_column='ProcurementUnitID', related_name='placements')
    part_in_station = models.ForeignKey(PartInStation, on_delete=models.CASCADE, db_column='PartInStationID')
    quantity = models.IntegerField(null=True, blank=True, db_column='Quantity')
    placement_date = models.DateTimeField(null=True, blank=True, db_column='PlacementDate')
    
    class Meta:
        db_table = 'StoragePlacement'   
    
    def __str__(self):
        return f"Placement of {self.quantity} {self.procurement_unit.part}"

