
from services.cacheService import *  
from services.dataService import *  
from services.tradeService import trade
from strategies.fenshi_lidu import fenshi_lidu

from utils.xtUtil import *

strategy_dict = {
    'static':{'live': False, 'sync_trade': True},
    'fenshi_lidu':{'live': False, 'sync_trade': True},
    'confirm_on_up':{'live': False, 'sync_trade': False}}
signal_data = {}
        

def calculate(min_data):
    schedules = fetch_all_schedule()
    # for stock_code, min_data_model in min_data.items():
        
    for stock_code, schedule in schedules.items():
        if stock_code not in min_data.keys():
            print('something wrong, missing market data of ', stock_code)
            continue
        kdata_signals = fenshi_lidu(min_data[stock_code]) # 既有买的, 也有卖的信号, 放在外面避免计算多次
        signal_data[stock_code] = kdata_signals
        df = kdata_signals.iloc[-1]
        # TODO
        # using loop and reflection to execute every signals:
        # strategy static
        # strategy confirm_on_up
        df['readable_time'] = timestamp_to_stamp_str(df['time'])
        if df['fenshi_lidu'] != None:
            print(df['readable_time'], df['fenshi_lidu'])
        
        for direction, direction_model in schedule.items():
            for strategy_name, strategy in direction_model.items():
                if strategy_name not in strategy_dict.keys():
                    print('Illegal strategy name')
                    return
                
                now = datetime.datetime.now()
                now_num = now.hour * 100 + now.minute
                # trade(stock_code,direction,strategy_name,df['close'], strategy_dict[strategy_name]['sync_trade']) # 勿开启
                        
                        
                if now_num < strategy['begin_time'] or now_num > strategy['end_time']:
                    print('Illegal time for signal: ' , now_num)
                elif df[strategy_name] == direction: # 死亡交叉, 考虑优化
                    print( df['readable_time'], 'try to trade: ', stock_code, direction, strategy_name)
                    if strategy_dict[strategy_name]["live"]:
                        trade(stock_code,direction,strategy_name,df['close'], strategy_dict[strategy_name]['sync_trade'])
                    else:
                        print('strategy closed now:', strategy_name)
                
        
    
    
def activate_strategy(strategy):
    strategy_dict[strategy]['live'] = True
    
def inactivate_strategy(strategy):
    strategy_dict[strategy]['live'] = False
    
def read_strategy(strategy):
    return strategy_dict[strategy]
    