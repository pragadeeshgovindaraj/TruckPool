from django.urls import path
from . import views
from .views import book_shipment, edit_shipment, shipment_details, generate_estimate, user_shipments, \
    view_shipment_details, book_carrier, payment_view, payment_success, chatbot_window, submit_review, \
    view_carrier_profile

urlpatterns = [

    path('book_shipment', book_shipment, name='book_shipment'),
    path('shipment_details/<int:shipment_id>/<str:sort_by>/', shipment_details, name='shipment_details'),
    path('edit_shipment/<int:shipment_id>/', edit_shipment, name='edit_shipment'),
    path('generate_estimate/', generate_estimate, name='generate_estimate'),
    path('user_shipments/<str:status>/', user_shipments, name='user_shipments'),
    #path('match_with_carrier', match_with_carrier, name='match_with_carrier'),
    path('book_carrier/', book_carrier, name='book_carrier'),
    path('payment_success/', payment_success, name='payment_success'),

    path('view_shipment_details/<int:shipment_id>/', view_shipment_details, name='view_shipment_details'),
    path('payment_view/<int:request_id>/', payment_view, name='payment_view'),
    path('chatbot_window_shipper', chatbot_window, name='chatbot_window_shipper'),
    path('submit_review/', submit_review, name='submit_review'),
    path('view_carrier_profile/', view_carrier_profile, name='view_carrier_profile'),

]