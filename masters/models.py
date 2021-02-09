from django.db import models

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=200, null=True)
    frigana = models.CharField(max_length=200, null=True)
    postal_code = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    tel = models.CharField(max_length=200, null=True)
    fax = models.CharField(max_length=200, null=True)
    for_csv = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name
        