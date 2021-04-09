from django.db import models
from django.utils.translation import gettext_lazy as _

TYPE_CHOICES = (
    ('P', _('Pachinko')),
    ('S', _('Slot'))
)

POSTAL_CODE = '537―0021'
ADDRESS = '大阪府大阪市東成区東中本2丁目4―15'
COMPANY_NAME = 'バッジオ株式会社'
CEO = '金 昇志'
TEL = '06-6753-8078'
FAX = '06-6753-8078'
TRANSFER_ACCOUNT = 'りそな銀行　船場支店（101）　普通　0530713　バッジオカブシキガイシャ'
REFAX = '06-6753-8079'
P_SENSOR_NUMBER = '8240-2413-3628'
INPUT_FORMATS = ['%Y/%m/%d', '%m/%d/%Y']

class MasterData(models.Model):
    name = models.CharField(max_length=200)
    frigana = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200)
    tel = models.CharField(max_length=100, null=True, blank=True)
    fax = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name


class Customer(MasterData):
    csv = models.CharField(max_length=200)


class Hall(MasterData):
    payee = models.CharField(max_length=200)


class Sender(MasterData):
    pass


class Product(models.Model):
    name = models.CharField(max_length=200)
    maker = models.CharField(max_length=200)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class Document(models.Model):
    name = models.CharField(max_length=200)
    term = models.CharField(max_length=200)
    taxation = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DocumentFee(models.Model):
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    model_price = models.IntegerField()
    unit_price = models.IntegerField()
    application_fee = models.IntegerField(default=30000)


class InventoryProduct(models.Model):
    name = models.CharField(max_length=200)
    identifier = models.CharField(max_length=20)
    purchase_date = models.DateField()
    supplier = models.CharField(max_length=200)
    person_in_charge = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.IntegerField()
    stock = models.IntegerField()
    amount = models.IntegerField()

    # @property
    # def amount(self):
    #     return self.quantity * self.price
