import unicodecsv as csv
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.views.generic.base import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.utils.translation import gettext as _
from users.views import AdminLoginRequiredMixin
# from masterdata.models import (

# )
from .models import *
from .forms import (
    TraderSalesContractForm, TraderPurchasesContractForm, HallSalesContractForm, HallPurchasesContractForm,
    ProductFormSet, DocumentFormSet, DocumentFeeFormSet, MilestoneFormSet, 
    TraderSalesSenderForm, TraderPurchasesSenderForm,
)
from .utilities import generate_contract_id, ordinal


# List of people in charge for common contract pages
class ContractManagerAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            contract = self.request.POST.get('contract')
            content_type = ContentType.objects.get(model=contract)
            contract_model = content_type.model_class()
            people = contract_model.objects.values('person_in_charge').annotate(
                people_count=Count('person_in_charge')
            ).filter(people_count=1)
            return JsonResponse({'people': list(people)}, status=200)
        return JsonResponse({'success': False}, status=400)


# Shipping label for trader sales contract page
class ContractShippingLabelAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST.get('data')
            if data == 'R':
                return JsonResponse({'data': _('Receipt date')}, status=200)
            elif data == 'C':
                return JsonResponse({'data': _('ID Change date')}, status=200)
            else:
                return JsonResponse({'data': _('Delivery date')}, status=200)
        return JsonResponse({'success': False}, status=400)


class ContractClassNameAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            object_id = self.request.POST.get('object_id')
            class_id = self.request.POST.get('class_id')
            ContentType.objects.get(id=class_id).model_class()
        return JsonResponse({'success': False}, status=400)


## Trader Sales contract ##
class TraderSalesValidateAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            # Check if contract form is valid
            contract_form = TraderSalesContractForm(data)
            if not contract_form.is_valid():
                return JsonResponse({'success': False}, status=200)
            # Check the validity of product formset
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            # If shipping method is receipt, salessenderform validation should be checked
            if contract_form.cleaned_data.get('shipping_method') == 'R':
                product_sender = {
                    'sender_id': data.get('product_sender_id'),
                    'expected_arrival_date': data.get('product_sender_expected_arrival_date')
                }
                document_sender = {
                    'sender_id': data.get('document_sender_id'),
                    'expected_arrival_date': data.get('document_sender_expected_arrival_date')
                }
                product_sender_form = TraderSalesSenderForm(product_sender)
                document_sender_form = TraderSalesSenderForm(document_sender)
                if product_sender_form.is_valid() and document_sender_form.is_valid():
                    pass
                else:
                    return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)


class TraderSalesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/trader_sales.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        contract_form = TraderSalesContractForm(self.request.POST)
        if contract_form.is_valid():
            contract = contract_form.save()
            
        product_formset = ProductFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'TraderSalesContract'},
            prefix='product'
        )
        for form in product_formset.forms:
            if form.is_valid():
                form.save()

        document_formset = DocumentFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'TraderSalesContract'},
            prefix='document'
        )
        for form in document_formset.forms:
            if form.is_valid():
                form.save()
        
        shipping_method = contract_form.cleaned_data.get('shipping_method')
        if shipping_method == 'R':
            product_sender = {
                'sender_id': self.request.POST.get('product_sender_id'),
                'expected_arrival_date': self.request.POST.get('product_sender_expected_arrival_date')
            }
            product_sender_form = TraderSalesSenderForm(product_sender, type='P', contract_id=contract.id)
            if product_sender_form.is_valid():
                product_sender_form.save()
            document_sender = {
                'sender_id': self.request.POST.get('document_sender_id'),
                'expected_arrival_date': self.request.POST.get('document_sender_expected_arrival_date')
            }
            document_sender_form = TraderSalesSenderForm(document_sender, type='D', contract_id=contract.id)
            if document_sender_form.is_valid():
                document_sender_form.save()
        # return render(request, self.template_name, self.get_context_data(**kwargs))
        return redirect('listing:sales-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_id'] = generate_contract_id()
        context['documents'] = Document.objects.all().values('id', 'name')
        context['senders'] = Sender.objects.all().values('id', 'name')
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        return context


class TraderSalesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        contract_form = TraderSalesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        created_at = contract_form.data.get('created_at', '')
        updated_at = contract_form.data.get('updated_at', '')
        customer_id = contract_form.data.get('customer_id', None)
        person_in_charge = contract_form.data.get('person_in_charge', '')
        sub_total = 0
        company = frigana = postal_code = address = tel = fax = None
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            company = customer.name
            frigana = customer.frigana
            postal_code = customer.postal_code
            address = customer.address
            tel = customer.tel
            fax = customer.fax

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="trader_sales_contract_{}.csv"'.format(contract_id)
        writer = csv.writer(response, encoding='utf-8-sig')

        rows = [
            ['','', _('Contract and invoice')],
            ['No. {}'.format(contract_id), '', '', '', '', '', _('Created date'), created_at],
            ['', '', '', '', '', '', _('Updated date'), updated_at],
            [_('Company'), company, '', _('Frigana'), frigana],
            [_('Postal code'), postal_code],
            [_('Address'), address, '', '', '', '', 'P-SENSOR ' + _('Member ID'), P_SENSOR_NUMBER],
            [_(_('TEL')), tel, '', _(_('FAX')), fax, '', _('Person in charge'), person_in_charge],
            [],
            [_('Product')],
            [_('Model name'), _('Product type'), _('Quantity'), _('Price'), _('Amount')],
        ]
        writer.writerows(rows)

        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
        if num_of_products:
            product_rows = []
            for form in product_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                sub_total += amount
                product_rows.append([product_name, dict(PRODUCT_TYPE_CHOICES)[type], quantity, price, amount])
            writer.writerows(product_rows)
        
        rows = [
            [],
            [_('Other')],
            [_('Document'), _('Quantity'), _('Price'), _('Amount')]
        ]
        writer.writerows(rows)

        document_formset = DocumentFormSet(
            self.request.POST,
            prefix='document'
        )
        num_of_documents = document_formset.total_form_count()
        if num_of_documents:
            document_rows = []
            for form in document_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                sub_total += amount
                document_rows.append([document_name, quantity, price, amount])
            writer.writerows(document_rows)
        
        shipping_method = contract_form.data.get('shipping_method')
        shipping_date = contract_form.data.get('shipping_date')
        payment_method = contract_form.data.get('payment_method')
        payment_due_date = contract_form.data.get('payment_due_date')
        insurance_fee = contract_form.data.get('insurance_fee', 0)
        remarks = contract_form.data.get('remarks', None)
        tax = int(sub_total * 0.1)
        total = sub_total + tax + int(insurance_fee)

        rows = [
            [],
            [_('Delivery date'), shipping_date, '', _('Sum'), sub_total],
            [_('Remarks'), remarks, '', _('Consumption tax') + '(10%)', tax],
            ['', '', '', _('Insurance fee') + '(' + _('No tax') + ')', insurance_fee],
            ['', '', '', _('Total amount'), total],
            [_('Shipping method'), dict(SHIPPING_METHOD_CHOICES)[shipping_method], '', _('Billing amount'), total],
            [_('Payment method'), dict(PAYMENT_METHOD_CHOICES)[payment_method], '', _('Payment due date'), payment_due_date],
            []
        ]
        writer.writerows(rows)

        if shipping_method == 'R':
            product_sender_id = self.request.POST.get('product_sender_id', None)
            product_sender_company = product_sender_address = product_sender_tel = product_sender_fax = None
            product_sender_expected_arrival_date = self.request.POST.get('product_sender_expected_arrival_date', None)
            if product_sender_id:
                product_sender = Sender.objects.get(id=product_sender_id)
                product_sender_company = product_sender.name
                product_sender_address = product_sender.address
                product_sender_tel = product_sender.tel
                product_sender_fax = product_sender.fax
            document_sender_company = document_sender_address = document_sender_tel = document_sender_fax = None
            document_sender_id = self.request.POST.get('document_sender_id', None)
            document_sender_expected_arrival_date = self.request.POST.get('document_sender_expected_arrival_date', None)
            if document_sender_id:
                document_sender = Sender.objects.get(id=document_sender_id)
                document_sender_company = document_sender.name
                document_sender_address = document_sender.address
                document_sender_tel = document_sender.tel
                document_sender_fax = document_sender.fax
            rows = [
                [_('Product sender'), '', '', _('Document sender')],
                [_('Company'), product_sender_company, '', _('Company'), document_sender_company],
                [_('Address'), product_sender_address, '', _('Address'), document_sender_address],
                [_('TEL'), product_sender_tel, '', _('TEL'), document_sender_tel],
                [_('FAX'), product_sender_fax, '', _('FAX'), document_sender_fax],
                [_('Expected arrival date'), product_sender_expected_arrival_date, '', _('Expected arrival date'), document_sender_expected_arrival_date]
            ]
            writer.writerows(rows)
        return response
## End of trader sales contract ##


## Trader purchases contract ##
class TraderPurchasesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/trader_purchases.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        contract_form = TraderPurchasesContractForm(self.request.POST)
        if contract_form.is_valid():
            contract = contract_form.save()
            
        product_formset = ProductFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'TraderPurchasesContract'},
            prefix='product'
        )
        for form in product_formset.forms:
            if form.is_valid():
                form.save()

        document_formset = DocumentFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'TraderPurchasesContract'},
            prefix='document'
        )
        for form in document_formset.forms:
            if form.is_valid():
                form.save()
        
        product_sender = {
            'sender_id': self.request.POST.get('product_sender_id'),
            'desired_arrival_date': self.request.POST.get('product_sender_desired_arrival_date'),
            'shipping_company': self.request.POST.get('product_sender_shipping_company'),
            'remarks': self.request.POST.get('product_sender_remarks')
        }
        product_sender_form = TraderPurchasesSenderForm(product_sender, type='P', contract_id=contract.id)
        if product_sender_form.is_valid():
            product_sender_form.save()
        document_sender = {
            'sender_id': self.request.POST.get('document_sender_id'),
            'desired_arrival_date': self.request.POST.get('document_sender_desired_arrival_date'),
            'shipping_company': self.request.POST.get('document_sender_shipping_company'),
            'remarks': self.request.POST.get('document_sender_remarks')
        }
        document_sender_form = TraderPurchasesSenderForm(document_sender, type='D', contract_id=contract.id)
        if document_sender_form.is_valid():
            document_sender_form.save()
        # return render(request, self.template_name, self.get_context_data(**kwargs))
        return redirect('listing:purchases-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_id'] = generate_contract_id('02')
        context['documents'] = Document.objects.all().values('id', 'name')
        context['senders'] = Sender.objects.all().values('id', 'name')
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        return context


class TraderPurchasesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        contract_form = TraderPurchasesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        customer_id = contract_form.data.get('customer_id', None)
        created_at = contract_form.data.get('created_at', '')
        updated_at = contract_form.data.get('updated_at', '')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        sub_total = 0
        company = frigana = postal_code = address = tel = fax = None
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            company = customer.name
            frigana = customer.frigana
            postal_code = customer.postal_code
            address = customer.address
            tel = customer.tel
            fax = customer.fax

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="trader_sales_contract_{}.csv"'.format(contract_id)
        writer = csv.writer(response, encoding='utf-8-sig')

        rows = [
            ['','', _('Contract and invoice')],
            ['No. {}'.format(contract_id), '', '', '', '', '', _('Created date'), created_at],
            ['', '', '', '', '', '', _('Updated date'), updated_at],
            [_('Company'), company, '', _('Frigana'), frigana],
            [_('Postal code'), postal_code],
            [_('Address'), address, '', '', '', '', 'P-SENSOR ' + _('Member ID'), P_SENSOR_NUMBER],
            [_('TEL'), tel, '', _('FAX'), fax, '', _('Person in charge'), person_in_charge],
            [],
            [_('Product')],
            [_('Model name'), _('Product type'), _('Quantity'), _('Price'), _('Amount')],
        ]
        writer.writerows(rows)

        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
        if num_of_products:
            product_rows = []
            for form in product_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                sub_total += amount
                product_rows.append([product_name, dict(PRODUCT_TYPE_CHOICES)[type], quantity, price, amount])
            writer.writerows(product_rows)
        
        rows = [
            [],
            [_('Other')],
            [_('Document'), _('Quantity'), _('Price'), _('Amount')]
        ]
        writer.writerows(rows)

        document_formset = DocumentFormSet(
            self.request.POST,
            prefix='document'
        )
        num_of_documents = document_formset.total_form_count()
        if num_of_documents:
            document_rows = []
            for form in document_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                sub_total += amount
                document_rows.append([document_name, quantity, price, amount])
            writer.writerows(document_rows)
        
        removal_date = contract_form.data.get('removal_date')
        shipping_date = contract_form.data.get('shipping_date')
        frame_color = contract_form.data.get('frame_color')
        receipt = contract_form.data.get('receipt')
        remarks = contract_form.data.get('remarks', None)
        insurance_fee = contract_form.data.get('insurance_fee', 0)
        tax = int(sub_total * 0.1)
        total = sub_total + tax + int(insurance_fee)

        rows = [
            [],
            ['', '', '', '', '', '', _('Sum'), sub_total],
            [_('Removal date'), removal_date, '', _('Frame color'), frame_color, '', _('Consumption tax') + '(10%)', tax],
            [_('Date of shipment'), shipping_date, '', _('Receipt'), receipt, '', _('Insurance fee') + '(' + _('No tax') + ')', insurance_fee],
            [_('Remarks'), remarks, '', '', '', '', _('Total amount'), total],
            []
        ]
        writer.writerows(rows)

        product_sender_company = product_sender_address = product_sender_tel = None
        product_sender_id = self.request.POST.get('product_sender_id', None)
        product_sender_shipping_company = self.request.POST.get('product_sender_shipping_company', None)
        product_sender_remarks = self.request.POST.get('product_sender_remarks', None)
        product_sender_desired_arrival_date = self.request.POST.get('product_sender_desired_arrival_date', None)
        if product_sender_id:
            product_sender = Sender.objects.get(id=product_sender_id)
            product_sender_company = product_sender.name
            product_sender_address = product_sender.address
            product_sender_tel = product_sender.tel
        document_sender_company = document_sender_address = document_sender_tel = None
        document_sender_id = self.request.POST.get('document_sender_id', None)
        document_sender_shipping_company = self.request.POST.get('document_sender_shipping_company', None)
        document_sender_remarks = self.request.POST.get('document_sender_remarks', None)
        document_sender_desired_arrival_date = self.request.POST.get('document_sender_desired_arrival_date', None)
        if document_sender_id:
            document_sender = Sender.objects.get(id=document_sender_id)
            document_sender_company = document_sender.name
            document_sender_address = document_sender.address
            document_sender_tel = document_sender.tel
        rows = [
            [_('Product sender'), '', '', _('Document sender')],
            [_('Company'), product_sender_company, '', _('Company'), document_sender_company],
            [_('Address'), product_sender_address, '', _('Address'), document_sender_address],
            [_('TEL'), product_sender_tel, '', _('TEL'), document_sender_tel],
            [_('Desired arrival date'), product_sender_desired_arrival_date, '', _('Desired arrival date'), document_sender_desired_arrival_date],
            [_('Shipping company'), product_sender_shipping_company, '', _('Shipping company'), document_sender_shipping_company],
            [_('Remarks'), product_sender_remarks, '', _('Remarks'), document_sender_remarks]
        ]
        writer.writerows(rows)

        transfer_deadline = self.request.POST.get('transfer_deadline', None)
        bank_name = self.request.POST.get('bank_name', None)
        account_number = self.request.POST.get('account_number', None)
        branch_name = self.request.POST.get('branch_name', None)
        account_holder = self.request.POST.get('account_holder', None)
        rows = [
            [],
            [_('Transfer deadline'), transfer_deadline, ''],
            [_('Bank name'), bank_name, '', _('Branch name'), branch_name],
            [_('Account number'), account_number, '', _('Account holder'), account_holder]
        ]
        writer.writerows(rows)
        return response


class TraderPurchasesValidateAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            # Check if contract form is valid
            contract_form = TraderPurchasesContractForm(data)
            if not contract_form.is_valid():
                return JsonResponse({'success': False}, status=200)
            # Check the validity of product formset
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            product_sender = {
                'sender_id': data.get('product_sender_id'),
                'desired_arrival_date': data.get('product_sender_desired_arrival_date'),
                'shipping_company': data.get('product_sender_shipping_company'),
                'remarks': data.get('product_sender_remarks')
            }
            document_sender = {
                'sender_id': data.get('document_sender_id'),
                'desired_arrival_date': data.get('document_sender_desired_arrival_date'),
                'shipping_company': data.get('document_sender_shipping_company'),
                'remarks': data.get('document_sender_remarks')
            }
            product_sender_form = TraderPurchasesSenderForm(product_sender)
            document_sender_form = TraderPurchasesSenderForm(document_sender)
            if product_sender_form.is_valid() and document_sender_form.is_valid():
                pass
            else:
                return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)
# End of trader purchases form


## Hall sales contract
class HallSalesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/hall_sales.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        contract_form = HallSalesContractForm(self.request.POST)
        if contract_form.is_valid():
            contract = contract_form.save()
            
        product_formset = ProductFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallSalesContract'},
            prefix='product'
        )
        for form in product_formset.forms:
            if form.is_valid():
                form.save()

        document_formset = DocumentFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallSalesContract'},
            prefix='document'
        )
        for form in document_formset.forms:
            if form.is_valid():
                form.save()
        
        document_fee_formset = DocumentFeeFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallSalesContract'},
            prefix='document_fee'
        )
        for form in document_fee_formset.forms:
            if form.is_valid():
                form.save()
        
        milestone_formset = MilestoneFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallSalesContract'},
            prefix='milestone'
        )
        for form in milestone_formset.forms:
            if form.is_valid():
                if form.cleaned_data.get('date') and form.cleaned_data.get('amount'):
                    form.save()
        
        # return render(request, self.template_name, self.get_context_data(**kwargs))
        return redirect('listing:sales-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_id'] = generate_contract_id('03')
        context['documents'] = Document.objects.all().values('id', 'name')
        document_fee_lambda = lambda df: {'id': df.id, 'name': df.get_type_display()}
        document_fees = [document_fee_lambda(document_fee) for document_fee in DocumentFee.objects.all()]
        context['document_fees'] = document_fees
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        context['documentfeeformset'] = DocumentFeeFormSet(prefix='document_fee')
        context['milestoneformset'] = MilestoneFormSet(prefix='milestone')
        return context


class HallSalesValidateAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            contract_form = HallSalesContractForm(data)
            if not contract_form.is_valid():
                return JsonResponse({'success': False}, status=200)
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_fee_formset = DocumentFeeFormSet(data, prefix='document_fee')
            if not document_fee_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            milestone_formset = MilestoneFormSet(data, prefix='milestone')
            if not milestone_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)


class HallSalesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        contract_form = HallSalesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        customer_id = contract_form.data.get('customer_id', None)
        created_at = contract_form.data.get('created_at', '')
        hall_id = contract_form.data.get('hall_id', None)
        sub_total = 0
        company = address = tel = fax = None
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            company = customer.name
            address = customer.address
            tel = customer.tel
            fax = customer.fax
        hall_name = hall_address = hall_tel = None
        if hall_id:
            hall = Hall.objects.get(id=hall_id)
            hall_name = hall.name
            hall_address = hall.address
            hall_tel = hall.tel

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="hall_sales_contract_{}.csv"'.format(contract_id)
        writer = csv.writer(response, encoding='utf-8-sig')
        rows = [
            ['','', _('Sales contract')],
            ['No. {}'.format(contract_id), '', '', '', _('Created date'), created_at],
            [],
            [_('Buyer') + '(' + _('A') + ')', '', '', _('Seller') + '(' + _('B') + ')'],
            ['', _('Company'), company, '', _('Company'), COMPANY_NAME],
            ['', _('Address'), address, '', _('Address'), ADDRESS],
            ['', _('TEL'), tel, '', _('TEL'), TEL],
            ['', _('FAX'), fax, '', _('FAX'), FAX],
            [],
            [_('Installation location')],
            ['', _('Hall name'), hall_name, '', _('Address'), hall_address],
            ['', _('TEL'), hall_tel],
            [],
            [_('Product')],
            ['', _('Model name'), _('Product type'), _('Quantity'), _('Price'), _('Amount')]
        ]
        writer.writerows(rows)

        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
        if num_of_products:
            product_rows = []
            for form in product_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                sub_total += amount
                product_rows.append([None, product_name, dict(PRODUCT_TYPE_CHOICES)[type], quantity, price, amount])
            writer.writerows(product_rows)
        
        rows = [
            [],
            [_('Other')],
            ['', _('Document'), _('Quantity'), _('Price'), _('Amount')]
        ]
        writer.writerows(rows)
        document_formset = DocumentFormSet(
            self.request.POST,
            prefix='document'
        )
        num_of_documents = document_formset.total_form_count()
        if num_of_documents:
            document_rows = []
            for form in document_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                sub_total += amount
                document_rows.append([None, document_name, quantity, price, amount])
            writer.writerows(document_rows)
        
        rows = [
            [],
            [_('Document fee')],
            ['', _('Product type'), _('Model count'), _('Unit count'), _('Amount')]
        ]
        writer.writerows(rows)
        document_fee_formset = DocumentFeeFormSet(
            self.request.POST,
            prefix='document_fee'
        )
        num_of_document_fees = document_fee_formset.total_form_count()
        if num_of_document_fees:
            document_fee_rows = []
            for form in document_fee_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                document_fee = DocumentFee.objects.get(id=id)
                type = document_fee.type
                model_count = form.cleaned_data.get('model_count', 0)
                unit_count = form.cleaned_data.get('unit_count', 0)
                model_price = document_fee.model_price
                unit_price = document_fee.unit_price
                amount = model_price * model_count + unit_price * unit_count + document_fee.application_fee
                sub_total += amount
                document_fee_rows.append([None, type, model_count, unit_count, amount])
            writer.writerows(document_fee_rows)

        remarks = contract_form.data.get('remarks', None)
        insurance_fee = contract_form.data.get('insurance_fee', 0)
        fee_included = contract_form.data.get('fee_included', False)
        shipping_date = contract_form.data.get('shipping_date')
        opening_date = contract_form.data.get('opening_date')
        payment_method = contract_form.data.get('payment_method')
        transfer_account = contract_form.data.get('transfer_account')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        confirmor = contract_form.data.get('confirmor')
        tax = int(sub_total * 0.1)
        total = sub_total + tax
        if fee_included:
            total += int(insurance_fee)

        rows = [
            [],
            [_('Remarks'), remarks, '', '', _('Sum'), sub_total],
            ['', '', '', '', _('Consumption tax') + '(10%)', tax],
            ['', '', '', '', _('Insurance fee') + '(' + _('No tax') + ')', insurance_fee],
            ['', '', '', '', _('Total amount'), total],
            []
        ]
        writer.writerows(rows)

        milestone_formset = MilestoneFormSet(
            self.request.POST,
            prefix='milestone'
        )
        rows = []
        idx = 1
        for form in milestone_formset.forms:
            form.is_valid()
            date = form.cleaned_data.get('date', None)
            amount = form.cleaned_data.get('amount', None)
            
            if idx == 1:
                rows.append([_('Shipping date'), shipping_date, _('Payment breakdown'), _(ordinal(idx)), date, amount])
            elif idx == 2:
                rows.append([_('Opening date'), opening_date, '', _(ordinal(idx)), date, amount])
            elif idx == 3:
                rows.append([_('Payment method'), dict(PAYMENT_METHOD_CHOICES)[payment_method], '', _(ordinal(idx)), date, amount])
            elif idx == 4:
                rows.append(['', '', '', _(ordinal(idx)), date, amount])
            else:
                rows.append(['', '', '', _(ordinal(idx)), date, amount])
            idx += 1
        writer.writerows(rows)
        
        rows = [
            [],
            [_('Transfer account'), transfer_account, _('Person in charge'), person_in_charge, _('Confirmor'), confirmor],
        ]
        writer.writerows(rows)
        return response
# End of hall sales contract


# Hall purchases contract
class HallPurchasesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/hall_purchases.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        contract_form = HallPurchasesContractForm(self.request.POST)
        if contract_form.is_valid():
            contract = contract_form.save()
            
        product_formset = ProductFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallPurchasesContract'},
            prefix='product'
        )
        for form in product_formset.forms:
            if form.is_valid():
                form.save()

        document_formset = DocumentFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallPurchasesContract'},
            prefix='document'
        )
        for form in document_formset.forms:
            if form.is_valid():
                form.save()
        
        # return render(request, self.template_name, self.get_context_data(**kwargs))
        return redirect('listing:purchases-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_fee_lambda = lambda df: {'id': df.id, 'name': df.get_type_display()}
        document_fees = [document_fee_lambda(document_fee) for document_fee in DocumentFee.objects.all()]
        context['contract_id'] = generate_contract_id('04')
        context['documents'] = Document.objects.all().values('id', 'name')
        context['document_fees'] = document_fees
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        context['documentfeeformset'] = DocumentFeeFormSet(prefix='document_fee')
        context['milestoneformset'] = MilestoneFormSet(prefix='milestone')
        return context


class HallPurchasesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        contract_form = HallPurchasesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        customer_id = contract_form.data.get('customer_id', None)
        created_at = contract_form.data.get('created_at', '')
        hall_id = contract_form.data.get('hall_id', None)
        sub_total = 0
        company = address = tel = fax = None
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            company = customer.name
            address = customer.address
            tel = customer.tel
            fax = customer.fax
        hall_name = hall_address = hall_tel = None
        if hall_id:
            hall = Hall.objects.get(id=hall_id)
            hall_name = hall.name
            hall_address = hall.address
            hall_tel = hall.tel

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="hall_purchases_contract_{}.csv"'.format(contract_id)
        writer = csv.writer(response, encoding='utf-8-sig')
        rows = [
            ['', '', _('Sales contract')],
            ['No. {}'.format(contract_id), '', '', '', _('Created date'), created_at],
            [],
            [_('Buyer') + '(' + _('A') + ')', '', '', _('Seller') + '(' + _('B') + ')'],
            ['', _('Company'), company, '', _('Company'), COMPANY_NAME],
            ['', _('Address'), address, '', _('Address'), ADDRESS],
            ['', _('TEL'), tel, '', _('TEL'), TEL],
            ['', _('FAX'), fax, '', _('FAX'), FAX],
            [],
            [_('Installation location')],
            ['', _('Hall name'), hall_name, '', _('Address'), hall_address],
            ['', _('TEL'), hall_tel],
            [],
            [_('Product')],
            ['', _('Model name'), _('Product type'), _('Quantity'), _('Price'), _('Amount')]
        ]
        writer.writerows(rows)

        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
        if num_of_products:
            product_rows = []
            for form in product_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                sub_total += amount
                product_rows.append([None, product_name, dict(PRODUCT_TYPE_CHOICES)[type], quantity, price, amount])
            writer.writerows(product_rows)
        
        rows = [
            [],
            [_('Other')],
            ['', _('Document'), _('Quantity'), _('Price'), _('Amount')]
        ]
        writer.writerows(rows)
        document_formset = DocumentFormSet(
            self.request.POST,
            prefix='document'
        )
        num_of_documents = document_formset.total_form_count()
        if num_of_documents:
            document_rows = []
            for form in document_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                sub_total += amount
                document_rows.append([None, document_name, quantity, price, amount])
            writer.writerows(document_rows)
        
        rows = [
            [],
            [_('Document fee')],
            ['', _('Product type'), _('Model count'), _('Unit count'), _('Amount')]
        ]
        writer.writerows(rows)
        document_fee_formset = DocumentFeeFormSet(
            self.request.POST,
            prefix='document_fee'
        )
        num_of_document_fees = document_fee_formset.total_form_count()
        if num_of_document_fees:
            document_fee_rows = []
            for form in document_fee_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('id')
                document_fee = DocumentFee.objects.get(id=id)
                type = document_fee.type
                model_count = form.cleaned_data.get('model_count', 0)
                unit_count = form.cleaned_data.get('unit_count', 0)
                model_price = document_fee.model_price
                unit_price = document_fee.unit_price
                amount = model_price * model_count + unit_price * unit_count + document_fee.application_fee
                sub_total += amount
                document_fee_rows.append([None, type, model_count, unit_count, amount])
            writer.writerows(document_fee_rows)

        remarks = contract_form.data.get('remarks', None)
        insurance_fee = contract_form.data.get('insurance_fee', 0)
        fee_included = contract_form.data.get('fee_included', False)
        shipping_date = contract_form.data.get('shipping_date')
        opening_date = contract_form.data.get('opening_date')
        payment_method = contract_form.data.get('payment_method')
        transfer_account = contract_form.data.get('transfer_account')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        confirmor = contract_form.data.get('confirmor')
        tax = int(sub_total * 0.1)
        total = sub_total + tax
        if fee_included:
            total += int(insurance_fee)

        rows = [
            [],
            [_('Remarks'), remarks, '', '', _('Sum'), sub_total],
            ['', '', '', '', _('Consumption tax') + '(10%)', tax],
            ['', '', '', '', _('Insurance fee') + '(' + _('No tax') + ')', insurance_fee],
            ['', '', '', '', _('Total amount'), total],
            []
        ]
        writer.writerows(rows)

        milestone_formset = MilestoneFormSet(
            self.request.POST,
            prefix='milestone'
        )
        rows = []
        idx = 1
        for form in milestone_formset.forms:
            form.is_valid()
            date = form.cleaned_data.get('date', None)
            amount = form.cleaned_data.get('amount', None)
            
            if idx == 1:
                rows.append([_('Shipping date'), shipping_date, _('Payment breakdown'), _(ordinal(idx)), date, amount])
            elif idx == 2:
                rows.append([_('Opening date'), opening_date, '', _(ordinal(idx)), date, amount])
            elif idx == 3:
                rows.append([_('Payment method'), dict(PAYMENT_METHOD_CHOICES)[payment_method], '', _(ordinal(idx)), date, amount])
            elif idx == 4:
                rows.append(['', '', '', _(ordinal(idx)), date, amount])
            else:
                rows.append(['', '', '', _(ordinal(idx)), date, amount])
            idx += 1
        writer.writerows(rows)
        
        rows = [
            [],
            [_('Transfer account'), transfer_account],
            [_('Person in charge'), person_in_charge, _('Confirmor'), confirmor]
        ]
        writer.writerows(rows)
        return response


class HallPurchasesValidateAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            contract_form = HallPurchasesContractForm(data)
            if not contract_form.is_valid():
                return JsonResponse({'success': False}, status=200)
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_fee_formset = DocumentFeeFormSet(data, prefix='document_fee')
            if not document_fee_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            milestone_formset = MilestoneFormSet(data, prefix='milestone')
            if not milestone_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)
# End of hall purchases contract
