import os
from page_analyzer.parsing import get_seo_data
from psycopg2 import connect, extras, errors
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')


def connect_db():
    try:
        with connect(DATABASE_URL) as conn:
            return conn
    except errors as error:
        print(error)
        return False


def get_urls():
    conn = connect_db()
    sql = '''SELECT DISTINCT ON (urls.id)
                urls.id,
                name,
                url_checks.created_at AS site_check,
                status_code
                FROM urls LEFT JOIN url_checks
                ON urls.id=url_checks.url_id
                ORDER BY urls.id DESC, site_check DESC;'''
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql)
            url_from_bd = curs.fetchall()
            return url_from_bd
    except errors as error:
        print(error)
        return False


def show_url(id_url):
    conn = connect_db()
    sql_for_url_name = 'SELECT id, name, created_at FROM urls WHERE id=%s'
    sql_for_check_info = '''SELECT
                        url_checks.id as check_id,
                        status_code,
                        h1,
                        title,
                        description,
                        url_checks.created_at as site_check
                        FROM urls
                        JOIN url_checks ON urls.id = url_checks.url_id
                        WHERE url_id = %s
                        ORDER BY check_id DESC;'''
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql_for_url_name, (id_url,))
            url_name = curs.fetchone()
            curs.execute(sql_for_check_info, (id_url,))
            url_check_info = curs.fetchall()
            return url_name, url_check_info
    except errors as error:
        print(error)
        return False


def check_url(id_url):
    conn = connect_db()
    sql = 'SELECT name FROM urls WHERE id = %s;'
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql, (id_url,))
            url = curs.fetchone()
            seo_data = get_seo_data(url[0])
            if seo_data:
                sql = '''INSERT INTO
                    url_checks (url_id,
                                created_at,
                                status_code,
                                description,
                                h1,
                                title)
                    VALUES (%s, %s, %s, %s, %s, %s)'''
                curs.execute(sql,
                             (id_url,
                              datetime.now(),
                              seo_data['status_code'],
                              seo_data['description'],
                              seo_data['h1'],
                              seo_data['title'],))
                conn.commit()
                return True
    except errors as error:
        print(error)
        return False


def add_urls(url):
    conn = connect_db()
    sql_for_get_id = 'SELECT id FROM urls WHERE name=%s'
    sql_for_add = 'INSERT INTO urls (name, created_at) VALUES (%s, %s)'
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql_for_add, (url, datetime.now(),))
            conn.commit()
            curs.execute(sql_for_get_id, (url,))
            url_from_bd = curs.fetchone()
            return url_from_bd['id']

    except errors as error:
        print(error)
        return False


def repeat(url):
    conn = connect_db()
    sql = 'SELECT id FROM urls WHERE name=%s'
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql, (url,))
            url_from_bd = curs.fetchone()
            if url_from_bd:
                return url_from_bd['id']

    except errors as error:
        print(error)
        return False
