# -*- coding: utf-8 -*-
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from models.connection import db
from models.model import User

from routes.auth import app as bp_auth
from routes.default import app as bp_default
from routes.vm_request import app as bp_vmReq

import os
from dotenv import load_dotenv
load_dotenv()

# ===== Flask e DB
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

# ===== Blueprint
app.register_blueprint(bp_auth)
app.register_blueprint(bp_default)
app.register_blueprint(bp_vmReq)

# ===== LoginManager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== Avvio app
if __name__ == "__main__":
    app.run(host="192.168.56.101", port=5000, debug=True)
