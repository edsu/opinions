import os

from sqlite3 import dbapi2 as sqlite3 
from flask import Flask, request, session, render_template, g

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'decisions.db'),
    DEBUG=True,
))

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def opinions():
    db = get_db()
    return render_template('opinions.html')


if __name__ == "__main__":
    init_db()
    app.run()
