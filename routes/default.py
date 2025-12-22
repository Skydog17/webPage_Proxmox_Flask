from flask import Blueprint
from flask import render_template

app = Blueprint('default', __name__)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/user')
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/details')
def vm_details():
    return render_template('vm_details.html')