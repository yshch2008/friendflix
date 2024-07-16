from utils.transformerUtil import *

def out_to_inner(model):
    for short_code, directions in model.items():
        for direction_name, strategies in directions.items():
            return {short_to_full_code(short_code): {
                direction_to_xtDirection(direction_name): strategies
            }}
        
    
def inner_to_out(model):
    for short_code, directions in model.items():
        for direction_code, strategies in directions.items():
            return {full_to_short_code(short_code): {
                xtDirection_to_direction(direction_code): strategies
            }}
