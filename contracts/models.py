from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.utils.translation import gettext_lazy as _
from masterdata.models import *


class ContractProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=1, choices=PRODUCT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    status = models.CharField(max_length=1, choices=STOCK_CHOICES, default='P')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def amount(self):
        return self.quantity * self.price
    
    @property
    def tax(self):
        return int(self.amount * 0.1)

    def get_insurance_fee(self):
        price = round(self.price / 1000) * 1000
        if price > THRESHOLD_PRICE:
            return int(200 * self.quantity * (price / THRESHOLD_PRICE))
        else:
            return 100 * self.quantity


class ContractDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def amount(self):
        return self.quantity * self.price
    
    @property
    def is_secure_payment(self):
        return self.document.name == SECURE_PAYMENT
        
    @property
    def tax(self):
        if self.is_secure_payment:
            return 0
        return int(self.amount * 0.1)


class ContractDocumentFee(models.Model):
    document_fee = models.ForeignKey(DocumentFee, on_delete=models.SET_NULL, null=True)
    model_count = models.IntegerField()
    unit_count = models.IntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def amount(self):
        model_price = self.document_fee.model_price
        unit_price = self.document_fee.unit_price
        application_fee = self.document_fee.application_fee
        return self.model_count * model_price + self.unit_count * unit_price + application_fee
    
    @property
    def tax(self):
        return int(self.amount * 0.1)


class Milestone(models.Model):
    date = models.DateField()
    amount = models.IntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class TraderContract(models.Model):
    contract_id = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    manager = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateField()
    updated_at = models.DateField()
    person_in_charge = models.CharField(max_length=200)
    remarks = models.TextField(null=True, blank=True)
    shipping_date = models.DateField()
    insurance_fee = models.IntegerField()

    class Meta:
        abstract = True

    @property
    def amount(self):
        sum = 0
        for product in self.products.all():
            sum += product.amount
        for document in self.documents.all():
            sum += document.amount
        return sum
    
    @property
    def tax(self):
        sum = 0
        for product in self.products.all():
            sum += product.tax
        for document in self.documents.all():
            sum += document.tax
        return sum

    @property
    def total(self):
        return self.amount + self.tax + self.insurance_fee

    @property
    def taxed_total(self):
        return self.total - self.insurance_fee
    
    def get_insurance_fee(self):
        sum = 0
        for product in self.products.all():
            sum += product.get_insurance_fee()
        return sum


class TraderSalesContract(TraderContract):
    shipping_method = models.CharField(max_length=1, choices=SHIPPING_METHOD_CHOICES)
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES)
    payment_due_date = models.DateField()
    memo = models.TextField(null=True, blank=True)
    products = GenericRelation(ContractProduct, related_query_name='trader_sales_contract')
    documents = GenericRelation(ContractDocument, related_query_name='trader_sales_contract')


class TraderPurchasesContract(TraderContract):
    removal_date = models.DateField()
    frame_color = models.CharField(max_length=100)
    receipt = models.CharField(max_length=100)
    transfer_deadline = models.DateField()
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200)
    account_holder = models.CharField(max_length=200)
    products = GenericRelation(ContractProduct, related_query_name='trader_purchases_contract')
    documents = GenericRelation(ContractDocument, related_query_name='trader_purchases_contract')


class TraderSalesSender(models.Model):
    contract = models.ForeignKey(TraderSalesContract, on_delete=models.CASCADE, related_name='senders')
    type = models.CharField(max_length=1, choices=ITEM_CHOICES)
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE)
    expected_arrival_date = models.DateField()

    
class TraderPurchasesSender(models.Model):
    contract = models.ForeignKey(TraderPurchasesContract, on_delete=models.CASCADE, related_name='senders')
    type = models.CharField(max_length=1, choices=ITEM_CHOICES)
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE)
    desired_arrival_date = models.DateField()
    shipping_company = models.CharField(max_length=100)
    remarks = models.TextField(null=True, blank=True)


class HallContract(models.Model):
    contract_id = models.CharField(max_length=200)
    created_at = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    remarks = models.TextField(null=True, blank=True)
    fee_included = models.BooleanField(default=True)
    insurance_fee = models.IntegerField()
    shipping_date = models.DateField()
    opening_date = models.DateField()
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES)
    transfer_account = models.CharField(max_length=255)
    person_in_charge = models.CharField(max_length=200)
    confirmor = models.CharField(max_length=200)

    class Meta:
        abstract = True
    
    @property
    def amount(self):
        sum = 0
        for product in self.products.all():
            sum += product.amount
        for document in self.documents.all():
            sum += document.amount
        return sum
        for document_fee in self.document_fees.all():
            sum += document_fee.amount
    
    @property
    def tax(self):
        sum = 0
        for product in self.products.all():
            sum += product.tax
        for document in self.documents.all():
            sum += document.tax
        for document_fee in self.document_fees.all():
            sum += document_fee.tax
        return sum

    @property
    def total(self):
        return self.amount + self.tax + self.insurance_fee
    
    @property
    def taxed_total(self):
        return self.total - self.insurance_fee

    def get_insurance_fee(self):
        sum = 0
        for product in self.products.all():
            sum += product.get_insurance_fee()
        return sum


class HallSalesContract(HallContract):
    products = GenericRelation(ContractProduct, related_query_name='hall_sales_contract')
    documents = GenericRelation(ContractDocument, related_query_name='hall_sales_contract')
    document_fees = GenericRelation(ContractDocumentFee, related_query_name='hall_sales_contract')
    milestones = GenericRelation(Milestone, related_query_name='hall_sales_contract')


class HallPurchasesContract(HallContract):
    memo = models.TextField(null=True, blank=True)
    products = GenericRelation(ContractProduct, related_query_name='hall_purchases_contract')
    documents = GenericRelation(ContractDocument, related_query_name='hall_purchases_contract')
    document_fees = GenericRelation(ContractDocumentFee, related_query_name='hall_purchases_contract')
    milestones = GenericRelation(Milestone, related_query_name='hall_purchases_contract')
