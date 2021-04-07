from django.urls import path
from .views import *

app_name = 'contract'
urlpatterns = [
    path('trader-sales/', TraderSalesContractView.as_view(), name='trader-sales'),
    path('trader-purchases/', TraderPurchasesContractView.as_view(), name='trader-purchases'),
    path('hall-sales/', HallSalesContractView.as_view(), name='hall-sales'),
    path('hall-purchases/', HallPurchasesContractView.as_view(), name='hall-purchases'),
    
    path('invoice/trader-sales/', TraderSalesInvoiceView.as_view(), name='trader-sales-invoice'),
    path('invoice/trader-purchases/', TraderPurchasesInvoiceView.as_view(), name='trader-purchases-invoice'),
    path('invoice/hall-sales/', HallSalesInvoiceView.as_view(), name='hall-sales-invoice'),
    path('invoice/hall-purchases/', HallPurchasesInvoiceView.as_view(), name='hall-purchases-invoice'),

    path('trader-sales/<int:pk>/update/', TraderSalesUpdateView.as_view(), name='trader-sales-update'),
    # path('trader-purchases/update', TraderPurchasesUpdateView.as_view(), name='trader-purchases-update'),
    # path('hall-sales/update/', HallSalesUpdateView.as_view(), name='hall-sales-update'),
    # path('hall-purchases/update/', HallPurchasesUpdateView.as_view(), name='hall-purchases-update'),

    path('validate/trader-sales/', TraderSalesValidateAjaxView.as_view(), name='trader-sales-validate'),
    path('validate/trader-purchases/', TraderPurchasesValidateAjaxView.as_view(), name='trader-purchases-validate'),
    path('validate/hall-sales/', HallSalesValidateAjaxView.as_view(), name='hall-sales-validate'),
    path('validate/hall-purchases/', HallPurchasesValidateAjaxView.as_view(), name='hall-purchases-validate'),

    path('shipping-label/', ContractShippingLabelAjaxView.as_view(), name='shipping-label'),
    path('manager/', ContractManagerAjaxView.as_view(), name='manager-list'),

]
