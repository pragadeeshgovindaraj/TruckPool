# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import CarrierUser, Carrier, ShipperIndividual, ShipperBusiness, ShipperUser, VehicleType


class CarrierUserCreationForm(UserCreationForm):
    class Meta:
        model = CarrierUser
        fields = ['email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add any additional customization for form fields here
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                # 'placeholder': self.fields[field_name].label,
                'class': 'form-control',  # Add other classes as needed
            })


class CarrierRegistrationForm(forms.ModelForm):
    vehicle_type = forms.ModelChoiceField(queryset=VehicleType.objects.all(), empty_label=None)

    class Meta:
        model = Carrier
        fields = ['first_name', 'last_name', 'contact_no', 'company_name', 'vehicle_type', 'address', 'postal_code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add any additional customization for form fields here
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                # 'placeholder': self.fields[field_name].label,
                'class': 'form-control',  # Add other classes as needed
            })

            '''       # Remove labels
        for field_name, field in self.fields.items():
            field.label = '''''


class ShipperIndividualRegistrationForm(forms.ModelForm):
    class Meta:
        model = ShipperIndividual
        fields = ['first_name', 'last_name', 'contact_no']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add any additional customization for form fields here
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                # 'placeholder': self.fields[field_name].label,
                'class': 'form-control',  # Add other classes as needed
            })

            '''       # Remove labels
        for field_name, field in self.fields.items():
            field.label = '''''


class ShipperBusinessRegistrationForm(forms.ModelForm):
    class Meta:
        model = ShipperBusiness
        fields = ['first_name', 'last_name', 'contact_no', 'company_name', 'company_URL', 'per_month_estimate_ship']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add any additional customization for form fields here
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                # 'placeholder': self.fields[field_name].label,
                'class': 'form-control',  # Add other classes as needed
            })

            '''       # Remove labels
        for field_name, field in self.fields.items():
            field.label = '''''


class ShipperUserCreationForm(UserCreationForm):
    class Meta:
        model = ShipperUser
        fields = ['email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add any additional customization for form fields here
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                # 'placeholder': self.fields[field_name].label,
                'class': 'form-control',  # Add other classes as needed
            })


class CustomAuthenticationForm(AuthenticationForm):
    # email = forms.EmailField(required=True, label="Enter Email Address..")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # del self.fields['username']
        for name in self.fields.keys():
            field = self.fields[name]
            self.fields[name].widget.attrs.update({
                'placeholder': self.fields[name].label,
                'class': 'form-control  form-control-user',
            })

            field.label = ''
            field.widget.attrs.update({'aria-label': field.label})
