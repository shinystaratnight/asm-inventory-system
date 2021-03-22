from django.forms import ModelForm
from django import forms
from .models import *


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class HallForm(ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'


class ReceiverForm(ModelForm):
    class Meta:
        model = Receiver
        fields = '__all__'


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class OtherForm(ModelForm):
    class Meta:
        model = Other
        fields = '__all__'