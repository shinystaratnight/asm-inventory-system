from django.forms import ModelForm
from django import forms

from .models import Sale, DocumentShippingAddress, ProductShippingAddress

class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'

class ProductShippingAddressFrom(ModelForm):
    class Meta:
        model = ProductShippingAddress
        fields = '__all__'

class DocumentShippingAddressFrom(ModelForm):
    class Meta:
        model = DocumentShippingAddress
        fields = '__all__'
