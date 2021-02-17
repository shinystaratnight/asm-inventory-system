from django.db import models

# Create your models here.
class Transaction(models.Model):
    contract_date = models.DateTimeField(null=True)
    supplier = models.CharField(max_length=200, null=True)
    delivery_destination = models.CharField(max_length=200, null=True)
    payment_deadline = models.DateTimeField(null=True)
    inventory_clearing = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.contract_date