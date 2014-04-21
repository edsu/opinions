#!/usr/bin/env python

import os
import flask

from sqlalchemy import func, select, desc
from flask.ext.sqlalchemy import SQLAlchemy

# create our app

app = flask.Flask(__name__)
db = SQLAlchemy(app)


# database models

class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(15), nullable=False)
    created = db.Column(db.DateTime)
    published = db.Column(db.DateTime)
    name = db.Column(db.Text)
    pdf_url = db.Column(db.Text)
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

    def __repr__(self):
        d = self.published.strftime("%Y-%m-%d")
        return "%s (%s) <%s>" % (self.name, d, self.pdf_url)

class ExternalUrl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text)
    created = db.Column(db.DateTime)
    hostname = db.Column(db.Text)
    opinion_id = db.Column(db.Integer, db.ForeignKey('opinion.id'))
    opinion = db.relationship('Opinion', 
        backref=db.backref('external_urls', lazy='dynamic'))

class Author(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


# define some web application routes

@app.route('/')
def home():
    return flask.render_template('home.html')

@app.route('/opinions/')
def opinions():
    opinions = Opinion.query.order_by(Opinion.published.desc()).all()
    return flask.render_template('opinions.html', opinions=opinions)

@app.route('/urls/')
def urls():
    urls = ExternalUrl.query.join(Opinion).order_by(Opinion.published.desc())
    return flask.render_template('urls.html', urls=urls)

@app.route('/authors/')
def authors():
    q = (select([Author.name, func.count(ExternalUrl.id).label("urls")]).
         where(Author.id == Opinion.author_id).
         where(Opinion.id == ExternalUrl.opinion_id).
         group_by(Author.name).
         order_by(desc("urls")))
    rows = db.session.query(q)
    return flask.render_template('authors.html', rows=rows)

@app.route('/authors.csv')
def authors_csv():
    q = (select([Author.id, Author.name, func.count(ExternalUrl.id).label("urls")]).
         where(Author.id == Opinion.author_id).
         where(Opinion.id == ExternalUrl.opinion_id).
         group_by(Author.name, Author.id).
         order_by(desc("urls")))
    cursor = db.session.query(q)
    results = ['"id","name",urls']
    for row in cursor:
        results.append('"%s","%s",%s' % row)

    return flask.Response('\n'.join(results), mimetype='text/csv')



# run the webapp

def init():
    db_uri = 'sqlite:///' + os.path.join(app.root_path, 'opinions.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['DEBUG'] = True
    db.create_all()

if __name__ == "__main__":
    init()
    app.run()
