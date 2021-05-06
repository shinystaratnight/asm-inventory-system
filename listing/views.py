import xlwt
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from users.views import AdminLoginRequiredMixin
from masterdata.models import InventoryProduct, STOCK_CHOICES
from contracts.models import ContractProduct
from listing.models import ExportHistory
from contracts.utilities import generate_random_number, date_dump, log_export_operation
from .filters import ProductFilter
from .forms import ListingSearchForm, ProductForm

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

class SalesListView(AdminLoginRequiredMixin, ListView):
    template_name = 'listing/sales.html'
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        trader_class_id = ContentType.objects.get(model='tradersalescontract').id
        hall_class_id = ContentType.objects.get(model='hallsalescontract').id
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
        user_id = self.request.user.id
        log_export_operation(user_id, "{} - {}".format(_("List"), _("Sales")))
        
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="listing_sales_{}.xls"'.format(generate_random_number())
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("{} - {}".format(_('List'), _('Sales')))

        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write(0, 0, _('Contract ID'), bold_style)
        ws.write(0, 1, _('Contract date'), bold_style)
        ws.write(0, 2, _('Customer'), bold_style)
        ws.write(0, 3, _('Delivered place'), bold_style)
        ws.write(0, 4, _('Person in charge'), bold_style)
        ws.write(0, 5, _('Payment date'), bold_style)
        ws.write(0, 6, _('Product name'), bold_style)
        ws.write(0, 7, _('Unit count'), bold_style)
        ws.write(0, 8, _('Amount'), bold_style)
        ws.write(0, 9, _('Inventory status'), bold_style)

        for i in range(10):
            ws.col(i).width = cell_width
        ws.col(2).width = ws.col(3).width = ws.col(6).width = wide_cell_width

        row_no = 1
        date_style.num_format_str = 'yyyy/mm/dd' if self.request.LANGUAGE_CODE == 'ja' else 'mm/dd/yyyy'
        queryset = self.get_queryset()
        for product in queryset:
            contract = product.content_object
            contract_id = contract.contract_id
            contract_date = contract.created_at
            customer = contract.customer.name if contract.customer else None
            person_in_charge = contract.person_in_charge
            if product.content_type_id == ContentType.objects.get(model='hallsalescontract').id:
                destination = contract.hall.name if contract.hall else None
                payment_date = contract.shipping_date
            else:
                destination = None
                payment_date = contract.payment_due_date
            product_name = product.product.name
            quantity = product.quantity
            amount = product.amount
            status = product.status
            
            ws.write(row_no, 0, contract_id, common_style)
            ws.write(row_no, 1, contract_date, date_style)
            ws.write(row_no, 2, customer, common_style)
            ws.write(row_no, 3, destination, common_style)
            ws.write(row_no, 4, person_in_charge, common_style)
            ws.write(row_no, 5, payment_date, date_style)
            ws.write(row_no, 6, product_name, common_style)
            ws.write(row_no, 7, quantity, common_style)
            ws.write(row_no, 8, amount, common_style)
            ws.write(row_no, 9, str(dict(STOCK_CHOICES)[status]), common_style)
            row_no += 1
        
        wb.save(response)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hall_contract_id'] = ContentType.objects.get(model='hallsalescontract').id
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
        trader_class_id = ContentType.objects.get(model='traderpurchasescontract').id
        hall_class_id = ContentType.objects.get(model='hallpurchasescontract').id
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
        user_id = self.request.user.id
        log_export_operation(user_id, "{} - {}".format(_("List"), _("Purchases")))

        
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="listing_purchases_{}.xls"'.format(generate_random_number())
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("{} - {}".format(_('List'), _('Purchases')))

        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write(0, 0, _('Contract ID'), bold_style)
        ws.write(0, 1, _('Contract date'), bold_style)
        ws.write(0, 2, _('Customer'), bold_style)
        ws.write(0, 3, _('Delivered place'), bold_style)
        ws.write(0, 4, _('Person in charge'), bold_style)
        ws.write(0, 5, _('Payment date'), bold_style)
        ws.write(0, 6, _('Product name'), bold_style)
        ws.write(0, 7, _('Unit count'), bold_style)
        ws.write(0, 8, _('Amount'), bold_style)
        ws.write(0, 9, _('Inventory status'), bold_style)

        for i in range(10):
            ws.col(i).width = cell_width
        ws.col(2).width = ws.col(3).width = ws.col(6).width = wide_cell_width

        row_no = 1
        date_style.num_format_str = 'yyyy/mm/dd' if self.request.LANGUAGE_CODE == 'ja' else 'mm/dd/yyyy'
        queryset = self.get_queryset()
        for product in queryset:
            contract = product.content_object
            contract_id = contract.contract_id
            contract_date = contract.created_at
            customer = contract.customer.name if contract.customer else None
            person_in_charge = contract.person_in_charge
            if product.content_type_id == ContentType.objects.get(model='hallpurchasescontract').id:
                destination = contract.hall.name if contract.hall else None
                payment_date = contract.shipping_date
            else:
                destination = None
                payment_date = contract.transfer_deadline
            product_name = product.product.name
            quantity = product.quantity
            amount = product.amount
            status = product.status

            ws.write(row_no, 0, contract_id, common_style)
            ws.write(row_no, 1, contract_date, date_style)
            ws.write(row_no, 2, customer, common_style)
            ws.write(row_no, 3, destination, common_style)
            ws.write(row_no, 4, person_in_charge, common_style)
            ws.write(row_no, 5, payment_date, date_style)
            ws.write(row_no, 6, product_name, common_style)
            ws.write(row_no, 7, quantity, common_style)
            ws.write(row_no, 8, amount, common_style)
            ws.write(row_no, 9, str(dict(STOCK_CHOICES)[status]), common_style)
            row_no += 1
        
        wb.save(response)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hall_contract_id'] = ContentType.objects.get(model='hallpurchasescontract').id
        params = self.request.GET.copy()
        for k, v in params.items():
            if v:
                context[k] = v
        return context


class ExportHistoryListView(AdminLoginRequiredMixin, ListView):
    template_name = 'listing/history.html'
    context_object_name = 'objects'
    paginate_by = 10

    def get_queryset(self):
        return ExportHistory.objects.order_by('-exported_at')
        # return ProductFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['history_filter'] = HistoryFilter(self.request.GET)
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
        user_id = self.request.user.id
        log_export_operation(user_id, "{} - {}".format(_("List"), _("Inventory")))
        
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="inventory_listing_{}.xls"'.format(generate_random_number())
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("{} - {}".format(_('List'), _('Inventory')))

        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write(0, 0, 'No.', bold_style)
        ws.write(0, 1, _('Product name'), bold_style)
        ws.write(0, 2, _('Control number'), bold_style)
        ws.write(0, 3, _('Purchase date'), bold_style)
        ws.write(0, 4, _('Supplier'), bold_style)
        ws.write(0, 5, _('Person in charge'), bold_style)
        ws.write(0, 6, _('Unit count'), bold_style)
        ws.write(0, 7, _('Price'), bold_style)
        ws.write(0, 8, _('Stock'), bold_style)
        ws.write(0, 9, _('Total price'), bold_style)

        for i in range(10):
            ws.col(i).width = cell_width
        ws.col(1).width = ws.col(4).width = wide_cell_width

        row_no = 1
        date_style.num_format_str = 'yyyy/mm/dd' if self.request.LANGUAGE_CODE == 'ja' else 'mm/dd/yyyy'
        queryset = self.get_queryset()
        for product in queryset:
            ws.write(row_no, 0, row_no, common_style)
            ws.write(row_no, 1, product.name, common_style)
            ws.write(row_no, 2, product.identifier, common_style)
            ws.write(row_no, 3, product.purchase_date, date_style)
            ws.write(row_no, 4, product.supplier, common_style)
            ws.write(row_no, 5, product.person_in_charge, common_style)
            ws.write(row_no, 6, product.quantity, common_style)
            ws.write(row_no, 7, product.price, common_style)
            ws.write(row_no, 8, product.stock, common_style)
            ws.write(row_no, 9, product.amount, common_style)
            row_no += 1
        
        wb.save(response)
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
            product_name = product.product.name
            status = product.status
            return JsonResponse({
                'contract_id': contract_id,
                'product_name': product_name,
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
            product_name = product.product.name
            status = product.status
            return JsonResponse({
                'contract_id': contract_id,
                'product_name': product_name,
                'status': status
            }, status=200)
        return JsonResponse({'success': False}, status=400)
