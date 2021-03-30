from django.views.generic.list import ListView
from users.views import AdminLoginRequiredMixin
from contracts.models import *


class SalesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/sales.html'
    context_object_name = 'products'

    def get_queryset(self):
        return ContractProduct.objects.all()


class PurchasesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/purchases.html'
    context_object_name = 'products'

    def get_queryset(self):
        return ContractProduct.objects.all()


class InventoryListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/inventory.html'
    context_object_name = 'products'

    def get_queryset(self):
        return ContractProduct.objects.all()
