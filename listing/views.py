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
from contracts.models import ContractProduct, InventoryProduct
from contracts.utilities import generate_random_number, date_dump
from .filters import ProductFilter
from .forms import ListingSearchForm, ProductForm


class SalesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'listing/sales.html'
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        trader_class_id = ContentType.objects.get(model='TraderSalesContract').id
        hall_class_id = ContentType.objects.get(model='HallSalesContract').id
        queryset = ContractProduct.objects.filter(
            Q(content_type_id=trader_class_id) |
            Q(content_type_id=hall_class_id)
        ).order_by('-pk')
        search_form = ListingSearchForm(self.request.GET)
        if search_form.is_valid():
            contract_id = search_form.cleaned_data.get('contract_id')
            created_at =  search_form.cleaned_data.get('created_at')
            customer = search_form.cleaned_data.get('customer')
            name = search_form.cleaned_data.get('name')
            inventory_status = search_form.cleaned_data.get('inventory_status')
            if contract_id:
                queryset = queryset.filter(
                    Q(trader_sales_contract__contract_id__icontains=contract_id) |
                    Q(hall_sales_contract__contract_id__icontains=contract_id)
                )
            if created_at:
                queryset = queryset.filter(
                    Q(trader_sales_contract__created_at=created_at) |
                    Q(hall_sales_contract__created_at=created_at)
                )
            if customer:
                queryset = queryset.filter(
                    Q(trader_sales_contract__customer__name__icontains=customer) |
                    Q(hall_sales_contract__customer__name__icontains=customer)
                )
            if name:
                queryset = queryset.filter(Q(product__name__icontains=name))
            if inventory_status:
                queryset = queryset.filter(Q(status=inventory_status))
        return queryset.order_by('-pk')
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="listing_sales_{}.csv"'.format(generate_random_number())
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Customer'), _('Delivered place'), _('Person in charge'),
            _('Payment date'), _('Product name'), _('Unit count'), _('Amount'), _('Inventory status')
        ])
        queryset = self.get_queryset()
        for product in queryset:
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
    template_name = 'listing/purchases.html'
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        trader_class_id = ContentType.objects.get(model='TraderPurchasesContract').id
        hall_class_id = ContentType.objects.get(model='HallPurchasesContract').id
        queryset = ContractProduct.objects.filter(
            Q(content_type_id=trader_class_id) |
            Q(content_type_id=hall_class_id)
        ).order_by('-pk')
        search_form = ListingSearchForm(self.request.GET)
        if search_form.is_valid():
            contract_id = search_form.cleaned_data.get('contract_id')
            created_at =  search_form.cleaned_data.get('created_at')
            customer = search_form.cleaned_data.get('customer')
            name = search_form.cleaned_data.get('name')
            inventory_status = search_form.cleaned_data.get('inventory_status')
            if contract_id:
                queryset = queryset.filter(
                    Q(trader_purchases_contract__contract_id__icontains=contract_id) |
                    Q(hall_purchases_contract__contract_id__icontains=contract_id)
                )
            if created_at:
                queryset = queryset.filter(
                    Q(trader_purchases_contract__created_at=created_at) |
                    Q(hall_purchases_contract__created_at=created_at)
                )
            if customer:
                queryset = queryset.filter(
                    Q(trader_purchases_contract__customer__name__icontains=customer) |
                    Q(hall_purchases_contract__customer__name__icontains=customer)
                )
            if name:
                queryset = queryset.filter(Q(product__name__icontains=name))
            if inventory_status:
                queryset = queryset.filter(Q(status=inventory_status))
        return queryset.order_by('-pk')
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="listing_purchases_{}.csv"'.format(generate_random_number())
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Contract ID'), _('Contract date'), _('Customer'), _('Delivered place'), _('Person in charge'),
            _('Payment date'), _('Product name'), _('Unit count'), _('Amount'), _('Inventory status')
        ])
        queryset = self.get_queryset()
        for product in queryset:
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
    template_name = 'listing/inventory.html'
    queryset = InventoryProduct.objects.all()
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        return ProductFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_filter'] = ProductFilter(self.request.GET)
        return context
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_listing_{}.csv"'.format(generate_random_number())
        writer = csv.writer(response, encoding='utf-8-sig')
        writer.writerow([
            _('Product name'), _('Control number'), _('Purchase date'), _('Supplier'), _('Person in charge'),
            _('Unit count'), _('Price'), _('Stock'), _('Total price')
        ])
        queryset = self.get_queryset()
        for product in queryset:
            writer.writerow([
                product.name, product.identifier, product.purchase_date, product.supplier, product.person_in_charge,
                product.quantity, product.price, product.stock, product.amount
            ])
        return response


class InventoryProductCreateView(AdminLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            product_form.save()
        return redirect('listing:inventory-list')


class InventoryProductUpdateView(AdminLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        product = InventoryProduct.objects.get(id=id)
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            data = product_form.cleaned_data
            product.name = data.get('name')
            product.identifier = data.get('identifier')
            product.purchase_date = data.get('purchase_date')
            product.supplier = data.get('supplier')
            product.person_in_charge = data.get('person_in_charge')
            product.quantity = data.get('quantity')
            product.price = data.get('price')
            product.stock = data.get('stock')
            product.amount = data.get('amount')
            product.save()
        return redirect('listing:inventory-list')


class InventoryProductDeleteView(AdminLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        product = InventoryProduct.objects.get(id=id)
        product.delete()
        return redirect('listing:inventory-list')


class InventoryProductDetailAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            id = self.request.POST.get('id')
            product = InventoryProduct.objects.get(id=id)
            return JsonResponse({
                'name': product.name,
                'identifier': product.identifier,
                'purchase_date': date_dump(product.purchase_date, self.request.LANGUAGE_CODE),
                'supplier': product.supplier,
                'person_in_charge': product.person_in_charge,
                'quantity': product.quantity,
                'price': product.price,
                'stock': product.stock,
                'amount': product.amount,
            }, status=200)
        return JsonResponse({'success': False}, status=400)


class SalesProductUpdateView(AdminLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        status = request.POST.get('status')
        product = ContractProduct.objects.get(id=id)
        product.status = status
        product.save()
        return redirect('listing:sales-list')


class PurchasesProductUpdateView(AdminLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        status = request.POST.get('status')
        product = ContractProduct.objects.get(id=id)
        product.status = status
        product.save()
        return redirect('listing:purchases-list')


class SalesProductDetailAjaxView(AdminLoginRequiredMixin, View):
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


class PurchasesProductDetailAjaxView(AdminLoginRequiredMixin, View):
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
