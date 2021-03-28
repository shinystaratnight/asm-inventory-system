from django.urls import path
from .views import *

app_name = 'contract'
urlpatterns = [
    path('trader-sales/', TraderSalesContractView.as_view(), name='trader-sales'),
    path('trader-purchases/', trader_purchases, name='trader-purchases'),
    path('hall-sales/', hall_sales, name='hall-sales'),
    path('hall-purchases/', hall_purchases, name='hall-purchases'),

    path('validate/trader-sales/', TraderSalesValidateView.as_view(), name='trader-sales-validate'),
    path('shipping-label/', ContractShippingLabelAjaxView.as_view(), name='shipping-label'),
    path('manager/', ContractManagerAjaxView.as_view(), name='manager'),
]
