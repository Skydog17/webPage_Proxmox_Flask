# app.py
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from proxmoxer import ProxmoxAPI
from datetime import datetime

# ===== Flask e DB =====
app = Flask(__name__)
app.secret_key = "secretkey123"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://flaskuser:flaskpass@localhost/340_progetto"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ===== Login =====
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# ===== Modelli =====
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('user','admin'), nullable=False)

class VMRequest(db.Model):
    __tablename__ = 'vm_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vm_type = db.Column(db.Enum('bronze','silver','gold'), nullable=False)
    status = db.Column(db.Enum('pending','approved','created','rejected'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vm_instance = db.relationship('VMInstance', backref='request', uselist=False)

class VMInstance(db.Model):
    __tablename__ = 'vm_instances'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('vm_requests.id', ondelete="CASCADE"), nullable=False)
    hostname = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    vm_user = db.Column(db.String(50))
    vm_password = db.Column(db.String(50))

# ===== Login manager =====
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== Rotte =====
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

@app.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    if current_user.role == "admin":
        requests_list = VMRequest.query.all()
    else:
        requests_list = VMRequest.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", requests=requests_list, user=current_user)

@app.route("/request_vm", methods=["POST"])
@login_required
def request_vm():
    if current_user.role != "user":
        flash("Solo gli utenti possono richiedere VM")
        return redirect(url_for("dashboard"))
    
    vm_type = request.form['vm_type']
    new_req = VMRequest(user_id=current_user.id, vm_type=vm_type)
    db.session.add(new_req)
    db.session.commit()
    flash("Richiesta inviata")
    return redirect(url_for("dashboard"))

@app.route("/approve/<int:req_id>")
@login_required
def approve(req_id):
    if current_user.role != "admin":
        flash("Non hai i permessi")
        return redirect(url_for("dashboard"))

    req = VMRequest.query.get(req_id)
    if not req or req.status != "pending":
        flash("Richiesta non valida")
        return redirect(url_for("dashboard"))

    # ===== Connessione a Proxmox (cluster nodo fisso) =====
    proxmox = ProxmoxAPI(
        '192.168.56.15',    # nodo fisso del cluster
        user='root@pam',
        password='PASSWORD',
        port=8006,
        verify_ssl=False
    )

    vm_id = 100 + req.id
    vm_name = f"vm-{req.id}"
    template = {
        "bronze": "local:template-bronze",
        "silver": "local:template-silver",
        "gold": "local:template-gold"
    }[req.vm_type]

    target_node = "pve"  # nome nodo nel cluster, es. 'pve'
    # ===== Clonazione VM =====
    proxmox.nodes(target_node).qemu.clone.create(
        newid=vm_id,
        name=vm_name,
        full=True,
        target=target_node,
        base=template
    )

    # Aggiornamento DB
    vm = VMInstance(
        request_id=req.id,
        hostname=vm_name,
        ip_address="IP_DA_CONFIGURARE",
        vm_user="ubuntu",
        vm_password="password123"
    )
    db.session.add(vm)
    req.status = "created"
    db.session.commit()
    flash(f"VM {vm_name} creata")
    return redirect(url_for("dashboard"))

# ===== Avvio app =====
if __name__ == "__main__":
    app.run(host="192.168.56.101", port=5000, debug=True)
