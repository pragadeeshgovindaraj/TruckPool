from django import forms

from .models import Shipment, PaymentDetails


class ShipmentForm(forms.ModelForm):
    length = forms.CharField(
        label='Length',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'maxlength' : '4'})

    )

    width = forms.CharField(
        label='Width',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'maxlength': '4'
                                      })

    )

    weight = forms.CharField(
        label='weight',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'maxlength': '6'
                                      })

    )

    estimated_quotation = forms.CharField(
        label='Estimate',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'maxlength': '6'
                                      })

    )

    unit_size = forms.ChoiceField(
        choices=[('m', 'm'), ('in', 'in') , ('cm', 'cm')],
        widget=forms.Select(attrs={'class': 'form-control btn btn-light-info text-info font-weight-medium dropdown-toggle'})
    )

    height = forms.CharField(
        label='height',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'maxlength': '4'
                                      })

    )

    pickup_city = forms.CharField(
        label='Pickup City',
        widget=forms.TextInput(attrs={'class': 'form-control',

                                      })

    )

    drop_off_city = forms.CharField(
        label='Drop Off City',
        widget=forms.TextInput(attrs={'class': 'form-control',

                                      })

    )

    unit_weight = forms.ChoiceField(
        choices=[('kg', 'kg'), ('lbs', 'lbs')],
        widget=forms.Select(attrs={
            'class': 'form-control btn btn-light-info text-info font-weight-medium dropdown-toggle'})
    )

    quantity = forms.CharField(
        label='quantity',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'maxlength': '3'
                                      })

    )

    pickup_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date',
                                                         'class' : 'form-control'},))



    class Meta:
        model = Shipment
        fields = ['length', 'height', 'width', 'weight', 'quantity', 'pickup_location', 'drop_off_location', 'pickup_date', 'status', 'estimated_quotation', 'pickup_address', 'drop_off_address'
                  ,'pickup_city', 'drop_off_city', 'shipper_user']

        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # del self.fields['username']
        for name in self.fields.keys():
            field = self.fields[name]
            self.fields[name].widget.attrs.update({
                'placeholder': self.fields[name].label,
                #'class': 'form-control',
            })

            field.label = ''
            field.widget.attrs.update({'aria-label': field.label})


class PaymentDetailsForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = ['request_id', 'amount', 'first_name', 'last_name', 'card_number', 'expiration_date', 'cvv']