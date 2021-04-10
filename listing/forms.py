from django.forms import ModelForm
from django import forms
from masterdata.models import InventoryProduct, INPUT_FORMATS


class ProductForm(ModelForm):
    purchase_date = forms.DateField(input_formats=INPUT_FORMATS)
    class Meta:
        model = InventoryProduct
        fields = '__all__'


class ListingSearchForm(forms.Form):
    contract_id = forms.CharField(required=False)
    created_at = forms.DateField(input_formats=INPUT_FORMATS, required=False)
    customer = forms.CharField(required=False)
    name = forms.CharField(required=False)
    inventory_status = forms.CharField(required=False)
