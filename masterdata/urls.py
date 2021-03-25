from django.urls import path
from .views import *

app_name = 'masterdata'
urlpatterns = [
    path('customer/', CustomerView.as_view(), name='customer'),
    path('hall/', HallView.as_view(), name='hall'),
    path('receiver/', ReceiverView.as_view(), name='receiver'),
    path('product/', ProductView.as_view(), name='product'),
    path('document/', DocumentView.as_view(), name='document'),
    path('search-customer/', CustomerSearchAjaxView.as_view(), name='customer-search'),
]