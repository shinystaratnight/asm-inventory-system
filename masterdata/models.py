from django.db import models
from django.utils.translation import gettext_lazy as _


class MasterData(models.Model):
    name = models.CharField(max_length=200)
    frigana = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200)
    tel = models.CharField(max_length=100, null=True, blank=True)
    fax = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name


class Customer(MasterData):
    csv = models.CharField(max_length=200)


class Hall(MasterData):
    payee = models.CharField(max_length=200)


class Receiver(MasterData):
    pass


TYPE_CHOICES = (
    ('P', _('Pachinko')),
    ('S', _('Slot'))
)

class Product(models.Model):
    name = models.CharField(max_length=200)
    maker = models.CharField(max_length=200)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Other(models.Model):
    name = models.CharField(max_length=200)
    term = models.CharField(max_length=200)
    taxation = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
