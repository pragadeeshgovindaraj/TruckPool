# users/urls.py
from django.urls import path
from . import views
from .views import index, register_carrier, register_shipper, signin_view, logout_view, success_registration, \
    shipper_view, carrier_view, forbidden_page, chat_with_bot

urlpatterns = [
    path('', index, name='index'),
    path('carrier_signup', register_carrier, name='carrier_signup'),
    path('shipper_signup', register_shipper, name='shipper_signup'),
    path('success_registration', success_registration, name='success_registration'),
    path('forbidden_page', forbidden_page, name='forbidden_page'),
    path('shipper_view', shipper_view, name='shipper_view'),
    path('carrier_view', carrier_view, name='carrier_view'),
    path('chat_with_bot/', chat_with_bot, name='chat_with_bot'),
    path('signin/', signin_view, name='signin'),
    path('logout/', logout_view, name='logout'),

]
