import sqlite3
from flask import current_app, g;


def get_db():
    if 'db' not in g:
        database = current_app.config["DATABASE"]
        if type(database) is tuple:
            g.db = sqlite3.connect(
                database[0]
            )
        else:
            g.db = sqlite3.connect(
                database
            )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv
