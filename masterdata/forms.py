from django.forms import ModelForm
from django import forms
from .models import Customer, Hall, ShippingAddress, Product, OtherProduct


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class HallForm(ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'


class ShippingAddressForm(ModelForm):
    class Meta:
        model = ShippingAddress
        fields = '__all__'


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class OtherProductForm(ModelForm):
    class Meta:
        model = OtherProduct
        fields = '__all__'