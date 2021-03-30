import csv
import time
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from users.views import AdminLoginRequiredMixin
from contracts.models import *


class SalesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/sales.html'
    queryset = ContractProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_list_{}.csv"'.format(int(time.time()))
        writer = csv.writer(response)
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Customer'), _('Delivered place'), _('Person in charge'),
            _('Payment day'), _('Product name'), _('Number of units'), _('Amount'), _('Inventory status')
        ])

        return response


class PurchasesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/purchases.html'
    queryset = ContractProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="purchase_list_{}.csv"'.format(int(time.time()))
        writer = csv.writer(response)
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Customer'), _('Delivered place'), _('Person in charge'),
            _('Payment day'), _('Product name'), _('Number of units'), _('Amount'), _('Inventory status')
        ])

        return response


class InventoryListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/inventory.html'
    queryset = ContractProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_list_{}.csv"'.format(int(time.time()))
        writer = csv.writer(response)
        writer.writerow([
            _('Product name'), _('Control number'), _('Purchases date'), _('Supplier'), _('Person in charge'),
            _('Number of units'), _('Price'), _('Stock'), _('Total price')
        ])

        for i in range(0, 5):
            writer.writerow([
                'Ｓ聖闘士星矢海皇覚醒ＳＰ－ＫＦ', '17884', '2021/03/31', 'アイエス販売', '金昇志', '10', '1500', '10', '15000'
            ])

        return response
