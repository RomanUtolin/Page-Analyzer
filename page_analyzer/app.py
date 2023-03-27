import os
import psycopg2
import psycopg2.extras
import psycopg2.errors
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from urllib.parse import urlparse
from validators import url as validator
from validators import length
from datetime import datetime
from dotenv import load_dotenv
from page_analyzer.parsing import get_status_code

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.secret_key = SECRET_KEY


def execute_sql(sql, *args, fetch=True, fetch_all=True):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
                curs.execute(sql, args)
                conn.commit()
                if fetch is True:
                    if fetch_all is True:
                        cur = curs.fetchall()
                    else:
                        cur = curs.fetchone()
                    return cur
    except psycopg2.errors as error:
        print(error)


def check_repeat_url(url):
    sql = 'SELECT name FROM urls WHERE name=%s'
    url_from_bd = execute_sql(sql, url, fetch_all=False)
    if url_from_bd:
        return True


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    sql = '''SELECT DISTINCT ON (urls.id)
            urls.id,
            name,
            url_checks.created_at AS site_check,
            status_code
            FROM urls LEFT JOIN url_checks
            ON urls.id=url_checks.url_id
            ORDER BY urls.id DESC, site_check DESC;'''
    url_from_bd = execute_sql(sql)
    return render_template('urls.html', sites=url_from_bd)


@app.post('/urls')
def add_urls():
    url = request.form.get('url')
    if validator(url) and length(url, max=255):
        url = urlparse(url)
        normal_url = f'{url.scheme}://{url.netloc}'
        if not check_repeat_url(normal_url):
            sql = 'INSERT INTO urls (name, created_at) VALUES (%s, %s)'
            execute_sql(sql, normal_url, datetime.now(), fetch=False)
            flash('Страница успешно добавлена', 'success')
        else:
            flash('Страница уже существует', 'info')
        sql = 'SELECT id FROM urls WHERE name=%s'
        url_from_bd = execute_sql(sql, normal_url, fetch_all=False)
        id_url = url_from_bd['id']
        return redirect(url_for('show_url', id_url=id_url))
    else:
        if len(url) == 0:
            flash('URL обязателен', 'danger')
        elif len(url) > 255:
            flash('URL превышает 255 символов', 'danger')
        flash('Некорректный URL', 'danger')
    return redirect(url_for('index'))


@app.get('/urls/<id_url>')
def show_url(id_url):
    sql = 'SELECT id, name, created_at FROM urls WHERE id=%s'
    url_name_from_bd = execute_sql(sql, id_url, fetch_all=False)
    sql = '''SELECT
            url_checks.id as check_id,
            status_code,
            h1,
            title,
            description,
            url_checks.created_at as site_check
            FROM urls JOIN url_checks ON urls.id = url_checks.url_id
            WHERE url_id = %s
            ORDER BY check_id DESC;'''
    url_check_from_bd = execute_sql(sql, id_url)
    if not url_name_from_bd:
        abort(404)
    return render_template('url_id.html', url=url_name_from_bd, url_check=url_check_from_bd)


@app.post('/urls/<id_url>/checks')
def check_url(id_url):
    sql = 'SELECT name FROM urls WHERE id = %s;'
    url = execute_sql(sql, id_url, fetch_all=False)
    status_code = get_status_code(url)
    sql = 'INSERT INTO url_checks (url_id, created_at, status_code) VALUES (%s, %s, %s)'
    execute_sql(sql, id_url, datetime.now(), status_code, fetch=False)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id_url=id_url))
