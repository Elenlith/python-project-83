import os
from flask import Flask, render_template, flash, get_flashed_messages, \
    request, redirect, url_for
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor
from datetime import datetime
from urllib.parse import urlparse
from validators import url as validate


app = Flask(__name__)


load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


def take_domain(url):
    url = urlparse(url)
    return url._replace(
        path='',
        params='',
        query='',
        fragment='').geturl()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls')
def get_urls():
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("""SELECT
                                urls.id, urls.name,
                                MAX(url_checks.created_at) AS created_at
                                FROM urls LEFT JOIN url_checks
                                ON urls.id = url_checks.url_id
                                GROUP BY urls.id
                                ORDER BY urls.id;""")
            urls = curs.fetchall()
    return render_template('urls_list.html', urls=urls)


@app.post('/urls')
def add_url():
    data = request.form.to_dict()
    url = take_domain(data['url'])
    if not validate(url) or len(url) > 255:
        messages = get_flashed_messages(with_categories=True)
        flash('Incorrect URL', 'alert-danger')
        return render_template('index.html', messages=messages, url=url), 422
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
                id = curs.fetchone().id
                flash('Website successfully added', 'alert-success')
                return redirect(url_for('get_url', id=id))
    except psycopg2.errors.UniqueViolation:
        with conn:
            with conn.cursor() as curs:
                curs.execute("SELECT id FROM urls WHERE name=(%s);", (url,))
                id = curs.fetchone().id
                flash('Website already exist', 'alert-info')
                return redirect(url_for('get_url', id=id))
