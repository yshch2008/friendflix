from xtquant import xtconstant

def short_to_full_code(entity_id):
    split_char = '.'
    exchange = ''
    if entity_id[:2] == '30':
        exchange='SZ'
    elif entity_id[:2] == '00':
        exchange='SZ'
    elif entity_id[:2] == '60':
        exchange='SH'
    return f"{entity_id}{split_char}{exchange}"


def full_to_short_code(qmt_code):
    code, exchange = qmt_code.split(".")
    exchange = exchange.lower()
    return code


def direction_to_xtDirection(direction):
    xt_direction = xtconstant.STOCK_BUY if direction == "buy" else xtconstant.STOCK_SELL
    return xt_direction


def xtDirection_to_direction(direction):
    return 'sell' if direction == xtconstant.STOCK_SELL else "buy"

