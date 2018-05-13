from django import forms
from .models import Phone, Player
from django.forms import inlineformset_factory

phone_details = ['number', 'name', 'residence']

class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = phone_details


PhoneFormset = inlineformset_factory(Player, Phone,
                                     fields=phone_details,
                                     can_delete=True,
                                     extra=1,
                                     form=PhoneForm,
                                     )
