
from flask import Blueprint
from flask_jwt_extended import get_jwt, jwt_required

from services.strategyService import *

schedule_bp = Blueprint("strategy", __name__)


@schedule_bp.route("/strategy/open")
def open_strategy(strategy):
    activate_strategy(strategy)
    
@schedule_bp.route("/strategy/close")
def close_strategy(strategy):
    inactivate_strategy(strategy)
    
@schedule_bp.route("/strategy/get")
def get_strategy(strategy):
    return read_strategy(strategy)
    