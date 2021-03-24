from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def sales(request):
    context = {}
    return render(request, 'csvs/sales.html', context)

@login_required(login_url='login')
def purchases(request):
    context = {}
    return render(request, 'csvs/purchases.html', context)