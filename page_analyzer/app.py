import os
from flask import Flask, render_template, flash, request, redirect
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
from urllib.parse import urlparse


app = Flask(__name__)


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    raw_url = request.form.get('url')
    try:
        with conn:
            with conn.cursor() as curs:
                url = f"{urlparse(raw_url).scheme}://{urlparse(raw_url).netloc}"
                curs.execute(
                    """
                    INSERT INTO urls (name, created_at)
                    VALUES (%(name)s, %(created_at)s)
                    RETURNING id;
                    """,
                    {'name': url, 'created_at': datetime.now()})
                flash('Страница успешно добавлена', 'success')
                return redirect('/')
    except psycopg2.errors.UniqueViolation:
        with conn:
            with conn.cursor() as curs:
                curs.execute("SELECT id FROM urls WHERE name=(%s);", (url,))
                flash('Страница уже существует', 'info')
                return redirect('/')


if __name__ == "__main__":
    app.run()
