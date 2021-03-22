from django.urls import path
from .views import *

app_name = 'contract'
urlpatterns = [
    path('trader-sales/', trader_sales, name='trader-sales'),
    path('trader-purchases/', trader_purchases, name='trader-purchases'),
    path('hall-sales/', hall_sales, name='hall-sales'),
    path('hall-purchases/', hall_purchases, name='hall-purchases'),
]
