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
            app.app.logger.info('successful get_urls from bd')
            return url_from_bd
    except errors as error:
        app.app.logger.warning(error)


def show_url(id_url, conn):
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
            app.app.logger.info('successful show_url from bd')
            return url_name, url_check_info
    except errors as error:
        app.app.logger.warning(error)


def check_url(id_url, conn):
    sql = 'SELECT name FROM urls WHERE id = %s;'
    msg = {}
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql, (id_url,))
            url = curs.fetchone()
            app.app.logger.info('successful get url_name from bd')
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
                msg['text'] = 'Страница успешно проверена'
                msg['categories'] = 'success'
                app.app.logger.info('successful check_url insert into bd')
                return msg
    except errors as error:
        app.app.logger.warning(error)
    msg['text'] = 'Произошла ошибка при проверке'
    msg['categories'] = 'danger'
    return msg


def add_urls(url, conn):
    sql_for_get_id = 'SELECT id FROM urls WHERE name=%s'
    sql_for_add = 'INSERT INTO urls (name, created_at) VALUES (%s, %s)'
    msg = {}
    id_url = repeat(url, conn)
    if id_url:
        msg['text'] = 'Страница уже существует'
        msg['categories'] = 'info'
        return id_url, msg
    else:
        try:
            with conn.cursor(cursor_factory=extras.DictCursor) as curs:
                curs.execute(sql_for_add, (url, datetime.now(),))
                conn.commit()
                app.app.logger.info(f'Successful select {url} from bd')
                curs.execute(sql_for_get_id, (url,))
                url_from_bd = curs.fetchone()
                app.app.logger.info(f'Successful add {url} to bd')
                msg['text'] = 'Страница успешно добавлена'
                msg['categories'] = 'success'
                return url_from_bd['id'], msg

        except errors as error:
            app.app.logger.info(f'Unsuccessful add {url} to bd', error)


def repeat(url, conn):
    sql = 'SELECT id FROM urls WHERE name=%s'
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as curs:
            curs.execute(sql, (url,))
            url_from_bd = curs.fetchone()
            app.app.logger.info(f'Successful Check repeat {url} from bd')
            if url_from_bd:
                return url_from_bd['id']

    except errors as error:
        app.app.logger.info(f'Unsuccessful Check repeat {url} from bd', error)
