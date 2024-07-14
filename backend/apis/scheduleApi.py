
from xtquant import xtdata
from xtquant import xtconstant

from services.cacheService import *  
from services.dataService import *  

from utils.xtUtil import *
from utils.algorism import *
from strategies.fenshi_lidu import lidu

from flask import Blueprint
from flask_jwt_extended import get_jwt, jwt_required
from models.user import add_watched_status_to_movies

schedule_bp = Blueprint("schedule", __name__)

# input short code but out put full code, and make the short code only stay here
# { stock_code: { [direction: sell, buy]:{strategy: max_amo, single_amo, single_percent, max_percent, 'begin_time': 930, 'end_time': 1500 }}
@schedule_bp.route("/schedule/add")
def add_scheduale(short_code, direction, strategy,  max_amo, single_amo, max_percent, single_percent, begin_time = 930, end_time = 1000): # 
    full_code = to_full_code(short_code)
    xt_direction = direction_to_xtConstant(direction)
    live_schedules = fetch_all_schedule()
    if full_code in live_schedules:
        create_schedule(full_code, xt_direction, strategy, max_amo, single_amo, max_percent, begin_time, end_time)
    else:
        create_schedule(full_code, xt_direction, strategy, max_amo, single_amo, max_percent, begin_time, end_time)
        prepare_data()
    return read_schedule(full_code, xt_direction)

@schedule_bp.route("/schedule/get")
def get_schedule(short_code, direction): # return 
    full_code = to_full_code(short_code)
    xt_direction = direction_to_xtConstant(direction)
    return read_schedule(full_code, xt_direction)

@schedule_bp.route("/schedule/update")
def update_schedule(short_code, direction, strategy, max_amo, single_amo, max_percent, begin_time = 930, end_time = 1000): # 
    full_code = to_full_code(short_code)
    xt_direction = direction_to_xtConstant(direction)
    create_schedule(full_code, xt_direction, strategy, max_amo, single_amo, max_percent, begin_time , end_time )
    return

@schedule_bp.route("/schedule/remove")
def remove_schedule(short_code, direction): # 
    return delete_schedule(to_full_code(short_code), direction_to_xtConstant(direction))
    
@schedule_bp.route("/schedule/list")
def fetch_all_schedule(): # 
    return fetch_all_schedule()

def direction_to_xtConstant(direction):
    xt_direction = xtconstant.STOCK_BUY if direction == 'buy' else xtconstant.STOCK_SELL
    return xt_direction