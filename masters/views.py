from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import CustomerForm
# Create your views here.


@login_required(login_url='login')
def dashboardPage(request):
    context = {}
    return render(request, 'index.html', context)


@login_required(login_url='login')
def customerPage(request):
    customers = Customer.objects.all()

    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer-master')

    context = {'customers': enumerate(customers)}
    return render(request, 'master_data_customer.html', context)
