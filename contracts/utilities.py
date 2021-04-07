import time
from contracts.models import *

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

def ordinal(num):
    return "%d%s" % (num,"tsnrhtdd"[(num//10%10!=1)*(num%10<4)*num%10::4])