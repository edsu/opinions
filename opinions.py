#!/usr/bin/env python

import os
import flask

from sqlalchemy import func, select, desc
from flask.ext.sqlalchemy import SQLAlchemy

# create/config our app

app = flask.Flask(__name__)
db = SQLAlchemy(app)

if 'DATABASE_URL' in os.environ:
    db_uri = os.environ['DATABASE_URL']
else:
    db_uri = 'sqlite:///' + os.path.join(app.root_path, 'opinions.db')

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['DEBUG'] = os.environ.get("DEBUG", False)


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

    author_id = db.Column(db.String(5), db.ForeignKey('author.id'))
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
    internet_archive = db.Column(db.Text)
    opinion_id = db.Column(db.Integer, db.ForeignKey('opinion.id'))
    opinion = db.relationship('Opinion',
        backref=db.backref('external_urls', lazy='dynamic'))

class Author(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


# web app

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

@app.route('/author/<author_id>')
def author(author_id):
    urls = ExternalUrl.query.join(Opinion).order_by(Opinion.published.desc()).filter(Opinion.author_id == author_id)
    return flask.render_template('author.html', urls=urls)

@app.route('/authors.csv')
def authors_csv():
    q = (select([Author.id, Author.name,
        func.count(ExternalUrl.id).label("urls")]).
         where(Author.id == Opinion.author_id).
         where(Opinion.id == ExternalUrl.opinion_id).
         group_by(Author.name, Author.id).
         order_by(desc("urls")).
         alias())
    cursor = db.session.query(q)
    results = ['id,name,urls']
    for row in cursor:
        results.append('"%s","%s",%s' % row)

    return flask.Response('\n'.join(results), mimetype='text/csv')


if __name__ == "__main__":
    db.create_all()
    app.run()
