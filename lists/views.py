import csv
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from users.views import AdminLoginRequiredMixin
from contracts.models import *
from contracts.utilities import *
from .filters import *


def ProductFilter(queryset, **params):
    return queryset


class SalesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/sales.html'
    queryset = ContractProduct.objects.all().order_by('pk')
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        trader_class_id = ContentType.objects.get(model='TraderSalesContract').id
        hall_class_id = ContentType.objects.get(model='HallSalesContract').id
        queryset = ContractProduct.objects.filter(
            Q(content_type_id=trader_class_id) |
            Q(content_type_id=hall_class_id)
        ).order_by('-pk')
        return queryset
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_list_{}.csv"'.format(generate_contract_id())
        writer = csv.writer(response)
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Customer'), _('Delivered place'), _('Person in charge'),
            _('Payment date'), _('Product name'), _('Number of units'), _('Amount'), _('Inventory status')
        ])
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['sales_filter'] = SalesFilter(self.request.GET)
        return context


class PurchasesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/purchases.html'
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        trader_class_id = ContentType.objects.get(model='TraderPurchasesContract').id
        hall_class_id = ContentType.objects.get(model='HallPurchasesContract').id
        queryset = ContractProduct.objects.filter(
            Q(content_type_id=trader_class_id) |
            Q(content_type_id=hall_class_id)
        ).order_by('-pk')
        return queryset
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="purchase_list_{}.csv"'.format(generate_contract_id())
        writer = csv.writer(response)
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Customer'), _('Delivered place'), _('Person in charge'),
            _('Payment date'), _('Product name'), _('Number of units'), _('Amount'), _('Inventory status')
        ])
        return response


class InventoryListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/inventory.html'
    queryset = InventoryProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return self.queryset
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_list_{}.csv"'.format(generate_contract_id())
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


class ListingSalesProductUpdateView(AdminLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        status = request.POST.get('status')
        product = ContractProduct.objects.get(id=id)
        if status != product.status:
            print('process')
        return redirect('list:sales')


class ListingPurchasesProductUpdateView(AdminLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        status = request.POST.get('status')
        product = ContractProduct.objects.get(id=id)
        if status != product.status:
            print('process')
        return redirect('list:sales')


class ListingSalesProductDetailAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            id = self.request.POST.get('id')
            product = ContractProduct.objects.get(id=id)
            if product.content_type_id == ContentType.objects.get(model='TraderSalesContract').id:
                contract = product.trader_sales_contract.first()
            elif product.content_type_id == ContentType.objects.get(model='HallSalesContract').id:
                contract = product.hall_sales_contract.first()
            else:
                return JsonResponse({'success': False}, status=400)
            contract_id = contract.contract_id
            contract_date = contract.created_at
            customer = contract.customer.name
            person_in_charge = contract.person_in_charge
            if product.content_type_id == ContentType.objects.get(model='HallSalesContract').id:
                destination = contract.hall.name
                payment_date = contract.shipping_date
            else:
                destination = None
                payment_date = contract.payment_due_date
            product_name = product.product.name
            quantity = product.quantity
            price = product.quantity * product.price
            status = product.status
            return JsonResponse({
                'contract_id': contract_id,
                'contract_date': contract_date,
                'customer': customer,
                'destination': destination,
                'person_in_charge': person_in_charge,
                'payment_date': payment_date,
                'product_name': product_name,
                'quantity': quantity,
                'price': price,
                'status': status
            }, status=200)
        return JsonResponse({'success': False}, status=400)


class ListingPurchasesProductDetailAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            id = self.request.POST.get('id')
            product = ContractProduct.objects.get(id=id)
            if product.content_type_id == ContentType.objects.get(model='TraderPurchasesContract').id:
                contract = product.trader_purchases_contract.first()
            elif product.content_type_id == ContentType.objects.get(model='HallPurchasesContract').id:
                contract = product.hall_purchases_contract.first()
            else:
                return JsonResponse({'success': False}, status=400)
            contract_id = contract.contract_id
            contract_date = contract.created_at
            customer = contract.customer.name
            person_in_charge = contract.person_in_charge
            if product.content_type_id == ContentType.objects.get(model='HallPurchasesContract').id:
                destination = contract.hall.name
                payment_date = contract.shipping_date
            else:
                destination = None
                payment_date = contract.transfer_deadline
            product_name = product.product.name
            quantity = product.quantity
            price = product.quantity * product.price
            status = product.status
            return JsonResponse({
                'contract_id': contract_id,
                'contract_date': contract_date,
                'customer': customer,
                'destination': destination,
                'person_in_charge': person_in_charge,
                'payment_date': payment_date,
                'product_name': product_name,
                'quantity': quantity,
                'price': price,
                'status': status
            }, status=200)
        return JsonResponse({'success': False}, status=400)
