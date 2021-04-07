from django.urls import path
from .views import *

app_name = 'list'
urlpatterns = [
    path('sales/', SalesListView.as_view(), name='sales'),
    path('purchases/', PurchasesListView.as_view(), name='purchases'),
    path('inventory/', InventoryListView.as_view(), name='inventory'),

    path('listing-sales-product/update/', ListingSalesProductUpdateView.as_view(), name='listing-sales-product-update'),
    path('listing-purchases-product/update/', ListingPurchasesProductUpdateView.as_view(), name='listing-purchases-product-update'),

    path('listing-sales-product/detail/', ListingSalesProductDetailAjaxView.as_view(), name='listing-sales-product-detail'),
    path('listing-purchases-product/detail/', ListingPurchasesProductDetailAjaxView.as_view(), name='listing-purchases-product-detail'),
]
