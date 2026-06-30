from flask import Flask, render_template, request, jsonify
import psycopg2
import json
import os

app = Flask(__name__)

# Render Environment Variable එකෙන් Database URL එක ලබා ගැනීම
DB_URL = os.environ.get("DATABASE_URL", "postgres://avnadmin:AVNS_AJNctiNyP1ujHPV3mh8@probox123-viscorquality-0270.l.aivencloud.com:28643/defaultdb?sslmode=require")

def get_db_connection():
    # SSL mode අත්‍යවශ්‍ය වේ
    conn = psycopg2.connect(DB_URL, sslmode='require')
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Tables නිර්මාණය කිරීම (Unique constraints සමඟ)
    c.execute('''CREATE TABLE IF NOT EXISTS quotations (id SERIAL PRIMARY KEY, q_no TEXT, customer TEXT, date TEXT, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales_orders (id SERIAL PRIMARY KEY, so_no TEXT, customer TEXT, date TEXT, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id TEXT PRIMARY KEY, name TEXT, address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS paper_types (id SERIAL PRIMARY KEY, type TEXT, name TEXT, UNIQUE(type, name))''')
    conn.commit()
    conn.close()

with app.app_context():
    init_db()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/programme-plan')
def programme_plan():
    return render_template('programme_plan.html')

# --- Document APIs ---
@app.route('/api/quotations', methods=['GET', 'POST'])
def manage_quotations():
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO quotations (q_no, customer, date, data) VALUES (%s, %s, %s, %s)",
                  (data['q_no'], data['customer'], data['date'], json.dumps(data['html_data'])))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    else:
        c.execute("SELECT q_no, customer, date, data FROM quotations ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return jsonify([{"q_no": r[0], "customer": r[1], "date": r[2], "data": r[3]} for r in rows])

@app.route('/api/sales_orders', methods=['GET', 'POST'])
def manage_sales_orders():
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO sales_orders (so_no, customer, date, data) VALUES (%s, %s, %s, %s)",
                  (data['so_no'], data['customer'], data['date'], json.dumps(data['html_data'])))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    else:
        c.execute("SELECT so_no, customer, date, data FROM sales_orders ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return jsonify([{"so_no": r[0], "customer": r[1], "date": r[2], "data": r[3]} for r in rows])

# --- Master Data Add/Edit/Upload APIs ---
@app.route('/api/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    # Upsert Logic: Customer ID එක දැනටමත් තිබේ නම් Update කරයි, නැත්නම් අලුතින් සාදයි
    c.execute("""
        INSERT INTO customers (id, name, address) VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, address = EXCLUDED.address
    """, (data['id'], data['name'], data['address']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/add_paper', methods=['POST'])
def add_paper():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    # Upsert Logic
    c.execute("""
        INSERT INTO paper_types (type, name) VALUES (%s, %s)
        ON CONFLICT (type, name) DO NOTHING
    """, (data['type'], data['name']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/upload_customers', methods=['POST'])
def upload_customers():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    for cust in data:
        c.execute("""
            INSERT INTO customers (id, name, address) VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, address = EXCLUDED.address
        """, (cust['id'], cust['name'], cust['address']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/upload_papers', methods=['POST'])
def upload_papers():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    for p in data:
        c.execute("""
            INSERT INTO paper_types (type, name) VALUES (%s, %s)
            ON CONFLICT (type, name) DO NOTHING
        """, (p['type'], p['name']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# --- Master Data Fetch APIs ---
@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, address FROM customers")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "address": r[2]} for r in rows])

@app.route('/api/papers', methods=['GET'])
def get_papers():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT type, name FROM paper_types")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"type": r[0], "name": r[1]} for r in rows])

if __name__ == '__main__':
    app.run(debug=True)
