import time
import os
import psycopg2
from flask import Flask, request, redirect

app = Flask(__name__)

#
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'phonebook'),
    'user': os.getenv('POSTGRES_USER', 'sladkiy'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),  
    'port': os.getenv('POSTGRES_PORT', '5432'),
    
    'password': os.environ['POSTGRES_PASSWORD'] 
}



def init_db():
    time.sleep(3) 
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL
                );
            ''')

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
        return redirect('/')

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, phone FROM contacts")
            contacts = cur.fetchall()

    html = '<h2>Телефонная книга в Docker</h2>'
    html += '<form method="POST"><input name="name" placeholder="Имя" required> <input name="phone" placeholder="Телефон" required> <button type="submit">Добавить</button></form>'
    html += '<ul>'
    for contact in contacts:
        html += f'<li>{contact[0]} : {contact[1]}</li>'
    html += '</ul>'
    
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
