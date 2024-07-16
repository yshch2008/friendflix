from utils.collectionUtil import *
from constants.config import schedule_data

# { full_code, direction, signal: {max_allow_amo, single_order_amo, single_order_percent}}
# class ScheduleService(object):
def get_max_allow_amo(full_code, direction, strategy_name):
    indexs = [full_code, direction, strategy_name]
    model = getSubDict(schedule_data, indexs)
    return model['max_allow_amo']

def get_single_order_amo(full_code, direction, strategy_name):
    indexs = [full_code, direction, strategy_name]
    model = getSubDict(schedule_data, indexs)
    return model['single_order_amo']

def create_schedule(schedule):
    for full_code, directions in schedule.items():
        for xt_direction, strategies in directions.items():
            for strategy_name, model in strategies.items():
                schedule_data[full_code] = {
                    xt_direction:{
                        strategy_name: model
                    }
                }
    
    
def read_schedule(full_code, xt_direction, strategy_name):
    indexs = [full_code, xt_direction, strategy_name]
    stock_model = getSubDict(schedule_data, indexs)
    return stock_model

def delete_schedule(full_code, direction, strategy_name):
    mirror = schedule_data[full_code][direction][strategy_name]
    del schedule_data[full_code][direction][strategy_name]
    return mirror

def fetch_all_schedule():
    return schedule_data