from flask import Flask, render_template

app = Flask(__name__)

# Main Dashboard Route
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Routes for the new windows
@app.route('/programme-plan')
def programme_plan():
    return "<h1>Programme Plan Window</h1><p>Content goes here.</p>"

@app.route('/inventory')
def inventory():
    return "<h1>Inventory Window</h1><p>Content goes here.</p>"

@app.route('/production-floor')
def production_floor():
    return "<h1>Production Floor Management Window</h1><p>Content goes here.</p>"

@app.route('/finished-goods')
def finished_goods():
    return "<h1>Finished Goods Window</h1><p>Content goes here.</p>"

@app.route('/maintenance')
def maintenance():
    return "<h1>Maintenance Window</h1><p>Content goes here.</p>"

@app.route('/quality')
def quality():
    return "<h1>Quality Window</h1><p>Content goes here.</p>"

@app.route('/third-party')
def third_party():
    return "<h1>3rd Party Services Window</h1><p>Content goes here.</p>"

if __name__ == '__main__':
    app.run(debug=True)
