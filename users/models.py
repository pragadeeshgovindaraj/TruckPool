from django.db import models

# Create your models here.

# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission, Group


class VehicleType(models.Model):
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    length = models.FloatField(help_text='length of vehicle')
    height = models.FloatField(help_text='height of vehicle')
    width = models.FloatField(help_text='width of vehicle')
    weight = models.FloatField(help_text='weight')

    def __str__(self):
        return self.code


class CarrierUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class CarrierUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CarrierUserManager()

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='carrier_user_permissions',  # Add this line
        help_text='Specific permissions for this user.'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='carrier_user_groups',  # Add this line
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class ShipperUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CarrierUserManager()
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='shipper_user_permissions',  # Add this line
        help_text='Specific permissions for this user.'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='shipper_user_groups',  # Add this line
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class ShipperIndividual(models.Model):
    user = models.OneToOneField(ShipperUser, on_delete=models.CASCADE)
    # Additional fields specific to the Carrier model
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    contact_no = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ShipperBusiness(models.Model):
    user = models.OneToOneField(ShipperUser, on_delete=models.CASCADE)
    # Additional fields specific to the Carrier model
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    contact_no = models.CharField(max_length=15)
    company_name = models.CharField(max_length=100)
    company_URL = models.CharField(max_length=250)
    per_month_estimate_ship = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company_name}"


# Create a new model for Carrier with a foreign key to CarrierUser
class Carrier(models.Model):
    user = models.OneToOneField(CarrierUser, on_delete=models.CASCADE)
    # Additional fields specific to the Carrier model
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    contact_no = models.CharField(max_length=15)
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=10)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company_name}"
