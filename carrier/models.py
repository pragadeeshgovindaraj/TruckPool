from django.core.exceptions import ValidationError
from django.db import models

from django.db import models
from users.models import Carrier


class CarrierPlan(models.Model):
    carrier_user = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    date_of_plan = models.DateField()
    start_location = models.CharField(max_length=255)
    start_address = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    end_address = models.CharField(max_length=255)
    space_available = models.FloatField(help_text='Space available in van in percentage')
    desired_rate = models.DecimalField(max_digits=10, decimal_places=4,
                                       help_text='Desired rate per cubic meter')

    start_city = models.CharField(max_length=80, blank=True)
    end_city = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, default='Open', blank=True)
    create_date = models.DateTimeField(auto_now_add=True)


    def clean(self):
        # Check if a plan already exists for the given date and carrier user with status "Open"
        existing_plans = CarrierPlan.objects.filter(
            date_of_plan=self.date_of_plan,
            carrier_user=self.carrier_user,
            status__in=['Open', 'In Transit']
        )

        if self.pk:  # If this is an update operation, exclude the current plan
            existing_plans = existing_plans.exclude(pk=self.pk)

        if existing_plans.exists():
            raise ValidationError("You already have an open plan for this date.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run full validation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Carrier Plan - {self.date_of_plan} ({self.start_location} to {self.end_location})"


class CarrierPlanRoute(models.Model):
    carrier_plan = models.ForeignKey(CarrierPlan, on_delete=models.CASCADE)
    path_data = models.JSONField()
    path_seq = models.JSONField()
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrier Plan - {self.carrier_plan}"


class CarrierCurrentLocation(models.Model):
    carrier_plan = models.ForeignKey(CarrierPlan, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Location ({self.carrier_plan.id} - {self.latitude}, {self.longitude})"