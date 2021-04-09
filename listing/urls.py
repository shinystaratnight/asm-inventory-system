from django.urls import path
from .views import *

app_name = 'listing'
urlpatterns = [
    path('sales/', SalesListView.as_view(), name='sales-list'),
    path('purchases/', PurchasesListView.as_view(), name='purchases-list'),
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),

    path('sales-product/update/', SalesProductUpdateView.as_view(), name='sales-product-update'),
    path('purchases-product/update/', PurchasesProductUpdateView.as_view(), name='purchases-product-update'),

    path('sales-product/detail/', SalesProductDetailAjaxView.as_view(), name='sales-product-detail'),
    path('purchases-product/detail/', PurchasesProductDetailAjaxView.as_view(), name='purchases-product-detail'),

    path('inventory-product/detail/', InventoryProductDetailAjaxView.as_view(), name='inventory-product-detail'),
    path('inventory-product/create/', InventoryProductCreateView.as_view(), name='inventory-product-create'),
    path('inventory-product/update/', InventoryProductUpdateView.as_view(), name='inventory-product-update'),
    path('inventory-product/delete/', InventoryProductDeleteView.as_view(), name='inventory-product-delete'),
]
