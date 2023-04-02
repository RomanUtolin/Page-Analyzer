import os
from page_analyzer import db, urls
from flask import (Flask,
                   render_template,
                   redirect,
                   url_for,
                   request,
                   flash,
                   abort)
from psycopg2 import connect, errors
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.secret_key = SECRET_KEY


def connect_db():
    try:
        with connect(DATABASE_URL) as conn:
            return conn
    except errors as error:
        print(error)
        return False


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    sites = db.get_urls(connect_db())
    return render_template('urls.html', sites=sites)


@app.post('/urls')
def add_urls():
    url = request.form.get('url')
    error = urls.validate_url(url)
    if error:
        flash(error['text'], 'danger')
        return render_template('index.html'), 422
    url = urls.normalized_url(url)
    id_url, msg = db.add_urls(url, connect_db())
    flash(msg['text'], msg['cat'])
    return redirect(url_for('show_url', id_url=id_url))


@app.get('/urls/<int:id_url>')
def show_url(id_url):
    url_name, url_check = db.show_url(id_url, connect_db())
    if not url_name:
        abort(404)
    return render_template('url_id.html', url=url_name, url_check=url_check)


@app.post('/urls/<int:id_url>/checks')
def check_url(id_url):
    msg = db.check_url(id_url, connect_db())
    flash(msg['text'], msg['cat'])
    return redirect(url_for('show_url', id_url=id_url))
