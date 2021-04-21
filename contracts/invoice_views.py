import unicodecsv as csv
import xlwt
from django.views.generic.base import View
from django.http import HttpResponse
from django.utils.translation import gettext as _
from users.views import AdminLoginRequiredMixin
from masterdata.models import (
    Customer, Hall, Sender, Product, Document, DocumentFee,
    PRODUCT_TYPE_CHOICES, SHIPPING_METHOD_CHOICES, PAYMENT_METHOD_CHOICES, TYPE_CHOICES,
    P_SENSOR_NUMBER, COMPANY_NAME, ADDRESS, TEL, FAX, POSTAL_CODE, CEO
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

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="trader_sales_contract_{}.xls"'.format(contract_id)
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("{} - {}".format(_('Sales contract'), _('Trader sales')), cell_overwrite_ok=True)

        header_height = int(256 * 3)
        cell_width = 256 * 12
        cell_height = int(256 * 1.5)
        font_size = 20 * 8 # pt
        
        common_style = xlwt.easyxf('font: height 160; align: vert center, horiz left, wrap on;')
        center_style = xlwt.easyxf('font: height 160; align: vert center, horiz center, wrap on;')
        table_center_style = xlwt.easyxf('font: height 160; align: vert center, horiz center, wrap on;\
                                    borders: top_color black, bottom_color black, right_color black, left_color black,\
                                    left thin, right thin, top thin, bottom thin;')
        table_left_style = xlwt.easyxf('font: height 160; align: vert center, horiz left, wrap on;\
                                    borders: top_color black, bottom_color black, right_color black, left_color black,\
                                    left thin, right thin, top thin, bottom thin;')
        title_style = xlwt.easyxf('font: bold on, height 280, color black;\
                                    align: vert center, horiz center, wrap on;')
        sub_title_style = xlwt.easyxf('font: bold on, height 200, color black;\
                                    align: vert center, horiz center, wrap on;')
        font_large_style = xlwt.easyfont('height 200, bold on')

        for i in range(8):
            ws.col(i).width = cell_width

        for i in range(1, 45):
            ws.row(i).height_mismatch = True
            ws.row(i).height = cell_height

        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write_merge(0, 0, 0, 7, _('Contract and invoice'), title_style)
        ws.write_merge(1, 1, 0, 1, 'No.  {}'.format(contract_id), common_style)
        ws.write(1, 6, _('Created date'), common_style)
        ws.write(1, 7, created_at, common_style)
        ws.write(2, 6, _('Created date'), common_style)
        ws.write(2, 7, updated_at, common_style)

        ws.write(4, 0, _('Company'), common_style)
        ws.write_merge(4, 4, 1, 3, company, common_style)
        ws.write(4, 4, _('Frigana'), common_style)
        ws.write_merge(4, 4, 5, 7, frigana, common_style)

        ws.write(5, 0, _('Postal code'), common_style)
        ws.write_merge(5, 5, 1, 2, postal_code, common_style)

        ws.write(6, 0, _('Address'), common_style)
        ws.write_merge(6, 6, 1, 3, address, common_style)

        ws.write_merge(6, 6, 4, 5, 'P-SENSOR {}'.format(_('Member ID')), center_style)
        ws.write_merge(6, 6, 6, 7, P_SENSOR_NUMBER, common_style)

        ws.write(7, 0, _('TEL'), common_style)
        ws.write(7, 1, tel, common_style)
        ws.write(7, 3, _('FAX'), common_style)
        ws.write(7, 4, fax, common_style)
        ws.write(7, 6, _('Person in charge'), common_style)
        ws.write(7, 7, person_in_charge, common_style)

        # Product Table
        ws.write_merge(9, 9, 0, 3, _('Model name'), table_center_style)
        ws.write(9, 4, _('Product type'), table_center_style)
        ws.write(9, 5, _('Quantity'), table_center_style)
        ws.write(9, 6, _('Price'), table_center_style)
        ws.write(9, 7, _('Amount'), table_center_style)

        row_no = 10
        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
        lazy_dict = dict(PRODUCT_TYPE_CHOICES)
        if num_of_products:
            for form in product_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('product_id')
                product_name = Product.objects.get(id=id).name
                type = form.cleaned_data.get('type')
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price

                ws.write_merge(row_no, row_no, 0, 3, product_name, table_center_style)
                ws.write(row_no, 4, str(lazy_dict[type]), table_center_style)
                ws.write(row_no, 5, quantity, table_center_style)
                ws.write(row_no, 6, price, table_center_style)
                ws.write(row_no, 7, amount, table_center_style)
                ws.row(row_no).height = int(cell_height * 1.3)
                row_no += 1

        # Document Table
        row_no += 1
        ws.write_merge(row_no, row_no, 0, 1, _('Document'), table_center_style)
        ws.write_merge(row_no, row_no, 2, 3, _('Quantity'), table_center_style)
        ws.write_merge(row_no, row_no, 4, 5, _('Price'), table_center_style)
        ws.write_merge(row_no, row_no, 6, 7, _('Amount'), table_center_style)
        row_no += 1

        document_formset = DocumentFormSet(
            self.request.POST,
            prefix='document'
        )
        num_of_documents = document_formset.total_form_count()
        if num_of_documents:
            for form in document_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('document_id')
                document_name = Document.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price
                ws.write_merge(row_no, row_no, 0, 1, document_name, table_center_style)
                ws.write_merge(row_no, row_no, 2, 3, quantity, table_center_style)
                ws.write_merge(row_no, row_no, 4, 5, price, table_center_style)
                ws.write_merge(row_no, row_no, 6, 7, amount, table_center_style)
                row_no += 1
        
        row_no += 1
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

        ws.write(row_no, 0, shipping_date_label, common_style)
        ws.write(row_no, 1, shipping_date, common_style)
        ws.write_merge(row_no, row_no, 5, 6, _('Sum'), table_left_style)
        ws.write(row_no, 7, sub_total, table_left_style)
        row_no += 1

        ws.write_merge(row_no, row_no + 2, 0, 0, _('Remarks'), common_style)
        ws.write_merge(row_no, row_no + 2, 1, 3, remarks, common_style)
        ws.write_merge(row_no, row_no, 5, 6, _('Consumption tax') + '(10%)', table_left_style)
        ws.write(row_no, 7, tax, table_left_style)
        row_no += 1
        ws.write_merge(row_no, row_no, 5, 6, _('Insurance fee') + '(' + _('No tax') + ')', table_left_style)
        ws.write(row_no, 7, fee, table_left_style)
        row_no += 1
        ws.write_merge(row_no, row_no, 5, 6, _('Total amount'), table_left_style)
        ws.write(row_no, 7, total, table_left_style)
        row_no += 1

        row_no += 1
        ws.write(row_no, 0, _('Shipping method'), common_style)
        ws.write_merge(row_no, row_no, 1, 2, str(dict(SHIPPING_METHOD_CHOICES)[shipping_method]), common_style)
        ws.write_merge(row_no, row_no, 4, 5, _('Billing amount'), common_style)
        ws.write_merge(row_no, row_no, 6, 7, total, common_style)
        row_no += 1
        ws.write(row_no, 0, _('Payment method'), common_style)
        ws.write_merge(row_no, row_no, 1, 2, str(dict(PAYMENT_METHOD_CHOICES)[payment_method]), common_style)
        ws.write_merge(row_no, row_no, 4, 5, _('Payment due date'), common_style)
        ws.write_merge(row_no, row_no, 6, 7, payment_due_date, common_style)
        row_no += 1

        row_no += 1
        content = "※{}\n".format(_("The contract will be effective when both seller and buyer sign and seal."))
        content += "※{}\n".format(_("As a general rule, the contract cannot be canceled once signed."))
        content += "※{}\n".format(_("3 days warranty after delivery will be provided just in case of defects or malfunctions in the products."))
        content += "※{}\n".format(_("The seller will keep the ownership of the products until the buyer makes the full payment."))
        content += "※{}\n".format(_("The Ownership of the products shall be transferred to the buyer when product delivery is completed and full payment is made."))
        content += "※{}\n".format(_("In the following cases, the seller may, without any procedure, request the immediate payment of the remaining balance, or cancel the contract and take back the products."))
        content += '    1) {}\n'.format(_("When the buyer fail to make the payment even once."))
        content += '    2) {}'.format(_("When the products were forfeited or disposed temporarily, or the request for arrangement, reconciliation, damage etc is received."))
        ws.write_merge(row_no, row_no + 6, 0, 7, content, common_style)
        row_no += 7

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
        
        row_no += 1
        ws.write_merge(row_no, row_no, 0, 3, _('Product sender'), sub_title_style)
        ws.write_merge(row_no, row_no, 4, 7, _('Document sender'), sub_title_style)
        row_no += 1
        ws.write(row_no, 0, _('Company'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_sender_company, common_style)
        ws.write(row_no, 4, _('Company'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_sender_company, common_style)
        row_no += 1
        ws.write(row_no, 0, _('Address'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_sender_address, common_style)
        ws.write(row_no, 4, _('Address'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_sender_address, common_style)
        ws.row(row_no).height = int(cell_height * 1.3)
        row_no += 1
        ws.write(row_no, 0, _('TEL'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_sender_tel, common_style)
        ws.write(row_no, 4, _('TEL'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_sender_tel, common_style)
        row_no += 1
        ws.write(row_no, 0, _('FAX'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_sender_fax, common_style)
        ws.write(row_no, 4, _('FAX'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_sender_fax, common_style)
        row_no += 1
        ws.write(row_no, 0, _('Expected arrival date'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_expected_arrival_date, common_style)
        ws.write(row_no, 4, _('Expected arrival date'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_expected_arrival_date, common_style)
        row_no += 1

        row_no += 1
        ws.write_merge(row_no, row_no, 0, 3, _('Buyer seal'), sub_title_style)
        ws.write_merge(row_no, row_no, 4, 7, _('Seller seal'), sub_title_style)
        row_no += 1
        seller_seal_pre = "    〒"
        seller_seal_pre += postal_code if postal_code else ""
        seller_seal_pre += " {}\n".format(address) if address else "\n"
        seller_seal_company = "   {}\n".format(customer.name) if customer_id else "    \n"
        seller_seal_post = "    {}: \n".format(_('CEO'))
        seller_seal_post += "    TEL: "
        seller_seal_post += tel if tel else "               "
        seller_seal_post += "  FAX: "
        seller_seal_post += fax if fax else ""
        seller_seal = (seller_seal_pre, (seller_seal_company, font_large_style), seller_seal_post)

        buyer_seal_pre = "    〒{} {}\n".format(POSTAL_CODE, ADDRESS)
        buyer_seal_company = "   {}\n".format(COMPANY_NAME)
        buyer_seal_post = "    {}: {}\n".format(_('CEO'), CEO)
        buyer_seal_post += "    TEL: {} FAX: {}".format(TEL, FAX)
        buyer_seal = (buyer_seal_pre, (buyer_seal_company, font_large_style), buyer_seal_post)
        ws.write_merge(row_no, row_no + 3, 0, 3, "", common_style)
        ws.row(row_no).set_cell_rich_text(0, seller_seal, common_style)
        ws.write_merge(row_no, row_no + 3, 4, 7, "", common_style)
        ws.row(row_no).set_cell_rich_text(4, buyer_seal, common_style)
        
        wb.save(response)
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
