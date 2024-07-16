from services.cacheService import *  
from services.dataService import *  
from services.tradeService import trade
from constants.config import period, min_data, index_data, strategy_data

from utils.xtUtil import *


def calculate(min_data):
    schedules = fetch_all_schedule()
    # for stock_code, min_data_model in min_data.items():
        
    for stock_code, schedule in schedules.items():
        if stock_code not in min_data.keys():
            print('something wrong, missing market data of ', stock_code)
            continue
        kdata_signals = strategy_data['executor'](min_data[stock_code]) # 既有买的, 也有卖的信号, 放在外面避免计算多次
        # kdata_signals = fenshi_lidu(min_data[stock_code]) # 既有买的, 也有卖的信号, 放在外面避免计算多次
        df = kdata_signals.iloc[-1]
        # TODO
        # using loop and reflection to execute every signals:
        # strategy static
        # strategy confirm_on_up
        if df['fenshi_lidu'] == xtconstant.STOCK_BUY or df['fenshi_lidu'] == xtconstant.STOCK_SELL:
            print(timestamp_to_stamp_str(df['time']), df['fenshi_lidu'])
        else:
            print('No trade signal appears for ', stock_code)
            continue
        
        for direction, direction_model in schedule.items():
            for strategy_name, strategy in direction_model.items():
                if strategy_name not in  strategy_data.keys():
                    print('Illegal strategy name')
                    return
                
                now = datetime.datetime.now()
                now_num = now.hour * 100 + now.minute
                # trade(stock_code,direction,strategy_name,df['close'],  strategy_data[strategy_name]['sync_trade']) # 勿开启
                        
                        
                if now_num < strategy['begin_time'] or now_num > strategy['end_time']:
                    print('Illegal time for signal: ' , now_num)
                elif df[strategy_name] == direction: # 死亡交叉, 考虑优化
                    print( df['readable_time'], 'try to trade: ', stock_code, direction, strategy_name)
                    if  strategy_data[strategy_name]["live"]:
                        trade(stock_code,direction,strategy_name,df['close'],  strategy_data[strategy_name]['sync_trade'])
                    else:
                        print('strategy closed now:', strategy_name)
                
        
    
    
def activate_strategy(strategy):
     strategy_data[strategy]['live'] = True
    
def inactivate_strategy(strategy):
     strategy_data[strategy]['live'] = False
    
def read_strategy(strategy):
    return  strategy_data[strategy]
    