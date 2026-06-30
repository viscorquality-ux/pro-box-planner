from flask import Flask, render_template, request, jsonify
import psycopg2
import json
import pandas as pd
import io
import csv

app = Flask(__name__)

# Aiven PostgreSQL Database Configuration
DB_HOST = "probox123-viscorquality-0270.l.aivencloud.com"
DB_PORT = "28643" # කරුණාකර ඔබගේ Aiven Port එක මෙහි යොදන්න (සාමාන්‍යයෙන් 25060 හෝ අදාළ port එක)
DB_USER = "avnadmin" # ඔබගේ Aiven User Name එක
DB_PASS = "AVNS_AJNctiNyP1ujHPV3mh8" # ඔබගේ Aiven Password එක
DB_NAME = "defaultdb" # ඔබගේ Aiven Database Name එක

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )

# Initialize Database Tables
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Customers Table
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                 customer_id VARCHAR(50) PRIMARY KEY, customer_name TEXT, address TEXT)''')
    # Paper Types Table
    c.execute('''CREATE TABLE IF NOT EXISTS paper_types (
                 id SERIAL PRIMARY KEY, paper_type TEXT, paper_name TEXT)''')
    # Quotations Table
    c.execute('''CREATE TABLE IF NOT EXISTS quotations (
                 id SERIAL PRIMARY KEY, q_no TEXT, customer TEXT, date TEXT, data JSONB)''')
    # Sales Orders Table
    c.execute('''CREATE TABLE IF NOT EXISTS sales_orders (
                 id SERIAL PRIMARY KEY, so_no TEXT, customer TEXT, date TEXT, data JSONB)''')
    conn.commit()
    c.close()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    return render_template('programme_plan.html') # Main file as requested

# ================= APIs for Quotations and Sales Orders =================

@app.route('/api/quotations', methods=['GET', 'POST'])
def manage_quotations():
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO quotations (q_no, customer, date, data) VALUES (%s, %s, %s, %s)",
                  (data['q_no'], data['customer'], data['date'], json.dumps(data['html_data'])))
        conn.commit()
        c.close()
        conn.close()
        return jsonify({"status": "success"})
    else:
        c.execute("SELECT q_no, customer, date, data FROM quotations ORDER BY id DESC")
        rows = c.fetchall()
        c.close()
        conn.close()
        return jsonify([{"q_no": r[0], "customer": r[1], "date": r[2], "data": r[3]} for r in rows])

@app.route('/api/sales_orders', methods=['GET', 'POST'])
def manage_sales_orders():
    conn = get_db_connection()
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
        c.execute("SELECT so_no, customer, date, data FROM sales_orders ORDER BY id DESC")
        rows = c.fetchall()
        c.close()
        conn.close()
        return jsonify([{"so_no": r[0], "customer": r[1], "date": r[2], "data": r[3]} for r in rows])

# ================= APIs for Updating Master Data (Customers & Papers) =================

@app.route('/api/upload_data', methods=['POST'])
def upload_data():
    conn = get_db_connection()
    c = conn.cursor()
    
    if 'customer_file' in request.files:
        file = request.files['customer_file']
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            c.execute('''INSERT INTO customers (customer_id, customer_name, address) 
                         VALUES (%s, %s, %s) ON CONFLICT (customer_id) 
                         DO UPDATE SET customer_name = EXCLUDED.customer_name, address = EXCLUDED.address''',
                      (row.iloc[0], row.iloc[1], row.iloc[2]))
                      
    if 'paper_file' in request.files:
        file = request.files['paper_file']
        df = pd.read_csv(file)
        c.execute("TRUNCATE TABLE paper_types RESTART IDENTITY") # Clear old list
        for _, row in df.iterrows():
            c.execute("INSERT INTO paper_types (paper_type, paper_name) VALUES (%s, %s)", 
                      (row.iloc[0].strip(), row.iloc[1].strip()))
                      
    conn.commit()
    c.close()
    conn.close()
    return jsonify({"status": "success", "message": "Data Updated Successfully!"})

# ================= APIs for Auto-fill =================

@app.route('/api/get_customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT customer_name, address FROM customers WHERE customer_id = %s", (customer_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    if row:
        return jsonify({"found": True, "name": row[0], "address": row[1]})
    return jsonify({"found": False})

@app.route('/api/get_papers', methods=['GET'])
def get_papers():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT paper_type, paper_name FROM paper_types")
    rows = c.fetchall()
    c.close()
    conn.close()
    
    paper_dict = {}
    for r in rows:
        p_type = r[0]
        p_name = r[1]
        if p_type not in paper_dict:
            paper_dict[p_type] = []
        paper_dict[p_type].append(p_name)
        
    return jsonify(paper_dict)

if __name__ == '__main__':
    app.run(debug=True)
