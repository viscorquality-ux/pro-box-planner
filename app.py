from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os

app = Flask(__name__)

# Aiven PostgreSQL Configuration
DB_CONFIG = {
    'dbname': 'defaultdb',
    'user': 'avnadmin',
    'password': 'YOUR_PASSWORD', # Need user to input this securely
    'host': 'probox123-viscorquality-0270.l.aivencloud.com',
    'port': '20635'
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Create tables with additional fields for history
    c.execute('''CREATE TABLE IF NOT EXISTS quotations 
                 (id SERIAL PRIMARY KEY, q_no TEXT, customer TEXT, date TEXT, data JSONB)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales_orders 
                 (id SERIAL PRIMARY KEY, so_no TEXT, customer TEXT, date TEXT, data JSONB)''')
    # Tables for persistent Master Data
    c.execute('''CREATE TABLE IF NOT EXISTS master_customers 
                 (customer_id TEXT PRIMARY KEY, customer_name TEXT, customer_address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS master_papers 
                 (id SERIAL PRIMARY KEY, paper_type TEXT, paper_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# API for Quotations
@app.route('/api/quotations', methods=['GET', 'POST'])
def manage_quotations():
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO quotations (q_no, customer, date, data) VALUES (%s, %s, %s, %s)",
                  (data['q_no'], data['customer'], data['date'], json.dumps(data['form_data'])))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    else:
        c.execute("SELECT q_no, customer, date, data FROM quotations")
        rows = c.fetchall()
        conn.close()
        return jsonify(rows)

# Add other routes similarly...
if __name__ == '__main__':
    app.run(debug=True)
