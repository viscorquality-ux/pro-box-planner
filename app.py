import os
import psycopg2
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Database connection function using Environment Variables
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            dbname=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Initialize Database Tables
def init_db():
    conn = get_db_connection()
    if conn:
        c = conn.cursor()
        # Quotations Table
        c.execute('''CREATE TABLE IF NOT EXISTS quotations 
                     (id SERIAL PRIMARY KEY, q_no TEXT, customer TEXT, date TEXT, data JSONB)''')
        # Sales Orders Table
        c.execute('''CREATE TABLE IF NOT EXISTS sales_orders 
                     (id SERIAL PRIMARY KEY, so_no TEXT, customer TEXT, date TEXT, data JSONB)''')
        # Master Data Tables
        c.execute('''CREATE TABLE IF NOT EXISTS master_customers 
                     (customer_id TEXT PRIMARY KEY, customer_name TEXT, customer_address TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS master_papers 
                     (id SERIAL PRIMARY KEY, paper_type TEXT, paper_name TEXT)''')
        conn.commit()
        c.close()
        conn.close()

init_db()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')
    
@app.route('/programme-plan')
def programme_plan():
    return render_template('programme_plan.html')
    
# API for Quotations
@app.route('/api/quotations', methods=['GET', 'POST'])
def manage_quotations():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Connection Failed"}), 500
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO quotations (q_no, customer, date, data) VALUES (%s, %s, %s, %s)",
                  (data['q_no'], data['customer'], data['date'], json.dumps(data['form_data'])))
        conn.commit()
        c.close()
        conn.close()
        return jsonify({"status": "success"})
    else:
        c.execute("SELECT q_no, customer, date, data FROM quotations")
        rows = c.fetchall()
        c.close()
        conn.close()
        return jsonify(rows)

# API for Sales Orders
@app.route('/api/sales_orders', methods=['GET', 'POST'])
def manage_sales_orders():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Connection Failed"}), 500
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO sales_orders (so_no, customer, date, data) VALUES (%s, %s, %s, %s)",
                  (data['so_no'], data['customer'], data['date'], json.dumps(data['form_data'])))
        conn.commit()
        c.close()
        conn.close()
        return jsonify({"status": "success"})
    else:
        c.execute("SELECT so_no, customer, date, data FROM sales_orders")
        rows = c.fetchall()
        c.close()
        conn.close()
        return jsonify(rows)
# --- අලුතින් එක් කළ යුතු API Routes ---

@app.route('/api/upload_customers', methods=['POST'])
def upload_customers():
    data = request.json # ලැයිස්තුවක් ලෙස එන JSON දත්ත
    conn = get_db_connection()
    c = conn.cursor()
    for row in data:
        # Upsert: ID එක තිබේ නම් දත්ත යාවත්කාලීන කරන්න, නැත්නම් අලුතින් දාන්න
        c.execute("""
            INSERT INTO master_customers (customer_id, customer_name, customer_address)
            VALUES (%s, %s, %s)
            ON CONFLICT (customer_id) 
            DO UPDATE SET customer_name = EXCLUDED.customer_name, customer_address = EXCLUDED.customer_address
        """, (row['id'], row['name'], row['address']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
# Manual data add karanna / edit karanna aluth route ekak
@app.route('/api/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    # ID eka thiyanawa nam update karanna, nathnam aluthin add karanna (Upsert)
    c.execute("""
        INSERT INTO master_customers (customer_id, customer_name, customer_address)
        VALUES (%s, %s, %s)
        ON CONFLICT (customer_id) 
        DO UPDATE SET customer_name = EXCLUDED.customer_name, customer_address = EXCLUDED.customer_address
    """, (data['id'], data['name'], data['address']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/upload_papers', methods=['POST'])
def upload_papers():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    for row in data:
        # Upsert: පවතින දත්ත මකා නොදැමීම
        c.execute("""
            INSERT INTO master_papers (paper_type, paper_name)
            VALUES (%s, %s)
            ON CONFLICT (paper_type, paper_name) DO NOTHING
        """, (row['type'], row['name']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
