import os
from flask import Flask, render_template, flash, get_flashed_messages, \
    request, redirect, url_for
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor
from datetime import datetime
from urllib.parse import urlparse
from page_analyzer.url import validate_url


app = Flask(__name__)


load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def establish_connection():
    return psycopg2.connect(DATABASE_URL)


def get_domain(raw_url):
    url = urlparse(raw_url)
    return f"{url.scheme}://{url.netloc}"


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def show_urls_list():
    conn = establish_connection()
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("""SELECT
                         urls.id, urls.name, urls.created_at
                         FROM urls
                         GROUP BY urls.id
                         ORDER BY urls.id DESC;""")
            urls = curs.fetchall()
    return render_template('urls_list.html', urls=urls)


@app.post('/urls')
def add_url():
    raw_url = request.form.get('url')
    url = get_domain(raw_url)
    alerts = validate_url(raw_url)
    if alerts:
        for alert in alerts:
            flash(alert, 'alert-danger')
        return render_template('index.html', url=raw_url), 422
    conn = establish_connection()
    try:
        with conn:
            with conn.cursor() as curs:
                curs.execute(
                    """
                    INSERT INTO urls (name, created_at)
                    VALUES (%(name)s, %(created_at)s)
                    RETURNING id;
                    """,
                    {'name': url, 'created_at': datetime.now()})
                id = curs.fetchone()[0]
                flash('Страница успешно добавлена', 'alert-success')
                return redirect(url_for('show_specific_url', id=id))
    except psycopg2.errors.UniqueViolation:
        with conn:
            with conn.cursor() as curs:
                curs.execute("SELECT id FROM urls WHERE name=(%s);", (url,))
                id = curs.fetchone()[0]
                flash('Страница уже существует', 'alert-info')
                return redirect(url_for('show_specific_url', id=id))


@app.get('/urls/<int:id>')
def show_specific_url(id):
    conn = establish_connection()
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("SELECT * FROM urls WHERE id=(%s);", (id,))
            site = curs.fetchone()
            messages = get_flashed_messages(with_categories=True)
    return render_template('url.html',
                           site=site,
                           messages=messages)
