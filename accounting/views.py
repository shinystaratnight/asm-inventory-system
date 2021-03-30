import csv
import time
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.utils.translation import gettext_lazy as _
from users.views import AdminLoginRequiredMixin
from contracts.models import *


class SalesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'accounting/sales.html'
    queryset = ContractProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="account_sales_{}.csv"'.format(int(time.time()))
        writer = csv.writer(response)
        writer.writerow(['2021/03/31', _('Income'), '課税売上10%', '93500', '（株）ライム'])
        writer.writerow(['2021/03/31', '', '非課売上', '100', '（株）ライム'])

        return response


class PurchasesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'accounting/purchases.html'
    queryset = ContractProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="account_purchases_{}.csv"'.format(int(time.time()))
        writer = csv.writer(response)
        writer.writerow(['2021/03/31', _('Expense'), '課対仕入10%', '93500', '（株）ライム'])
        writer.writerow(['2021/03/31', '', '非課仕入', '260', '（株）ライム'])

        return response
