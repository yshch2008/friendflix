
#coding:utf-8
import time, datetime, traceback, sys
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant

from constants.account_test import account_id
from constants.account_test import qmt_path

from utils.xtUtil import _to_qmt_code, merge_kdata, get_first_timestamp_of_today, time_to_stamp
from utils.algorism import *
from utils.lidu import lidu
from services.tradeService import *
from services.cacheService import *

def simpleStart():
    # if neet to buy or sell
    to_trade = False

    # 创建资金账号为 xxxxxx 的证券账号对象
    xt_trader = init_xt_trader()
    # 关注列表
    stock_list = {"002273":{"name":"水晶光电", "action_type": "buy", "per_amo": 60000, "max_amo": 130000},
                   "300843":{"name":"胜蓝股份" , "action_type": "sell","per_percent": 100, "per_amo": 60000, "max_amo": 130000},
                    "300176":{"name":"派生科技" , "action_type": "sell","per_percent": 100, "per_amo": 60000, "max_amo": 130000}}
    stock_full_code_list = []
    # 取关列表
    # 使用分钟订阅数据计算信号, 后期改为订阅实时数据
    period = '1m'
    min_data = {}
    signal_data = {}
    def on_data(datas):
        nonlocal min_data
        for stock_full_code, data in datas.items():
            # 数据存起来
            # min_data[stock_full_code] = pd.DataFrame(data)
            merge_kdata(min_data, data)
            kdata_signals = lidu(min_data[stock_full_code])
            signal_data[stock_full_code] = kdata_signals
            
            if kdata_signals['买入信号'].iloc[-1] > 0:
                if to_trade:
                    # such as buy 100 stocks of 600xxx at 10
                    vol = 6099 / 100 / data['close'][-1]
                    price = data['close'][-1]

                    async_seq = xt_trader.order_stock_async(
                        acct,
                        stock_full_code,
                        xtconstant.STOCK_BUY,
                        vol,
                        xtconstant.FIX_PRICE,
                        price,
                        'strategy_name_sell',
                        stock_full_code
                        )
                    print('async_seq', async_seq)
                else:
                    print("买入信号触发, 不实际操作")
                    
                if kdata_signals['卖出信号'].iloc[-1] > 0:
                    if to_trade:
                        # such as buy 100 stocks of 600xxx at 10
                        vol = data['openInt'][-1]
                        price = data['close'][-1]

                        async_seq = xt_trader.order_stock_async(
                            acct,
                            stock_full_code,
                            xtconstant.STOCK_SELL,
                            vol,
                            xtconstant.FIX_PRICE,
                            price,
                            'strategy_name_sell',
                            stock_full_code
                            )
                        print('async_seq', async_seq)
                    else:
                        print("卖出信号触发, 不实际操作")
            else:
                print(signal_data)
            
            
    # 单股订阅分钟K
    # for stockCode, data in buying_list.items():
    #     full_stock_code = _to_qmt_code(stockCode)
    #     xtdata.subscribe_quote(full_stock_code, period=period,count= 240, callback= on_data)
    
    # for stockCode, data in selling_list.items():
    #     xtdata.subscribe_quote(_to_qmt_code(stockCode), period=period,  end_time='', count= 240, callback= on_data)
    #     #xtdata.subscribe_quote(_to_qmt_code(stockCode), period=period, start_time='', end_time='', count=0, callback= on_data)
    
    day_begin_time = get_first_timestamp_of_today()
    for stock_code in stock_list:
        stock_full_code = _to_qmt_code(stock_code)
        stock_full_code_list.append(stock_full_code)
        min_data[stock_full_code] = []
        now = time_to_stamp(time.time())
        
        if len(min_data[stock_full_code]) < 1:
            xtdata. download_history_data2(stock_list= stock_full_code_list, period='1m', start_time=day_begin_time)
            res = xtdata. get_market_data(stock_list=stock_full_code_list, period='1m', start_time=day_begin_time)
            print(res)
            
            
            his_data = xtdata.download_history_data(stock_code=stock_full_code, period=period, start_time=day_begin_time, end_time=now)
            print(his_data)
            # min_data[stock_full_code] = xtdata.get_market_data(field_list=[], stock_list = [stock_full_code], period=period, start_time=day_begin_time, end_time=now, count=-1, dividend_type='front', fill_data=True)
            # print(min_data[stock_full_code])
            # level2实时行情
            l2_datas = xtdata.get_l2_quote([], stock_full_code, day_begin_time, now, -1)
            print(l2_datas)

    
    # 订阅全推行情
    book_tickData = xtdata.subscribe_whole_quote(code_list= stock_full_code_list, callback=on_data)
    
    
    xtdata.run()
    
    
