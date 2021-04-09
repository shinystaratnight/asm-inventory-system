import unicodecsv as csv
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from users.views import AdminLoginRequiredMixin
from contracts.models import *
from contracts.utilities import generate_random_number

paginate_by = 3

class SalesListView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'accounting/sales.html'
    
    def get_contract_list(self):
        trader_qs = TraderSalesContract.objects.all()
        hall_qs = HallSalesContract.objects.all()
        params = self.request.GET.copy()
        for k, v in params.items():
            if v:
                if k == "contract_id":
                    trader_qs = trader_qs.filter(contract_id__icontains=v)
                    hall_qs = hall_qs.filter(contract_id__icontains=v)
                elif k == 'created_at':
                    try:
                        v = datetime.datetime.strptime(v, '%Y-%m-%d').date()
                    except ValueError:
                        v = datetime.datetime.strptime(v, '%Y/%m/%d').date()
                    trader_qs = trader_qs.filter(created_at=v)
                    hall_qs = hall_qs.filter(created_at=v)
                elif k == 'customer':
                    trader_qs = trader_qs.filter(customer__name__icontains=v)
                    hall_qs = hall_qs.filter(customer__name__icontains=v)
        contract_list = list(trader_qs) + list(hall_qs)
        return contract_list
    
    def get_paginator(self):
        page = self.request.GET.get('page', 1)
        paginator = Paginator(self.get_contract_list(), paginate_by)
        return paginator.page(page)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = self.get_paginator()
        params = self.request.GET
        for k, v in params.items():
            if v:
                context[k] = v
        return context
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="accounting_sales_{}.csv"'.format(generate_random_number())
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Type'), _('Taxation'), _('Amount'), _('Customer'),
        ])
        contract_list = self.get_contract_list()
        for contract in contract_list:
            writer.writerow([
                contract.contract_id, contract.created_at, _('Income'), '課税売上10%', contract.taxed_total, contract.customer.name
            ])
            writer.writerow([
                contract.contract_id, contract.created_at, _('Income'), '非課売上', contract.insurance_fee, contract.customer.name
            ])
        return response


class PurchasesListView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'accounting/purchases.html'
    
    def get_contract_list(self):
        trader_qs = TraderPurchasesContract.objects.all()
        hall_qs = HallPurchasesContract.objects.all()
        params = self.request.GET.copy()
        for k, v in params.items():
            if v:
                if k == "contract_id":
                    trader_qs = trader_qs.filter(contract_id__icontains=v)
                    hall_qs = hall_qs.filter(contract_id__icontains=v)
                elif k == 'created_at':
                    try:
                        v = datetime.datetime.strptime(v, '%Y-%m-%d').date()
                    except ValueError:
                        v = datetime.datetime.strptime(v, '%Y/%m/%d').date()
                    trader_qs = trader_qs.filter(created_at=v)
                    hall_qs = hall_qs.filter(created_at=v)
                elif k == 'customer':
                    trader_qs = trader_qs.filter(customer__name__icontains=v)
                    hall_qs = hall_qs.filter(customer__name__icontains=v)
        contract_list = list(trader_qs) + list(hall_qs)
        return contract_list
    
    def get_paginator(self):
        page = self.request.GET.get('page', 1)
        paginator = Paginator(self.get_contract_list(), paginate_by)
        return paginator.page(page)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = self.get_paginator()
        params = self.request.GET
        for k, v in params.items():
            if v:
                context[k] = v
        return context
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="accounting_purchases_{}.csv"'.format(generate_random_number())
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Type'), _('Taxation'), _('Amount'), _('Customer'),
        ])
        contract_list = self.get_contract_list()
        for contract in contract_list:
            writer.writerow([
                contract.contract_id, contract.created_at, _('Expense'), '課対仕入10%', contract.taxed_total, contract.customer.name
            ])
            writer.writerow([
                contract.contract_id, contract.created_at, _('Income'), '非課仕入', contract.insurance_fee, contract.customer.name
            ])
        return response
