from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import CustomerForm, HallForm, ShippingAddressForm, ProductForm, ProductOtherForm
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


@login_required(login_url='login')
def hallPage(request):
    halls = Hall.objects.all()

    form = HallForm()
    if request.method == 'POST':
        form = HallForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hall-details')

    context = { 'halls': enumerate(halls) }
    return render(request, 'master_data_hall_details.html', context)


@login_required(login_url='login')
def shippingAddressPage(request):
    shipping_addresses = ShippingAddress.objects.all()

    form = ShippingAddressForm()
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shipping-addresses')

    context = { 'shipping_addresses': enumerate(shipping_addresses) }
    return render(request, 'master_data_shipping_addresses.html', context)


@login_required(login_url='login')
def productPage(request):

    products = Product.objects.all()

    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products')

    context = { 'products': enumerate(products) }
    return render(request, 'master_data_product_name.html', context)


@login_required(login_url='login')
def OtherPage(request):

    product_others = ProductOrder.objects.all()

    form = ProductOtherForm()
    if request.method == 'POST':
        form = ProductOtherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product-others')

    context = { 'product_others': enumerate(product_others) }
    return render(request, 'master_data_others.html', context)