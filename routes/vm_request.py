from flask import Blueprint,redirect,url_for,flash
from flask_login import login_required, current_user
from proxmoxer import ProxmoxAPI

from models.model import VMRequest, VMInstance
from models.connection import db

app = Blueprint('vmReq', __name__)

@app.route("/approve/<int:req_id>")
@login_required
def approve(req_id):
    if current_user.role != "admin":
        flash("Non hai i permessi")
        return redirect(url_for("default.dashboard"))

    req = VMRequest.query.get(req_id)
    if not req or req.status != "pending":
        flash("Richiesta non valida")
        return redirect(url_for("default.dashboard"))

    # ===== Connessione a Proxmox con API Token =====
    proxmox = ProxmoxAPI(
        '192.168.56.15',    # IP di un nodo del cluster
        user='root@pam',    # solo utente e realm
        token_name='flaskToken',  # il token creato in Proxmox
        token_value='35117d4a-2392-4d29-8275-d4de3bf1bb63',    # il secret generato
        port=8006,
        verify_ssl=False,
	timeout=60
    )

    # Template e risorse in base al tipo di VM richiesto
    lxc_templates = {
        "bronze": {"template": "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst", "cores": 1, "memory": 2048, "disk": 10},
        "silver": {"template": "local:vztmpl/ubuntu-24.04-standard_24.04-1_amd64.tar.zst", "cores": 2, "memory": 4096, "disk": 20},
        "gold": {"template": "local:vztmpl/ubuntu-24.04-standard_24.04-1_amd64.tar.zst", "cores": 4, "memory": 8192, "disk": 40}
    }

    tmpl = lxc_templates[req.vm_type]

    # Genera un nuovo ID per il container
    vm_id = 3020 + req.id  # esempio, assicurati sia libero
    vm_name = f"ct-{req.id}"

    # Nodo target nel cluster
    target_node = "px1"

    # ===== Creazione LXC =====
    task =  proxmox.nodes(target_node).lxc.create(
        vmid=vm_id,
        hostname=vm_name,
        ostemplate=tmpl["template"],
        cores=tmpl["cores"],
        memory=tmpl["memory"],
        swap=512,
        rootfs=f"local-lvm:{tmpl['disk']}",  # usa lo storage "local" per il root disk
        password="Password&1",           # password utente root del container
        net0="name=eth0,bridge=vmbr0,ip=dhcp"
    )

    print(task)

    # Aggiornamento DB
    vm = VMInstance(
        request_id=req.id,
        hostname=vm_name,
        ip_address="IP",
        vm_user="root",
        vm_password="Password&1"
    )
    db.session.add(vm)
    req.status = "created"
    db.session.commit()
    flash(f"Container {vm_name} creato")
    return redirect(url_for("default.dashboard"))