import xlwt
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from users.views import AdminLoginRequiredMixin
from masterdata.models import NO_FEE_PURCHASES, NO_FEE_SALES, FEE_PURCHASES, FEE_SALES
from contracts.models import TraderSalesContract, HallSalesContract, TraderPurchasesContract, HallPurchasesContract
from contracts.utilities import generate_random_number, log_export_operation
from .forms import SearchForm

paginate_by = 3

cell_width = 256 * 20
wide_cell_width = 256 * 45
cell_height = int(256 * 1.5)
header_height = int(cell_height * 1.5)
font_size = 20 * 10 # pt

common_style = xlwt.easyxf('font: height 200; align: vert center, horiz left, wrap on;\
                            borders: top_color black, bottom_color black, right_color black, left_color black,\
                            left thin, right thin, top thin, bottom thin;')
date_style = xlwt.easyxf('font: height 200; align: vert center, horiz left, wrap on;\
                            borders: top_color black, bottom_color black, right_color black, left_color black,\
                            left thin, right thin, top thin, bottom thin;')
bold_style = xlwt.easyxf('font: bold on, height 200; align: vert center, horiz left, wrap on;\
                            borders: top_color black, bottom_color black, right_color black, left_color black,\
                            left thin, right thin, top thin, bottom thin;')


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
        log_export_operation(user_id, "{} - {}".format(_("Accounting software CSV"), _("Sale")))

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="accounting_sales_{}.xls"'.format(generate_random_number())
        wb = xlwt.Workbook(encoding='utf-8')

        if self.request.LANGUAGE_CODE == 'en':
            ws = wb.add_sheet('Accounting CSV - Sales')
        else:
            ws = wb.add_sheet("{} - {}".format(_('Accounting software CSV'), _('Sale')))
        
        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write(0, 0, _('No'), bold_style)
        ws.write(0, 1, _('Contract ID'), bold_style)
        ws.write(0, 2, _('Contract date'), bold_style)
        ws.write(0, 3, _('Type'), bold_style)
        ws.write(0, 4, _('Taxation'), bold_style)
        ws.write(0, 5, _('Amount'), bold_style)
        ws.write(0, 6, _('Customer'), bold_style)

        for i in range(10):
            ws.col(i).width = cell_width
        ws.col(6).width = wide_cell_width

        row_no = 1
        contract_list = self.get_contract_list()
        date_style.num_format_str = 'yyyy/mm/dd' if self.request.LANGUAGE_CODE == 'ja' else 'mm/dd/yyyy'
        for contract in contract_list:
            ws.write(row_no * 2 - 1, 0, "{}".format(row_no * 2 - 1), common_style)
            ws.write(row_no * 2 - 1, 1, contract.contract_id, common_style)
            ws.write(row_no * 2 - 1, 2, contract.created_at, date_style)
            ws.write(row_no * 2 - 1, 3, _('Income'), common_style)
            ws.write(row_no * 2 - 1, 4, FEE_SALES, common_style)
            ws.write(row_no * 2 - 1, 5, contract.taxed_total, common_style)
            ws.write(row_no * 2 - 1, 6, contract.customer.name if contract.customer else None, common_style)

            ws.write(row_no * 2, 0, "{}".format(row_no * 2), common_style)
            ws.write(row_no * 2, 1, contract.contract_id, common_style)
            ws.write(row_no * 2, 2, contract.created_at, date_style)
            ws.write(row_no * 2, 3, None, common_style)
            ws.write(row_no * 2, 4, NO_FEE_SALES, common_style)
            ws.write(row_no * 2, 5, contract.fee, common_style)
            ws.write(row_no * 2, 6, contract.customer.name if contract.customer else None, common_style)
            row_no += 1
        
        wb.save(response)
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
        log_export_operation(user_id, "{} - {}".format(_("Accounting software CSV"), _("Purchase")))

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="accounting_purchases_{}.xls"'.format(generate_random_number())
        wb = xlwt.Workbook(encoding='utf-8')
        if self.request.LANGUAGE_CODE == 'en':
            ws = wb.add_sheet('Accounting CSV - Purchases')
        else:
            ws = wb.add_sheet("{} - {}".format(_('Accounting software CSV'), _('Purchase')))

        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write(0, 0, _('No'), bold_style)
        ws.write(0, 1, _('Contract ID'), bold_style)
        ws.write(0, 2, _('Contract date'), bold_style)
        ws.write(0, 3, _('Type'), bold_style)
        ws.write(0, 4, _('Taxation'), bold_style)
        ws.write(0, 5, _('Amount'), bold_style)
        ws.write(0, 6, _('Customer'), bold_style)

        for i in range(10):
            ws.col(i).width = cell_width
        ws.col(6).width = wide_cell_width

        row_no = 1
        date_style.num_format_str = 'yyyy/mm/dd' if self.request.LANGUAGE_CODE == 'ja' else 'mm/dd/yyyy'
        contract_list = self.get_contract_list()
        for contract in contract_list:
            ws.write(row_no * 2 - 1, 0, "{}".format(row_no * 2 - 1), common_style)
            ws.write(row_no * 2 - 1, 1, contract.contract_id, common_style)
            ws.write(row_no * 2 - 1, 2, contract.created_at, date_style)
            ws.write(row_no * 2 - 1, 3, _('Expense'), common_style)
            ws.write(row_no * 2 - 1, 4, FEE_PURCHASES, common_style)
            ws.write(row_no * 2 - 1, 5, contract.taxed_total, common_style)
            ws.write(row_no * 2 - 1, 6, contract.customer.name if contract.customer else None, common_style)

            ws.write(row_no * 2, 0, "{}".format(row_no * 2), common_style)
            ws.write(row_no * 2, 1, contract.contract_id, common_style)
            ws.write(row_no * 2, 2, contract.created_at, date_style)
            ws.write(row_no * 2, 3, None, common_style)
            ws.write(row_no * 2, 4, NO_FEE_PURCHASES, common_style)
            ws.write(row_no * 2, 5, contract.fee, common_style)
            ws.write(row_no * 2, 6, contract.customer.name if contract.customer else None, common_style)
            row_no += 1
        
        wb.save(response)
        return response
