from django import forms
from django.forms import formset_factory, BaseFormSet

from .models import *


class ProductForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices = PRODUCT_TYPE_CHOICES)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))


class DocumentForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))


class ItemValidationFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        
        for form in self.forms:
            quantity = form.cleaned_data.get('quantity')
            if quantity < 1:
                form.add_error('quantity', 'Quantity should be larger than 1.')
                return
            
            price = form.cleaned_data.get('price')
            if price < 1:
                form.add_error('price', 'Price should be postive integer value.')
                return

ProductFormSet = formset_factory(ProductForm, formset=ItemValidationFormSet, extra=0)
DocumentFormSet = formset_factory(DocumentForm, formset=ItemValidationFormSet, extra=0)