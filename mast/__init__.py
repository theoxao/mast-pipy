from flask import Flask,g,current_app
from flask_cors import *
import os


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True)
    database = None
    if 'DATABASE_URL' in os.environ:
        database = os.environ['DATABASE_URL']
    else:
        database = '/Users/theo/workspace/theo/mast-db/mast.db',
    print(database)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=database
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from . import sqlite
    sqlite.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    return app


