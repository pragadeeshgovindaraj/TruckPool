from django import forms

from .models import CarrierPlan


class CarrierPlanForm(forms.ModelForm):
    space_available = forms.CharField(
        label='Available Space %',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'maxlength': '6'
                                      })

    )

    desired_rate = forms.CharField(
        label='Desired Rate',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'maxlength': '6'
                                      })

    )

    date_of_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date',
                                                                 'class' : 'form-control'}, ))

    start_city = forms.CharField(
        label='From City',
        widget=forms.TextInput(attrs={'class': 'form-control',

                                      })

    )

    end_city = forms.CharField(
        label='To City',
        widget=forms.TextInput(attrs={'class': 'form-control',

                                      })

    )

    class Meta:
        model = CarrierPlan
        fields = ['date_of_plan', 'start_location', 'start_address', 'start_city', 'end_location', 'end_address',
                  'end_city', 'space_available',
                  'desired_rate', 'carrier_user']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CarrierPlanForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['carrier_user'].initial = user.carrier
        # del self.fields['username']
        for name in self.fields.keys():
            field = self.fields[name]
            self.fields[name].widget.attrs.update({
                'placeholder': self.fields[name].label,
                # 'class': 'form-control',
            })

            field.label = ''
            field.widget.attrs.update({'aria-label': field.label})
