import unicodecsv as csv
from django.views.generic.base import View
from django.http import HttpResponse
from django.utils.translation import gettext as _
from users.views import AdminLoginRequiredMixin
from masterdata.models import (
    Customer, Hall, Sender, Product, Document, DocumentFee,
    PRODUCT_TYPE_CHOICES, SHIPPING_METHOD_CHOICES, PAYMENT_METHOD_CHOICES, TYPE_CHOICES,
    P_SENSOR_NUMBER, COMPANY_NAME, ADDRESS, TEL, FAX,
)
from .forms import (
    TraderSalesContractForm, TraderPurchasesContractForm, HallSalesContractForm, HallPurchasesContractForm,
    TraderSalesProductSenderForm, TraderSalesDocumentSenderForm,
    TraderPurchasesProductSenderForm, TraderPurchasesDocumentSenderForm,
    ProductFormSet, DocumentFormSet, DocumentFeeFormSet, MilestoneFormSet
)
from .utilities import get_shipping_date_label, ordinal, update_csv_history


class TraderSalesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        update_csv_history(user_id, "{} - {}".format(_("Sales contract"), _("Trader sales")))
        contract_form = TraderSalesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        created_at = contract_form.data.get('created_at', '')
        updated_at = contract_form.data.get('updated_at', '')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        customer_id = contract_form.data.get('customer_id', None)
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
                id = form.cleaned_data.get('product_id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
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
                id = form.cleaned_data.get('document_id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                document_rows.append([document_name, quantity, price, amount])
            writer.writerows(document_rows)
        
        shipping_method = contract_form.data.get('shipping_method')
        shipping_date = contract_form.data.get('shipping_date')
        payment_method = contract_form.data.get('payment_method')
        payment_due_date = contract_form.data.get('payment_due_date')
        sub_total = contract_form.data.get('sub_total')
        tax = contract_form.data.get('tax')
        fee = contract_form.data.get('fee')
        total = contract_form.data.get('total')
        remarks = contract_form.data.get('remarks', None)
        shipping_date_label = get_shipping_date_label(shipping_method)

        rows = [
            [],
            [shipping_date_label, shipping_date, '', _('Sum'), sub_total],
            [_('Remarks'), remarks, '', _('Consumption tax') + '(10%)', tax],
            ['', '', '', _('Insurance fee') + '(' + _('No tax') + ')', fee],
            ['', '', '', _('Total amount'), total],
            [_('Shipping method'), dict(SHIPPING_METHOD_CHOICES)[shipping_method], '', _('Billing amount'), total],
            [_('Payment method'), dict(PAYMENT_METHOD_CHOICES)[payment_method], '', _('Payment due date'), payment_due_date],
            []
        ]
        writer.writerows(rows)

        product_sender_form = TraderSalesProductSenderForm(self.request.POST)
        document_sender_form = TraderSalesDocumentSenderForm(self.request.POST)
        product_sender_id = self.request.POST.get('product_sender_id', None)
        product_expected_arrival_date = self.request.POST.get('product_expected_arrival_date', None)
        product_sender_company = None
        if product_sender_id:
            product_sender = Sender.objects.get(id=product_sender_id)
            product_sender_company = product_sender.name
        product_sender_address = product_sender_form.data.get('product_sender_address')
        product_sender_tel = product_sender_form.data.get('product_sender_tel')
        product_sender_fax = product_sender_form.data.get('product_sender_fax')
        
        document_sender_id = self.request.POST.get('document_sender_id', None)
        document_expected_arrival_date = self.request.POST.get('document_expected_arrival_date', None)
        document_sender_company = None
        if document_sender_id:
            document_sender = Sender.objects.get(id=document_sender_id)
            document_sender_company = document_sender.name
        document_sender_address = document_sender_form.data.get('document_sender_address')
        document_sender_tel = document_sender_form.data.get('document_sender_tel')
        document_sender_fax = document_sender_form.data.get('document_sender_fax')
        
        rows = [
            [_('Product sender'), '', '', _('Document sender')],
            [_('Company'), product_sender_company, '', _('Company'), document_sender_company],
            [_('Address'), product_sender_address, '', _('Address'), document_sender_address],
            [_('TEL'), product_sender_tel, '', _('TEL'), document_sender_tel],
            [_('FAX'), product_sender_fax, '', _('FAX'), document_sender_fax],
            [_('Expected arrival date'), product_expected_arrival_date, '', _('Expected arrival date'), document_expected_arrival_date]
        ]
        writer.writerows(rows)
        return response


class TraderPurchasesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        update_csv_history(user_id, "{} - {}".format(_("Sales contract"), _("Trader purchases")))
        contract_form = TraderPurchasesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        created_at = contract_form.data.get('created_at', '')
        updated_at = contract_form.data.get('updated_at', '')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        customer_id = contract_form.data.get('customer_id', None)
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
                id = form.cleaned_data.get('product_id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
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
                id = form.cleaned_data.get('document_id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                document_rows.append([document_name, quantity, price, amount])
            writer.writerows(document_rows)
        
        removal_date = contract_form.data.get('removal_date')
        shipping_date = contract_form.data.get('shipping_date')
        frame_color = contract_form.data.get('frame_color')
        receipt = contract_form.data.get('receipt')
        remarks = contract_form.data.get('remarks', None)
        sub_total = contract_form.data.get('sub_total')
        tax = contract_form.data.get('tax')
        fee = contract_form.data.get('fee')
        total = contract_form.data.get('total')

        rows = [
            [],
            ['', '', '', '', '', '', _('Sum'), sub_total],
            [_('Removal date'), removal_date, '', _('Frame color'), frame_color, '', _('Consumption tax') + '(10%)', tax],
            [_('Date of shipment'), shipping_date, '', _('Receipt'), receipt, '', _('Insurance fee') + '(' + _('No tax') + ')', fee],
            [_('Remarks'), remarks, '', '', '', '', _('Total amount'), total],
            []
        ]
        writer.writerows(rows)

        product_sender_form = TraderPurchasesProductSenderForm(self.request.POST)
        document_sender_form = TraderPurchasesDocumentSenderForm(self.request.POST)
        product_sender_id = self.request.POST.get('product_sender_id', None)
        product_shipping_company = self.request.POST.get('product_shipping_company', None)
        product_sender_remarks = self.request.POST.get('product_sender_remarks', None)
        product_desired_arrival_date = self.request.POST.get('product_desired_arrival_date', None)
        product_sender_company = None
        if product_sender_id:
            product_sender = Sender.objects.get(id=product_sender_id)
            product_sender_company = product_sender.name
        product_sender_address = product_sender_form.data.get('product_sender_address')
        product_sender_tel = product_sender_form.data.get('product_sender_tel')

        document_sender_company = None
        document_sender_id = self.request.POST.get('document_sender_id', None)
        document_shipping_company = self.request.POST.get('document_shipping_company', None)
        document_sender_remarks = self.request.POST.get('document_sender_remarks', None)
        document_desired_arrival_date = self.request.POST.get('document_desired_arrival_date', None)
        if document_sender_id:
            document_sender = Sender.objects.get(id=document_sender_id)
            document_sender_company = document_sender.name
        document_sender_address = document_sender_form.data.get('document_sender_address')
        document_sender_tel = document_sender_form.data.get('document_sender_tel')

        rows = [
            [_('Product sender'), '', '', _('Document sender')],
            [_('Company'), product_sender_company, '', _('Company'), document_sender_company],
            [_('Address'), product_sender_address, '', _('Address'), document_sender_address],
            [_('TEL'), product_sender_tel, '', _('TEL'), document_sender_tel],
            [_('Desired arrival date'), product_desired_arrival_date, '', _('Desired arrival date'), document_desired_arrival_date],
            [_('Shipping company'), product_shipping_company, '', _('Shipping company'), document_shipping_company],
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


class HallSalesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        update_csv_history(user_id, "{} - {}".format(_("Sales contract"), _("Hall sales")))
        contract_form = HallSalesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        customer_id = contract_form.data.get('customer_id', None)
        created_at = contract_form.data.get('created_at', '')
        hall_id = contract_form.data.get('hall_id', None)
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
                id = form.cleaned_data.get('product_id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
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
                id = form.cleaned_data.get('document_id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
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
                id = form.cleaned_data.get('document_fee_id')
                document_fee = DocumentFee.objects.get(id=id)
                type = document_fee.type
                model_count = form.cleaned_data.get('model_count', 0)
                unit_count = form.cleaned_data.get('unit_count', 0)
                model_price = document_fee.model_price
                unit_price = document_fee.unit_price
                amount = model_price * model_count + unit_price * unit_count + document_fee.application_fee
                document_fee_rows.append([None, dict(TYPE_CHOICES)[type], model_count, unit_count, amount])
            writer.writerows(document_fee_rows)

        remarks = contract_form.data.get('remarks', None)
        sub_total = contract_form.data.get('sub_total')
        tax = contract_form.data.get('tax')
        fee = contract_form.data.get('fee')
        total = contract_form.data.get('total')
        shipping_date = contract_form.data.get('shipping_date')
        opening_date = contract_form.data.get('opening_date')
        payment_method = contract_form.data.get('payment_method')
        transfer_account = contract_form.data.get('transfer_account')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        confirmor = contract_form.data.get('confirmor')
        
        rows = [
            [],
            [_('Remarks'), remarks, '', '', _('Sum'), sub_total],
            ['', '', '', '', _('Consumption tax') + '(10%)', tax],
            ['', '', '', '', _('Insurance fee') + '(' + _('No tax') + ')', fee],
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
            elif idx >= 4:
                rows.append(['', '', '', _(ordinal(idx)), date, amount])
            idx += 1
        writer.writerows(rows)
        
        rows = [
            [],
            [_('Transfer account'), transfer_account, _('Person in charge'), person_in_charge, _('Confirmor'), confirmor],
        ]
        writer.writerows(rows)
        return response


class HallPurchasesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        update_csv_history(user_id, "{} - {}".format(_("Sales contract"), _("Hall purchases")))
        contract_form = HallPurchasesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        customer_id = contract_form.data.get('customer_id', None)
        created_at = contract_form.data.get('created_at', '')
        hall_id = contract_form.data.get('hall_id', None)
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
                id = form.cleaned_data.get('product_id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
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
                id = form.cleaned_data.get('document_id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
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
                id = form.cleaned_data.get('document_fee_id')
                document_fee = DocumentFee.objects.get(id=id)
                type = document_fee.type
                model_count = form.cleaned_data.get('model_count', 0)
                unit_count = form.cleaned_data.get('unit_count', 0)
                model_price = document_fee.model_price
                unit_price = document_fee.unit_price
                amount = model_price * model_count + unit_price * unit_count + document_fee.application_fee
                document_fee_rows.append([None, dict(TYPE_CHOICES)[type], model_count, unit_count, amount])
            writer.writerows(document_fee_rows)

        remarks = contract_form.data.get('remarks', None)
        sub_total = contract_form.data.get('sub_total')
        tax = contract_form.data.get('tax')
        fee = contract_form.data.get('fee')
        total = contract_form.data.get('total')
        shipping_date = contract_form.data.get('shipping_date')
        opening_date = contract_form.data.get('opening_date')
        payment_method = contract_form.data.get('payment_method')
        transfer_account = contract_form.data.get('transfer_account')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        confirmor = contract_form.data.get('confirmor')
        memo = contract_form.data.get('memo')

        rows = [
            [],
            [_('Remarks'), remarks, '', '', _('Sum'), sub_total],
            ['', '', '', '', _('Consumption tax') + '(10%)', tax],
            ['', '', '', '', _('Insurance fee') + '(' + _('No tax') + ')', fee],
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
            elif idx >= 4:
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
