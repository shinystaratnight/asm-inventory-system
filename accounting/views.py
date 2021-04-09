import csv
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

paginate_by = 5


class SalesListView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'accounting/sales.html'
    
    def get_querylist(self):
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
        page = self.request.POST.get('page', 1)
        paginator = Paginator(contract_list, paginate_by)
        return paginator.page(page)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = self.get_querylist()
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
        writer.writerow(['1617130845', '2021/03/31', _('Income'), '課税売上10%', '93500', '（株）ライム'])
        writer.writerow(['1617130845', '2021/03/31', '', '非課売上', '100', '（株）ライム'])
        return response


class PurchasesListView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'accounting/purchases.html'
    
    def get_querylist(self):
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
        page = self.request.POST.get('page', 1)
        paginator = Paginator(contract_list, paginate_by)
        return paginator.page(page)

    def get_queryset(self):
        return self.queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = self.get_querylist()
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
        writer.writerow(['1617130845', '2021/03/31', _('Expense'), '課対仕入10%', '93500', '（株）ライム'])
        writer.writerow(['1617130845', '2021/03/31', '', '非課仕入', '260', '（株）ライム'])
        return response
