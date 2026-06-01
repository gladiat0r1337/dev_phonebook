import os
import time
import psycopg2
from psycopg2 import OperationalError
from flask import Flask, request, redirect, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_CONFIG = {
    'dbname': os.environ['POSTGRES_DB'],
    'user': os.environ['POSTGRES_USER'],
    'host': os.environ['POSTGRES_HOST'],  
    'port': os.environ['POSTGRES_PORT'],
    'password': os.environ['POSTGRES_PASSWORD'] 
}

def init_db():
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Подключение к БД] Попытка {attempt} из {max_retries}...")
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS contacts (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            phone VARCHAR(20) NOT NULL
                        );
                    ''')
            print("[Успех] База данных инициализирована!")
            return
            
        except OperationalError as e:
            print(f"[Ожидание] База данных еще не готова: {e}")
            if attempt == max_retries:
                print("[КРИТИЧЕСКАЯ ОШИБКА] Не удалось подключиться к БД. Остановка сервиса.")
                raise
            time.sleep(2)

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']

        if phone.isdigit():
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
        
        return redirect('/')

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, phone FROM contacts ORDER BY id DESC")
            contacts = cur.fetchall()

    return render_template('index.html', contacts=contacts)

@app.route('/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)