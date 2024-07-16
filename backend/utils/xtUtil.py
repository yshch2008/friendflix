

import time
import pandas as pd
import numpy as np

def decode_entity_id(entity_id: str):
    """
    decode entity id to entity_type, exchange, code

    :param entity_id:
    :return: tuple with format (entity_type, exchange, code)
    """
    result = entity_id.split("_")
    entity_type = result[0]
    exchange = result[1]
    code = "".join(result[2:])
    return entity_type, exchange, code



def timestamp_to_stamp_str(xtTime):
    if type(xtTime) == int:
        return time.strftime("%Y%m%d%H%M%S", time.localtime(xtTime/ 1000))
    if type(xtTime) == float:
        return time.strftime("%Y%m%d%H%M%S", time.localtime(xtTime))
    if type(xtTime) == np.int64:
        return time.strftime("%Y%m%d%H%M%S", time.localtime(int(xtTime/1000)))
        
    print ('Meet error when convert timestamp_to_stamp_str', type(xtTime))
    return None


def time_to_stamp_str(xtTime):
    return xtTime.strftime("%Y%m%d%H%M%S")


def to_pd_timestamp(the_time) -> pd.Timestamp:
    if the_time is None:
        return None
    if type(the_time) == int:
        return pd.Timestamp.fromtimestamp(the_time / 1000)

    if type(the_time) == float:
        return pd.Timestamp.fromtimestamp(the_time)

    return pd.Timestamp(the_time)

def get_first_timestamp_of_today():
    # 获得当前时间时间戳
    now = int(time.time())
    #转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    result = f"{otherStyleTime} 09:30:00"
    return result
    
def merge_kdata(min_data: dict, tick_data:  dict):
    for stock_full_code, data in min_data:
        if stock_full_code in tick_data:
            tick_kData = tick_data[stock_full_code]
            tick_kData['close'] = tick_kData['lastPrice']
            if len(data) == 0:
                data.append(tick_kData)
            elif data[-1]['time'] - tick_data['time'] >= 60 * 1000:
                data.append(tick_kData)
            else:
                tick_kData['time'] = data[-1]['time']
                tick_kData['amo'] += data[-1]['amo']
                tick_kData['vol'] += data[-1]['vol']
                data[-1] = tick_kData