from django.db import models
from django.utils import timezone

from users.models import ShipperUser

from users.models import ShipperIndividual

from users.models import Carrier

from TruckPool_Django import settings
from carrier.models import CarrierPlan


# Create your models here.
class Shipment(models.Model):
    shipper_user = models.ForeignKey(ShipperIndividual, on_delete=models.CASCADE)
    length = models.FloatField()

    height = models.FloatField()
    width = models.FloatField()
    weight = models.FloatField()
    quantity = models.IntegerField()
    pickup_location = models.CharField(max_length=255)
    pickup_address = models.CharField(max_length=255)
    drop_off_location = models.CharField(max_length=255)
    drop_off_address = models.CharField(max_length=255)
    # is_stackable = models.BooleanField(default=False)
    # is_hazardous = models.BooleanField(default=False)
    pickup_date = models.DateField()
    status = models.CharField(max_length=20, default='Pending', blank=True)
    direct_distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pickup_city = models.CharField(max_length=80, blank=True)
    drop_off_city = models.CharField(max_length=80, blank=True)

    estimated_quotation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qrcode_image = models.ImageField(upload_to='static/images/shipment_qrcodes/', null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Shipment - {self.pk}, length : {self.length}, height: {self.height}, width: {self.width} '


class CarrierRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('paid', 'paid'),
        ('fulfilled', 'fulfilled'),
    ]

    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    carrier_plan = models.ForeignKey(CarrierPlan, on_delete=models.CASCADE)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date = models.DateTimeField(auto_now_add=True)
    quote = models.FloatField()

    def __str__(self):
        return f"Carrier Request - {self.shipment.title} by {self.carrier.user.username}"


class PaymentDetails(models.Model):
    request_id = models.ForeignKey(CarrierRequest, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    card_number = models.CharField(max_length=16)
    expiration_date = models.CharField(max_length=7)
    cvv = models.CharField(max_length=4)
    payment_date = models.DateField(default=timezone.now)


    def __str__(self):
        return f"Payment for Request {self.request_id}"


class Rating(models.Model):
    shipper_user = models.ForeignKey(ShipperUser, on_delete=models.CASCADE)
    ship_request = models.ForeignKey(CarrierRequest, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'),
                                                     (5, '5 Stars')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shipper_user.username} - {self.ship_request.id} - {self.rating}"


class Review(models.Model):
    shipper_user = models.ForeignKey(ShipperUser, on_delete=models.CASCADE)
    ship_request = models.ForeignKey(CarrierRequest, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shipper_user.username} - {self.ship_request.id} - {self.timestamp}"


class ShipmentRequestTracking(models.Model):
    STATUS_CHOICES = [
        ('picked', 'Picked'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]
    carrier_plan = models.ForeignKey(CarrierPlan, on_delete=models.CASCADE)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    current_status =  models.CharField(max_length=20, choices=STATUS_CHOICES, default='')
    est_pickup_time = models.DateTimeField(blank=True, null=True)
    est_drop_off_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.shipment.id} - {self.current_status}"