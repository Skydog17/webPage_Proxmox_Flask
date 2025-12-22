(''')from flask import Flask
from flask import url_for, request

from routes.default import app as bp_default

app = Flask(__name__)
app.register_blueprint(bp_default)

#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///labo1.db"

if __name__ == "__main__":
    app.run(debug=True)
(''')

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime

# ----------------------
# APP CONFIG
# ----------------------
app = Flask(__name__)
app.secret_key = "super-secret-key"

# Connessione MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://flaskuser:flaskpass@localhost/340_progetto"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ----------------------
# MODELLI DATABASE
# ----------------------

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('user','admin'), nullable=False)

class VMRequest(db.Model):
    __tablename__ = "vm_requests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vm_type = db.Column(db.Enum('bronze','silver','gold'), nullable=False)
    status = db.Column(db.Enum('pending','approved','created','rejected'), default='pending')
    created_at = db.Column(db.DateTime)

class VMInstance(db.Model):
    __tablename__ = "vm_instances"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('vm_requests.id'), nullable=False)
    hostname = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    vm_user = db.Column(db.String(50))
    vm_password = db.Column(db.String(50))

# ----------------------
# DECORATOR LOGIN
# ----------------------
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect("/")
            if role and session.get("role") != role:
                return "Accesso negato", 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ----------------------
# ROUTES LOGIN
# ----------------------
@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return render_template("login.html", error="Credenziali errate")

    session["user_id"] = user.id
    session["role"] = user.role

    if user.role == "admin":
        return redirect("/admin")
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ----------------------
# DASHBOARD UTENTE
# ----------------------
@app.route("/dashboard")
@login_required(role="user")
def dashboard():
    requests_vm = VMRequest.query.filter_by(user_id=session["user_id"]).all()
    return render_template("user_dashboard.html", requests=requests_vm)

@app.route("/request-vm", methods=["POST"])
@login_required(role="user")
def request_vm():
    vm_type = request.form["vm_type"]

    new_request = VMRequest(
        user_id=session["user_id"],
        vm_type=vm_type,
        status="pending",
        created_at=datetime.now()
    )
    db.session.add(new_request)
    db.session.commit()

    return redirect("/dashboard")

# ----------------------
# DASHBOARD ADMIN
# ----------------------
@app.route("/admin")
@login_required(role="admin")
def admin_dashboard():
    rows = (
        db.session.query(VMRequest, User.username)
        .join(User, VMRequest.user_id == User.id)
        .filter(VMRequest.status == "pending")
        .all()
    )

    requests_data = []
    for r, username in rows:
        requests_data.append({
            "id": r.id,
            "vm_type": r.vm_type,
            "username": username
        })

    return render_template("admin_dashboard.html", requests=requests_data)

@app.route("/approve/<int:req_id>")
@login_required(role="admin")
def approve(req_id):
    req = VMRequest.query.get(req_id)
    if not req:
        return "Richiesta non trovata", 404

    req.status = "created"

    # ----------------------------
    # SIMULAZIONE CREAZIONE VM
    # ----------------------------
    vm = VMInstance(
        request_id=req.id,
        hostname=f"vm-{req.id}",
        ip_address="192.168.1." + str(100 + req.id),
        vm_user="ubuntu",
        vm_password="password123"
    )
    db.session.add(vm)
    db.session.commit()

    db.session.commit()
    return redirect("/admin")

@app.route("/reject/<int:req_id>")
@login_required(role="admin")
def reject(req_id):
    req = VMRequest.query.get(req_id)
    if not req:
        return "Richiesta non trovata", 404

    req.status = "rejected"
    db.session.commit()
    return redirect("/admin")

@app.route("/vm/<int:req_id>")
@login_required()
def vm_details(req_id):
    vm = VMInstance.query.filter_by(request_id=req_id).first()
    if not vm:
        return "VM non trovata", 404
    return render_template("vm_details.html", vm=vm)

# ----------------------
# MAIN
# ----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # crea le tabelle se non esistono
    app.run(host="0.0.0.0", port=5000, debug=True)
