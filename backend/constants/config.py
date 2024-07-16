from strategies.fenshi_lidu import fenshi_lidu

real_trade_switch = False

account_id = "60603327"
qmt_path = r"D:\dongbeizhengquanNET\userdata_mini"
split_limit = 58888  # 免 5 改 10000, 不免60000
period = "1m"
time_formmat = "%Y-%m-%d %H:%M:%S"
min_data = {}
schedule_data = {}

index_data = {
    "emotion_flag": False,
    "emotion_stock_code": "601857.SH",
    "begin_timestamp": "20240504",
}

strategy_data = {
    "static": {"live": False, "sync_trade": True, 'executor': fenshi_lidu},
    "fenshi_lidu": {"live": False, "sync_trade": True, 'executor': fenshi_lidu},
    "confirm_on_up": {"live": False, "sync_trade": False, 'executor': fenshi_lidu},
}
