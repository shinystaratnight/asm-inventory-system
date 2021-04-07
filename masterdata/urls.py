from django.urls import path
from .views import *

app_name = 'masterdata'
urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('halls/', HallListView.as_view(), name='hall-list'),
    path('senders/', SenderListView.as_view(), name='sender-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('documents/', DocumentListView.as_view(), name='document-list'),

    path('customer-update/', CustomerUpdateView.as_view(), name='customer-update'),
    path('customer-delete/', CustomerDeleteView.as_view(), name='customer-delete'),

    path('customer/', CustomerDetailAjaxView.as_view(), name='customer-detail'),

    path('search-customer/', CustomerSearchAjaxView.as_view(), name='customer-search'),
    path('search-hall/', HallSearchAjaxView.as_view(), name='hall-search'),
    path('search-product/', ProductSearchAjaxView.as_view(), name='product-search'),

    path('sender-detail/', SenderDetailAjaxView.as_view(), name='sender-detail')
]