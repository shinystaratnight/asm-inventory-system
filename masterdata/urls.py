from django.urls import path
from .views import *

app_name = 'masterdata'
urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customer/', CustomerDetailAjaxView.as_view(), name='customer-detail'),
    path('customer-update/', CustomerUpdateView.as_view(), name='customer-update'),
    path('customer-delete/', CustomerDeleteView.as_view(), name='customer-delete'),

    path('halls/', HallListView.as_view(), name='hall-list'),
    path('hall/', HallDetailAjaxView.as_view(), name='hall-detail'),
    path('hall-update/', HallUpdateView.as_view(), name='hall-update'),
    path('hall-delete/', HallDeleteView.as_view(), name='hall-delete'),

    path('senders/', SenderListView.as_view(), name='sender-list'),
    path('sender/', SenderDetailAjaxView.as_view(), name='sender-detail'),
    path('sender-update/', SenderUpdateView.as_view(), name='sender-update'),
    path('sender-delete/', SenderDeleteView.as_view(), name='sender-delete'),

    path('products/', ProductListView.as_view(), name='product-list'),
    path('product/', ProductDetailAjaxView.as_view(), name='product-detail'),
    path('product-update/', ProductUpdateView.as_view(), name='product-update'),
    path('product-delete/', ProductDeleteView.as_view(), name='product-delete'),

    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('document/', DocumentDetailAjaxView.as_view(), name='document-detail'),
    path('document-update/', DocumentUpdateView.as_view(), name='document-update'),
    path('document-delete/', DocumentDeleteView.as_view(), name='document-delete'),

    path('search-customer/', CustomerSearchAjaxView.as_view(), name='customer-search'),
    path('search-hall/', HallSearchAjaxView.as_view(), name='hall-search'),
    path('search-product/', ProductSearchAjaxView.as_view(), name='product-search'),
]