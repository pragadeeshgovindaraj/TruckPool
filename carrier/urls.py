from django.urls import path
from . import views
from .views import carrier_plans, make_plan, carrier_shipment_details, label_document, label_document_view, \
    generate_qr_code, carrier_shipments_requests, shipment_accept, chatbot_window, shipment_truck_view, generate_route, \
    carrier_profile, update_trip_status, shipment_reject

urlpatterns = [

    path('carrier_plans', carrier_plans, name='carrier_plans'),
    path('make_plan', make_plan, name='make_plan'),
    path('carrier_profile', carrier_profile, name='carrier_profile'),
    path('carrier_shipment_details/<int:request_id>/', carrier_shipment_details, name='carrier_shipment_details'),
    path('shipment_truck_view/<int:request_id>/', shipment_truck_view, name='shipment_truck_view'),
    path('label_document_view/<int:shipment_id>/', label_document_view, name='label_document_view'),
    path('label_document/<int:shipment_id>/', label_document, name='label_document'),
    path('generate_qr_code/<int:shipment_id>/', generate_qr_code, name='generate_qr_code'),
    path('carrier_shipments_requests/<int:plan_id>/', carrier_shipments_requests, name='carrier_shipments_requests'),
    path('shipment_accept/<int:request_id>/', shipment_accept, name='shipment_accept'),
    path('shipment_reject/<int:request_id>/', shipment_reject, name='shipment_reject'),
    path('generate_route/<int:plan_id>/<str:criteria>', generate_route, name='generate_route'),
    path('chatbot_window_carrier', chatbot_window, name='chatbot_window_carrier'),
    path('update_trip_status/', update_trip_status, name='update_trip_status'),

]