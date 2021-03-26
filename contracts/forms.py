from django import forms
from django.forms import formset_factory

from .models import *


class ProductForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices = PRODUCT_TYPE_CHOICES)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    amount = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))

ProductFormSet = formset_factory(ProductForm, extra=0)