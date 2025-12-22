# -*- coding: utf-8 -*-
from flask import Flask
from flask_login import LoginManager

from models.connection import db
from models.model import User

from routes.auth import app as bp_auth
from routes.default import app as bp_default

# ===== Flask e DB
app = Flask(__name__)
app.secret_key = "secretkey123"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://flaskuser:flaskpass@localhost/340_progetto"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ===== Blueprint
app.register_blueprint(bp_auth)
app.register_blueprint(bp_default)

# ===== Usato nel progetto del Laboratorio 1
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== Avvio app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # crea tabelle se non esistono
    app.run(host="192.168.56.101", port=5000, debug=True)
