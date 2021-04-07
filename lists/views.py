import unicodecsv as csv
import datetime
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


class SalesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/sales.html'
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        trader_class_id = ContentType.objects.get(model='TraderSalesContract').id
        hall_class_id = ContentType.objects.get(model='HallSalesContract').id
        queryset = ContractProduct.objects.filter(
            Q(content_type_id=trader_class_id) |
            Q(content_type_id=hall_class_id)
        ).order_by('-pk')
        params = self.request.GET.copy()
        for k, v in params.items():
            if v:
                if k == "contract_id":
                    queryset = queryset.filter(
                        Q(trader_sales_contract__contract_id__icontains=v) |
                        Q(hall_sales_contract__contract_id__icontains=v)
                    )
                elif k == 'created_at':
                    try:
                        v = datetime.datetime.strptime(v, '%Y-%m-%d').date()
                    except ValueError:
                        v = datetime.datetime.strptime(v, '%Y/%m/%d').date()
                    queryset = queryset.filter(
                        Q(trader_sales_contract__created_at=v) |
                        Q(hall_sales_contract__created_at=v)
                    )
                elif k == 'customer':
                    queryset = queryset.filter(
                        Q(trader_sales_contract__customer__name__icontains=v) |
                        Q(hall_sales_contract__customer__name__icontains=v)
                    )
                elif k == 'name':
                    queryset = queryset.filter(Q(product__name__icontains=v))
                elif k == 'inventory_status':
                    queryset = queryset.filter(Q(status=v))
        return queryset.order_by('-pk')
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="listing_sales_{}.csv"'.format(generate_contract_id())
        qs = self.get_queryset()
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Customer'), _('Delivered place'), _('Person in charge'),
            _('Payment date'), _('Product name'), _('Number of units'), _('Amount'), _('Inventory status')
        ])
        for product in qs:
            contract = product.content_object
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
            amount = product.amount
            status = product.status
            writer.writerow([
                contract_id, contract_date, customer, destination, person_in_charge, payment_date, product_name,
                quantity, amount, dict(STOCK_CHOICES)[status]
            ])
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hall_contract_id'] = ContentType.objects.get(model='HallSalesContract').id
        params = self.request.GET.copy()
        for k, v in params.items():
            if v:
                context[k] = v
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
        params = self.request.GET.copy()
        for k, v in params.items():
            if v:
                if k == "contract_id":
                    queryset = queryset.filter(
                        Q(trader_purchases_contract__contract_id__icontains=v) |
                        Q(hall_purchases_contract__contract_id__icontains=v)
                    )
                elif k == 'created_at':
                    try:
                        v = datetime.datetime.strptime(v, '%Y-%m-%d').date()
                    except ValueError:
                        v = datetime.datetime.strptime(v, '%Y/%m/%d').date()
                    queryset = queryset.filter(
                        Q(trader_purchases_contract__created_at=v) |
                        Q(hall_purchases_contract__created_at=v)
                    )
                elif k == 'customer':
                    queryset = queryset.filter(
                        Q(trader_purchases_contract__customer__name__icontains=v) |
                        Q(hall_purchases_contract__customer__name__icontains=v)
                    )
                elif k == 'name':
                    queryset = queryset.filter(Q(product__name__icontains=v))
                elif k == 'inventory_status':
                    queryset = queryset.filter(Q(status=v))
        return queryset.order_by('-pk')
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="listing_purchases_{}.csv"'.format(generate_contract_id())
        qs = self.get_queryset()
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Customer'), _('Delivered place'), _('Person in charge'),
            _('Payment date'), _('Product name'), _('Number of units'), _('Amount'), _('Inventory status')
        ])
        for product in qs:
            contract = product.content_object
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
            amount = product.amount
            status = product.status
            writer.writerow([
                contract_id, contract_date, customer, destination, person_in_charge, payment_date, product_name,
                quantity, amount, dict(STOCK_CHOICES)[status]
            ])
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hall_contract_id'] = ContentType.objects.get(model='HallPurchasesContract').id
        params = self.request.GET.copy()
        for k, v in params.items():
            if v:
                context[k] = v
        return context


class InventoryListView(AdminLoginRequiredMixin, ListView):
    template_name = 'lists/inventory.html'
    queryset = InventoryProduct.objects.all().order_by('-pk')
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
            contract = product.content_object
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
            contract = product.content_object
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
