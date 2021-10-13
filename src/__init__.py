from flask import Flask, jsonify
from src.database import db, migrate
from src.order import order
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:

        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI='sqlite:///flipzon.db',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )

    else:

        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    migrate.init_app(app, db)

    app.register_blueprint(order)
    return app
