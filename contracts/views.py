from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='login')
def trader_sales(request):
    context = {}
    return render(request, 'sales_contract_trader_sales.html', context)

@login_required(login_url='login')
def trader_purchases(request):
    context = {}
    return render(request, 'sales_contract_trader_purchases.html', context)

@login_required(login_url='login')
def hall_sales(request):
    context = {}
    return render(request, 'sales_contract_hall_sales.html', context)

@login_required(login_url='login')
def hall_purchases(request):
    context = {}
    return render(request, 'sales_contract_trader_purchases.html', context)