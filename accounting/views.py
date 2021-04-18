import unicodecsv as csv
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from users.views import AdminLoginRequiredMixin
from masterdata.models import NO_FEE_PURCHASES, NO_FEE_SALES, FEE_PURCHASES, FEE_SALES
from contracts.models import TraderSalesContract, HallSalesContract, TraderPurchasesContract, HallPurchasesContract
from contracts.utilities import generate_random_number, update_csv_history
from .forms import SearchForm

paginate_by = 3

class SalesListView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'accounting/sales.html'
    
    def get_contract_list(self):
        trader_qs = TraderSalesContract.objects.all()
        hall_qs = HallSalesContract.objects.all()
        search_form = SearchForm(self.request.GET)
        if search_form.is_valid():
            contract_id = search_form.cleaned_data.get('contract_id')
            created_at = search_form.cleaned_data.get('created_at')
            customer = search_form.cleaned_data.get('customer')
            if contract_id:
                trader_qs = trader_qs.filter(contract_id__icontains=contract_id)
                hall_qs = hall_qs.filter(contract_id__icontains=contract_id)
            if created_at:
                trader_qs = trader_qs.filter(created_at=created_at)
                hall_qs = hall_qs.filter(created_at=created_at)
            if customer:
                trader_qs = trader_qs.filter(customer__name__icontains=customer)
                hall_qs = hall_qs.filter(customer__name__icontains=customer)
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
        user_id = self.request.user.id
        update_csv_history(user_id, "{} - {}".format(_("Accounting software CSV"), _("Sale")))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="accounting_sales_{}.csv"'.format(generate_random_number())
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Type'), _('Taxation'), _('Amount'), _('Customer'),
        ])
        contract_list = self.get_contract_list()
        for contract in contract_list:
            writer.writerow([
                contract.contract_id, contract.created_at, _('Income'), FEE_SALES, contract.taxed_total, contract.customer.name if contract.customer else None
            ])
            writer.writerow([
                contract.contract_id, contract.created_at, None, NO_FEE_SALES, contract.fee, contract.customer.name if contract.customer else None
            ])
        return response


class PurchasesListView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'accounting/purchases.html'
    
    def get_contract_list(self):
        trader_qs = TraderPurchasesContract.objects.all()
        hall_qs = HallPurchasesContract.objects.all()
        search_form = SearchForm(self.request.GET)
        if search_form.is_valid():
            contract_id = search_form.cleaned_data.get('contract_id')
            created_at = search_form.cleaned_data.get('created_at')
            customer = search_form.cleaned_data.get('customer')
            if contract_id:
                trader_qs = trader_qs.filter(contract_id__icontains=contract_id)
                hall_qs = hall_qs.filter(contract_id__icontains=contract_id)
            if created_at:
                trader_qs = trader_qs.filter(created_at=created_at)
                hall_qs = hall_qs.filter(created_at=created_at)
            if customer:
                trader_qs = trader_qs.filter(customer__name__icontains=customer)
                hall_qs = hall_qs.filter(customer__name__icontains=customer)
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
        user_id = self.request.user.id
        update_csv_history(user_id, "{} - {}".format(_("Accounting software CSV"), _("Purchase")))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="accounting_purchases_{}.csv"'.format(generate_random_number())
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Type'), _('Taxation'), _('Amount'), _('Customer'),
        ])
        contract_list = self.get_contract_list()
        for contract in contract_list:
            writer.writerow([
                contract.contract_id, contract.created_at, _('Expense'), FEE_PURCHASES, contract.taxed_total, contract.customer.name if contract.customer else None
            ])
            writer.writerow([
                contract.contract_id, contract.created_at, None, NO_FEE_PURCHASES, contract.fee, contract.customer.name if contract.customer else None
            ])
        return response
