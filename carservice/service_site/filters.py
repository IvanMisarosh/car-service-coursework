import django_filters
from . import models

class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = models.Customer
        fields = {
            'first_name': ['startswith'],
            'last_name': ['icontains'],
            'email': ['startswith'],
            'phone_number': ['icontains']
            }   