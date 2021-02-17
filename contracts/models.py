from django.db import models

# Create your models here.

class Sale(models.Model):
    SHIPPING_METHOD = (
        ('Shipping', 'Shipping'),
        ('Picking up', 'Picking up'),
        ('ID change', 'ID change'),
        ('* Blank', '* Blank')
    )
    PAYMENT_METHOD = (
        ('Transfer', 'Transfer'),
        ('Check', 'Check'),
        ('Bill', 'Bill'),
        ('Cash', 'Cash')
    )
    transaction_id = models.CharField(max_length=200, null=True)
    contract_date = models.DateTimeField(null=True)
    in_charge = models.CharField(max_length=200, null=True)
    membership_number = models.CharField(max_length=200, null=True)
    shipping_method = models.CharField(max_length=200, null=True, choices=SHIPPING_METHOD)
    shipping_method_date = models.DateTimeField(null=True)
    remarks = models.CharField(max_length=200, null=True)
    payment_method = models.CharField(max_length=200, null=True, choices=PAYMENT_METHOD)
    payment_deadline = models.DateTimeField(null=True)
    subtotal = models.FloatField(null=True, blank=True)
    consumption_tax = models.FloatField(null=True, blank=True)
    insurance_fee = models.FloatField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    product_shipping_address = models.OneToOneField("ProductShippingAddress", on_delete=models.CASCADE)
    # document_shipping_address = models.ForeignKey('DocumentShippingAddress', null=True, on_delete=models.CASCADE)
    update_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.contract_date


class DocumentShippingAddress(models.Model):
    company_name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    tel = models.CharField(max_length=200, null=True)
    fax = models.CharField(max_length=200, null=True)
    expected_arrival_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    desired_arrival_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    shipping_company = models.CharField(max_length=200, null=True, blank=True)
    remark = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.company_name

class ProductShippingAddress(models.Model):
    company_name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    tel = models.CharField(max_length=200, null=True)
    fax = models.CharField(max_length=200, null=True)
    expected_arrival_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    desired_arrival_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    shipping_company = models.CharField(max_length=200, null=True, blank=True)
    remark = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.company_name
