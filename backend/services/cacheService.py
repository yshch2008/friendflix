from utils.collectionUtil import *

schedule_stock_dict = {}# { full_code: { [direction: sell, buy]: { max_allow_amo, single_order_amo, single_order_percent, monitor_signal:['simple', 'confirm_on_lidu', 'confirm_on_up'] }}}

def get_max_allow_amo(full_code, direction):
    indexs = [full_code, direction]
    stock_model = getSubDict(schedule_stock_dict, indexs)
    return stock_model['max_allow_amo']

def get_single_order_amo(full_code, direction):
    indexs = [full_code, direction]
    stock_model = getSubDict(schedule_stock_dict, indexs)
    return stock_model['single_order_amo']