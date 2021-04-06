from django.urls import path
from .views import *

app_name = 'contract'
urlpatterns = [
    path('trader-sales/', TraderSalesContractView.as_view(), name='trader-sales'),
    path('trader-sales/invoice/', TraderSalesInvoiceView.as_view(), name='trader-sales-invoice'),
    path('trader-purchases/', TraderPurchasesContractView.as_view(), name='trader-purchases'),
    path('trader-purchases/invoice/', TraderPurchasesInvoiceView.as_view(), name='trader-purchases-invoice'),
    path('hall-sales/', HallSalesContractView.as_view(), name='hall-sales'),
    path('hall-sales/invoice/', HallSalesInvoiceView.as_view(), name='hall-sales-invoice'),
    path('hall-purchases/', HallPurchasesContractView.as_view(), name='hall-purchases'),
    path('hall-purchases/invoice/', HallPurchasesInvoiceView.as_view(), name='hall-purchases-invoice'),

    path('validate/trader-sales/', TraderSalesValidateAjaxView.as_view(), name='trader-sales-validate'),
    path('validate/trader-purchases/', TraderPurchasesValidateAjaxView.as_view(), name='trader-purchases-validate'),
    path('validate/hall-sales/', HallSalesValidateAjaxView.as_view(), name='hall-sales-validate'),
    path('validate/hall-purchases/', HallPurchasesValidateAjaxView.as_view(), name='hall-purchases-validate'),

    path('shipping-label/', ContractShippingLabelAjaxView.as_view(), name='shipping-label'),
    path('manager/', ContractManagerAjaxView.as_view(), name='manager'),
]
