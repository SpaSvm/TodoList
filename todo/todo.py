import sqlite3
import os
from flask import Flask, redirect, url_for, render_template, request, flash


DATABASE = 'TodoDatabase.db'
SECRET_KEY = 'todo'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

def get_db():
    db = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
    c = db.cursor()
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS task (
        id INTEGER PRIMARY KEY,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        body TEXT NOT NULL
        );
        """
    )
    db.commit()
    db.row_factory = sqlite3.Row
    return db


@app.route('/')
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT * FROM task'
    ).fetchall()
    return render_template('index.html', tasks=tasks)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        body = request.form['body']
        error = None
        if not body:
            error = 'Необходимо заполнить поле.'
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task (body) VALUES ("{}")'.format(body)
            )
            db.commit()
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/<int:id>/update', methods=['GET', 'POST'])
def update(id):
    db = get_db()
    task = db.execute(
        'SELECT * FROM task WHERE id = ?', (id,)
    ).fetchone()
    if request.method == 'POST':
        body = request.form['body']
        error = None
        db.execute(
            'UPDATE task SET body = "{}" WHERE id = "{}"'.format(body, id)
        )
        db.commit()
        return redirect(url_for('index'))
    return render_template('update.html', task=task)


@app.route('/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    db = get_db()
    task = db.execute(
        'SELECT * FROM task WHERE id = ?', (id,)
    ).fetchone()
    db.execute('DELETE FROM task WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
