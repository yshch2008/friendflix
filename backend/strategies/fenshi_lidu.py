import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from  MyTT import *
from  utils.yourTT import *
from xtquant import xtconstant


# 读取股票数据
def fenshi_lidu(kData_list) -> pd.DataFrame:
    df = pd.DataFrame(kData_list)
    #基础数据定义
    TIMESTAMP = df.time.values
    CLOSE=df.close.values 
    OPEN=df.open.values  
    HIGH=df.high.values
    VOL=df.volume.values.sum()
    AMO=df.amount.values.sum()
    PRE=df.preClose.values
    
    AVE = AMO/ VOL/ 100
    print("AVE: ", AVE)
    均价向上运行 = (CLOSE > PRE) & (CLOSE/ AVE > 1 + 15/ 1000)
    均价向下运行 = (CLOSE < PRE) & (CLOSE/ AVE < 1 - 15/ 1000)
    
    上穿信号 = CROSS(SUM(均价向上运行,0),0.5)
    下穿信号 =  CROSS(SUM(均价向下运行,0),0.5)
    
    二次上穿 = SUM(上穿信号,0)*CROSS(COUNT(CLOSE < PRE, BARSLAST(上穿信号)),0.5) # 绿三角 + 蓝三角, 含义: 攻击遇阻, 主力放弃
    二次下穿 = SUM(下穿信号,0)*CROSS(COUNT(CLOSE > PRE, BARSLAST(下穿信号)),0.5) # 红三角 + 黄三角
    # 二次上穿 =  上穿信号 &  (REF(上穿信号,1) == False) # 绿三角 + 蓝三角, 含义: 攻击遇阻, 主力放弃
    # 二次下穿 = 下穿信号 & (REF(下穿信号, 1) == False) # 红三角 + 黄三角
    
    二次上穿临界 = CONST(SUM(IF(二次上穿, REF(CLOSE,1), 0),0))
    二次下穿临界 = CONST(SUM(IF(二次下穿, REF(CLOSE,1), 0),0))
    急涨 = CROSS(SUM(均价向上运行 & (CLOSE > 二次上穿临界 * (1+2/100)),0),0.5)
    急跌 = CROSS(SUM(均价向下运行 & (CLOSE< 二次下穿临界 * (1-2/100)),0),0.5)
    
    #X_17 = SUM(X_15,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_15)),0.5)
    急涨慢跌 = SUM(急涨,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(急涨)),0.5) # 绿三角, 主力拉高出货
    # X_18 = SUM(X_16,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_16)),0.5)
    急跌慢涨 = SUM(急跌,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(急跌)),0.5) # 红三角, 承接力度充足, 可能有新主力接力
    
    诱多出货 =  CONST(SUM(IF(急涨慢跌,REF(CLOSE,1),0),0))
    探底拉升 =  CONST(SUM(IF(急跌慢涨,REF(CLOSE,1),0),0))
    X_19 = (CLOSE>REF(CLOSE,1)) & (CLOSE>诱多出货*(1+3/100))
    X_20 = (CLOSE<REF(CLOSE,1)) & (CLOSE<探底拉升*(1-3/100))
    X_21 = CROSS(SUM(X_19,0),0.5)
    X_22 = CROSS(SUM(X_20,0),0.5)
    X_23 = SUM(X_21,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_21)),0.5)
    X_24 = SUM(X_22,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_22)),0.5)
    X_25 = CONST(SUM(IF(X_23,REF(CLOSE,1),0),0))
    X_26 = CONST(SUM(IF(X_24,REF(CLOSE,1),0),0))
    X_27 = CROSS((SUM((X_19 & (CLOSE>X_25*(1+3/100))),0)),0.5)
    X_28 = CROSS(SUM(X_20 & (CLOSE<X_26*(1-3/100)),0),0.5)
    尖顶见顶 = SUM(X_27,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_27)),0.5)
    尖底见底 = SUM(X_28,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_28)),0.5)
    
    卖出信号 = 二次上穿 | 急涨慢跌 | 尖顶见顶 | (COUNT(二次上穿 | 急涨慢跌 | 尖顶见顶, 60) > 1)
    买入信号 = (二次下穿 | 急跌慢涨 | 尖底见底) & (COUNT(二次上穿 | 急涨慢跌 | 尖顶见顶, 60) < 1 ) # 弱市避雷, 8000亿以上的量能可以考虑, 有企稳走二波的可能性
    if 卖出信号:
        df['fenshi_lidu'] = xtconstant.STOCK_SELL
    elif 买入信号:
        df['fenshi_lidu'] = xtconstant.STOCK_BUY
        
    # df['时间'] = pd.to_datetime(df['time'], unit='ms')
    # print(df)
    return df

# 读取股票数据
def lidu2(df: pd.DataFrame) -> pd.DataFrame:
    #基础数据定义
    TIMESTAMP = df.time.values
    CLOSE=df.close.values 
    OPEN=df.open.values  
    HIGH=df.high.values
    VOL=df.volume.values
    AMO=df.amount.values
    PRE=df.preClose.values
    
    AVE = AMO/ VOL/ 100
    print("AVE: ", AVE)
    均价向上运行 = (CLOSE > PRE) & (CLOSE/ AVE > 1 + 15/ 1000)
    均价向下运行 = (CLOSE < PRE) & (CLOSE/ AVE < 1 - 15/ 1000)
    
    上穿信号 = CROSS(SUM(均价向上运行,0),0.5)
    下穿信号 =  CROSS(SUM(均价向下运行,0),0.5)
    
    二次上穿 = SUM(上穿信号,0)*CROSS(COUNT(CLOSE < PRE, BARSLAST(上穿信号)),0.5) # 绿三角 + 蓝三角, 含义: 攻击遇阻, 主力放弃
    二次下穿 = SUM(下穿信号,0)*CROSS(COUNT(CLOSE > PRE, BARSLAST(下穿信号)),0.5) # 红三角 + 黄三角
    # 二次上穿 =  上穿信号 &  (REF(上穿信号,1) == False) # 绿三角 + 蓝三角, 含义: 攻击遇阻, 主力放弃
    # 二次下穿 = 下穿信号 & (REF(下穿信号, 1) == False) # 红三角 + 黄三角
    
    二次上穿临界 = CONST(SUM(IF(二次上穿, REF(CLOSE,1), 0),0))
    二次下穿临界 = CONST(SUM(IF(二次下穿, REF(CLOSE,1), 0),0))
    急涨 = CROSS(SUM(均价向上运行 & (CLOSE > 二次上穿临界 * (1+2/100)),0),0.5)
    急跌 = CROSS(SUM(均价向下运行 & (CLOSE< 二次下穿临界 * (1-2/100)),0),0.5)
    
    #X_17 = SUM(X_15,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_15)),0.5)
    急涨慢跌 = SUM(急涨,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(急涨)),0.5) # 绿三角, 主力拉高出货
    # X_18 = SUM(X_16,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_16)),0.5)
    急跌慢涨 = SUM(急跌,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(急跌)),0.5) # 红三角, 承接力度充足, 可能有新主力接力
    
    诱多出货 =  CONST(SUM(IF(急涨慢跌,REF(CLOSE,1),0),0))
    探底拉升 =  CONST(SUM(IF(急跌慢涨,REF(CLOSE,1),0),0))
    X_19 = (CLOSE>REF(CLOSE,1)) & (CLOSE>诱多出货*(1+3/100))
    X_20 = (CLOSE<REF(CLOSE,1)) & (CLOSE<探底拉升*(1-3/100))
    X_21 = CROSS(SUM(X_19,0),0.5)
    X_22 = CROSS(SUM(X_20,0),0.5)
    X_23 = SUM(X_21,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_21)),0.5)
    X_24 = SUM(X_22,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_22)),0.5)
    X_25 = CONST(SUM(IF(X_23,REF(CLOSE,1),0),0))
    X_26 = CONST(SUM(IF(X_24,REF(CLOSE,1),0),0))
    X_27 = CROSS((SUM((X_19 & (CLOSE>X_25*(1+3/100))),0)),0.5)
    X_28 = CROSS(SUM(X_20 & (CLOSE<X_26*(1-3/100)),0),0.5)
    尖顶见顶 = SUM(X_27,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_27)),0.5)
    尖底见底 = SUM(X_28,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_28)),0.5)
    
    卖出信号 = 二次上穿 | 急涨慢跌 | 尖顶见顶 | (COUNT(二次上穿 | 急涨慢跌 | 尖顶见顶, 60) > 1)
    买入信号 = (二次下穿 | 急跌慢涨 | 尖底见底) & (COUNT(二次上穿 | 急涨慢跌 | 尖顶见顶, 60) < 1 ) # 弱市避雷, 8000亿以上的量能可以考虑, 有企稳走二波的可能性
    df["卖出信号"] = 卖出信号
    df["买入信号"] = 买入信号
    df['时间'] = pd.to_datetime(df['time'], unit='ms')
    print(df)
    return df