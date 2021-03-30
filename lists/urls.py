from django.urls import path
from .views import *

app_name = 'list'
urlpatterns = [
    path('sales/', SalesListView.as_view(), name='sales'),
    path('purchases/', PurchasesListView.as_view(), name='purchases'),
    path('inventory/', InventoryListView.as_view(), name='inventory'),
]
