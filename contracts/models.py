from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.utils.translation import gettext_lazy as _
from masterdata.models import Customer

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

class TraderSalesContract(models.Model):
    contract_id = models.CharField(max_length=200)
    person_in_charge = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, related_name='trader_sales_contracts', on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(null=True, blank=True)
    shipping_method = models.CharField(max_length=1, choices=SHIPPING_METHOD_CHOICES)
    shipping_date = models.DateField()
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES)
    payment_due_date = models.DateField()
    insurance_fee = models.PositiveIntegerField(null=True, blank=True)
    # total = models.PositiveIntegerField()
    update_at = models.DateField()
    created_at = models.DateField()

    def __str__(self):
        return self.contract_date
    
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


class TraderSalesProduct(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=1, choices=PRODUCT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    contract = models.ForeignKey(TraderSalesContract, related_name='products', on_delete=models.CASCADE)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def total_amount(self):
        return self.quantity * self.price


class Sender(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    tel = models.CharField(max_length=30, null=True, blank=True)
    fax = models.CharField(max_length=30, null=True, blank=True)


class ProductSender(Sender):
    contract = models.OneToOneField(TraderSalesContract, on_delete=models.CASCADE)
    expected_arrival_date = models.DateField()


class DocumentSender(Sender):
    contract = models.OneToOneField(TraderSalesContract, on_delete=models.CASCADE)
    expected_arrival_date = models.DateField()
