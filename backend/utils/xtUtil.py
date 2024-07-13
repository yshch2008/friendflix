

import time
import pandas as pd

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


def _to_qmt_code(entity_id):
    split_char = '.'
    exchange = ''
    if entity_id[:2] == '30':
        exchange='SZ'
    elif entity_id[:2] == '00':
        exchange='SZ'
    elif entity_id[:2] == '60':
        exchange='SH'
    return f"{entity_id}{split_char}{exchange}"


def _to_shortcode(qmt_code):
    code, exchange = qmt_code.split(".")
    exchange = exchange.lower()
    return code

def _to_zvt_entity_id(qmt_code):
    code, exchange = qmt_code.split(".")
    exchange = exchange.lower()
    return f"stock_{exchange}_{code}"


def time_to_stamp(xtTime):
    # 获得当前时间时间戳
    now = int(xtTime)
    #转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print(otherStyleTime)
    return otherStyleTime


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