from django.forms import ModelForm
from django import forms
from masterdata.models import InventoryProduct, INPUT_FORMATS


class ProductForm(ModelForm):
    # purchase_date = forms.DateField(input_formats=INPUT_FORMATS)
    class Meta:
        model = InventoryProduct
        fields = '__all__'