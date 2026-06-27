from flask import Flask, render_template, request, jsonify
import sqlite3
import json

app = Flask(__name__)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Create Quotations Table
    c.execute('''CREATE TABLE IF NOT EXISTS quotations 
                 (id INTEGER PRIMARY KEY, q_no TEXT, customer TEXT, date TEXT, data TEXT)''')
    # Create Sales Orders Table
    c.execute('''CREATE TABLE IF NOT EXISTS sales_orders 
                 (id INTEGER PRIMARY KEY, so_no TEXT, customer TEXT, date TEXT, data TEXT)''')
    conn.commit()
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
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO quotations (q_no, customer, date, data) VALUES (?, ?, ?, ?)",
                  (data['q_no'], data['customer'], data['date'], json.dumps(data['html_data'])))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    else:
        c.execute("SELECT q_no, customer, date, data FROM quotations")
        rows = c.fetchall()
        conn.close()
        return jsonify(rows)

# API for Sales Orders
@app.route('/api/sales_orders', methods=['GET', 'POST'])
def manage_sales_orders():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO sales_orders (so_no, customer, date, data) VALUES (?, ?, ?, ?)",
                  (data['so_no'], data['customer'], data['date'], json.dumps(data['form_data'])))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    else:
        c.execute("SELECT so_no, customer, date, data FROM sales_orders")
        rows = c.fetchall()
        conn.close()
        return jsonify(rows)

# Other routes...
@app.route('/inventory')
def inventory(): return "<h1>Inventory Window</h1>"
@app.route('/production-floor')
def production_floor(): return "<h1>Production Floor Management Window</h1>"
@app.route('/finished-goods')
def finished_goods(): return "<h1>Finished Goods Window</h1>"
@app.route('/maintenance')
def maintenance(): return "<h1>Maintenance Window</h1>"
@app.route('/quality')
def quality(): return "<h1>Quality Window</h1>"
@app.route('/third-party')
def third_party(): return "<h1>3rd Party Services Window</h1>"

if __name__ == '__main__':
    app.run(debug=True)
