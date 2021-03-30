from django.urls import path
from .views import *

urlpatterns = [
    path('sales/', SalesListView.as_view(), name='sales-list'),
    path('purchases/', PurchasesListView.as_view(), name='purchases-list'),
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
]
