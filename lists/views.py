from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def sales(request):
    context = {}
    return render(request, 'lists/sales.html', context)

@login_required(login_url='login')
def purchases(request):
    context = {}
    return render(request, 'lists/purchases.html', context)

@login_required(login_url='login')
def inventory(request):
    context = {}
    return render(request, 'lists/inventory.html', context)
