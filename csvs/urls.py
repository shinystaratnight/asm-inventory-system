from django.urls import path
from .views import *

app_name = 'csv'
urlpatterns = [
    path('sales/', SalesListView.as_view(), name='sales'),
    path('purchases/', PurchasesListView.as_view(), name='purchases'),
]