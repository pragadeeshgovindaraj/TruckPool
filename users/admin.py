from django.contrib import admin

from .models import Carrier, ShipperIndividual, ShipperBusiness

# Register your models here.
admin.site.register(Carrier)
admin.site.register(ShipperIndividual)
admin.site.register(ShipperBusiness)