from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Sale)
admin.site.register(DocumentShippingAddress)
admin.site.register(ProductShippingAddress)
