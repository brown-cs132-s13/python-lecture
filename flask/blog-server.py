# -*- coding: utf-8 -*-

#This example largely adapted from Flaskr,
#https://github.com/mitsuhiko/flask/blob/master/examples/flaskr/flaskr.py

from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db

    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, title, text from entries order by id desc')
    entries = cur.fetchall()
    cur = db.execute('select post, content from comments order by id asc')
    comments = cur.fetchall()
    comments_per_id = {}
    for comment in comments:
        try:
            comments_per_id[comment['post']].append(comment)
        except KeyError:
            comments_per_id[comment['post']] = [comment]
    return render_template('show_entries.html', entries=entries, comments=comments_per_id)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/add-comment', methods=['POST'])
def add_comment():
    db = get_db()
    db.execute('insert into comments (post, content) values (?, ?)',
                 [request.form['post_id'], request.form['content']])
    db.commit()
    flash('New comment was successfully posted')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    init_db()
    app.run()