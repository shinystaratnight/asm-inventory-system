from django.urls import path
from masterdata.views import CustomerView, HallView, ShippingAddressView, ProductView, OtherProductView

app_name = 'master'
urlpatterns = [
    path('customer/', CustomerView.as_view(), name='customer'),
    path('hall/', HallView.as_view(), name='hall'),
    path('shipping-address/', ShippingAddressView.as_view(), name='shipping-address'),
    path('product/', ProductView.as_view(), name='product'),
    path('other/', OtherProductView.as_view(), name='other'),
]