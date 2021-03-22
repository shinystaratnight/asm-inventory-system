from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='login')
def sales_history(request):
    context = {}
    return render(request, 'history/list_sales_history.html', context)

@login_required(login_url='login')
def purchases_history(request):
    context = {}
    return render(request, 'history/list_purchases_history.html', context)

@login_required(login_url='login')
def inventory(request):
    context = {}
    return render(request, 'history/list_inventory.html', context)