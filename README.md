# ProgettoFinale\_M340



## Descrizione

Portale web per la creazione e gestione di container su Proxmox. Permette a utenti non amministrativi di richiedere macchine virtuali, mentre gli admin possono approvare o rifiutare le richieste. Il portale interagisce con l’hypervisor Proxmox tramite API.



## Prerequisiti

\- Macchina Proxmox con almeno 3 schede di rete: NAT, Rete interna, Host-only

\- Container/VM per ospitare il portale con: Python 3.10, pip, Flask, MySQL server



## Installazione

1\. Configurazione rete del container:

&nbsp;  - Scheda 1: IP statico 192.168.56.101 (accesso al portale)

&nbsp;  - Scheda 2: DHCP (accesso a internet)

2\. Clonare il repository:

&nbsp;  - git clone <URL\_REPO>

&nbsp;  - cd webPage\_Proxmox\_Flask



3\. Creare e attivare l’ambiente virtuale:

&nbsp;  - python3 -m venv venv

&nbsp;  - source venv/bin/activate



4\. Installare le dipendenze:

&nbsp;  - pip install -r requirements.txt





5\. Configurare il database copiando il contenuto del file `db.txt` nel database MySQL

6\. Creare un token, così da potersi collegare dall'api
&nbsp;  - Datacenter -> Permissions -> API Tokens - Add
&nbsp;  - Salvare il secret perchè non si potrà più vedere

7\. Creare un file .env nella cartella del progetto
Dentro questo file bisognerà inserire:
&nbsp;  - SQLALCHEMY_DATABASE_URI = URL del DB

&nbsp;  - SECRET_KEY = Chiave segreta

&nbsp;  - SECRET_TOKEN = Il SECRET del token prima generato

&nbsp;  - TOKEN_NAME = Il nome del token (TokenID)

&nbsp;  - VM_USER = Il nome dell'user delle VM create

&nbsp;  - VM_PASS = la password dell'user delle VM create


## Avvio del portale

python3 app.py
Accedere via browser all’IP statico del container: `http://192.168.56.101:5000`


## Login e ruoli

**Utente standard (`user`)**: visualizza i propri container, controlla lo stato e le informazioni, può richiedere la creazione di un container  

**Amministratore (`admin`)**: visualizza tutte le richieste, può approvare o rifiutare le richieste, crea container tramite API Proxmox



## Funzionamento

1\. L’utente effettua una richiesta di container tramite portale  

2\. L’admin approva o rifiuta la richiesta  

3\. In caso di approvazione, il portale crea il container su Proxmox usando l’API  

4\. Il portale restituisce le informazioni della macchina (hostname, IP, credenziali) all’utente



## Fonti

1\. \[Proxmox API Documentation](https://pve.proxmox.com/pve-docs/api-viewer/index.html#/nodes/{node}/lxc) 

2\. \[LoginManager Documentation] (https://flask-login.readthedocs.io/en/latest/)

3\. \[StackOverflow - Creare un container via API](https://stackoverflow.com/questions/51133991/proxmoxer-how-to-create-lxc-container-specifying-disk-size)

4\. \[Forum Proxmox - Avviare un container](https://forum.proxmox.com/threads/hi-i-know-proxmoxer-is-not-developed-by-the-proxmox-team-but.146170)

5\. \[ChatGPT - Creazione Frontend](https://chatgpt.com)
