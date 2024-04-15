from functools import wraps
from django.shortcuts import redirect
from .models import ShipperUser, CarrierUser


def shipper_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not isinstance(request.user, ShipperUser):
            # Redirect to a forbidden page or login page or any other appropriate page
            return redirect('forbidden_page')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def carrier_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not isinstance(request.user, CarrierUser):
            # Redirect to a forbidden page or login page or any other appropriate page
            return redirect('forbidden_page')
        return view_func(request, *args, **kwargs)

    return _wrapped_view
