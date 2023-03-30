import os
from page_analyzer import db, urls
from flask import (Flask,
                   render_template,
                   redirect,
                   url_for,
                   request,
                   flash,
                   abort)
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    sites = db.get_urls()
    return render_template('urls.html', sites=sites)


@app.post('/urls')
def add_urls():
    url = request.form.get('url')
    errors = urls.validate_url(url)
    if not errors:
        url = urls.normalized_url(url)
        id_url, flash_msg = db.add_urls(url)
        for msg, cat in flash_msg:
            flash(msg, cat)
        return redirect(url_for('show_url', id_url=id_url))
    else:
        for msg, cat in errors:
            flash(msg, cat)
        return render_template('index.html'), 422


@app.get('/urls/<id_url>')
def show_url(id_url):
    url_name, url_check = db.show_url(id_url)
    if not url_name:
        abort(404)
    return render_template('url_id.html', url=url_name, url_check=url_check)


@app.post('/urls/<id_url>/checks')
def check_url(id_url):
    db.check_url(id_url)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id_url=id_url))
