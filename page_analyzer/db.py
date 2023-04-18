from page_analyzer import app
from page_analyzer.parsing import get_seo_data
from psycopg2 import extras, errors
from datetime import datetime


def get_urls(conn):
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
            app.app.logger.info('successful get all urls from bd')
            return url_from_bd
    except errors as error:
        app.app.logger.warning(error)


def show_url(id_url, conn):
    sql = '''SELECT
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
    url_from_bd = get_url_by_id(id_url, conn)
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql, (id_url,))
            url_check_info = curs.fetchall()
            app.app.logger.info(f'successful check_info id={id_url} from bd')
            return url_from_bd, url_check_info
    except errors as error:
        app.app.logger.warning(error)


def check_url(id_url, conn):
    sql = '''INSERT INTO
             url_checks (url_id,
             created_at,
             status_code,
             description,
             h1,
             title)
             VALUES (%s, %s, %s, %s, %s, %s)'''
    msg = {}
    url = get_url_by_id(id_url, conn)
    seo_data = get_seo_data(url[0])
    if seo_data:
        try:
            with conn.cursor(cursor_factory=extras.DictCursor) as curs:
                curs.execute(sql,
                             (id_url,
                              datetime.now(),
                              seo_data['status_code'],
                              seo_data['description'],
                              seo_data['h1'],
                              seo_data['title'],))
                conn.commit()
                msg['text'] = 'Страница успешно проверена'
                msg['categories'] = 'success'
                app.app.logger.info(f'successful check id={id_url} insert bd')
                return msg
        except errors as error:
            app.app.logger.warning(error)
    msg['text'] = 'Произошла ошибка при проверке'
    msg['categories'] = 'danger'
    return msg


def add_urls(url, conn):
    sql_for_add = 'INSERT INTO urls (name, created_at) VALUES (%s, %s)'
    msg = {}
    url_from_bd = get_id_url(url, conn)
    if url_from_bd:
        msg['text'] = 'Страница уже существует'
        msg['categories'] = 'info'
        return url_from_bd['id'], msg
    else:
        try:
            with conn.cursor(cursor_factory=extras.DictCursor) as curs:
                curs.execute(sql_for_add, (url, datetime.now(),))
                conn.commit()
                app.app.logger.info(f'Successful add {url} to bd')
                url_from_bd = get_id_url(url, conn)
                msg['text'] = 'Страница успешно добавлена'
                msg['categories'] = 'success'
                return url_from_bd['id'], msg

        except errors as error:
            app.app.logger.warning(error)


def get_id_url(url, conn):
    sql = 'SELECT id FROM urls WHERE name=%s'
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql, (url,))
            url_from_bd = curs.fetchone()
            app.app.logger.info(f'Successful get {url} from bd')
            return url_from_bd

    except errors as error:
        app.app.logger.warning(error)


def get_url_by_id(id_url, conn):
    sql = 'SELECT name, id, created_at FROM urls WHERE id=%s'
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql, (id_url,))
            url_from_bd = curs.fetchone()
            app.app.logger.info(f'successful get {id_url} from bd')
            return url_from_bd
    except errors as error:
        app.app.logger.warning(error)
