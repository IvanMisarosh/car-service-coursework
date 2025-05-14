from import_export import resources, fields
from . import models
from import_export import resources, fields
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

class ProcurementOrderResource(resources.ModelResource):
    order_number = Field(
        attribute='order_number',
        column_name='Order Number'
    )
    employee_name = Field(
        column_name='Employee'
    )
    employee_position = Field(
        attribute='employee__employee_position__position_name',
        column_name='Position'
    )
    supplier_name = Field(
        attribute='supplier__supplier_name',
        column_name='Supplier'
    )
    supplier_contact = Field(
        column_name='Supplier Contact'
    )
    status = Field(
        attribute='procurement_status__status_name',
        column_name='Status'
    )
    total_price = Field(
        attribute='total_price',
        column_name='Total Price'
    )
    order_date = Field(
        attribute='order_date',
        column_name='Order Date'
    )
    
    class Meta:
        model = models.ProcurementOrder
        fields = (
            'order_number', 'employee_name', 'employee_position', 
            'supplier_name', 'supplier_contact', 'status',
            'total_price', 'order_date'
        )
        export_order = fields

    def dehydrate_employee_name(self, procurement_order):
        return f"{procurement_order.employee.first_name} {procurement_order.employee.last_name}"
    
    def dehydrate_supplier_contact(self, procurement_order):
        contacts = []
        if procurement_order.supplier.email:
            contacts.append(procurement_order.supplier.email)
        if procurement_order.supplier.phone_number:
            contacts.append(procurement_order.supplier.phone_number)
        return ", ".join(contacts) if contacts else "N/A"

class VisitServiceResource(resources.ModelResource):
    visit_number = Field(
        attribute='visit__visit_number',
        column_name='Visit Number'
    )
    car = Field(
        attribute='visit__car',
        column_name='Car'
    )
    service_name = Field(
        attribute='service__service_name',
        column_name='Service'
    )
    service_price = Field(
        attribute='service__price',
        column_name='Price per Unit'
    )
    quantity = Field(
        column_name='Quantity'
    )
    total_price = Field(
        column_name='Total Price'
    )
    visit_date = Field(
        attribute='visit__visit_date',
        column_name='Visit Date'
    )
    status = Field(
        attribute='visit__visit_status__status_name',
        column_name='Visit Status'
    )
    payment_status = Field(
        attribute='visit__payment_status__payment_name',
        column_name='Payment Status'
    )
    
    class Meta:
        model = models.VisitService
        fields = (
            'visit_number', 'car', 'service_name', 'service_price',
            'quantity', 'total_price', 'visit_date', 'status', 'payment_status'
        )
        export_order = fields
    
    def dehydrate_total_price(self, visit_service):
        return visit_service.get_total_price()


class CustomerResource(resources.ModelResource):
    """
    Resource for exporting Customer data with related car information.
    Includes nested car data (model, brand, and color).
    """
    # Basic customer fields will be exported automatically
    
    # Custom field to include car information in the export
    cars = fields.Field(column_name='cars', attribute='cars')
    
    class Meta:
        model = models.Customer
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'cars')
        export_order = fields
    
    def dehydrate_cars(self, customer):
        """
        Custom method to format car information for each customer.
        Returns car model, brand and color information in a readable format.
        """
        car_info = []
        for car in customer.cars.all():
            # Get brand name through the relationship (car_model -> car_brand -> brand_name)
            brand_name = car.car_model.car_brand.brand_name if car.car_model.car_brand else "N/A"
            
            # Get model name
            model_name = car.car_model.model_name if car.car_model else "N/A"
            
            # Get color name
            color_name = car.color.color_name if hasattr(car.color, 'color_name') else "N/A"
            
            car_info.append(f"{brand_name} {model_name} ({color_name})")
        
        # Join all car information with semicolons
        return "; ".join(car_info) if car_info else "No cars"
    

class VisitResource(resources.ModelResource):
    visit_number = Field(
        attribute='visit_number',
        column_name='Visit Number'
    )
    customer_name = Field(
        column_name='Customer Name'
    )
    car_vin = Field(
        attribute='car__vin',
        column_name='VIN'
    )
    employee_name = Field(
        column_name='Employee Name'
    )
    station_address = Field(
        attribute='employee__station__address',
        column_name='Service Station'
    )
    visit_status = Field(
        attribute='visit_status__status_name',
        column_name='Visit Status'
    )
    payment_status = Field(
        attribute='payment_status__payment_name',
        column_name='Payment Status'
    )
    visit_date = Field(
        attribute='visit_date',
        column_name='Visit Date'
    )
    planned_end_date = Field(
        attribute='planned_end_date',
        column_name='Planned End Date'
    )
    actual_end_date = Field(
        attribute='actual_end_date',
        column_name='Actual End Date'
    )
    details = Field(
        attribute='details',
        column_name='Details'
    )
    price = Field(
        attribute='price',
        column_name='Price'
    )
    payment_date = Field(
        attribute='payment_date',
        column_name='Payment Date'
    )
    
    class Meta:
        model = models.Visit
        fields = (
            'visit_number', 'customer_name', 'car_vin', 'employee_name', 
            'station_address', 'visit_status', 'payment_status', 'visit_date',
            'planned_end_date', 'actual_end_date', 'details', 'price', 'payment_date'
        )
        export_order = fields
    
    def dehydrate_customer_name(self, visit):
        return f"{visit.car.customer.first_name} {visit.car.customer.last_name}"
    
    def dehydrate_employee_name(self, visit):
        return f"{visit.employee.first_name} {visit.employee.last_name}"