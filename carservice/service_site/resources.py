from import_export import resources, fields
from . import models
from import_export import resources, fields
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

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