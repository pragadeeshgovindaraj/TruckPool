from django.contrib.auth.backends import  BaseBackend
from .models import ShipperUser, CarrierUser


class ShipperUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Implement authentication logic for ShipperUser
        try:
            user = ShipperUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except ShipperUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ShipperUser.objects.get(pk=user_id)
        except ShipperUser.DoesNotExist:
            return None


class CarrierUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Implement authentication logic for CarrierUser
        try:
            user = CarrierUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except CarrierUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CarrierUser.objects.get(pk=user_id)
        except CarrierUser.DoesNotExist:
            return None
