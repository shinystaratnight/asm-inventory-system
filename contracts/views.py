import unicodecsv as csv
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.views.generic.base import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from users.views import AdminLoginRequiredMixin
from masterdata.models import Document
from .models import *
from .forms import *
from .utilities import *


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
            product_sender_form = SalesSenderForm(product_sender, type='P', contract_id=contract.id)
            if product_sender_form.is_valid():
                product_sender_form.save()
            document_sender = {
                'sender_id': self.request.POST.get('document_sender_id'),
                'expected_arrival_date': self.request.POST.get('document_sender_expected_arrival_date')
            }
            document_sender_form = SalesSenderForm(document_sender, type='D', contract_id=contract.id)
            if document_sender_form.is_valid():
                document_sender_form.save()
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
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
        p_sensor_number = '8240-2413-3628'
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
            ['','', '売買契約 兼 請求書'],
            ['No. {}'.format(contract_id), '', '', '', '', '', '契約日', created_at],
            ['', '', '', '', '', '', '更新日', updated_at],
            ['会社名', company, '', 'フリガナ', frigana],
            ['郵便番号', postal_code],
            ['住所', address, '', '', '', '', 'P-SENSOR 会員番号', p_sensor_number],
            ['TEL', tel, '', 'FAX', fax, '', '担当名', person_in_charge],
            [],
            ['商品名'],
            ['機種名', '中分類', '数量', '単価', '金額'],
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
                product_rows.append([product_name, type, quantity, price, amount])
            writer.writerows(product_rows)
        
        rows = [
            [],
            ['商品名そのほか'],
            ['書類', '数量', '単価', '金額']
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
            ['機械発送日', shipping_date, '', '小計', sub_total],
            ['備考', remarks, '', '消費税 (10%)', tax],
            ['', '', '', '保険代 (非課税)', insurance_fee],
            ['', '', '', '合計', total],
            ['運送方法', shipping_method, '', '御請求金額', total],
            ['お支払方法', payment_method, '', '支払期限', payment_due_date],
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
                ['商品発送先', '', '', '書類発送先'],
                ['会社名', product_sender_company, '', '会社名', document_sender_company],
                ['住所', product_sender_address, '', '住所', document_sender_address],
                ['TEL', product_sender_tel, '', 'TEL', document_sender_tel],
                ['FAX', product_sender_fax, '', 'FAX', document_sender_fax],
                ['到着予定日', product_sender_expected_arrival_date, '', '到着予定日', document_sender_expected_arrival_date]
            ]
            writer.writerows(rows)
   
        return response


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
                product_sender_form = SalesSenderForm(product_sender)
                document_sender_form = SalesSenderForm(document_sender)
                if product_sender_form.is_valid() and document_sender_form.is_valid():
                    pass
                else:
                    return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)


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
        product_sender_form = PurchasesSenderForm(product_sender, type='P', contract_id=contract.id)
        if product_sender_form.is_valid():
            product_sender_form.save()
        document_sender = {
            'sender_id': self.request.POST.get('document_sender_id'),
            'desired_arrival_date': self.request.POST.get('document_sender_desired_arrival_date'),
            'shipping_company': self.request.POST.get('document_sender_shipping_company'),
            'remarks': self.request.POST.get('document_sender_remarks')
        }
        document_sender_form = PurchasesSenderForm(document_sender, type='D', contract_id=contract.id)
        if document_sender_form.is_valid():
            document_sender_form.save()
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
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
        p_sensor_number = '8240-2413-3628'
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
            ['','', '売買契約 兼 請求書'],
            ['No. {}'.format(contract_id), '', '', '', '', '', '契約日', created_at],
            ['', '', '', '', '', '', '更新日', updated_at],
            ['会社名', company, '', 'フリガナ', frigana],
            ['郵便番号', postal_code],
            ['住所', address, '', '', '', '', 'P-SENSOR 会員番号', p_sensor_number],
            ['TEL', tel, '', 'FAX', fax, '', '担当名', person_in_charge],
            [],
            ['商品名'],
            ['機種名', '中分類', '数量', '単価', '金額'],
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
                product_rows.append([product_name, type, quantity, price, amount])
            writer.writerows(product_rows)
        
        rows = [
            [],
            ['商品名そのほか'],
            ['書類', '数量', '単価', '金額']
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
            ['', '', '', '', '', '', '小計', sub_total],
            ['撤去日', removal_date, '', '枠色', frame_color, '', '消費税 (10%)', tax],
            ['発送日', shipping_date, '', '引取', receipt, '', '保険代 (非課税)', insurance_fee],
            ['備考', remarks, '', '', '', '', '合計', total],
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
            ['商品発送先', '', '', '書類発送先'],
            ['会社名', product_sender_company, '', '会社名', document_sender_company],
            ['住所', product_sender_address, '', '住所', document_sender_address],
            ['TEL', product_sender_tel, '', 'TEL', document_sender_tel],
            ['到着希望日', product_sender_desired_arrival_date, '', '到着希望日', document_sender_desired_arrival_date],
            ['運送会社', product_sender_shipping_company, '', '運送会社', document_sender_shipping_company],
            ['備考', product_sender_remarks, '', '備考', document_sender_remarks]
        ]
        writer.writerows(rows)

        transfer_deadline = self.request.POST.get('transfer_deadline', None)
        bank_name = self.request.POST.get('bank_name', None)
        account_number = self.request.POST.get('account_number', None)
        branch_name = self.request.POST.get('branch_name', None)
        account_holder = self.request.POST.get('account_holder', None)
        rows = [
            [],
            ['振込期限日', transfer_deadline, ''],
            ['銀行名', bank_name, '', '支店名', branch_name],
            ['口座番号', account_number, '', '口座名義', account_holder]
        ]
        writer.writerows(rows)
   
        return response


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
        
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_id'] = generate_contract_id()
        context['documents'] = Document.objects.all().values('id', 'name')
        documentfee = lambda df: {'id': df.id, 'name': df.get_type_display()}
        documentfees = [documentfee(document) for document in DocumentFee.objects.all()]
        context['documentfees'] = documentfees
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        context['documentfeeformset'] = DocumentFormSet(prefix='documentfee')
        MilestoneFormSet = formset_factory(MilestoneForm, formset=MilestoneValidationFormSet, extra=5)
        context['milestoneformset'] = MilestoneFormSet(prefix='milestone')
        return context


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
        
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_id'] = generate_contract_id()
        context['documents'] = Document.objects.all().values('id', 'name')
        documentfee = lambda df: {'id': df.id, 'name': df.get_type_display()}
        documentfees = [documentfee(document) for document in DocumentFee.objects.all()]
        context['documentfees'] = documentfees
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        context['documentfeeformset'] = DocumentFormSet(prefix='documentfee')
        MilestoneFormSet = formset_factory(MilestoneForm, formset=MilestoneValidationFormSet, extra=5)
        context['milestoneformset'] = MilestoneFormSet(prefix='milestone')
        return context


class HallSalesValidateAjaxView(AdminLoginRequiredMixin, View):
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
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)
