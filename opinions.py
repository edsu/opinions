import os

from sqlite3 import dbapi2 as sqlite3 
from flask import Flask, request, session, render_template, g
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db_uri = 'sqlite:///' + os.path.join(app.root_path, 'opinions.db')
print db_uri
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)


class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    published = db.Column(db.DateTime)
    name = db.Column(db.Text)
    url = db.Column(db.Text)
    reporter_id = db.Column(db.Text)
    docket_num = db.Column(db.Text)
    part_num = db.Column(db.Text)
    author = db.relationship('Author',
        backref=db.backref('opinions', lazy='dynamic'))

class Url(db.Model):
    url = db.Column(db.Text, primary_key=True)
    created = db.Column(db.DateTime)
    text = db.Column(db.Text)
    opinion = db.relationship('Opinion', 
        backref=db.backref('urls', lazy='dynamic'))

class Author(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.Text)


@app.route('/')
def opinions():
    return render_template('opinions.html')


if __name__ == "__main__":
    db.create_all()
    app.run()
