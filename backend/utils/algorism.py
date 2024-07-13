import pandas as pd
import time


def ma(s: pd.Series, window: int = 5) -> pd.Series:
    """

    :param s:
    :param window:
    :return:
    """
    return s.rolling(window=window, min_periods=window).mean()

def ema(s: pd.Series, window: int = 12) -> pd.Series:
    return s.ewm(span=window, adjust=False, min_periods=window).mean()

def live_or_dead(x):
    if x:
        return 1
    else:
        return -1
    
def macd(
    s: pd.Series,
    slow: int = 26,
    fast: int = 12,
    n: int = 9,
    return_type: str = "df",
    normal: bool = False,
    count_live_dead: bool = False,
):
    # 短期均线
    ema_fast = ema(s, window=fast)
    # 长期均线
    ema_slow = ema(s, window=slow)

    # 短期均线 - 长期均线 = 趋势的力度
    diff: pd.Series = ema_fast - ema_slow
    # 力度均线
    dea: pd.Series = diff.ewm(span=n, adjust=False).mean()

    # 力度 的变化
    m: pd.Series = (diff - dea) * 2

    # normal it
    if normal:
        diff = diff / s
        dea = dea / s
        m = m / s

    if count_live_dead:
        live = (diff > dea).apply(lambda x: live_or_dead(x))
        bull = (diff > 0) & (dea > 0)
        live_count = live * (live.groupby((live != live.shift()).cumsum()).cumcount() + 1)

    if return_type == "se":
        if count_live_dead:
            return diff, dea, m, live, bull, live_count
        return diff, dea, m
    else:
        if count_live_dead:
            return pd.DataFrame(
                {"diff": diff, "dea": dea, "macd": m, "live": live, "bull": bull, "live_count": live_count}
            )
        return pd.DataFrame({"diff": diff, "dea": dea, "macd": m})
    
def tickToMin():
    # 获得当前时间时间戳
    now = int(time.time())
    #转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print( )