import time, datetime, traceback, sys
from xtquant.xttype import StockAccount
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant import xtconstant


from constants.account_id import *
from cacheService import *
account = StockAccount(account_id, 'STOCK')

xt_trader = None
on_road_dict = {} # { full_code: { [direction: sell, buy]: { sys_id:{signal, type:"sync, async", price, vol, , status: "on_road"}  }}}
finished_dict ={}
cancelled_dict = {}

# async_buy, -- used by confirm_on_up
def async_buy(full_code, price):
    direction = xtconstant.STOCK_BUY
    max_amo = get_max_allow_amo(full_code, direction)
    
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
    amo = get_single_order_amo(full_code, direction)
    amo = split_amo_limit if amo == None else amo
    
    # 判断是否继续买入
    if max_amo < holding_amo + onroad_amo + amo:
        return
    
    
    if amo/ price < 100: # 金额不够1手, 下单1手, 特殊情况, 后续完善 # TODO
        amo = price * 100
        
        # 写入 on_road_dict
        on_road_dict[full_code][direction][seq] = None
        seq = xt_trader.order_stock_async(account, full_code, direction, amo/ price, xtconstant.FIX_PRICE, price, 'async_buy_too_expensive', '不够1手, 下单1手')
        
    else:
        rest_amo = amo
        while rest_amo > split_amo_limit:
            single_count = int(split_amo_limit/ price/ 100) * 100
            if rest_amo < split_amo_limit * 2:
                single_count = int(rest_amo/ price/ 100) * 100 # 整手, 剩余所有的额度
                
            # 写入 on_road_dict
            on_road_dict[full_code][direction][seq] = None
            seq = xt_trader.order_stock_async(account, full_code, direction, single_count, xtconstant.FIX_PRICE, price, 'async_buy', '拆单')

            rest_amo -= single_count * price
            
# sync_buy, used by static and signals, will not split order
def sync_buy(full_code, price):
    direction = xtconstant.STOCK_BUY
    max_amo = get_max_allow_amo(full_code, direction)
    
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
    amo = get_single_order_amo(full_code, direction)
    amo = split_amo_limit if amo == None else amo
    
    # 判断是否继续买入
    if max_amo < holding_amo + amo:
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
                is_valued_cancel = waiting_count * item['price'] >= split_amo_limit * 1.1  # 未成交金额满足再下一单
                
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
    vol = 6099 / 100 / data['close'][-1]
    price = data['close'][-1]

    async_seq = xt_trader.order_stock_async(
        account,
        full_code,
        xtconstant.STOCK_SELL,
        vol,
        xtconstant.FIX_PRICE,
        price,
        'strategy_name_sell',
        full_code
        )
    print('async_seq', async_seq)
                    

class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        连接断开
        :return:
        """
        print("connection lost")

    def on_stock_order(self, order):
        """
        委托回报推送
        :param order: XtOrder对象
        :return:
        """
        print("我是委托回报推送")
        print(order.stock_code, order.order_status, order.order_sysid)

    def on_stock_asset(self, asset):
        """
        资金变动推送  注意，该回调函数目前不生效
        :param asset: XtAsset对象
        :return:
        """
        print("on asset callback")
        print(asset.account_id, asset.cash, asset.total_asset)

    def on_stock_trade(self, trade):
        """
        成交变动推送
        :param trade: XtTrade对象
        :return:
        """
        print("已经成交！！！")
        self.handle_on_stock_trade(trade)
        print(trade.account_id, trade.stock_code, trade.order_id)

    def on_stock_position(self, position):
        """
        持仓变动推送  注意，该回调函数目前不生效
        :param position: XtPosition对象
        :return:
        """
        print("on position callback")
        print(position.stock_code, position.volume)

    def on_order_error(self, order_error):
        """
        委托失败推送
        :param order_error:XtOrderError 对象
        :return:
        """
        print("on order_error callback")
        print(order_error.order_id, order_error.error_id, order_error.error_msg)

    def on_cancel_error(self, cancel_error):
        """
        撤单失败推送
        :param cancel_error: XtCancelError 对象
        :return:
        """
        print("on cancel_error callback")
        print(cancel_error.order_id, cancel_error.error_id, cancel_error.error_msg)

    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse 对象
        :return:
        """
        print("已经下单！！！！")

        print(response.account_id)
        self.handle_order_async_response(response)

        print(response.account_id, response.order_id, response.seq, response.order_remark)

    def on_account_status(self, status):
        """
        :param response: XtAccountStatus 对象
        :return:
        """
        print("on_account_status")
        print(status.account_id, status.account_type, status.status)

    def on_cancel_order_stock_async_response(self, response):
        """
        :param response: XtCancelOrderResponse 对象
        :return:
        """
        self.handle_cancel_respond(response)
        print('异步撤单回报')

    def handle_order_async_response(self, response):
        '''
        异步下单回报推送处理
        :return:
        '''
        order_remark = response.order_remark
        side = order_remark[:1]
        code = order_remark[1:]
        if (side == 'b'):
            if (self.order_live_dict[code]['order_status'] == BUY_ORDER_TBD):
                self.order_live_dict[code]['order_status'] = BUY_ORDER_PD
                self.order_live_dict[code].update({'buy_order_id': response.order_id})
                # 新增1
                if ('wait_epoach' not in self.order_live_dict[code]):
                    self.order_live_dict[code].update({'wait_epoach': 0})
                else:
                    self.order_live_dict[code]['wait_epoach'] = 0


        else:
            if (self.order_live_dict[code]['order_status'] == SELL_ORDER_TBD):
                self.order_live_dict[code]['order_status'] = SELL_ORDER_PD
                self.order_live_dict[code].update({'sell_order_id': response.order_id})
                if ('wait_epoach' not in self.order_live_dict[code]):
                    self.order_live_dict[code].update({'wait_epoach': 0})
                else:
                    self.order_live_dict[code]['wait_epoach'] = 0

    def handle_on_stock_trade(self, trade):
        '''
        成交回报推送处理
        :return:
        '''
        order_remark = trade.order_remark
        side = order_remark[:1]
        code = order_remark[1:]
        if (side == 'b'):
            if ('buy_order_id' in self.order_live_dict[code]):
                self.order_live_dict[code]['order_status'] = POS
                self.order_live_dict[code].update({'buy_traded_price': trade.traded_price})
                self.order_live_dict[code].update({'pos_epoach':0})

            else:
                self.order_live_dict[code].update({'buy_order_id': trade.order_id})
                self.order_live_dict[code]['order_status'] = POS
                self.order_live_dict[code].update({'buy_traded_price': trade.traded_price})
                self.order_live_dict[code].update({'pos_epoach':0})


            if ('wait_epoach' in self.order_live_dict[code]):
                self.order_live_dict[code]['wait_epoach'] = 0
        else:
            if ('sell_order_id' in self.order_live_dict[code]):
                self.order_live_dict[code]['order_status'] = END
            else:
                self.order_live_dict[code].update({'sell_order_id': trade.order_id})
                self.order_live_dict[code]['order_status'] = END
            if ('wait_epoach' in self.order_live_dict[code]):
                self.order_live_dict[code]['wait_epoach'] = 0

    def handle_cancel_respond(self, response):
        buy_cancel_dict = {k: v for k, v in self.order_live_dict.items() if v['buy_order_id'] == response.order_id}
        sell_cancel_dict = {k: v for k, v in self.order_live_dict.items() if v['sell_order_id'] == response.order_id}
        if (len(buy_cancel_dict) == 1):
            code = list(buy_cancel_dict.keys())[0]
            if (self.order_live_dict[code]['order_status'] == BUY_ORDER_CC_TBD):
                if (response.cancel_result == 0):
                    self.order_live_dict[code]['order_status'] = END
                else:
                    self.order_live_dict[code]['order_status'] = POS
        elif (len(sell_cancel_dict) == 1):
            code = list(buy_cancel_dict.keys())[0]
            if (self.order_live_dict[code]['order_status'] == SELL_ORDER_CC_TBD):
                if (response.cancel_result == 0):
                    self.order_live_dict[code]['order_status'] = POS
                else:
                    self.order_live_dict[code]['order_status'] = END
        else:
            print('撤单order_id在buy和sell均不存在')

    '''
       回调类函数-------------------------------------------------------------------------------------------------------
    '''


def init_xt_trader():
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
