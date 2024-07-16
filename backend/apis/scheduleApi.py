from services.cacheService import *
from services.dataService import *
from services.scheduleService import *

from utils.algorism import *

from transformers.scheduleTransformer import *

from flask import Blueprint

schedule_bp = Blueprint("schedule", __name__)


# input short code but out put full code, and make the short code only stay here
# { stock_code: { [direction: sell, buy]:{strategy: max_amo, single_amo, single_percent, max_percent, 'begin_time': 930, 'end_time': 1500 }}
@schedule_bp.route("/schedule/add")
def add_schedule(schedule: dict):  #
    model = out_to_inner(schedule)
    existing_schedule_dict = fetch_all_schedule()
    need_prepare = False
    if full_code not in existing_schedule_dict:
        need_prepare = True
    result = inner_to_out(create_schedule(model))
    if need_prepare:
        prepare_data()
    return result


@schedule_bp.route("/schedule/adds")
def add_schedules(schedules: list):  #
    models = []
    for schedule in schedules:
        models.append(out_to_inner(schedule))

    existing_schedule_dict = fetch_all_schedule()
    need_prepare = False

    for model in models:
        for full_code, directions in model.items():
            if full_code not in existing_schedule_dict:
                need_prepare = True
        create_schedule(model)

    if need_prepare:
        prepare_data()

    return fetch_all_schedule()


@schedule_bp.route("/schedule/get")
def get_schedule(short_code, direction):  # return
    full_code = to_full_code(short_code)
    xt_direction = direction_to_xtConstant(direction)
    return read_schedule(full_code, xt_direction)


@schedule_bp.route("/schedule/update")
def update_schedule(schedule: dict):  #
    model = out_to_inner(schedule)
    existing_schedule_dict = fetch_all_schedule()
    if full_code not in existing_schedule_dict:
        return False
    result = inner_to_out(create_schedule(model))
    return result


@schedule_bp.route("/schedule/remove")
def remove_schedule(short_code, direction):  #
    return delete_schedule(to_full_code(short_code), direction_to_xtConstant(direction))


@schedule_bp.route("/schedule/list")
def list_all_schedule():  #
    return fetch_all_schedule()
