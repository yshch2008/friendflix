from utils.collectionUtil import *

schedule_stock_dict = {}# { full_code, direction, signal: {max_allow_amo, single_order_amo, single_order_percent}}


def get_max_allow_amo(full_code, direction):
    indexs = [full_code, direction]
    stock_model = getSubDict(schedule_stock_dict, indexs)
    return stock_model['max_allow_amo']

def get_single_order_amo(full_code, direction):
    indexs = [full_code, direction]
    stock_model = getSubDict(schedule_stock_dict, indexs)
    return stock_model['single_order_amo']

def create_schedule(full_code, direction, signal, max_allow_amo, single_order_amo, single_order_percent):
    schedule_stock_dict[full_code][direction][signal] = {
        max_allow_amo, single_order_amo, single_order_percent
    }
    return schedule_stock_dict[full_code][direction]

def read_schedule(full_code, direction):
    indexs = [full_code, direction]
    stock_model = getSubDict(schedule_stock_dict, indexs)
    return stock_model

def delete_schedule(full_code, direction):
    mirror = schedule_stock_dict[full_code][direction]
    del schedule_stock_dict[full_code][direction]
    return mirror

def fetch_all_schedule():
    return schedule_stock_dict