import time
from django.utils.translation import gettext as _
from contracts.models import (
    TraderSalesContract, TraderPurchasesContract, HallSalesContract, HallPurchasesContract
)
from listing.models import ExportHistory

def generate_contract_id(prefix='01'):
    year = time.strftime("%y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    contract_id = prefix + year + month + day
    count = TraderSalesContract.objects.count()
    count += TraderPurchasesContract.objects.count()
    count += HallSalesContract.objects.count()
    count += HallPurchasesContract.objects.count()
    contract_id += str(count + 1).zfill(5)
    return contract_id

def generate_random_number():
    return int(time.time() * 100)

def ordinal(num):
    return "%d%s" % (num,"tsnrhtdd"[(num//10%10!=1)*(num%10<4)*num%10::4])

def date_dump(date, lang_code):
    if lang_code == 'en':
        return date.strftime('%m/%d/%Y')
    return date.strftime('%Y/%m/%d')

def get_shipping_date_label(mode):
    if mode == 'R':
        return _('Receipt date')
    elif mode == 'C':
        return _('ID Change date')
    return _('Delivery date')

def log_export_operation(user_id, export):
    data = {
        'user_id': user_id,
        'export': export
    }
    ExportHistory.objects.create(**data)
