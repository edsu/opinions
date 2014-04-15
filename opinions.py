#!/usr/bin/env python

import os
import flask

from flask.ext.sqlalchemy import SQLAlchemy


app = flask.Flask(__name__)
db = SQLAlchemy(app)

class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(15), nullable=False)
    created = db.Column(db.DateTime)
    published = db.Column(db.DateTime)
    name = db.Column(db.Text)
    url = db.Column(db.Text, unique=True)
    reporter_id = db.Column(db.Text)
    docket_num = db.Column(db.Text)
    part_num = db.Column(db.Text)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author',
        backref=db.backref('opinions', lazy='dynamic'))

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            if hasattr(self, name):
                setattr(self, name, value)


class Url(db.Model):
    url = db.Column(db.Text, primary_key=True)
    created = db.Column(db.DateTime)
    text = db.Column(db.Text)

    opinion_id = db.Column(db.Integer, db.ForeignKey('opinion.id'))
    opinion = db.relationship('Opinion', 
        backref=db.backref('urls', lazy='dynamic'))


class Author(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


@app.route('/')
def opinions():
    return flask.render_template('opinions.html')


def init():
    db_uri = 'sqlite:///' + os.path.join(app.root_path, 'opinions.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.create_all()


if __name__ == "__main__":
    init()
    app.run()
