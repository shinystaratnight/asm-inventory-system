from django.views.generic.list import ListView
from users.views import AdminLoginRequiredMixin
from contracts.models import *


class SalesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/sales.html'
    queryset = ContractProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset


class PurchasesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/purchases.html'
    queryset = ContractProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset


class InventoryListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/inventory.html'
    queryset = ContractProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset
