import time
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView, View
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from users.views import AdminLoginRequiredMixin
from masterdata.models import Document
from .models import *
from .forms import *


def generate_contract_id():
    return int(time.time())


class TraderSalesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/trader_sales.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        product_formset = ProductFormSet(self.request.POST)
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_id'] = generate_contract_id()
        context['documents'] = Document.objects.all().values('name')
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        return context


class TraderSalesValidateView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            # Check if contract form is valid
            contract_form = TraderSalesContractForm(data)
            if not contract_form.is_valid():
                print(contract_form.errors)
                return JsonResponse({'success': False}, status=200)
            # Check the validity of product formset
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                print(product_formset.errors)
                print(product_formset.non_form_errors())
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                print(document_formset.errors)
                print(document_formset.non_form_errors())
                return JsonResponse({'success': False}, status=200)
            # If shipping method is receipt, senderform validation should be checked
            if contract_form.cleaned_data.get('shipping_method') == 'R':
                product_sender = {
                    'id': data.get('product_sender_id'),
                    'expected_arrival_date': data.get('produt_sender_expected_arrival_date')
                }
                document_sender = {
                    'id': data.get('document_sender_id'),
                    'expected_arrival_date': data.get('document_sender_expected_arrival_date')
                }
                product_sender_form = SenderForm(product_sender)
                document_sender_form = SenderForm(document_sender)
                if product_sender_form.is_valid() and document_sender_form.is_valid():
                    pass
                else:
                    return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)

class ContractShippingLabelAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST.get('data')
            if data == 'R':
                return JsonResponse({'data': _('Receipt date')}, status=200)
            elif data == 'C':
                return JsonResponse({'data': _('ID Change date')}, status=200)
            else:
                return JsonResponse({'data': _('Delivery date')}, status=200)
        return JsonResponse({'success': False}, status=200)


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

