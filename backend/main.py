import psycopg2

# from db import close_db, init_db
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from views import all_blueprints

# from mainProcess import *
from apis import scheduleApi
from services.tradeService import init_xt_trader


app = Flask(__name__)
app.config.from_prefixed_env()
# app.teardown_appcontext(close_db)
for bp in all_blueprints:
    app.register_blueprint(bp)

FRONTEND_URL = app.config.get("FRONTEND_URL", "*")
cors = CORS(app, origins=FRONTEND_URL, methods=["GET", "POST", "DELETE"])
jwt = JWTManager(app)

if app.debug:
    app.logger.debug("Starting app with config:")
    for key, value in app.config.items():
        app.logger.debug(f"{key}={value}")

with app.app_context():
    try:
        print("hello dataService")
        init_xt_trader()
        scheduleApi.add_schedules(
            [{"300176": {"sell": {"fenshi_lidu": {'max_amo': 0, 'single_amo': 0, 'single_percent': 100, 'max_percent': 100, 'begin_time': 930, 'end_time': 1455}}}},
             {"300843": {"sell": {"fenshi_lidu": {'max_amo': 0, 'single_amo': 0, 'single_percent': 100, 'max_percent': 100, 'begin_time': 930, 'end_time': 1455}}}},
             ]
        )
        # scheduleApi.add_schedule('300176','sell','fenshi_lidu', 0, 0, 100, 100, 930, 1500)
        # scheduleApi.add_schedule('300843','sell','fenshi_lidu', 0, 0, 100, 100, 930, 1500)
        # print('hello simpleStart')
        # init_db(app)
    except psycopg2.errors.ConnectionFailure:
        app.logger.error("Failed to connect to the database, exiting")
        exit(1)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("hello simpleStart")
    # simpleStart()
