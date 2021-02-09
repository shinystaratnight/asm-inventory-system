from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='login')
def accounting_sales(request):
    context = {}
    return render(request, 'accounting_csv_sales.html', context)

@login_required(login_url='login')
def accounting_purchases(request):
    context = {}
    return render(request, 'accounting_csv_purchases.html', context)
