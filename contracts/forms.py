from django import forms
from django.forms import formset_factory, BaseFormSet
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from masterdata.models import Product, TYPE_CHOICES
from .models import *

INPUT_FORMATS = ['%Y/%m/%d', '%m/%d/%Y']

# Common Forms like Product, Document and Insurance Fee
class ProductForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}))
    type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PRODUCT_TYPE_CHOICES)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class', None):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        contract_class_name = ContentType.objects.get(model=self.contract_class)
        contract_class = contract_class_name.model_class()
        contract = contract_class.objects.get(id=self.contract_id)
        product = Product.objects.get(id=self.cleaned_data.get('id'))
        data = {
            'type': self.cleaned_data.get('type'),
            'quantity': self.cleaned_data.get('quantity'),
            'price': self.cleaned_data.get('price'),
            'product': product,
            'content_object': contract,
        }
        ContractProduct.objects.create(**data)


class DocumentForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}))
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class', None):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        contract_class_name = ContentType.objects.get(model=self.contract_class)
        contract_class = contract_class_name.model_class()
        contract = contract_class.objects.get(id=self.contract_id)
        document = Document.objects.get(id=self.cleaned_data.get('id'))
        data = {
            'quantity': self.cleaned_data.get('quantity'),
            'price': self.cleaned_data.get('price'),
            'document': document,
            'content_object': contract,
        }
        ContractDocument.objects.create(**data)


class DocumentFeeForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}))
    number_of_models = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    number_of_units = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class', None):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        contract_class_name = ContentType.objects.get(model=self.contract_class)
        contract_class = contract_class_name.model_class()
        contract = contract_class.objects.get(id=self.contract_id)
        data = {
            'number_of_models': self.cleaned_data.get('number_of_models'),
            'number_of_units': self.cleaned_data.get('number_of_units'),
            'content_object': contract,
        }
        ContractDocumentFee.objects.create(**data)


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
        contract_class = kwargs.get('contract_class', None)
        
        data = {}
        if contract_id:
            data['contract_id'] = contract_id
        if contract_class:
            data['contract_class'] = contract_class
        return data


class DocumentFeeValidationFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        if self.total_form_count() == 0:
            raise ValidationError("At least one document fee must be added.")
        for form in self.forms:
            number_of_models = form.cleaned_data.get('number_of_models')
            if number_of_models < 1:
                form.add_error('number_of_models', 'Number of models should be positive integer value.')
                return
            number_of_units = form.cleaned_data.get('number_of_units')
            if number_of_units < 1:
                form.add_error('number_of_units', 'Number of units should be postive integer value.')
                return
    
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        contract_id = kwargs.get('contract_id', None)
        contract_class = kwargs.get('contract_class', None)
        
        data = {}
        if contract_id:
            data['contract_id'] = contract_id
        if contract_class:
            data['contract_class'] = contract_class
        return data


ProductFormSet = formset_factory(ProductForm, formset=ItemValidationFormSet, extra=0)
DocumentFormSet = formset_factory(DocumentForm, formset=ItemValidationFormSet, extra=0)
DocumentFeeFormSet = formset_factory(DocumentFeeForm, formset=DocumentFeeValidationFormSet, extra=0)
# End of Common Forms

class MilestoneForm(forms.Form):
    date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control datepicker-milestone'}))
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class', None):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        contract_class_name = ContentType.objects.get(model=self.contract_class)
        contract_class = contract_class_name.model_class()
        contract = contract_class.objects.get(id=self.contract_id)
        data = {
            'date': self.cleaned_data.get('date'),
            'amount': self.cleaned_data.get('amount'),
            'content_object': contract,
        }
        Milestone.objects.create(**data)

class MilestoneValidationFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        # Add Here
    
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        contract_id = kwargs.get('contract_id', None)
        contract_class = kwargs.get('contract_class', None)
        
        data = {}
        if contract_id:
            data['contract_id'] = contract_id
        if contract_class:
            data['contract_class'] = contract_class
        return data

#===================================#
# Trader Sales Forms
class TraderSalesContractForm(forms.Form):
    contract_id = forms.CharField()
    customer_id = forms.IntegerField()
    manager = forms.CharField(required=False)
    person_in_charge = forms.CharField()
    remarks = forms.CharField(required=False)
    shipping_method = forms.CharField()
    shipping_date = forms.DateField(input_formats=INPUT_FORMATS)
    payment_method = forms.CharField()
    payment_due_date = forms.DateField(input_formats=INPUT_FORMATS)
    insurance_fee = forms.IntegerField()
    created_at = forms.DateField(input_formats=INPUT_FORMATS)
    updated_at = forms.DateField(input_formats=INPUT_FORMATS)
    # insurance_included = forms.BooleanField()

    def save(self):
        contract_data = self.cleaned_data
        return TraderSalesContract.objects.create(**contract_data)


class SalesSenderForm(forms.Form):
    sender_id = forms.IntegerField()
    expected_arrival_date = forms.DateField(input_formats=INPUT_FORMATS)

    def __init__(self, *args, **kwargs):
        if kwargs.get('type', None):
            self.type = kwargs.pop('type')
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        data = {
            'contract': TraderSalesContract.objects.get(id=self.contract_id),
            'type': self.type,
            'sender': Receiver.objects.get(id=self.cleaned_data.get('sender_id')),
            'expected_arrival_date': self.cleaned_data.get('expected_arrival_date'),
        }
        SaleSender.objects.create(**data)


class PurchasesSenderForm(forms.Form):
    sender_id = forms.IntegerField()
    desired_arrival_date = forms.DateField(input_formats=INPUT_FORMATS)
    shipping_company = forms.CharField()
    remarks = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('type', None):
            self.type = kwargs.pop('type')
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        data = {
            'contract': TraderPurchasesContract.objects.get(id=self.contract_id),
            'type': self.type,
            'sender': Receiver.objects.get(id=self.cleaned_data.get('sender_id')),
            'desired_arrival_date': self.cleaned_data.get('desired_arrival_date'),
            'shipping_company': self.cleaned_data.get('shipping_company'),
            'remarks': self.cleaned_data.get('remarks'),
        }
        PurchaseSender.objects.create(**data)

# End of Trader Sales Forms
