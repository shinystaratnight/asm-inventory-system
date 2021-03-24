from django.urls import path
from .views import *

urlpatterns = [
    path('sales/', sales, name='csv-sales'),
    path('purchases/', purchases, name='csv-purchases'),
]