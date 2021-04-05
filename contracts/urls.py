from django.urls import path
from .views import *

app_name = 'contract'
urlpatterns = [
    path('trader-sales/', TraderSalesContractView.as_view(), name='trader-sales'),
    path('trader-sales/invoice/', TraderSalesInvoiceView.as_view(), name='trader-sales-invoice'),
    path('trader-purchases/', TraderPurchasesContractView.as_view(), name='trader-purchases'),
    path('trader-purchases/invoice/', TraderPurchasesInvoiceView.as_view(), name='trader-purchases-invoice'),
    path('hall-sales/', HallSalesContractView.as_view(), name='hall-sales'),
    path('hall-purchases/', HallPurchasesContractView.as_view(), name='hall-purchases'),

    path('validate/trader-sales/', TraderSalesValidateAjaxView.as_view(), name='trader-sales-validate'),
    path('shipping-label/', ContractShippingLabelAjaxView.as_view(), name='shipping-label'),
    path('manager/', ContractManagerAjaxView.as_view(), name='manager'),
]
