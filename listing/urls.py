from django.urls import path
from .views import *

app_name = 'listing'
urlpatterns = [
    path('sales/', SalesListView.as_view(), name='sales-list'),
    path('purchases/', PurchasesListView.as_view(), name='purchases-list'),
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),

    path('contract-product/update/', ContractProductUpdateView.as_view(), name='contract-product-update'),

    path('sales-product/detail/', SalesProductDetailAjaxView.as_view(), name='sales-product-detail'),
    path('purchases-product/detail/', PurchasesProductDetailAjaxView.as_view(), name='purchases-product-detail'),
]
