import time
import datetime

from xtquant import xtdata
from xtquant import xtconstant

from constants.config import period, min_data, index_data

from services.cacheService import *
from services.scheduleService import *
from services.strategyService import calculate

from utils.xtUtil import *
from utils.algorism import *

# min_data = {}


def prepare_data():
    subscribed_seq = get_subscribed_seq()
    if subscribed_seq != None and subscribed_seq != "":
        xtdata.unsubscribe_quote()

    index_data["begin_timestamp"] = get_first_timestamp_of_today()

    # 订阅全推行情
    book_tickData = xtdata.subscribe_whole_quote(code_list=[index_data['emotion_stock_code']], callback=on_data)
    create_subscribed_seq(book_tickData)
    xtdata.run()
    # TODO
    # for stock_full_code, data in res.items():
    # l2_datas = xtdata.get_l2_quote([], stock_full_code, day_begin_time, now, -1)
    # for stock_code in stock_list:
    #     l2_datas = xtdata.get_l2_transaction([], key, kData_begin_timestamp, now_timestamp, -1)
    #     print(l2_datas)
    #     # l2_datas =xtdata.get_l2_order(field_list=[], stock_code= key, start_time=kData_begin_timestamp, end_time=now_timestamp, count=-1)

    # print(book_tickData)


def on_data(tick_data):
    emotion_stock_model = tick_data[index_data['emotion_stock_code']]
    # maybe use it for control weight we buy in the future
    index_data['emotion_flag'] = True if abs(emotion_stock_model['lastPrice'] / emotion_stock_model['lastClose'] - 1) < 0.0075 else False
    
    stock_list = list(fetch_all_schedule().keys())
    now_timestamp = time_to_stamp_str(datetime.datetime.now())

    xtdata.download_history_data2(
        stock_list=stock_list,
        period=period,
        start_time=index_data["begin_timestamp"],
        end_time=now_timestamp,
        callback=history_callback,
    )
    kdata = xtdata.get_local_data(
        field_list=[],
        stock_list=stock_list,
        period=period,
        start_time=index_data["begin_timestamp"],
        end_time=now_timestamp,
        count=-1,
        dividend_type="front",
        fill_data=True,
    ) 
    calculate(update_stock_min_data(kdata))


def read_stock_min_data(full_code):
    return None if full_code not in min_data else min_data[full_code]


def create_stock_min_data(full_code, data_list):
    if full_code not in min_data:
        min_data[full_code] = data_list
    return None if full_code not in min_data else min_data[full_code]


def update_stock_min_data(xt_data):
    for full_code, data in xt_data.items():
        min_data[full_code] = xt_data[full_code]
    return min_data


def append_stock_min_data(full_code, data):
    if full_code not in min_data:
        return
    data_list = min_data[full_code]
    data_list.append(data)
    return None if full_code not in min_data else min_data[full_code]


def fetch_min_data():
    return min_data


def history_callback(download_info):
    pass
    # print(download_info)
    # download min k data for stocks to calculate signal


def merge_kdata(tick_data: dict):
    for full_code, data in min_data.items():
        if full_code in tick_data:
            stock_tick_data = tick_data[full_code]
            if stock_tick_data["time"] == min_data[full_code].iloc[-1]["time"]:
                print("duplicate tick")
                continue
            stock_tick_data["askPrice"] = stock_tick_data["askPrice"][0:1]
            stock_tick_data["bidPrice"] = stock_tick_data["bidPrice"][0:1]
            stock_tick_data["askVol"] = stock_tick_data["askVol"][0:1]
            stock_tick_data["bidVol"] = stock_tick_data["bidVol"][0:1]
            stock_tick_data["close"] = stock_tick_data["lastPrice"]
            stock_tick_data["readable_time"] = timestamp_to_stamp_str(
                stock_tick_data["time"]
            )
            if len(min_data[full_code]) == 0:  # add as a new min_k_data
                min_data[full_code] = pd.concat(
                    [min_data[full_code], pd.DataFrame(stock_tick_data)],
                    ignore_index=True,
                )
            elif (
                stock_tick_data["time"] - data.iloc[-1]["time"] < 60000
            ):  # merge as one min_k_data
                stock_tick_data["time"] = min_data[full_code].iloc[-1]["time"]
                min_data[full_code] = min_data[full_code].drop(
                    min_data[full_code].tail(1).index
                )
                min_data[full_code] = pd.concat(
                    [min_data[full_code], pd.DataFrame(stock_tick_data)],
                    ignore_index=True,
                )
                # min_data[full_code].loc[-1] = pd.DataFrame(stock_tick_data)
            else:  # add as a new min_k_data
                # print('merge_kdata  data', data)
                # print('merge_kdata  stock_tick_data', stock_tick_data)
                # data.append(pd.DataFrame(stock_tick_data))
                min_data[full_code] = pd.concat(
                    [min_data[full_code], pd.DataFrame(stock_tick_data)],
                    ignore_index=True,
                )
                # data = data.append(stock_tick_data, ignore_index=True)


# def merge_kdata(tick_data:  dict):
#     for full_code, data in min_data.items():
#         # print('merge_kdata', full_code, data)
#         if full_code in tick_data:
#             stock_tick_data = tick_data[full_code]
#             if stock_tick_data['time'] == data.iloc[-1]['time']:
#                 print('duplicate tick')
#                 continue
#             print('merge_kdata  data')
#             print(data)
#             stock_tick_data['close'] = stock_tick_data['lastPrice']
#             stock_tick_data['readable_time'] = timestamp_to_stamp_str(stock_tick_data['time'])
#             if len(data) == 0:# add as a new min_k_data
#                 print('add as a new min_k_data 1' )
#                 data = pd.concat([data ,pd.DataFrame(stock_tick_data)], ignore_index=True)
#             elif stock_tick_data['time'] - data.iloc[-1]['time'] < 60000: # merge as one min_k_data
#                 print('merge as one min_k_data' )
#                 stock_tick_data['time'] = data.iloc[-1]['time']
#                 data.iloc[-1] = pd.DataFrame(stock_tick_data)
#             else: # add as a new min_k_data
#                 print('add as a new min_k_data 2' )
#                 # print('merge_kdata  data', data)
#                 # print('merge_kdata  stock_tick_data', stock_tick_data)
#                 # data.append(pd.DataFrame(stock_tick_data))
#                 data = pd.concat([data ,pd.DataFrame(stock_tick_data)], ignore_index=True)
#                 # data = data.append(stock_tick_data, ignore_index=True)

#             print('merge_kdata  data')
#             print(data)
