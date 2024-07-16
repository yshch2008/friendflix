import time, datetime, traceback, sys
from xtquant.xttype import StockAccount
from xtquant.xttrader import XtQuantTrader
from xtquant import xtconstant


from constants.config import account_id, qmt_path, split_limit, real_trade_switch
from services.scheduleService import fetch_all_schedule
from utils.MyXtQuantTraderCallback import *

account = StockAccount(account_id, 'STOCK')

xt_trader = None
on_road_dict = {} # { full_code: { [direction: sell, buy]: { sys_id:{signal, type:"sync, async", price, vol, , status: "on_road"}  }}}
finished_dict ={}
cancelled_dict = {}

def trade(full_code, direction, strategy_name, price, sync_trade):
    schedules = fetch_all_schedule()
    if full_code not in schedules:
        print('Illegal stock code found: ', full_code)
    strategy = schedules[full_code][direction][strategy_name]
    if not real_trade_switch:
        print('Real trade is not available: ', full_code, direction, strategy_name, price, sync_trade)
        return
    if direction == xtconstant.STOCK_BUY:
        if sync_trade:
            sync_buy(full_code, price, strategy['max_amo'], strategy['single_amo'])
        else:
            async_buy(full_code, price, strategy['max_amo'], strategy['single_amo'])
    elif direction == xtconstant.STOCK_SELL:
        if sync_trade:
            sync_sell(full_code, price)
        else:
            pass
            
        

# async_buy, -- used by confirm_on_up
def async_buy(full_code, price, max_amo, single_amo):
    direction = xtconstant.STOCK_BUY
    
    # 查询在途买单和持仓总合
    on_road_stock_list = xt_trader.query_stock_orders(account, cancelable_only = True)
    onroad_amo=0
    if len(on_road_stock_list) > 0:
        for item in on_road_stock_list:
            if item['stock_code'] == full_code and item['order_type'] == direction:
                onroad_amo = (item['order_volume'] - item['traded_volume']) * item['price']
                
    holding_stock_list = xt_trader.query_stock_positions(account)
    holding_amo = 0
    if len(holding_stock_list) > 0:
        for item in holding_stock_list:
            if item['stock_code'] == full_code:
                holding_amo = item['volume'] * item['avg_price'] # 持仓数量 * 买入成本
                
    # 读取单笔购买金额, 如果没有填就用最小金额
    amo = single_amo
    amo = split_limit if amo == 0 else amo
    
    # 判断是否继续买入
    if max_amo < holding_amo + onroad_amo + amo:
        print('超过持仓限制')
        return
    
    if amo/ price < 100: # 金额不够1手, 下单1手, 特殊情况, 后续完善 # TODO
        amo = price * 100
        
        # 写入 on_road_dict
        on_road_dict[full_code][direction][seq] = None
        seq = xt_trader.order_stock_async(account, full_code, direction, amo/ price, xtconstant.FIX_PRICE, price, 'async_buy_too_expensive', '不够1手, 下单1手')
        
    else:
        rest_amo = amo
        while rest_amo > split_limit:
            single_count = int(split_limit/ price/ 100) * 100
            if rest_amo < split_limit * 2:
                single_count = int(rest_amo/ price/ 100) * 100 # 整手, 剩余所有的额度
                
            # 写入 on_road_dict
            on_road_dict[full_code][direction][seq] = None
            seq = xt_trader.order_stock_async(account, full_code, direction, single_count, xtconstant.FIX_PRICE, price, 'async_buy', '拆单')

            rest_amo -= single_count * price
            
# sync_buy, used by static and signals, will not split order
def sync_buy(full_code, price, max_amo, single_amo):
    direction = xtconstant.STOCK_BUY    
    # 查询并取消在途买单
    on_road_stock_list = xt_trader.query_stock_orders(account, cancelable_only = True)
    if len(on_road_stock_list) > 0:
        for item in on_road_stock_list:
            if item['stock_code'] == full_code and item['order_type'] == direction:
                xt_trader.cancel_order_stock(account, item['order_id'])
                
    # 查询持仓总合
    holding_stock_list = xt_trader.query_stock_positions(account)
    holding_amo = 0
    if len(holding_stock_list) > 0:
        for item in holding_stock_list:
            if item['stock_code'] == full_code:
                holding_amo = item['volume'] * item['avg_price'] # 持仓数量 * 买入成本
                
    # 读取单笔购买金额, 如果没有填就用最小金额
    amo = single_amo
    amo = split_limit if amo == 0 else amo
    
    # 判断是否继续买入
    if max_amo < holding_amo + amo:
        print('超过持仓限制')
        return
    vol = int(amo/ price/ 100) * 100
    follow_buy_sell(full_code, direction, vol, price)

# async_sell, -- 看起来用不到
# sync_sell, used by static, stop_poor_order and signals, will not split order
def sync_sell(full_code, price):
    direction = xtconstant.STOCK_SELL
    
    # 查询并取消在途
    on_road_stock_list = xt_trader.query_stock_orders(account, cancelable_only = True)
    if len(on_road_stock_list) > 0:
        for item in on_road_stock_list:
            if item['stock_code'] == full_code and item['order_type'] == direction:
                xt_trader.cancel_order_stock(account, item['order_id'])
                
    # 查询持仓总合
    holding_stock_list = xt_trader.query_stock_positions(account)
    holding_vol = 0
    if len(holding_stock_list) > 0:
        for item in holding_stock_list:
            if item['stock_code'] == full_code:
                holding_vol = item['volume']  # 持仓数量 
                
    follow_buy_sell(full_code, direction, holding_vol, price)
            
    
def follow_buy_sell(full_code, direction, vol, price): # 不拆单, 不成交则重新挂单 # TODO 用最大可能成交(向上挂买足够数量或向下挂卖足够数量)
    order_id = xt_trader.order_stock(account, full_code, direction, vol, xtconstant.FIX_PRICE, price, 'sync_' + direction, '不拆单')
    time.sleep(0.03) # TODO 消除抖动
    # 查询在途委托, 判断是否成交
    on_road_stock_list = xt_trader.query_stock_orders(account, cancelable_only = True)
    if len(on_road_stock_list) > 0:
        for item in on_road_stock_list:
            if item['stock_code'] == full_code and item['order_type'] == direction:
                waiting_count = item['order_volume'] - item['traded_volume']
                
                has_no_traded = item['traded_volume'] == 0 # 完全无成交
                is_valued_cancel = waiting_count * item['price'] >= split_limit * 1.1  # 未成交金额满足再下一单
                
                if item['order_id'] == order_id and (has_no_traded or is_valued_cancel ):
                    xt_trader.cancel_order_stock(account, item['order_id']) # 取消该订单, 重新下单
                    
                    following_cost = 0.01 if direction == xtconstant.STOCK_BUY else -0.01
                    order_id = follow_buy_sell(full_code, direction, waiting_count % 100 + 100, price + following_cost)
    
    # 写入 on_road_dict
    on_road_dict[full_code][direction][order_id] = None
    print(order_id)
    
    return order_id
# TODO
# 维护数据一致性和完整性的东西暂时可以省略

    # 循环查询订单, 直到成交
        # 挂单失败 -- 调用自己, 再次下单, 核买次数 += 1, 挂单价用 A. 核买次数 > 3: MAX(当前价 - 2 * 核买次数 - 1, 卖限价); B. 当前价 - 2 * 核买次数 - 1
        # 部分成交 -- 轮询两次, 调用自己再次下单, 核买次数 += 1
        # 全部成交 -- 
    # such as buy 100 stocks of 600xxx at 10
    # vol = 6099 / 100 / data['close'][-1]
    # price = data['close'][-1]

    # async_seq = xt_trader.order_stock_async(
    #     account,
    #     full_code,
    #     xtconstant.STOCK_SELL,
    #     vol,
    #     xtconstant.FIX_PRICE,
    #     price,
    #     'strategy_name_sell',
    #     full_code
    #     )
    # print('async_seq', async_seq)

def init_xt_trader():
    global xt_trader
    session_id = int(time.time())  # different strategy has different session_id
    
    xt_trader = XtQuantTrader(qmt_path, session_id)

    callback = MyXtQuantTraderCallback()
    xt_trader.register_callback(callback)

    # 启动交易线程
    xt_trader.start()

    # 建立交易连接，返回0表示连接成功
    print('connect, 0 means connected, -1 failed.', xt_trader.connect())

    acct = StockAccount(account_id, 'STOCK')  # STOCK or CREDIT
    # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
    print('trade call_back register, 0 means registered, -1 failed:', xt_trader.subscribe(acct))

    # return xt_trader
