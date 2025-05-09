from import_export import resources, fields
from . import models
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

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