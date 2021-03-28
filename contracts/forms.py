from django import forms
from django.forms import formset_factory, BaseFormSet
from django.core.exceptions import ValidationError
from .models import *

# Common Forms like Product, Document and Insurance Fee
class ProductForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}))
    type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices = PRODUCT_TYPE_CHOICES)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))


class DocumentForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}))
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))


class DocumentFeeForm(forms.Form):
    pass


class ItemValidationFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        if self.total_form_count() == 0:
            raise ValidationError("At least one product or document must be added.")
        for form in self.forms:
            quantity = form.cleaned_data.get('quantity')
            if quantity < 1:
                form.add_error('quantity', 'Quantity should be positive integer value.')
                return
            price = form.cleaned_data.get('price')
            if price < 1:
                form.add_error('price', 'Price should be postive integer value.')
                return

ProductFormSet = formset_factory(ProductForm, formset=ItemValidationFormSet, extra=0)
DocumentFormSet = formset_factory(DocumentForm, formset=ItemValidationFormSet, extra=0)
# End of Common Forms

#===================================#
# Trader Sales Forms
class TraderSalesContractForm(forms.Form):
    id = forms.IntegerField()
    manager = forms.CharField(required=False)
    person_in_charge = forms.CharField()
    created_at = forms.DateField()
    updated_at = forms.DateField()
    shipping_method = forms.CharField()
    shipping_date = forms.DateField()
    remarks = forms.CharField(required=False)
    payment_method = forms.CharField()


class SenderForm(forms.Form):
    id = forms.IntegerField()
    expected_arrival_date = forms.DateField()
# End of Trader Sales Forms
