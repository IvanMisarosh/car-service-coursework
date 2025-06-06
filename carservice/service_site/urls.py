from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('customers/', views.customer_list, name='customers'),
    path('customer-details/', views.customer_details, name="customer-details"),
    path('customers/edit/<int:pk>/', views.get_customer_edit_row, name='edit-customer-row'),
    path('customers/row/<int:pk>/', views.get_customer_row, name='get-customer-row'),
    path('customers/add/', views.CustomerAddView.as_view(), name='add-customer-form'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete-customer'),
    path('cars/add/', views.CarAddView.as_view(), name='add-car-form'),
    path("cars/<int:car_id>/delete/", views.delete_car, name="delete-car"),
    path("cars/<int:car_id>/row/", views.selected_customer_car_list_row, name="selected-customer-car"),
    path("customers/<int:customer_id>/cars/", views.selected_customer_car_list, name="selected-customer-car-list"),

    path('export/customers/', views.export_customers, name='export-customers'),
    path('export/customers/xlsx/', views.export_customers, {'format': 'xlsx'}, name='export_customers_xlsx'),
    path('export/customers/json/', views.export_customers, {'format': 'json'}, name='export_customers_json'),

    path('customer-search/', views.customer_search, name='customer-search'),
    path('customer-search-page/', views.get_customer_search, name='customer-search-page'),
    path('select-visit-customer/', views.select_visit_customer, name='select-visit-customer'),

    path('visits/', views.Visits.as_view(), name='visits'),
    path("visits/<int:visit_id>/delete/", views.Visits.as_view(), name="delete-visit"),
    path('export/visits/', views.export_visits, name='export-visits'),

    path('add-staged-service/', views.add_staged_service, name='add-staged-service'),
    path('update-staged-service/', views.update_staged_service, name='update-staged-service'),
    path('remove-staged-service/', views.remove_staged_service, name='remove-staged-service'),
    path('save-staged-services/', views.save_staged_services, name='save-staged-services'),
    path('clear-staged-services/', views.clear_staged_services, name='clear-staged-services'),

    path('add-staged-part/', views.add_staged_part, name='add-staged-part'),
    path('update-staged-part/', views.update_staged_part, name='update-staged-part'),
    path('remove-staged-part/', views.remove_staged_part, name='remove-staged-part'),
    path('save-staged-parts/', views.save_staged_parts, name='save-staged-parts'),

    path('select-car-in-car-search-modal', views.select_car_from_search, name='select-car-in-car-search-modal'),

    path('visit-detail/car-search', views.car_search, name='car-search'),
    path('visit-detail/service-search', views.service_search, name='service-search'),
    path('visit-detail/update-visit-car', views.update_visit_car, name='update-visit-car'),
    path('visit-detail/<int:visit_id>/', views.visit_details, name='visit-detail'),
    path('visit/info/<int:visit_id>/', views.visit_info, name='visit-info'),
    path('visit-detail/get-form', views.get_visit_form, name='get-visit-form'),
    path('visit-detail/', views.save_visit_form, name='save-visit'),

    path('export-visit-services/<int:visit_id>', views.export_visit_services, name='export-visit-services'),

    path('visit-service/<int:visit_service_id>/edit/', views.edit_visit_service, name='visit-service-edit'),
    path('visit-service/<int:visit_service_id>/delete/', views.delete_visit_service, name='visit-service-delete'),
    path('visit-services/<int:visit_id>/', views.visit_services, name='visit-services'),

    path('visit-service/part-search', views.part_search, name='part-search'),
    path('required-parts/<int:required_part_id>/delete/', views.delete_required_part, name='delete-required-part'),
    path('service-part-search/<int:visit_service_id>', views.visit_service_with_part_search, name='service-part-search'),

    path('procurement/orders/add/', views.add_order, name='add-procurement-order'),
    path('procurement/orders/', views.procurement_orders, name='procurement-orders'),
    path('procurement/order/<int:order_id>/items/', views.procurement_order_items, name='procurement-order-items'),

    path('export-procurement-orders/', views.export_procurement_orders, name='export-procurement-orders'),
    
    path('order-info/<int:pk>/', views.order_info, name='order-info'),
    path('order/<int:order_id>/update/', views.update_order_row, name='update-order'),
    path("procurements/<int:order_id>/delete/", views.delete_procurement_order, name="delete-procurement-order"),
    path('edit-order-info/<int:pk>/', views.edit_order_info, name='edit-order-info'),

    path('procurement/unit/<int:unit_id>', views.edit_unit, name="edit_unit"),

    path('procurement/order/<int:order_id>/unit/add', views.AddOrderUnitView.as_view(), name='add-order-unit'),
    path("procurement-units/<int:unit_id>/delete/", views.delete_procurement_unit, name="delete-procurement-unit"),
    path('unit/<int:pk>/placements/', views.unit_placements, name='unit_placements'),
    path('unit/<int:unit_id>/add-placement/', views.AddPlacementView.as_view(), name='add_placement'),
    path('unit/<int:unit_id>/update/', views.update_row, name='update-unit'),
    path("unit/<int:placement_id>/remove-placement/", views.remove_placement, name="remove-placement"),

    path('populate-unit-part-select', views.part_search_for_unit, name='unit-part-search'),

    path('suppliers/', views.SuppliersView.as_view(), name='suppliers'),
    path('suppliers/<int:supplier_id>/edit/', views.SupplierView.as_view(), name='edit-supplier'),
    path('suppliers/<int:supplier_id>/delete/', views.SupplierView.as_view(), name='delete-supplier'),
    path('suppliers/add-supplier-form', views.SupplierView.as_view(), name='add-supplier-form'),
    path('suppliers/edit-row/<int:pk>/', views.get_supplier_edit_row, name="edit-supplier-row"),
    path('suppliers/get-list-row/<int:pk>/', views.get_supplier_row, name="get-list-row"),

    path('car-models/', views.CarModelsView.as_view(), name='car-models'),
    path('car-models/<int:car_model_id>/delete/', views.CarModelsView.as_view(), name='delete-car-model'),
    path('car-models/add', views.add_car_model, name="add-car-model"),
    path('get-car-model-card/<int:pk>', views.view_car_model, name="view-car-model"),
    path('edit-car-model/<int:pk>', views.edit_car_model, name='edit-car-model'),

    path('carmodels/check-model-name', views.check_model_name, name='check-model-name'),

    # Part URLs
    path('parts/', views.PartsView.as_view(), name='parts'),
    path('part/add/', views.PartFormView.as_view(), name='add-part-form'),
    path('part/<int:part_id>/edit/', views.PartEditView.as_view(), name='edit-part'),
    path("parts/<int:part_id>/delete/", views.delete_part, name="delete-part"),
    path('part/<int:part_id>/edit-form/', views.PartEditView.as_view(), name='edit-part-form'),
    path('part/<int:part_id>/row/', views.PartRowView.as_view(), name='get-part-row'),
    path('parts/<int:part_id>/availability/', views.part_availability, name='part-availability'),

    # Маршрути для станцій
    path('stations/', views.StationsView.as_view(), name='stations'),
    path('add-station/', views.add_station, name='add-station'),
    path('stations/<int:station_id>/delete/', views.delete_station, name='station-delete'),
    path('view-station/<int:pk>/', views.view_station, name='view-station'),
    path('edit-station/<int:pk>/', views.edit_station, name='edit-station'),
    path('station-employees/<int:pk>/', views.station_employees, name='station-employees'),
    path('station-equipment/<int:pk>/', views.station_equipment, name='station-equipment'),
    path('station-empty/<int:pk>/', views.station_empty, name='station-summary'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]
