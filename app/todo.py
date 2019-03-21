import sqlite3
import os
from flask import Flask, redirect, url_for, render_template, request


app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY = 'todo',
    DEBUG = True,
    DATABASE = os.path.join(app.instance_path, 'app.sqlite'),
)
if __name__ == '__main__':
    app.run()

DATABASE = 'schema.sql'

def get_db():
    db = getattr('_schema', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr('_schema', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read())
        db.commit()


@app.route('/')
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT * FROM tasks'
    ).fetchall()
    return render_template('index.html', tasks=tasks)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        body = request.form['body']
        db = get_db()
        db.execute(
            'INSERT INTO tasks (body,) VALUES (?,)', (body,)
        )
        db.commit()
        return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/delete', methods=('GET', 'POST'))
def delete(id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))
