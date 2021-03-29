from django import forms
from django.forms import formset_factory, BaseFormSet
from django.core.exceptions import ValidationError
from masterdata.models import Product
from .models import *

# Common Forms like Product, Document and Insurance Fee
class ProductForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}))
    type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices = PRODUCT_TYPE_CHOICES)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        contract = TraderSalesContract.objects.get(id=self.contract_id)
        product = Product.objects.get(id=self.cleaned_data.get('id'))
        data = {
            'type': self.cleaned_data.get('type'),
            'quantity': self.cleaned_data.get('quantity'),
            'price': self.cleaned_data.get('price'),
            'product': product,
            'content_object': contract,
        }
        TraderSalesProduct.objects.create(**data)


class DocumentForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}))
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)


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
    
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        contract_id = kwargs.get('contract_id', None)
        if contract_id:
            return {'contract_id': contract_id}
        return {}

ProductFormSet = formset_factory(ProductForm, formset=ItemValidationFormSet, extra=0)
DocumentFormSet = formset_factory(DocumentForm, formset=ItemValidationFormSet, extra=0)
# End of Common Forms

#===================================#
# Trader Sales Forms
class TraderSalesContractForm(forms.Form):
    contract_id = forms.CharField()
    customer_id = forms.IntegerField()
    manager = forms.CharField(required=False)
    person_in_charge = forms.CharField()
    remarks = forms.CharField(required=False)
    shipping_method = forms.CharField()
    shipping_date = forms.DateField()
    payment_method = forms.CharField()
    payment_due_date = forms.DateField()
    insurance_fee = forms.IntegerField()
    created_at = forms.DateField()
    updated_at = forms.DateField()
    # insurance_included = forms.BooleanField()

    def save(self):
        contract_data = self.cleaned_data
        return TraderSalesContract.objects.create(**contract_data)


class SenderForm(forms.Form):
    id = forms.IntegerField()
    expected_arrival_date = forms.DateField()
# End of Trader Sales Forms
