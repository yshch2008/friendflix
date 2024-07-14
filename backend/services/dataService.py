import time
import datetime

from xtquant import xtdata

from backend.constants.config import period, real_trade_switch

from services.cacheService import *  
from services.scheduleService import *  

from utils.xtUtil import *
from utils.algorism import *

min_data = {}

def prepare_data():
    subscribed_seq = get_subscribed_seq()
    if subscribed_seq != None and subscribed_seq != '':
        xtdata.unsubscribe_quote()
    stock_list = fetch_all_schedule().keys
    kData_begin_timestamp = ''
    now = datetime.datetime.now()
    if now.weekday == 0:
        fourDayAgo = (now - datetime.timedelta(days = 4))
        kData_begin_timestamp = time_to_stamp(fourDayAgo)
    else:
        twoDayAgo = (now - datetime.timedelta(days = 2))
        kData_begin_timestamp = time_to_stamp(twoDayAgo)
    now_timestamp = time_to_stamp(time.time())
    xtdata. download_history_data2(stock_list= stock_list, period=period, start_time = kData_begin_timestamp)
    res = xtdata.get_market_data(stock_list=stock_list, period=period, start_time=kData_begin_timestamp, end_time = now_timestamp, count=240, fill_data=False )
    print(res)
    # TODO
    # for stock_full_code, data in res.items():
    # l2_datas = xtdata.get_l2_quote([], stock_full_code, day_begin_time, now, -1)
    update_stock_min_data(res)
    # 订阅全推行情
    book_tickData = xtdata.subscribe_whole_quote(code_list= stock_list, callback=on_data)
    print(book_tickData)
    xtdata.run()
    
        # for stock_full_code, data in datas.items():
        #     # 数据存起来
        #     # min_data[stock_full_code] = pd.DataFrame(data)
        #     merge_kdata(fetch_min_data(), data)
            
        #     kdata_signals = lidu(min_data[stock_full_code])
        #     signal_data[stock_full_code] = kdata_signals
            
        #     if kdata_signals['买入信号'].iloc[-1] > 0:
        #         if real_trade_switch:
        #             # such as buy 100 stocks of 600xxx at 10
        #             vol = 6099 / 100 / data['close'][-1]
        #             price = data['close'][-1]

        #             async_seq = xt_trader.order_stock_async(
        #                 acct,
        #                 stock_full_code,
        #                 xtconstant.STOCK_BUY,
        #                 vol,
        #                 xtconstant.FIX_PRICE,
        #                 price,
        #                 'strategy_name_sell',
        #                 stock_full_code
        #                 )
        #             print('async_seq', async_seq)
        #         else:
        #             print("买入信号触发, 不实际操作")
                    
        #         if kdata_signals['卖出信号'].iloc[-1] > 0:
        #             if to_trade:
        #                 # such as buy 100 stocks of 600xxx at 10
        #                 vol = data['openInt'][-1]
        #                 price = data['close'][-1]

        #                 async_seq = xt_trader.order_stock_async(
        #                     acct,
        #                     stock_full_code,
        #                     xtconstant.STOCK_SELL,
        #                     vol,
        #                     xtconstant.FIX_PRICE,
        #                     price,
        #                     'strategy_name_sell',
        #                     stock_full_code
        #                     )
        #                 print('async_seq', async_seq)
        #             else:
        #                 print("卖出信号触发, 不实际操作")
        #     else:
        #         print(signal_data)
            

            
def read_stock_min_data(full_code):
    return None if full_code not in min_data else min_data[full_code]

def create_stock_min_data(full_code, data_list):
    if full_code not in min_data: 
        min_data[full_code] = data_list
    return None if full_code not in min_data else min_data[full_code]

def update_stock_min_data(xt_data):
    min_data = xt_data
    return min_data

def append_stock_min_data(full_code, data):
    if full_code not in min_data: 
        return
    data_list = min_data[full_code]
    data_list.append(data)
    return None if full_code not in min_data else min_data[full_code]

def fetch_min_data():
    return min_data
        
def on_data(tick_data):
        merge_kdata(tick_data)

def merge_kdata(tick_data:  dict):
    for full_code, data in min_data:
        if full_code in tick_data:
            tick_kData = tick_data[full_code]
            tick_kData['close'] = tick_kData['lastPrice']
            tick_kData['readable_time'] = time_to_stamp(tick_data['time'])
            if len(data) == 0:
                data.append(tick_kData)
            elif data[-1]['time'] - tick_data['time'] >= 60 * 1000:
                data.append(tick_kData)
            else:
                tick_kData['time'] = data[-1]['time']
                tick_kData['amo'] += data[-1]['amo']
                tick_kData['vol'] += data[-1]['vol']
                data[-1] = tick_kData