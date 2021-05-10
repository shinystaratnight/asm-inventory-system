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
from .utilities import get_shipping_date_label, ordinal, log_export_operation

header_height = int(256 * 3)
cell_width = 256 * 12
cell_height = int(256 * 1.5)
address_cell_height = int(cell_height * 1.3)
font_size = 20 * 8 # pt

common_style = xlwt.easyxf('font: height 160; align: vert center, horiz left, wrap on;')
center_style = xlwt.easyxf('font: height 160; align: vert center, horiz center, wrap on;')
number_style = xlwt.easyxf('font: height 160; align: vert center, horiz left, wrap on;\
                            borders: top_color black, bottom_color black, right_color black, left_color black,\
                            left thin, right thin, top thin, bottom thin;', num_format_str='#,##0')
table_center_style = xlwt.easyxf('font: height 160; align: vert center, horiz center, wrap on;\
                            borders: top_color black, bottom_color black, right_color black, left_color black,\
                            left thin, right thin, top thin, bottom thin;')
table_left_style = xlwt.easyxf('font: height 160; align: vert center, horiz left, wrap on;\
                            borders: top_color black, bottom_color black, right_color black, left_color black,\
                            left thin, right thin, top thin, bottom thin;')
table_date_style = xlwt.easyxf('font: height 160; align: vert center, horiz left, wrap on;\
                            borders: top_color black, bottom_color black, right_color black, left_color black,\
                            left thin, right thin, top thin, bottom thin;')
title_style = xlwt.easyxf('font: bold on, height 280, color black;\
                            align: vert center, horiz center, wrap on;')
sub_title_style = xlwt.easyxf('font: bold on, height 200, color black;\
                            align: vert center, horiz center, wrap on;')
sub_title_left_style = xlwt.easyxf('font: bold on, height 200, color black;\
                            align: vert center, horiz left, wrap on;')
font_large_style = xlwt.easyfont('height 200, bold on')


top_padding_height = int(256 * 0.4)
cell_width_list = [ 256 *  11, 256 * 10, int(256 * 13.5), int(256 * 2.5), 
                    int(256 * 5.5), int(256 * 8.5), 256 * 11, int(256 * 7.5),
                    int(256 * 14.5), int(256 * 9.5), int(256 * 8.5)]
cell_height = int(20 * 15)

header_height = int(20 * 21)
space_height = int(20 * 5.25)
company_height = int(20 * 23.25)
height_18 = int(20 * 18)
height_16 = int(20 * 16)
height_16_5 = int(20 * 16.5)
height_15 = 20 * 15
height_13_5 = int(20 * 13.5)
height_12 = 20 * 12



border_bottom = xlwt.easyxf('borders: bottom_color black, bottom thin;')
border_left = xlwt.easyxf('borders: left_color black, left thin;')
border_right = xlwt.easyxf('borders: right_color black, right thin;')
border_top = xlwt.easyxf('borders: top_color black, top thin;')
bold_medium_top = xlwt.easyxf('borders: top_color black, top medium;')

font_11_left = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left')
font_14_left = xlwt.easyxf('font: height 280, name ＭＳ Ｐゴシック; align: vert center, horiz left')
font_11_center_with_border = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center;\
                                        borders: top_color black, left_color black, right_color black, bottom_color black,\
                                        top thin, bottom thin, left thin, right thin;')
font_11_left_with_border = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                        borders: top_color black, left_color black, right_color black, bottom_color black,\
                                        top thin, bottom thin, left thin, right thin;')

title_style = xlwt.easyxf('font: height 360, name ＭＳ Ｐゴシック, color black;\
                            align: vert center, horiz center, wrap on;')
contract_date_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert bottom, horiz center, wrap on;')
company_title_style = xlwt.easyxf('font: bold on, height 320, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap off, shrink on;\
                                    borders: bottom_color black, bottom thin;')
company_label_style = xlwt.easyxf('font: height 280, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap on;\
                                    borders: bottom_color black, bottom thin;')
in_charge_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left, wrap off;\
                                borders: bottom_color black, bottom thin;')
company_supplier = xlwt.easyxf('font: height 240, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap on;\
                                borders: bottom_color black, bottom thin;')
company_supplier_label = xlwt.easyxf('font: height 240, name ＭＳ Ｐゴシック; align: vert center, horiz right, wrap on;\
                                    borders: bottom_color black, bottom thin;')
product_table_first_th_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap on;\
                                    borders: top_color black, left_color black, right_color black, top medium, left medium, right thin;')
product_table_th_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap on;\
                                    borders: top_color black, right_color black, top medium, right thin;')
product_table_last_th_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap on;\
                                    borders: top_color black, right_color black, top medium, right medium;')
product_first_content_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left, wrap on;\
                                    borders: top_color black, left_color black, right_color black, bottom_color black, bottom thin, top thin, left medium, right thin;')
product_content_style = xlwt.easyxf('font: height 220, name ＭＳ ゴシック; align: vert center, horiz right, wrap on;\
                                    borders: top_color black, right_color black, bottom_color black, bottom thin, top thin, right thin;',
                                    num_format_str='#,##0')
product_last_content_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz right, wrap on;\
                                    borders: top_color black, right_color black, bottom_color black, bottom thin, top thin, right medium;')                                    
shipping_date_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left, wrap on;\
                                    borders: top_color black, top medium;')
shipping_date_label_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left, wrap on;\
                                    borders: top_color black, left_color black, left thin, top medium;')
remark_lebel_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                borders: left_color black, left thin;')
remark_content_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                borders: left_color black, bottom_color black, bottom thin, left thin;')
subtotal_label_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap on;\
                                    borders: top_color black, left_color black, top medium, left medium;')
subtotal_value_style = xlwt.easyxf('font: height 220, name ＭＳ ゴシック; align: vert center, horiz right, wrap on;\
                                    borders: top_color black, left_color black, right_color black, top medium, left medium, right medium;',
                                    num_format_str='#,##0')
fee_label_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap on;\
                                    borders: top_color black, left_color black, top thin, left medium;')
fee_value_style = xlwt.easyxf('font: height 220, name ＭＳ ゴシック; align: vert center, horiz right, wrap on;\
                                    borders: top_color black, left_color black, right_color black, top thin, left medium, right medium;',
                                    num_format_str='#,##0')
total_label_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center, wrap on;\
                                    borders: top_color black, left_color black, bottom_color black,\
                                    bottom medium, top thin, left medium;')
total_value_style = xlwt.easyxf('font: height 220, bold on, name ＭＳ ゴシック; align: vert center, horiz right, wrap on;\
                                    borders: top_color black, left_color black, right_color black, bottom_color black,\
                                    bottom medium, top thin, left medium, right medium;',
                                    num_format_str='"¥"#,###')
remark_text_style = xlwt.easyxf('font: height 200, name ＭＳ Ｐゴシック; align: vert center, horiz left;')
sender_table_title_style = xlwt.easyxf('font: bold on, height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center;\
                                        borders: bottom_color black, bottom thin;')
sender_table_field_style = xlwt.easyxf('font: height 180, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                        borders: left_color black, left thin;')
sender_address_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert top, horiz left; \
                                    borders: right_color black, right thin;')
sender_table_text_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                        borders: right_color black, right thin;')
seal_address_tel_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                        borders: right_color black, left_color black, left thin, right thin;')
seal_company_style = xlwt.easyxf('font: height 320, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                        borders: right_color black, left_color black, left thin, right thin;')
seal_supplier_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                        borders: left_color black, left thin;')
seal_mark_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz left;\
                                        borders: right_color black, right thin;')
billed_deadline_label_style = xlwt.easyxf('font: height 280, bold on, name ＭＳ Ｐゴシック; align: vert center, horiz center;\
                                        borders: right_color black, top_color black, bottom_color black, left_color black,\
                                        right thin, top medium, left medium, bottom medium;')
billing_amount_value_style = xlwt.easyxf('font: height 280, bold on, name ＭＳ Ｐゴシック; align: vert center, horiz center;\
                                        borders: right_color black, top_color black, bottom_color black, left_color black,\
                                        right medium, top medium, left thin, bottom medium;',
                                        num_format_str='"¥"#,###')
billed_deadline_value_style = xlwt.easyxf('font: height 280, bold on, name ＭＳ Ｐゴシック; align: vert center, horiz center;\
                                        borders: right_color black, top_color black, bottom_color black, left_color black,\
                                        right medium, top medium, left thin, bottom medium;')
transfer_account_style = xlwt.easyxf('font: height 220, name ＭＳ Ｐゴシック; align: vert center, horiz center;\
                                        borders: left_color black, top_color black, top thin, left thin;')


class TraderSalesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        log_export_operation(user_id, "{} - {}".format(_("Sales contract"), _("Trader sales")))
        contract_form = TraderSalesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        created_at = contract_form.data.get('created_at', '')
        updated_at = contract_form.data.get('updated_at', '')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        customer_id = contract_form.data.get('customer_id')
        manager = contract_form.data.get('manager')
        company = frigana = postal_code = address = tel = fax = ""
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
        ws = wb.add_sheet('請求書', cell_overwrite_ok=True)

        for i in range(11):
            ws.col(i).width = cell_width_list[i]

        for i in range(1, 80):
            ws.row(i).height_mismatch = True
            ws.row(i).height = cell_height

        ws.row(0).height_mismatch = True
        ws.row(0).height = top_padding_height

        ws.row(1).height = header_height

        ws.write_merge(1, 1, 1, 8, '売買契約書　兼　請求書', title_style)
        ws.write_merge(1, 1, 9, 10, created_at, contract_date_style)

        ws.row(2).height = space_height

        ws.row(3).height = company_height
        ws.write_merge(3, 3, 0, 2, company, company_title_style)
        ws.write_merge(3, 3, 3, 4, _('CO.'), company_label_style)

        ws.row(4).height = space_height

        ws.row(5).height = height_18
        ws.write_merge(5, 5, 1, 2, manager, company_supplier)
        ws.write(5, 3, '', border_bottom)
        ws.write(5, 4, _('Mr.'), company_supplier_label)

        ws.row(6).height = height_16_5
        ws.write_merge(6, 6, 1, 5, address, font_11_left)
        ws.write_merge(6, 6, 7, 10, 'P-SENSOR {} {}'.format(_('Member ID'), P_SENSOR_NUMBER), font_11_left)

        ws.row(7).height = height_16_5
        ws.write_merge(7, 7, 1, 2, 'FAX {}'.format(fax), font_11_left)
        ws.write_merge(7, 7, 4, 6, 'TEL {}'.format(tel), font_11_left)
        
        ws.write(7, 7, '担当：', in_charge_style)
        ws.write_merge(7, 7, 8, 10, person_in_charge, in_charge_style)

        ws.row(8).height = space_height

        ws.row(9).height = height_15
        ws.write_merge(9, 9, 0, 6, '商　品　名', product_table_first_th_style)
        ws.write(9, 7, '数量', product_table_th_style)
        ws.write(9, 8, '単　価', product_table_th_style)
        ws.write_merge(9, 9, 9, 10, '金　額', product_table_th_style)

        # Product Table
        row_no = 10
        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
        if num_of_products:
            for form in product_formset.forms:
                form.is_valid()
                id = form.cleaned_data.get('product_id')
                product_name = Product.objects.get(id=id).name
                quantity = form.cleaned_data.get('quantity', 0)
                price = form.cleaned_data.get('price', 0)
                amount = quantity * price

                ws.row(row_no).height = height_18
                ws.write_merge(row_no, row_no, 0, 6, product_name, product_first_content_style)
                ws.write(row_no, 7, quantity, product_content_style)
                ws.write(row_no, 8, price, product_content_style)
                ws.write_merge(row_no, row_no, 9, 10, amount, product_content_style)
                row_no += 1

        # Document Table
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

                ws.row(row_no).height = height_18
                ws.write_merge(row_no, row_no, 0, 6, document_name, product_first_content_style)
                ws.write(row_no, 7, quantity, product_content_style)
                ws.write(row_no, 8, price, product_content_style)
                ws.write_merge(row_no, row_no, 9, 10, amount, product_content_style)
                row_no += 1
        
        total_number = num_of_products + num_of_documents
        if total_number < 6:
            for i in range(0, 6 - total_number):
                ws.row(row_no).height = height_18
                ws.write_merge(row_no, row_no, 0, 6, None, product_first_content_style)
                ws.write(row_no, 7, None, product_content_style)
                ws.write(row_no, 8, None, product_content_style)
                ws.write_merge(row_no, row_no, 9, 10, None, product_content_style)
                row_no += 1

        shipping_method = contract_form.data.get('shipping_method')
        shipping_date = contract_form.data.get('shipping_date')
        payment_method = contract_form.data.get('payment_method')
        payment_due_date = contract_form.data.get('payment_due_date')
        sub_total = contract_form.data.get('sub_total')
        tax = contract_form.data.get('tax')
        fee = contract_form.data.get('fee')
        total = contract_form.data.get('total')
        remarks = contract_form.data.get('remarks')
        shipping_date_label = get_shipping_date_label(shipping_method)

        try:
            sub_total = int(sub_total)
            tax = int(tax)
            fee = int(fee)
            total = int(total)
        except ValueError:
            sub_total = 0
            tax = 0
            fee = 0
            total = 0
        
        ws.row(row_no).height = height_15
        ws.write_merge(row_no, row_no, 0, 1, '{}: '.format(shipping_date_label), shipping_date_label_style)
        ws.write_merge(row_no, row_no, 2, 6, shipping_date, shipping_date_style)
        ws.write_merge(row_no, row_no, 7, 8, '小　計', subtotal_label_style)
        ws.write_merge(row_no, row_no, 9, 10, sub_total, subtotal_value_style)
        row_no += 1

        ws.row(row_no).height = height_15
        ws.write(row_no, 0, '※備考', remark_lebel_style)
        ws.write_merge(row_no, row_no, 7, 8, '消費税（10%）', fee_label_style)
        ws.write_merge(row_no, row_no, 9, 10, tax, fee_value_style)
        row_no += 1

        ws.row(row_no).height = height_15
        ws.write_merge(18, 19, 0, 6, remarks, remark_content_style)
        ws.write_merge(18, 18, 7, 8, '保険代（非課税）', fee_label_style)
        ws.write_merge(18, 18, 9, 10, fee, fee_value_style)
        row_no += 1

        ws.row(row_no).height = height_15
        
        ws.write_merge(row_no, row_no, 7, 8, '合　計', total_label_style)
        ws.write_merge(row_no, row_no, 9, 10, total, total_value_style)
        row_no += 1

        ws.row(row_no).height = space_height
        row_no += 1
        remark_text_list = [
            "※ 売主、買主、双方の署名・捺印が揃った時点で契約が成立したものとします。",
            "※ 契約が成立後、原則として売買契約を解除できないものとします。",
            "※ 当該商品に不備及び故障がある場合の保障は、納品後３日以内とします。",
            "※ 買主が代金金額の支払いを完了するまでは、売買物件の所有権は売主において留保する。",
            "※ 売買物件の所有権は、引渡しが終了し、支払いが完了した時点で買主に移行するものとする。",
            "※ 下記の場合の売主は、何らかの手続きを経ずして、その選択により期限の利益を喪失せしめて残代金の",
            "  即時支払いを求めるか、又は本契約を解除して売買物件を引き上げる事が出来る。",
            "1)代金の支払いを1回でも怠った場合。",
            "2)仮差押え、仮処分等の執行を受け、整理・和議・破損等の申立てを受けた場合。"
        ]

        for remark_text in remark_text_list:
            ws.row(row_no).height = height_12
            ws.write(row_no, 0, remark_text, remark_text_style)
            row_no += 1

        ws.row(row_no).height = space_height * 2
        row_no += 1

        product_sender_form = TraderSalesProductSenderForm(self.request.POST)
        document_sender_form = TraderSalesDocumentSenderForm(self.request.POST)
        product_sender_id = self.request.POST.get('product_sender_id')
        product_expected_arrival_date = self.request.POST.get('product_expected_arrival_date')
        product_sender_company = ""
        if product_sender_id:
            product_sender = Sender.objects.get(id=product_sender_id)
            product_sender_company = product_sender.name
        product_sender_address = product_sender_form.data.get('product_sender_address')
        product_sender_tel = product_sender_form.data.get('product_sender_tel')
        product_sender_fax = product_sender_form.data.get('product_sender_fax')
        
        document_sender_id = self.request.POST.get('document_sender_id')
        document_expected_arrival_date = self.request.POST.get('document_expected_arrival_date')
        document_sender_company = ""
        if document_sender_id:
            document_sender = Sender.objects.get(id=document_sender_id)
            document_sender_company = document_sender.name
        document_sender_address = document_sender_form.data.get('document_sender_address')
        document_sender_tel = document_sender_form.data.get('document_sender_tel', "")
        document_sender_fax = document_sender_form.data.get('document_sender_fax', "")

        ws.row(row_no).height = height_13_5
        ws.write_merge(row_no, row_no, 0, 5, '【商品発送先】', sender_table_title_style)
        ws.write_merge(row_no, row_no, 6, 10, '【書類発送先】', sender_table_title_style)
        row_no += 1

        ws.row(row_no).height = space_height
        ws.write(row_no, 0, '', border_left)
        ws.write(row_no, 6, '', border_left)
        ws.write(row_no, 5, '', border_right)
        ws.write(row_no, 10, '', border_right)
        row_no += 1
        
        ws.row(row_no).height = height_16
        ws.write(row_no, 0, '会社名：', sender_table_field_style)
        ws.write_merge(row_no, row_no, 1, 5, product_sender_company, sender_table_text_style)
        ws.write(row_no, 6, '会社名：', sender_table_field_style)
        ws.write_merge(row_no, row_no, 7, 10, document_sender_company, sender_table_text_style)
        row_no += 1

        for i in range(0, 6):
            ws.row(row_no + i).height = height_16
        ws.write(row_no, 0, '住所：', sender_table_field_style)
        ws.write(row_no, 6, '住所：', sender_table_field_style)
        ws.write_merge(row_no, row_no + 3, 1, 5, '〒 {}'.format(product_sender_address), sender_address_style)
        ws.write_merge(row_no, row_no + 3, 7, 10, '〒 {}'.format(document_sender_address), sender_address_style)
        row_no += 1

        ws.write(row_no, 0, '', border_left)
        ws.write(row_no, 6, '', sender_table_field_style)
        row_no += 1

        ws.write(row_no, 0, '', border_left)
        ws.write(row_no, 6, '', sender_table_field_style)
        row_no += 1

        ws.write(row_no, 0, '', border_left)
        ws.write(row_no, 6, '', sender_table_field_style)
        row_no += 1

        ws.write(row_no, 0, 'TEL／FAX：', sender_table_field_style)
        ws.write_merge(row_no, row_no, 1, 5, '{} / {}'.format(product_sender_tel, product_sender_fax), sender_table_text_style)
        ws.write(row_no, 6, 'TEL／FAX：', sender_table_field_style)
        ws.write_merge(row_no, row_no, 7, 10, '{} / {}'.format(document_sender_tel, document_sender_fax), sender_table_text_style)
        row_no += 1

        ws.write(row_no, 0, '到着予定日：', sender_table_field_style)
        ws.write(row_no, 6, '到着予定日：', sender_table_field_style)
        ws.write_merge(row_no, row_no, 1, 5, product_expected_arrival_date, sender_table_text_style)
        ws.write_merge(row_no, row_no, 7, 10, document_expected_arrival_date, sender_table_text_style)
        row_no += 1

        ws.row(row_no).height = space_height
        ws.write(row_no, 0, '', border_left)
        ws.write(row_no, 6, '', border_left)
        ws.write(row_no, 10, '', border_right)
        row_no += 1

        ws.row(row_no).height = space_height
        for i in range(0, 11):
            ws.write(row_no, i, '', border_top)
        row_no += 1

        ws.row(row_no).height = height_13_5
        ws.write_merge(row_no, row_no, 0, 5, '【買主 署名捺印欄】', sender_table_title_style)
        ws.write_merge(row_no, row_no, 6, 10, '【売主 署名捺印欄】', sender_table_title_style)
        row_no += 1

        ws.row(row_no).height = space_height
        ws.write(row_no, 6, '', border_left)
        ws.write(row_no, 0, '', border_left)
        ws.write(row_no, 5, '', border_right)
        ws.write(row_no, 10, '', border_right)
        row_no += 1

        for i in range(0, 5):
            ws.row(row_no + i).height = height_16
            ws.write(row_no + i, 0, '', border_left)
        
        # ws.write_merge(row_no, row_no, 0, 5, '〒537-0021　大阪府大阪市東成区東中本2丁目4-15', seal_address_tel_style)
        ws.write_merge(row_no, row_no, 6, 10, '〒537-0021　大阪府大阪市東成区東中本2丁目4-15', seal_address_tel_style)
        row_no += 1
        
        # ws.write_merge(row_no, row_no + 1, 0, 5, 'バッジオ株式会社', seal_company_style)
        ws.write_merge(row_no, row_no + 1, 6, 10, 'バッジオ株式会社', seal_company_style)
        row_no += 2

        # ws.write_merge(row_no, row_no, 0, 4, '代表取締役　金　昇志', seal_supplier_style)
        ws.write_merge(row_no, row_no, 6, 9, '代表取締役　金　昇志', seal_supplier_style)
        ws.write(row_no, 5, '㊞', seal_mark_style)
        ws.write(row_no, 10, '㊞', seal_mark_style)
        row_no += 1

        # ws.write_merge(row_no, row_no, 0, 5, 'TEL 06-6753-8078 FAX 06-6753-8079', seal_address_tel_style)
        ws.write_merge(row_no, row_no, 6, 10, 'TEL 06-6753-8078 FAX 06-6753-8079', seal_address_tel_style)
        row_no += 1

        ws.row(row_no).height = space_height
        ws.write(row_no, 0, '', border_left)
        ws.write(row_no, 6, '', border_left)
        ws.write(row_no, 10, '', border_right)
        row_no += 1

        ws.row(row_no).height = space_height
        for i in range(0, 11):
            ws.write(row_no, i, '', border_top)
        row_no += 1

        ws.write(row_no, 5, '下記の通り御請求申し上げます。', font_11_left)
        row_no += 1

        ws.write_merge(row_no, row_no, 0, 2, '運送方法', font_11_center_with_border)
        ws.write_merge(row_no, row_no + 1, 5, 7, '御請求金額', billed_deadline_label_style)
        ws.write_merge(row_no, row_no + 1, 8, 10, total, billing_amount_value_style)
        row_no += 1

        ws.write_merge(row_no, row_no, 0, 2, '発送', font_11_center_with_border)
        row_no += 2

        ws.write_merge(row_no, row_no, 0, 2, 'お支払方法', font_11_center_with_border)
        ws.write_merge(row_no + 1, row_no + 1, 0, 2, '振込', font_11_center_with_border)

        ws.write_merge(row_no, row_no + 1, 5, 7, 'お支払期限', billed_deadline_label_style)
        ws.write_merge(row_no, row_no + 1, 8, 10, payment_due_date, billed_deadline_value_style)
        row_no += 2

        ws.row(row_no).height = space_height
        row_no += 1

        ws.row(row_no).height = height_16
        ws.write(row_no, 0, '※ お振込み手数料は貴社ご負担でお願い致します。', font_11_left)
        row_no += 1

        ws.write_merge(row_no, row_no, 0, 1, '振込先口座', transfer_account_style)
        ws.write_merge(row_no, row_no, 2, 10, 'りそな銀行　船場支店（101）　普通　0530713　バッジオカブシキガイシャ', font_11_left_with_border)
        row_no += 1

        ws.write(row_no, 0, '', border_left)
        ws.write_merge(row_no, row_no, 2, 10, '', font_11_left_with_border)
        row_no += 1

        ws.write(row_no, 0, '', border_left)
        ws.write_merge(row_no, row_no, 2, 10, '', font_11_left_with_border)
        row_no += 1

        ws.row(row_no).height = space_height
        for i in range(0, 11):
            ws.write(row_no, i, '', border_top)
        row_no += 1

        ws.row(row_no).height = height_16
        ws.write(row_no, 0, '内容をご確認の上、ご捺印後弊社まで返信お願いします。', font_11_left)
        ws.write(row_no, 7, 'FAX 06-6753-8079', font_14_left)
        row_no += 1

        ws.row(row_no).height = height_16
        ws.write(row_no, 0, '※ 請求書原本が必要な場合は必ずチェックしてください。　【　必要　・　不要　】', font_11_left)
        row_no += 2

        ws.write(row_no, 0, 'No.{}'.format(contract_id), font_11_left)
        
        wb.save(response)
        return response


class TraderPurchasesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        log_export_operation(user_id, "{} - {}".format(_("Sales contract"), _("Trader purchases")))
        contract_form = TraderPurchasesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        created_at = contract_form.data.get('created_at', '')
        updated_at = contract_form.data.get('updated_at', '')
        person_in_charge = contract_form.data.get('person_in_charge', '')
        customer_id = contract_form.data.get('customer_id')
        manager = contract_form.data.get('manager')
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
        response['Content-Disposition'] = 'attachment; filename="trader_purchases_contract_{}.xls"'.format(contract_id)
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("{} - {}".format(_('Sales contract'), _('Trader purchases')), cell_overwrite_ok=True)

        for i in range(8):
            ws.col(i).width = cell_width

        for i in range(1, 80):
            ws.row(i).height_mismatch = True
            ws.row(i).height = cell_height

        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write_merge(0, 0, 0, 7, _('Contract and invoice'), title_style)
        ws.write_merge(1, 1, 0, 1, 'No.  {}'.format(contract_id), common_style)
        ws.write(1, 6, _('Created date'), common_style)
        ws.write(1, 7, created_at, common_style)
        ws.write(2, 6, _('Updated date'), common_style)
        ws.write(2, 7, updated_at, common_style)

        ws.write(4, 0, _('Company'), common_style)
        ws.write_merge(4, 4, 1, 3, company, common_style)
        ws.write(4, 4, _('Frigana'), common_style)
        ws.write_merge(4, 4, 5, 7, frigana, common_style)

        ws.write_merge(5, 5, 1, 3, manager, common_style)

        ws.write(6, 0, _('Postal code'), common_style)
        ws.write_merge(6, 6, 1, 2, postal_code, common_style)

        ws.write(7, 0, _('Address'), common_style)
        ws.write_merge(7, 7, 1, 3, address, common_style)

        ws.write_merge(7, 7, 4, 5, 'P-SENSOR {}'.format(_('Member ID')), center_style)
        ws.write_merge(7, 7, 6, 7, P_SENSOR_NUMBER, common_style)

        ws.write(8, 0, _('TEL'), common_style)
        ws.write(8, 1, tel, common_style)
        ws.write(8, 3, _('FAX'), common_style)
        ws.write(8, 4, fax, common_style)
        ws.write(8, 6, _('Person in charge'), common_style)
        ws.write(8, 7, person_in_charge, common_style)

        # Product Table
        ws.write_merge(10, 10, 0, 3, _('Model name'), table_center_style)
        ws.write(10, 4, _('Product type'), table_center_style)
        ws.write(10, 5, _('Quantity'), table_center_style)
        ws.write(10, 6, _('Price'), table_center_style)
        ws.write(10, 7, _('Amount'), table_center_style)

        row_no = 11
        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
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
                ws.write(row_no, 4, str(dict(PRODUCT_TYPE_CHOICES)[type]), table_center_style)
                ws.write(row_no, 5, quantity, table_center_style)
                ws.write(row_no, 6, price, table_center_style)
                ws.write(row_no, 7, amount, table_center_style)
                ws.row(row_no).height = address_cell_height
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
        
        removal_date = contract_form.data.get('removal_date')
        shipping_date = contract_form.data.get('shipping_date')
        frame_color = contract_form.data.get('frame_color')
        receipt = contract_form.data.get('receipt')
        remarks = contract_form.data.get('remarks')
        sub_total = contract_form.data.get('sub_total')
        tax = contract_form.data.get('tax')
        fee = contract_form.data.get('fee')
        total = contract_form.data.get('total')

        try:
            sub_total = int(sub_total)
            tax = int(tax)
            fee = int(fee)
            total = int(total)
        except ValueError:
            sub_total = 0
            tax = 0
            fee = 0
            total = 0

        row_no += 1
        ws.write(row_no, 0, _('Removal date'), common_style)
        ws.write(row_no, 1, removal_date, common_style)
        ws.write(row_no, 3, _('Frame color'), common_style)
        ws.write(row_no, 4, frame_color, common_style)
        ws.write_merge(row_no, row_no, 5, 6, _('Sum'), table_left_style)
        ws.write(row_no, 7, sub_total, number_style)
        row_no += 1

        ws.write(row_no, 0, _('Date of shipment'), common_style)
        ws.write(row_no, 1, shipping_date, common_style)
        ws.write(row_no, 3, _('Receipt'), common_style)
        ws.write(row_no, 4, receipt, common_style)
        ws.write_merge(row_no, row_no, 5, 6, _('Consumption tax') + '(10%)', table_left_style)
        ws.write(row_no, 7, tax, number_style)
        row_no += 1

        ws.write_merge(row_no, row_no + 1, 0, 0, _('Remarks'), common_style)
        ws.write_merge(row_no, row_no + 1, 1, 4, remarks, common_style)
        ws.write_merge(row_no, row_no, 5, 6, _('Insurance fee') + '(' + _('No tax') + ')', table_left_style)
        ws.write(row_no, 7, fee, number_style)
        row_no += 1

        ws.write_merge(row_no, row_no, 5, 6, _('Total amount'), table_left_style)
        ws.write(row_no, 7, total, number_style)
        row_no += 1

        row_no += 1
        content = "※{}\n".format(_("It is assumed that the contract has been concluded with the arrival of our certificate of sale."))
        content += "※{}\n".format(_('If you cancel after sending the proof of purchase, you will be compensated for 100%% of the closing price.'))
        content += "※{}\n".format(_("We will notify you of any missing items or damage within 3 days after the item arrives. No further returns or exchanges will be accepted."))
        ws.write_merge(row_no, row_no + 2, 0, 7, content, common_style)
        row_no += 3

        product_sender_form = TraderPurchasesProductSenderForm(self.request.POST)
        document_sender_form = TraderPurchasesDocumentSenderForm(self.request.POST)
        product_sender_id = self.request.POST.get('product_sender_id')
        product_shipping_company = self.request.POST.get('product_shipping_company')
        product_sender_remarks = self.request.POST.get('product_sender_remarks')
        product_desired_arrival_date = self.request.POST.get('product_desired_arrival_date')
        product_sender_company = None
        if product_sender_id:
            product_sender = Sender.objects.get(id=product_sender_id)
            product_sender_company = product_sender.name
        product_sender_address = product_sender_form.data.get('product_sender_address')
        product_sender_tel = product_sender_form.data.get('product_sender_tel')

        document_sender_company = None
        document_sender_id = self.request.POST.get('document_sender_id')
        document_shipping_company = self.request.POST.get('document_shipping_company')
        document_sender_remarks = self.request.POST.get('document_sender_remarks')
        document_desired_arrival_date = self.request.POST.get('document_desired_arrival_date')
        if document_sender_id:
            document_sender = Sender.objects.get(id=document_sender_id)
            document_sender_company = document_sender.name
        document_sender_address = document_sender_form.data.get('document_sender_address')
        document_sender_tel = document_sender_form.data.get('document_sender_tel')

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
        ws.row(row_no).height = address_cell_height
        row_no += 1
        ws.write(row_no, 0, _('TEL'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_sender_tel, common_style)
        ws.write(row_no, 4, _('TEL'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_sender_tel, common_style)
        row_no += 1
        ws.write(row_no, 0, _('Desired arrival date'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_desired_arrival_date, common_style)
        ws.write(row_no, 4, _('Desired arrival date'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_desired_arrival_date, common_style)
        row_no += 1
        ws.write(row_no, 0, _('Shipping company'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_shipping_company, common_style)
        ws.write(row_no, 4, _('Shipping company'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_shipping_company, common_style)
        row_no += 1
        ws.write(row_no, 0, _('Remarks'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, product_sender_remarks, common_style)
        ws.write(row_no, 4, _('Remarks'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, document_sender_remarks, common_style)
        row_no += 1

        row_no += 1
        content_desc = "{}\n".format(_("Please check the contents, seal it, and fax it to us."))
        content_refax = "{}：バッジオ(株)　06-6753-8079".format(_("Return address"))
        ws.write_merge(row_no, row_no + 1, 0, 7, "", common_style)
        content = (content_desc, (content_refax, font_large_style))
        ws.row(row_no).set_cell_rich_text(0, content, center_style)
        row_no += 2

        row_no += 1
        ws.write_merge(row_no, row_no, 0, 3, _('Buyer'), sub_title_style)
        ws.write_merge(row_no, row_no, 4, 7, _('Seller'), sub_title_style)
        row_no += 1
        seller_seal_pre = "    〒"
        seller_seal_pre += postal_code if postal_code else ""
        seller_seal_pre += " {}\n".format(address) if address else "\n"
        seller_seal_company = "   {}\n".format(customer.name) if customer_id else "    \n"
        seller_seal_post = "    TEL: "
        seller_seal_post += tel if tel else "               "
        seller_seal_post += "  FAX: "
        seller_seal_post += fax if fax else ""
        seller_seal = (seller_seal_pre, (seller_seal_company, font_large_style), seller_seal_post)

        buyer_seal_pre = "    〒{} {}\n".format(POSTAL_CODE, ADDRESS)
        buyer_seal_company = "   {}\n".format(COMPANY_NAME)
        buyer_seal_post = "    TEL: {} FAX: {}".format(TEL, FAX)
        buyer_seal = (buyer_seal_pre, (buyer_seal_company, font_large_style), buyer_seal_post)
        ws.write_merge(row_no, row_no + 3, 0, 3, "", common_style)
        ws.row(row_no).set_cell_rich_text(0, seller_seal, common_style)
        ws.write_merge(row_no, row_no + 3, 4, 7, "", common_style)
        ws.row(row_no).set_cell_rich_text(4, buyer_seal, common_style)
        row_no += 4

        transfer_deadline = self.request.POST.get('transfer_deadline')
        bank_name = self.request.POST.get('bank_name')
        account_number = self.request.POST.get('account_number')
        branch_name = self.request.POST.get('branch_name')
        account_holder = self.request.POST.get('account_holder')
        
        row_no += 1
        ws.write(row_no, 0, _('Transfer deadline'), table_center_style)
        ws.write_merge(row_no, row_no, 1, 3, transfer_deadline, table_left_style)
        ws.write(row_no, 4, _('Original invoice'), table_center_style)
        ws.write_merge(row_no, row_no, 5, 7, "{} ∙ {}".format(_('Required'), _('Not required')), table_center_style)
        row_no += 1
        ws.write_merge(row_no, row_no + 1, 0, 0, _("Transfer account"), table_center_style)
        ws.write(row_no, 1, _('Bank name'), table_center_style)
        ws.write_merge(row_no, row_no, 2, 3, bank_name, table_left_style)
        ws.write(row_no, 4, _('Branch name'), table_center_style)
        ws.write_merge(row_no, row_no, 5, 7, branch_name, table_left_style)
        row_no += 1
        ws.write(row_no, 1, _('Account number'), table_center_style)
        ws.write_merge(row_no, row_no, 2, 3, account_number, table_left_style)
        ws.write(row_no, 4, _('Account holder'), table_center_style)
        ws.write_merge(row_no, row_no, 5, 7, account_holder, table_left_style)

        wb.save(response)
        return response


class HallSalesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        log_export_operation(user_id, "{} - {}".format(_("Sales contract"), _("Hall sales")))
        contract_form = HallSalesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        customer_id = contract_form.data.get('customer_id')
        created_at = contract_form.data.get('created_at', '')
        hall_id = contract_form.data.get('hall_id')
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

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="hall_sales_contract_{}.xls"'.format(contract_id)
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("{} - {}".format(_('Sales contract'), _('Hall sales')))

        for i in range(8):
            ws.col(i).width = cell_width

        for i in range(1, 80):
            ws.row(i).height_mismatch = True
            ws.row(i).height = cell_height

        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write_merge(0, 0, 0, 7, _('Sales contract'), title_style)
        ws.write_merge(1, 1, 0, 1, 'No.  {}'.format(contract_id), common_style)
        ws.write(1, 7, created_at, common_style)

        ws.write_merge(3, 3, 0, 3, "{}({})".format(_('Buyer'), _('A')), sub_title_left_style)
        ws.write_merge(3, 3, 4, 7, "{}({})".format(_('Seller'), _('B')), sub_title_left_style)

        ws.write(4, 0, _('Company'), common_style)
        ws.write_merge(4, 4, 1, 3, company, common_style)
        ws.write(4, 4, _('Company'), common_style)
        ws.write_merge(4, 4, 5, 7, COMPANY_NAME, common_style)
        ws.row(4).height = address_cell_height

        ws.write(5, 4, _('Address'), common_style)
        ws.write_merge(5, 5, 5, 7, ADDRESS, common_style)
        
        ws.write(6, 4, _('TEL'), common_style)
        ws.write(6, 5, TEL, common_style)
        ws.write(6, 6, _('FAX'), common_style)
        ws.write(6, 7, FAX, common_style)

        ws.write_merge(8, 8, 0, 7, _('Installation location'), sub_title_left_style)
        ws.write(9, 0, _('Hall name'), common_style)
        ws.write_merge(9, 9, 1, 3, hall_name, common_style)
        ws.write(9, 4, _('Address'), common_style)
        ws.write_merge(9, 9, 5, 7, hall_address, common_style)
        ws.row(9).height = address_cell_height
        
        ws.write(10, 0, _('TEL'), common_style)
        ws.write_merge(10, 10, 1, 3, hall_tel, common_style)

        ws.write_merge(11, 12, 0, 7, _('The buyer (hereinafter referred to as A) and the seller (hereinafter referred to as B) have entered into a sales contract including the transaction contract stated on the back of the following products (hereinafter referred to as properties).'), common_style)

        # Product Table
        ws.write_merge(14, 14, 0, 3, _('Model name'), table_center_style)
        ws.write(14, 4, _('Product type'), table_center_style)
        ws.write(14, 5, _('Quantity'), table_center_style)
        ws.write(14, 6, _('Price'), table_center_style)
        ws.write(14, 7, _('Amount'), table_center_style)

        row_no = 15
        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
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
                ws.write(row_no, 4, str(dict(PRODUCT_TYPE_CHOICES)[type]), table_center_style)
                ws.write(row_no, 5, quantity, table_center_style)
                ws.write(row_no, 6, price, table_center_style)
                ws.write(row_no, 7, amount, table_center_style)
                ws.row(row_no).height = address_cell_height
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
        
        # Document Fee Table
        row_no += 1
        ws.write_merge(row_no, row_no, 0, 1, _('Product type'), table_center_style)
        ws.write_merge(row_no, row_no, 2, 3, _('Model count'), table_center_style)
        ws.write_merge(row_no, row_no, 4, 5, _('Unit count'), table_center_style)
        ws.write_merge(row_no, row_no, 6, 7, _('Amount'), table_center_style)
        row_no += 1

        document_fee_formset = DocumentFeeFormSet(
            self.request.POST,
            prefix='document_fee'
        )
        num_of_document_fees = document_fee_formset.total_form_count()
        if num_of_document_fees:
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

                ws.write_merge(row_no, row_no, 0, 1, str(dict(TYPE_CHOICES)[type]), table_center_style)
                ws.write_merge(row_no, row_no, 2, 3, model_count, table_center_style)
                ws.write_merge(row_no, row_no, 4, 5, unit_count, table_center_style)
                ws.write_merge(row_no, row_no, 6, 7, amount, table_center_style)
                row_no += 1

        remarks = contract_form.data.get('remarks')
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

        try:
            sub_total = int(sub_total)
            tax = int(tax)
            fee = int(fee)
            total = int(total)
        except ValueError:
            sub_total = 0
            tax = 0
            fee = 0
            total = 0
        
        row_no += 1
        ws.write_merge(row_no, row_no + 3, 0, 0, _('Remarks'), common_style)
        ws.write_merge(row_no, row_no + 3, 1, 3, remarks, common_style)
        ws.write_merge(row_no, row_no, 5, 6, _('Sum'), table_left_style)
        ws.write(row_no, 7, sub_total, number_style)
        row_no += 1

        ws.write_merge(row_no, row_no, 5, 6, _('Consumption tax') + '(10%)', table_left_style)
        ws.write(row_no, 7, tax, number_style)
        row_no += 1

        ws.write_merge(row_no, row_no, 5, 6, _('Insurance fee') + '(' + _('No tax') + ')', table_left_style)
        ws.write(row_no, 7, fee, number_style)
        row_no += 1

        ws.write_merge(row_no, row_no, 5, 6, _('Total amount'), table_left_style)
        ws.write(row_no, 7, total, number_style)
        row_no += 1

        row_no += 1
        ws.write_merge(row_no, row_no, 4, 7, _('We will charge you as follows.'), common_style)

        row_no += 1
        ws.write(row_no, 0, _('Shipping date'), common_style)
        ws.write(row_no, 1, shipping_date, common_style)
        ws.write(row_no + 1, 0, _('Opening date'), common_style)
        ws.write(row_no + 1, 1, opening_date, common_style)
        ws.write(row_no + 2, 0, _('Payment method'), common_style)
        ws.write(row_no + 2, 1, str(dict(PAYMENT_METHOD_CHOICES)[payment_method]), common_style)
        
        ws.write_merge(row_no, row_no + 4, 4, 4, _('Payment breakdown'), table_center_style)

        milestone_formset = MilestoneFormSet(
            self.request.POST,
            prefix='milestone'
        )

        table_date_style.num_format_str = 'yyyy/mm/dd' if self.request.LANGUAGE_CODE == 'ja' else 'mm/dd/yyyy'

        idx = 1
        for form in milestone_formset.forms:
            form.is_valid()
            date = form.cleaned_data.get('date')
            amount = form.cleaned_data.get('amount')
            
            ws.write(row_no + idx - 1, 5, _(ordinal(idx)), table_center_style)
            ws.write(row_no + idx - 1, 6, date, table_date_style)
            ws.write(row_no + idx - 1, 7, amount, table_left_style)
            idx += 1
        row_no += 5
        
        row_no += 1
        ws.write_merge(row_no, row_no, 0, 7, _('Please bear the transfer fee at your expense.'), common_style)

        row_no += 1
        ws.write(row_no, 0, _('Transfer account'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, transfer_account, common_style)
        ws.write(row_no, 4, _('Person in charge'), common_style)
        ws.write(row_no, 5, person_in_charge, common_style)
        ws.write(row_no, 6, _('Confirmor'), common_style)
        ws.write(row_no, 7, confirmor, common_style)
        ws.row(row_no).height = address_cell_height

        wb.save(response)
        return response


class HallPurchasesInvoiceView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        log_export_operation(user_id, "{} - {}".format(_("Sales contract"), _("Hall purchases")))
        contract_form = HallPurchasesContractForm(self.request.POST)
        contract_id = contract_form.data.get('contract_id', '')
        customer_id = contract_form.data.get('customer_id')
        created_at = contract_form.data.get('created_at', '')
        hall_id = contract_form.data.get('hall_id')
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

        
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="hall_purchases_contract_{}.xls"'.format(contract_id)
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("{} - {}".format(_('Sales contract'), _('Hall purchases')))

        for i in range(8):
            ws.col(i).width = cell_width

        for i in range(1, 80):
            ws.row(i).height_mismatch = True
            ws.row(i).height = cell_height

        ws.row(0).height_mismatch = True
        ws.row(0).height = header_height

        ws.write_merge(0, 0, 0, 7, _('Sales contract'), title_style)
        ws.write_merge(1, 1, 0, 1, 'No.  {}'.format(contract_id), common_style)
        ws.write(1, 7, created_at, common_style)

        ws.write_merge(3, 3, 0, 3, "{}({})".format(_('Buyer'), _('A')), sub_title_left_style)
        ws.write_merge(3, 3, 4, 7, "{}({})".format(_('Seller'), _('B')), sub_title_left_style)

        ws.write(4, 0, _('Company'), common_style)
        ws.write_merge(4, 4, 1, 3, company, common_style)
        ws.write(4, 4, _('Company'), common_style)
        ws.write_merge(4, 4, 5, 7, COMPANY_NAME, common_style)
        ws.row(4).height = address_cell_height

        ws.write(5, 4, _('Address'), common_style)
        ws.write_merge(5, 5, 5, 7, ADDRESS, common_style)
        
        ws.write(6, 4, _('TEL'), common_style)
        ws.write(6, 5, TEL, common_style)
        ws.write(6, 6, _('FAX'), common_style)
        ws.write(6, 7, FAX, common_style)

        ws.write_merge(8, 8, 0, 7, _('Installation location'), sub_title_left_style)
        ws.write(9, 0, _('Hall name'), common_style)
        ws.write_merge(9, 9, 1, 3, hall_name, common_style)
        ws.write(9, 4, _('Address'), common_style)
        ws.write_merge(9, 9, 5, 7, hall_address, common_style)
        ws.row(9).height = address_cell_height
        
        ws.write(10, 0, _('TEL'), common_style)
        ws.write_merge(10, 10, 1, 3, hall_tel, common_style)

        ws.write_merge(11, 12, 0, 7, _('The buyer (hereinafter referred to as A) and the seller (hereinafter referred to as B) have entered into a sales contract including the transaction contract stated on the back of the following products (hereinafter referred to as properties).'), common_style)

        # Product Table
        ws.write_merge(14, 14, 0, 3, _('Model name'), table_center_style)
        ws.write(14, 4, _('Product type'), table_center_style)
        ws.write(14, 5, _('Quantity'), table_center_style)
        ws.write(14, 6, _('Price'), table_center_style)
        ws.write(14, 7, _('Amount'), table_center_style)

        row_no = 15
        product_formset = ProductFormSet(
            self.request.POST,
            prefix='product'
        )
        num_of_products = product_formset.total_form_count()
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
                ws.write(row_no, 4, str(dict(PRODUCT_TYPE_CHOICES)[type]), table_center_style)
                ws.write(row_no, 5, quantity, table_center_style)
                ws.write(row_no, 6, price, table_center_style)
                ws.write(row_no, 7, amount, table_center_style)
                ws.row(row_no).height = address_cell_height
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
        
        # Document Fee Table
        row_no += 1
        ws.write_merge(row_no, row_no, 0, 1, _('Product type'), table_center_style)
        ws.write_merge(row_no, row_no, 2, 3, _('Model count'), table_center_style)
        ws.write_merge(row_no, row_no, 4, 5, _('Unit count'), table_center_style)
        ws.write_merge(row_no, row_no, 6, 7, _('Amount'), table_center_style)
        row_no += 1

        document_fee_formset = DocumentFeeFormSet(
            self.request.POST,
            prefix='document_fee'
        )
        num_of_document_fees = document_fee_formset.total_form_count()
        if num_of_document_fees:
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
                
                ws.write_merge(row_no, row_no, 0, 1, str(dict(TYPE_CHOICES)[type]), table_center_style)
                ws.write_merge(row_no, row_no, 2, 3, model_count, table_center_style)
                ws.write_merge(row_no, row_no, 4, 5, unit_count, table_center_style)
                ws.write_merge(row_no, row_no, 6, 7, amount, table_center_style)
                row_no += 1

        remarks = contract_form.data.get('remarks')
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

        try:
            sub_total = int(sub_total)
            tax = int(tax)
            fee = int(fee)
            total = int(total)
        except ValueError:
            sub_total = 0
            tax = 0
            fee = 0
            total = 0

        row_no += 1
        ws.write_merge(row_no, row_no + 3, 0, 0, _('Remarks'), common_style)
        ws.write_merge(row_no, row_no + 3, 1, 3, remarks, common_style)
        ws.write_merge(row_no, row_no, 5, 6, _('Sum'), table_left_style)
        ws.write(row_no, 7, sub_total, number_style)
        row_no += 1

        ws.write_merge(row_no, row_no, 5, 6, _('Consumption tax') + '(10%)', table_left_style)
        ws.write(row_no, 7, tax, number_style)
        row_no += 1

        ws.write_merge(row_no, row_no, 5, 6, _('Insurance fee') + '(' + _('No tax') + ')', table_left_style)
        ws.write(row_no, 7, fee, number_style)
        row_no += 1

        ws.write_merge(row_no, row_no, 5, 6, _('Total amount'), table_left_style)
        ws.write(row_no, 7, total, number_style)
        row_no += 1

        row_no += 1
        ws.write_merge(row_no, row_no, 4, 7, _('We will charge you as follows.'), common_style)

        row_no += 1
        ws.write(row_no, 0, _('Shipping date'), common_style)
        ws.write(row_no, 1, shipping_date, common_style)
        ws.write(row_no + 1, 0, _('Opening date'), common_style)
        ws.write(row_no + 1, 1, opening_date, common_style)
        ws.write(row_no + 2, 0, _('Payment method'), common_style)
        ws.write(row_no + 2, 1, str(dict(PAYMENT_METHOD_CHOICES)[payment_method]), common_style)
        
        ws.write_merge(row_no, row_no + 4, 4, 4, _('Payment breakdown'), table_center_style)

        milestone_formset = MilestoneFormSet(
            self.request.POST,
            prefix='milestone'
        )
        
        table_date_style.num_format_str = 'yyyy/mm/dd' if self.request.LANGUAGE_CODE == 'ja' else 'mm/dd/yyyy'
        idx = 0
        for form in milestone_formset.forms:
            form.is_valid()
            date = form.cleaned_data.get('date')
            amount = form.cleaned_data.get('amount')
            
            ws.write(row_no + idx, 5, _(ordinal(idx + 1)), table_center_style)
            ws.write(row_no + idx, 6, date, table_date_style)
            ws.write(row_no + idx, 7, amount, table_left_style)
            idx += 1
        row_no += 5
       
        row_no += 1
        ws.write(row_no, 0, _('Transfer account'), common_style)
        ws.write_merge(row_no, row_no, 1, 7, transfer_account, common_style)
        row_no += 1
        ws.write(row_no, 0, _('Person in charge'), common_style)
        ws.write_merge(row_no, row_no, 1, 3, person_in_charge, common_style)
        ws.write(row_no, 4, _('Confirmor'), common_style)
        ws.write_merge(row_no, row_no, 5, 7, confirmor, common_style)

        wb.save(response)
        return response
