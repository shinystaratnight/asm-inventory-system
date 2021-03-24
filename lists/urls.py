from django.urls import path
from .views import *

urlpatterns = [
    path('sales/', sales, name='list-sales'),
    path('purchases/', purchases, name='list-purchases'),
    path('inventories/', inventory, name='list-inventories'),
]
