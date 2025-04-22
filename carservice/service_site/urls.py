from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('customers/', views.customer_list, name='customers'),
    path('customer-details/', views.customer_details, name="customer-details"),
    path('visits/', views.Visits.as_view(), name='visits'),

    path('add-staged-service/', views.add_staged_service, name='add-staged-service'),
    path('update-staged-service/', views.update_staged_service, name='update-staged-service'),
    path('remove-staged-service/', views.remove_staged_service, name='remove-staged-service'),
    path('save-staged-services/', views.save_staged_services, name='save-staged-services'),
    path('clear-staged-services/', views.clear_staged_services, name='clear-staged-services'),

    path('select-car-in-car-search-modal', views.select_car_in_car_search_modal, name='select-car-in-car-search-modal'),

    path('visit-detail/', views.VisitDetailView.as_view(), name='create-visit'),
    path('visit-detail/car-search', views.car_search, name='car-search'),
    path('visit-detail/service-search', views.service_search, name='service-search'),
    path('visit-detail/update-visit-car', views.update_visit_car, name='update-visit-car'),
    path('visit-detail/<int:visit_id>/', views.VisitDetailView.as_view(), name='visit-detail'),

    path('visit-service/<int:visit_service_id>/', views.VisitServiceView.as_view(), name='visit-service'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
