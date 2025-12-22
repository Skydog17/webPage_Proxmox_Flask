from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user, logout_user,login_required

from models.connection import db
from models.model import User

app = Blueprint('auth', __name__)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Credenziali errate")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))