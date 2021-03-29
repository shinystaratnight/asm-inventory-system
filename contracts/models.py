from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.utils.translation import gettext_lazy as _
from masterdata.models import Customer, Receiver, Hall, Product, Document

SHIPPING_METHOD_CHOICES = (
    ('D', _('Delivery')),
    ('R', _('Receipt')),
    ('C', _('ID Change')),
    ('B', _('* Blank')),
)

PAYMENT_METHOD_CHOICES = (
    ('TR', _('Transfer')),
    ('CH', _('Check')),
    ('BL', _('Bill')),
    ('CA', _('Cash')),
)

PRODUCT_TYPE_CHOICES = (
    ('M', _('Main body')),
    ('F', _('Frame')),
    ('C', _('Cell')),
    ('N', _('Nail sheet')),
)

class TraderSalesProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=1, choices=PRODUCT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class TraderSalesDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class TraderSalesContract(models.Model):
    contract_id = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, related_name='trader_sales_contracts', on_delete=models.SET_NULL, null=True)
    manager = models.CharField(max_length=200, null=True, blank=True)
    person_in_charge = models.CharField(max_length=200)
    remarks = models.TextField(null=True, blank=True)
    shipping_method = models.CharField(max_length=1, choices=SHIPPING_METHOD_CHOICES)
    shipping_date = models.DateField()
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES)
    payment_due_date = models.DateField()
    insurance_fee = models.IntegerField()
    updated_at = models.DateField()
    created_at = models.DateField()
    products = GenericRelation(TraderSalesProduct, related_query_name='contract')
    documents = GenericRelation(TraderSalesDocument, related_query_name='contract')

    @property
    def sub_total(self):
        return 100
    
    @property
    def consumption_tax(self):
        return 100

    @property
    def total(self):
        return 100
    
    @property
    def billing_amount(self):
        return self.total


ITEM_CHOICES = (
    ('P', _('Product')),
    ('D', _('Document'))
)

class SaleSender(models.Model):
    type = models.CharField(max_length=1, choices=ITEM_CHOICES)
    sender = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    expected_arrival_date = models.DateField()


class PurchaseSender(models.Model):
    type = models.CharField(max_length=1, choices=ITEM_CHOICES)
    sender = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    desired_arrival_date = models.DateField()
    shipping_company = models.CharField(max_length=100)
    remarks = models.TextField(null=True, blank=True)
