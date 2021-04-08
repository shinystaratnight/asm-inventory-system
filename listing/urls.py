from django.urls import path
from .views import *

app_name = 'listing'
urlpatterns = [
    path('sales/', SalesListView.as_view(), name='sales-list'),
    path('purchases/', PurchasesListView.as_view(), name='purchases-list'),
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),

    path('sales-product/update/', ListingSalesProductUpdateView.as_view(), name='sales-product-update'),
    path('purchases-product/update/', ListingPurchasesProductUpdateView.as_view(), name='purchases-product-update'),

    path('sales-product/detail/', ListingSalesProductDetailAjaxView.as_view(), name='sales-product-detail'),
    path('purchases-product/detail/', ListingPurchasesProductDetailAjaxView.as_view(), name='purchases-product-detail'),
]
