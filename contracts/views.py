import time 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
# Create your views here.

@login_required(login_url='login')
def trader_sales(request):
    transaction_id = generate_transaction_id()

    product_shipping_address_form = ProductShippingAddressFrom()
    sale_form = SaleForm()
    # print("****", request.method)
    if request.method == 'POST':
        product_shipping_address_data = {
            'company_name': request.POST.get('product_shipping_company'),
            'address': request.POST.get('product_shipping_address'),
            'tel': request.POST.get('product_shipping_tel'),
            'fax': request.POST.get('product_shipping_fax'),
            'expected_arrival_date': request.POST.get('product_shipping_arrival_date'),
        }
        product_shipping_address_form = ProductShippingAddressFrom(product_shipping_address_data)
        # print('*********', product_shipping_address_form.is_valid())
        # print(product_shipping_address_data)
        if product_shipping_address_form.is_valid():
            # print('if ***', product_shipping_address_form.is_valid())
            product_shipping_address_form.save()
        else:
            return redirect('trader-sales')

        sale_data = {
            'transaction_id': request.POST.get('transaction_id'),
            'contract_date': request.POST.get('contract_date'),
            'in_charge': request.POST.get('in_charge'),
            'membership_number': request.POST.get('membership_number'),
            'shipping_method': request.POST.get('shipping_method'),
            'shipping_method_date': request.POST.get('shipping_method_date'),
            'remarks': request.POST.get('remarks'),
            'payment_method': request.POST.get('payment_method'),
            'payment_deadline': request.POST.get('payment_deadline'),
            'subtotal': request.POST.get('subtotal'),
            'consumption_tax': request.POST.get('consumption_tax'),
            'insurance_fee': request.POST.get('insurance_fee'),
            'total_amount': request.POST.get('total_amount'),
            'product_shipping_address': product_shipping_address_form,
            'update_at': request.POST.get('update_at'),
        }
        sale_form = SaleForm(sale_data)
        print(sale_form.is_valid())
        if sale_form.is_valid():
            sale_form.save()
            return redirect('trader-sales')
    context = {'transaction_id': transaction_id}
    return render(request, 'contracts/trader_sales.html', context)

@login_required(login_url='login')
def trader_purchases(request):
    context = {}
    return render(request, 'contracts/trader_purchases.html', context)

@login_required(login_url='login')
def hall_sales(request):
    context = {}
    return render(request, 'contracts/hall_sales.html', context)

@login_required(login_url='login')
def hall_purchases(request):
    context = {}
    return render(request, 'contracts/hall_purchases.html', context)

def generate_transaction_id():
    ts = time.time()
    return int(ts)
