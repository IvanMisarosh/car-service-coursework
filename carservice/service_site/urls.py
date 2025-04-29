from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('customers/', views.customer_list, name='customers'),
    path('customer-details/', views.customer_details, name="customer-details"),

    path('customer-search/', views.customer_search, name='customer-search'),
    path('customer-search-page/', views.get_customer_search, name='customer-search-page'),
    path('select-visit-customer/', views.select_visit_customer, name='select-visit-customer'),

    path('visits/', views.Visits.as_view(), name='visits'),

    path('add-staged-service/', views.add_staged_service, name='add-staged-service'),
    path('update-staged-service/', views.update_staged_service, name='update-staged-service'),
    path('remove-staged-service/', views.remove_staged_service, name='remove-staged-service'),
    path('save-staged-services/', views.save_staged_services, name='save-staged-services'),
    path('clear-staged-services/', views.clear_staged_services, name='clear-staged-services'),

    path('add-staged-part/', views.add_staged_part, name='add-staged-part'),
    path('update-staged-part/', views.update_staged_part, name='update-staged-part'),
    path('remove-staged-part/', views.remove_staged_part, name='remove-staged-part'),
    path('save-staged-parts/', views.save_staged_parts, name='save-staged-parts'),

    path('select-car-in-car-search-modal', views.select_car_in_car_search_modal, name='select-car-in-car-search-modal'),

    path('visit-detail/', views.VisitDetailView.as_view(), name='create-visit'),
    path('visit-detail/car-search', views.car_search, name='car-search'),
    path('visit-detail/service-search', views.service_search, name='service-search'),
    path('visit-detail/update-visit-car', views.update_visit_car, name='update-visit-car'),
    path('visit-detail/<int:visit_id>/', views.VisitDetailView.as_view(), name='visit-detail'),

    path('visit-service/<int:visit_service_id>/', views.VisitServiceView.as_view(), name='visit-service'),
    path('visit-services/<int:visit_id>/', views.visit_services, name='visit-services'),

    path('visit-service/part-search', views.part_search, name='part-search'),
    path('service-part-search/<int:visit_service_id>', views.visit_service_with_part_search, name='service-part-search'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
