import os
from flask import Flask, render_template, flash, \
    request, redirect, url_for
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor, RealDictCursor
from datetime import datetime
import requests
from page_analyzer.url import validate_url
from page_analyzer.seo_data_parser import get_page_data
from page_analyzer.url import normalize_url


app = Flask(__name__)


load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def show_urls_list():
    conn = get_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute("""SELECT
                         urls.id, urls.name,
                         url_checks.status_code,
                         url_checks.h1, url_checks.title,
                         url_checks.description,
                         url_checks.created_at
                         FROM urls LEFT JOIN url_checks
                         ON urls.id = url_checks.url_id
                         AND url_checks.created_at = (SELECT
                         MAX(created_at) FROM url_checks
                         WHERE url_id = urls.id)
                         ORDER BY urls.id DESC;""")
            urls = curs.fetchall()
    return render_template('urls_list.html', urls=urls)


@app.post('/urls')
def add_url():
    raw_url = request.form.get('url')
    url = normalize_url(raw_url)
    alerts = validate_url(raw_url)
    if alerts:
        for alert in alerts:
            flash(alert, 'alert-danger')
        return render_template('index.html', url=raw_url), 422
    conn = get_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute(
                    """
                    INSERT INTO urls (name, created_at)
                    VALUES (%(name)s, %(created_at)s)
                    RETURNING id;
                    """,
                    {'name': url, 'created_at': datetime.now()})
                id = curs.fetchone().id
                flash('Страница успешно добавлена', 'alert-success')
                return redirect(url_for('show_specific_url', id=id))
    except psycopg2.errors.UniqueViolation:
        with conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute("SELECT id FROM urls WHERE name=(%s);", (url,))
                id = curs.fetchone().id
                flash('Страница уже существует', 'alert-info')
                return redirect(url_for('show_specific_url', id=id))


@app.get('/urls/<int:id>')
def show_specific_url(id):
    conn = get_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute("SELECT * FROM urls WHERE id=(%s);", (id,))
            site = curs.fetchone()
            curs.execute("""SELECT * FROM url_checks
                         WHERE url_id=(%s) ORDER BY id DESC;""", (id,))
            checks = curs.fetchall()
            return render_template('url.html',
                                   site=site,
                                   checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    conn = get_connection()
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            try:
                curs.execute("SELECT name FROM urls WHERE id=(%s);", (id,))
                url = curs.fetchone().name
                response = requests.get(url)
                status_code, h1, title, description = get_page_data(response)
                curs.execute(
                    """
                    INSERT INTO url_checks (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        created_at)
                    VALUES (
                        %(url_id)s,
                        %(status_code)s,
                        %(h1)s,
                        %(title)s,
                        %(description)s,
                        %(created_at)s);""", {
                        'url_id': id,
                        'status_code': status_code,
                        'h1': h1,
                        'title': title,
                        'description': description,
                        'created_at': datetime.now()
                    })
                flash('Страница успешно проверена', 'alert-success')
                return redirect(url_for('show_specific_url', id=id))
            except requests.exceptions.RequestException:
                flash('Произошла ошибка при проверке', 'alert-danger')
                return redirect(url_for('show_specific_url', id=id))
