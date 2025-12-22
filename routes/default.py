from flask import Blueprint,render_template,redirect,request,url_for,render_template,flash
from flask_login import login_required, current_user

from models.model import VMRequest
from models.connection import db

app = Blueprint('default', __name__)

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
        return redirect(url_for("default.dashboard"))
    
    vm_type = request.form['vm_type']
    new_req = VMRequest(user_id=current_user.id, vm_type=vm_type)
    db.session.add(new_req)
    db.session.commit()
    flash("Richiesta inviata")
    return redirect(url_for("default.dashboard"))
