from django import forms
from .models import *



class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ["name", "email", "phone", "address"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            }
        



class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["brand", "model", "year", "color", "license_plate", "last_service_date", "client", "kms"]
        widgets = {
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "year": forms.NumberInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "license_plate": forms.TextInput(attrs={"class": "form-control"}),
            "last_service_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "client": forms.Select(attrs={"class": "form-control"}),
            "kms": forms.NumberInput(attrs={"class": "form-control"}),
            }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['client'].widget.attrs['disabled'] = True


# class ClientDataForm(forms.ModelForm):
#     class Meta:
#         model = ClientData
#         fields = '__all__'
#         widgets = {
#             'client_data': forms.Select(attrs={'class': 'form-control'}),
#             'car_data': forms.Select(attrs={'class': 'form-control'}),
#         }

    