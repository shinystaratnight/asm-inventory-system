from django import forms
from django.forms import formset_factory, BaseFormSet
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from masterdata.models import (
    Product, Document, Sender, DocumentFee,
    TYPE_CHOICES, INPUT_FORMATS, PRODUCT_TYPE_CHOICES, SHIPPING_METHOD_CHOICES, PAYMENT_METHOD_CHOICES,
)
from .models import (
    TraderSalesContract, TraderPurchasesContract, HallSalesContract, HallPurchasesContract,
    TraderSalesSender, TraderPurchasesSender,
    ContractProduct, ContractDocument, ContractDocumentFee, Milestone,
)
from .utilities import generate_contract_id


# Common Forms like Product, Document and Insurance Fee
class ProductForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'product-type-selectbox'}), choices=PRODUCT_TYPE_CHOICES)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    tax = forms.IntegerField(widget=forms.HiddenInput(attrs={'disabled': 'disabled'}), required=False)
    fee = forms.IntegerField(widget=forms.HiddenInput(attrs={'disabled': 'disabled'}), required=False)
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class', None):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        id = self.cleaned_data.get('id', None)
        if id:
            contract_product = ContractProduct.objects.get(id=id)
            contract_product.type = self.cleaned_data.get('type')
            contract_product.quantity = self.cleaned_data.get('quantity')
            contract_product.price = self.cleaned_data.get('price')
            contract_product.save()
        else:
            contract_class_name = ContentType.objects.get(model=self.contract_class)
            contract_class = contract_class_name.model_class()
            contract = contract_class.objects.get(id=self.contract_id)
            product = Product.objects.get(id=self.cleaned_data.get('product_id'))
            data = {
                'type': self.cleaned_data.get('type'),
                'quantity': self.cleaned_data.get('quantity'),
                'price': self.cleaned_data.get('price'),
                'product': product,
                'content_object': contract,
            }
            ContractProduct.objects.create(**data)


class DocumentForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    document_id = forms.IntegerField(widget=forms.HiddenInput())
    taxable = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    tax = forms.IntegerField(widget=forms.HiddenInput(attrs={'disabled': 'disabled'}), required=False)
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class', None):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        id = self.cleaned_data.get('id', None)
        if id:
            contract_document = ContractDocument.objects.get(id=id)
            contract_document.quantity = self.cleaned_data.get('quantity')
            contract_document.price = self.cleaned_data.get('price')
            contract_document.save()
        else:
            contract_class_name = ContentType.objects.get(model=self.contract_class)
            contract_class = contract_class_name.model_class()
            contract = contract_class.objects.get(id=self.contract_id)
            document = Document.objects.get(id=self.cleaned_data.get('document_id'))
            data = {
                'quantity': self.cleaned_data.get('quantity'),
                'price': self.cleaned_data.get('price'),
                'document': document,
                'content_object': contract,
            }
            ContractDocument.objects.create(**data)


class DocumentFeeForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    document_fee_id = forms.IntegerField(widget=forms.HiddenInput())
    model_price = forms.IntegerField(widget=forms.HiddenInput())
    unit_price = forms.IntegerField(widget=forms.HiddenInput())
    application_fee = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    model_count = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    unit_count = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    tax = forms.IntegerField(widget=forms.HiddenInput(attrs={'disabled': 'disabled'}), required=False)
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class', None):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        id = self.cleaned_data.get('id', None)
        if id:
            contract_document_fee = ContractDocumentFee.objects.get(id=id)
            contract_document_fee.model_count = self.cleaned_data.get('model_count')
            contract_document_fee.unit_count = self.cleaned_data.get('unit_count')
            contract_document_fee.save()
        else:
            contract_class_name = ContentType.objects.get(model=self.contract_class)
            contract_class = contract_class_name.model_class()
            contract = contract_class.objects.get(id=self.contract_id)
            document_fee = DocumentFee.objects.get(id=self.cleaned_data.get('document_fee_id'))
            data = {
                'model_count': self.cleaned_data.get('model_count'),
                'unit_count': self.cleaned_data.get('unit_count'),
                'document_fee': document_fee,
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
            model_count = form.cleaned_data.get('model_count')
            if model_count < 1:
                form.add_error('model_count', 'Number of models should be positive integer value.')
                return
            unit_count = form.cleaned_data.get('unit_count')
            if unit_count < 1:
                form.add_error('unit_count', 'Number of units should be postive integer value.')
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


class MilestoneForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker-nullable'}),
        input_formats=INPUT_FORMATS,
        required=False
    )
    amount = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class', None):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def clean_date(self):
        data = self.cleaned_data['date']
        return data
    
    def save(self):
        id = self.cleaned_data.get('id', None)
        if id:
            milestone = Milestone.objects.get(id=id)
            milestone.date = self.cleaned_data.get('date')
            milestone.amount = self.cleaned_data.get('amount')
            milestone.save()
        else:
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
        total_forms = 0
        for form in self.forms:
            if form.is_valid():
                if form.cleaned_data.get('amount') and form.cleaned_data.get('date') == None:
                    form.add_error('date', 'This field is required.')
                    return
                if form.cleaned_data.get('date') and form.cleaned_data.get('amount') == None:
                    form.add_error('amount', 'This field is required.')
                    return
                if form.cleaned_data.get('amount') and form.cleaned_data.get('date'):
                    total_forms += 1
        if total_forms == 0:
            raise ValidationError("At least one milestone should be set.")
         
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
MilestoneFormSet = formset_factory(MilestoneForm, formset=MilestoneValidationFormSet, extra=5)
# End of Common Forms


#===================================#
# Trader Sales Forms
class TraderSalesContractForm(forms.Form):
    contract_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}),
        initial=generate_contract_id())
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    updated_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    customer_id = forms.IntegerField()
    customer_name = forms.CharField(required=False)
    manager = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    frigana = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    fax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}))
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-140-px'}), required=False)
    sub_total = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    tax = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    fee = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), initial=0)
    total = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    billing_amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), initial=0, required=False)
    shipping_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=SHIPPING_METHOD_CHOICES)
    shipping_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    payment_due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    memo = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-112-px'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        super().__init__(*args, **kwargs)

    def save(self):
        if self.id:
            contract = TraderSalesContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.updated_at = cleaned_data.get('updated_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.manager = cleaned_data.get('manager')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.remarks = cleaned_data.get('remarks')
            contract.shipping_date = cleaned_data.get('shipping_date')
            contract.fee = cleaned_data.get('fee')
            contract.shipping_method = cleaned_data.get('shipping_method')
            contract.payment_method = cleaned_data.get('payment_method')
            contract.payment_due_date = cleaned_data.get('payment_due_date')
            contract.memo = cleaned_data.get('memo')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'contract_id': cleaned_data.get('contract_id'),
                'created_at': cleaned_data.get('created_at'),
                'updated_at': cleaned_data.get('updated_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'manager': cleaned_data.get('manager'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'remarks': cleaned_data.get('remarks'),
                'shipping_date': cleaned_data.get('shipping_date'),
                'fee': cleaned_data.get('fee'),
                'shipping_method': cleaned_data.get('shipping_method'),
                'payment_method': cleaned_data.get('payment_method'),
                'payment_due_date': cleaned_data.get('payment_due_date'),
                'memo': cleaned_data.get('memo')
            }
            return TraderSalesContract.objects.create(**contract_data)


class TraderSalesProductSenderForm(forms.Form):
    p_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    product_sender_id = forms.IntegerField()
    product_sender_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70', 'readonly': 'readonly'}), required=False)
    product_sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    product_sender_fax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    product_expected_arrival_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        if self.cleaned_data.get('p_id'):
            contract_sender = TraderSalesSender.objects.get(id=self.cleaned_data.get('p_id'))
            contract_sender.sender = Sender.objects.get(id=self.cleaned_data.get('product_sender_id'))
            contract_sender.expected_arrival_date = self.cleaned_data.get('product_expected_arrival_date')
            contract_sender.save()
            return contract_sender
        else:
            data = {
                'contract': TraderSalesContract.objects.get(id=self.contract_id),
                'type': 'P',
                'sender': Sender.objects.get(id=self.cleaned_data.get('product_sender_id')),
                'expected_arrival_date': self.cleaned_data.get('product_expected_arrival_date'),
            }
            return TraderSalesSender.objects.create(**data)


class TraderSalesDocumentSenderForm(forms.Form):
    d_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    document_sender_id = forms.IntegerField()
    document_sender_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70', 'readonly': 'readonly'}), required=False)
    document_sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    document_sender_fax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    document_expected_arrival_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        if self.cleaned_data.get('d_id'):
            contract_sender = TraderSalesSender.objects.get(id=self.cleaned_data.get('d_id'))
            contract_sender.sender = Sender.objects.get(id=self.cleaned_data.get('document_sender_id'))
            contract_sender.expected_arrival_date = self.cleaned_data.get('document_expected_arrival_date')
            contract_sender.save()
            return contract_sender
        else:
            data = {
                'contract': TraderSalesContract.objects.get(id=self.contract_id),
                'type': 'D',
                'sender': Sender.objects.get(id=self.cleaned_data.get('document_sender_id')),
                'expected_arrival_date': self.cleaned_data.get('document_expected_arrival_date'),
            }
            return TraderSalesSender.objects.create(**data)
# End of Trader Sales Forms


# Trader Purchases Forms
class TraderPurchasesContractForm(forms.Form):
    contract_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}),
        initial=generate_contract_id('02'))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    updated_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    customer_id = forms.IntegerField()
    customer_name = forms.CharField(required=False)
    manager = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    frigana = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    fax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}))
    removal_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    shipping_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    frame_color = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    receipt = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70'}), required=False)
    sub_total = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    tax = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    fee = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), initial=0)
    total = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    transfer_deadline = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    bank_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    account_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    branch_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    account_holder = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        super().__init__(*args, **kwargs)
    
    def save(self):
        if self.id:
            contract = TraderPurchasesContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.updated_at = cleaned_data.get('updated_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.manager = cleaned_data.get('manager')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.removal_date = cleaned_data.get('removal_date')
            contract.shipping_date = cleaned_data.get('shipping_date')
            contract.frame_color = cleaned_data.get('frame_color')
            contract.receipt = cleaned_data.get('receipt')
            contract.remarks = cleaned_data.get('remarks')
            contract.fee = cleaned_data.get('fee')
            contract.transfer_deadline = cleaned_data.get('transfer_deadline')
            contract.bank_name = cleaned_data.get('bank_name')
            contract.account_number = cleaned_data.get('account_number')
            contract.branch_name = cleaned_data.get('branch_name')
            contract.account_holder = cleaned_data.get('account_holder')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'contract_id': cleaned_data.get('contract_id'),
                'created_at': cleaned_data.get('created_at'),
                'updated_at': cleaned_data.get('updated_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'manager': cleaned_data.get('manager'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'removal_date': cleaned_data.get('removal_date'),
                'shipping_date': cleaned_data.get('shipping_date'),
                'frame_color': cleaned_data.get('frame_color'),
                'receipt': cleaned_data.get('receipt'),
                'remarks': cleaned_data.get('remarks'),
                'fee': cleaned_data.get('fee'),
                'transfer_deadline': cleaned_data.get('transfer_deadline'),
                'bank_name': cleaned_data.get('bank_name'),
                'account_number': cleaned_data.get('account_number'),
                'branch_name': cleaned_data.get('branch_name'),
                'account_holder': cleaned_data.get('account_holder')
            }
            return TraderPurchasesContract.objects.create(**contract_data)


class TraderPurchasesProductSenderForm(forms.Form):
    p_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    product_sender_id = forms.IntegerField()
    product_sender_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70', 'readonly': 'readonly'}), required=False)
    product_sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    product_desired_arrival_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    product_shipping_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_sender_remarks = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        if self.cleaned_data.get('p_id'):
            contract_sender = TraderPurchasesSender.objects.get(id=self.cleaned_data.get('p_id'))
            contract_sender.sender = Sender.objects.get(id=self.cleaned_data.get('product_sender_id'))
            contract_sender.desired_arrival_date = self.cleaned_data.get('product_desired_arrival_date')
            contract_sender.shipping_company = self.cleaned_data.get('product_shipping_company')
            contract_sender.remarks = self.cleaned_data.get('product_sender_remarks')
            contract_sender.save()
            return contract_sender
        else:
            data = {
                'contract': TraderPurchasesContract.objects.get(id=self.contract_id),
                'type': 'P',
                'sender': Sender.objects.get(id=self.cleaned_data.get('product_sender_id')),
                'desired_arrival_date': self.cleaned_data.get('product_desired_arrival_date'),
                'shipping_company': self.cleaned_data.get('product_shipping_company'),
                'remarks': self.cleaned_data.get('product_sender_remarks'),
            }
            return TraderPurchasesSender.objects.create(**data)


class TraderPurchasesDocumentSenderForm(forms.Form):
    d_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    document_sender_id = forms.IntegerField()
    document_sender_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70', 'readonly': 'readonly'}), required=False)
    document_sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    document_desired_arrival_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    document_shipping_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    document_sender_remarks = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id', None):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        if self.cleaned_data.get('d_id'):
            contract_sender = TraderPurchasesSender.objects.get(id=self.cleaned_data.get('d_id'))
            contract_sender.sender = Sender.objects.get(id=self.cleaned_data.get('document_sender_id'))
            contract_sender.desired_arrival_date = self.cleaned_data.get('document_desired_arrival_date')
            contract_sender.shipping_company = self.cleaned_data.get('document_shipping_company')
            contract_sender.remarks = self.cleaned_data.get('document_sender_remarks')
            contract_sender.save()
            return contract_sender
        else:
            data = {
                'contract': TraderPurchasesContract.objects.get(id=self.contract_id),
                'type': 'D',
                'sender': Sender.objects.get(id=self.cleaned_data.get('document_sender_id')),
                'desired_arrival_date': self.cleaned_data.get('document_desired_arrival_date'),
                'shipping_company': self.cleaned_data.get('document_shipping_company'),
                'remarks': self.cleaned_data.get('document_sender_remarks'),
            }
            return TraderPurchasesSender.objects.create(**data)
# End of trader purchases form


# Hall Sales Forms
class HallSalesContractForm(forms.Form):
    contract_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}),
        initial=generate_contract_id('03'))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    customer_id = forms.IntegerField()
    customer_name = forms.CharField(required=False)
    hall_id = forms.IntegerField()
    hall_name = forms.CharField(required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-197-px'}), required=False)
    sub_total = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    tax = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    fee = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), initial=0)
    total = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    shipping_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    opening_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    transfer_account = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "りそな銀行 船場支店（101）普通 0530713 バッジオカブシキガイシャ"}))
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}))
    confirmor = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        super().__init__(*args, **kwargs)

    def save(self):
        if self.id:
            contract = HallSalesContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.hall_id = cleaned_data.get('hall_id')
            contract.remarks = cleaned_data.get('remarks')
            contract.fee = cleaned_data.get('fee')
            contract.shipping_date = cleaned_data.get('shipping_date')
            contract.opening_date = cleaned_data.get('opening_date')
            contract.payment_method = cleaned_data.get('payment_method')
            contract.transfer_account = cleaned_data.get('transfer_account')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.confirmor = cleaned_data.get('confirmor')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'contract_id': cleaned_data.get('contract_id'),
                'created_at': cleaned_data.get('created_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'hall_id': cleaned_data.get('hall_id'),
                'remarks': cleaned_data.get('remarks'),
                'fee': cleaned_data.get('fee'),
                'shipping_date': cleaned_data.get('shipping_date'),
                'opening_date': cleaned_data.get('opening_date'),
                'payment_method': cleaned_data.get('payment_method'),
                'transfer_account': cleaned_data.get('transfer_account'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'confirmor': cleaned_data.get('confirmor')
            }
            return HallSalesContract.objects.create(**contract_data)
# End of hall sales form


# Hall Purchases Forms
class HallPurchasesContractForm(forms.Form):
    contract_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}),
        initial=generate_contract_id('04'))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    customer_id = forms.IntegerField()
    customer_name = forms.CharField(required=False)
    hall_id = forms.IntegerField()
    hall_name = forms.CharField(required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-197-px'}), required=False)
    sub_total = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    tax = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    fee = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), initial=0)
    total = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    shipping_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    opening_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    transfer_account = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "りそな銀行 船場支店（101）普通 0530713 バッジオカブシキガイシャ"}))
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}))
    confirmor = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    memo = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-92-px'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        super().__init__(*args, **kwargs)

    def save(self):
        if self.id:
            contract = HallPurchasesContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.hall_id = cleaned_data.get('hall_id')
            contract.remarks = cleaned_data.get('remarks')
            contract.fee = cleaned_data.get('fee')
            contract.shipping_date = cleaned_data.get('shipping_date')
            contract.opening_date = cleaned_data.get('opening_date')
            contract.payment_method = cleaned_data.get('payment_method')
            contract.transfer_account = cleaned_data.get('transfer_account')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.confirmor = cleaned_data.get('confirmor')
            contract.memo = cleaned_data.get('memo')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'contract_id': cleaned_data.get('contract_id'),
                'created_at': cleaned_data.get('created_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'hall_id': cleaned_data.get('hall_id'),
                'remarks': cleaned_data.get('remarks'),
                'fee': cleaned_data.get('fee'),
                'shipping_date': cleaned_data.get('shipping_date'),
                'opening_date': cleaned_data.get('opening_date'),
                'payment_method': cleaned_data.get('payment_method'),
                'transfer_account': cleaned_data.get('transfer_account'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'confirmor': cleaned_data.get('confirmor'),
                'memo': cleaned_data.get('memo')
            }
            return HallPurchasesContract.objects.create(**contract_data)
# End of hall purchases form
