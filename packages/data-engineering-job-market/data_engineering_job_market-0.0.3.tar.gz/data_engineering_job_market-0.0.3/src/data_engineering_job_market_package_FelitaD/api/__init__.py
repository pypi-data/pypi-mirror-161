from flask import Flask

from api.db import db
from config.definitions import JOB_MARKET_DB_PWD, JOB_MARKET_DB_USER


def create_app(*args, **kwargs):
    app = Flask(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # library has its own tracker
    app.config['SECRET_KEY'] = 'super-secret'
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f'postgresql://{JOB_MARKET_DB_USER}:{JOB_MARKET_DB_PWD}@localhost:5432/job_market'
    with app.app_context():
        db.init_app(app)
        db.Model.metadata.reflect(db.engine)

    return app
