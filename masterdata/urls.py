from django.urls import path
from .views import CustomerView

app_name = 'master'
urlpatterns = [
    path('customer/', CustomerView.as_view(), name='customer'),
    # path('hall/', halls, name='hall'),
    # path('shipping-addresses/', shipping_addresses, name='shipping-address'),
    # path('product/', products, name='product'),
    # path('other/', others, name='other'),
]