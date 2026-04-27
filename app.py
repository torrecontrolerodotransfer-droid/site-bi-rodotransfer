

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "rodotransfer-secret-key-2025"

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Usuários
USERS = {
    'operacional': generate_password_hash('Rodo@2025'),    
    'frotas': generate_password_hash('Rodo.2025'),
    'comercial': generate_password_hash('Rodo2025@'),
    'sac': generate_password_hash('Rodo@2025'),
    'financeiro': generate_password_hash('Rodo.2025'),
    'gerencia': generate_password_hash('Rodo2025@'),
    'coordenacao': generate_password_hash('Rodo@2025'),
    'torre_de_controle': generate_password_hash('Rodo.2025'),
    'supervisao': generate_password_hash('Rodo2025@')
}

# Permissões
USER_PERMISSIONS = {
    'frotas': ['monitoramento','multa','checklist'],
    'comercial': ['vendas-comissao'],
    'gerencia': ['acompanhamento-entrega','vendas-comissao','manifestos','follow-up','coletas','monitoramento','checklist'],
    'operacional': ['acompanhamento-entrega','manifestos','coletas'],
    'financeiro': ['Gestão de Clientes'],
    'coordenacao': ['acompanhamento-entrega','manifestos','coletas'],
    'supervisao': ['acompanhamento-entrega','manifestos','coletas'],
    'sac': ['acompanhamento-entrega'],
    'torre_de_controle': ['acompanhamento-entrega','vendas-comissao','manifestos','follow-up','coletas','monitoramento','multa','checklist']
}

# Relatórios
REPORTS = [
    {
        "id":"acompanhamento-entrega",
        "title":"Acompanhamento de Entrega",
        "embedUrl":"https://app.powerbi.com/view?r=eyJrIjoiZjYxNGZmYjctMDYzZC00NDk3LTk4ODgtMmQ0MTEzYTEzNTllIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9"
    },
    {
        "id":"vendas-comissao",
        "title":"Vendas de Fretes x Comissão",
        "embedUrl":"https://app.powerbi.com/view?r=eyJrIjoiMmIyNDI3M2ItNjIwOS00MmZmLWIzZjctZmJiZGFkNzU0Y2VhIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9"
    },
    {
        "id":"manifestos",
        "title":"Acompanhamento Manifestos",
        "embedUrl":"https://app.powerbi.com/view?r=eyJrIjoiNmI3ZmFmNzAtM2FmYy00NjdjLWIyMGMtN2FlMjRiMmM3ZThhIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9"
    },
    {
        "id":"Gestão de Clientes",
        "title":"Gestão de Clientes",
        "embedUrl":"https://app.powerbi.com/view?r=eyJrIjoiMmViZWU5ZDItOTY4Yi00ZDg1LWI4MzgtYjZlYzczMTE5M2I4IiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9"
    },
    {
        "id":"coletas",
        "title":"Acompanhamento de Coletas",
        "embedUrl":"https://app.powerbi.com/view?r=eyJrIjoiZGNkZTllYmUtMzMxOC00MDI4LWE0NDgtZTA2MjZmMTZhYjBlIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9"
    },
    {
        "id":"monitoramento",
        "title":"Gestão de Monitoramento e Telemetria",
        "embedUrl":"https://app.powerbi.com/view?r=eyJrIjoiOGY1ZGMwZDctMjg5NC00MjE3LWJhMjItN2E1MjM0ZTU4M2FjIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9"
    },
    {
        "id":"multa",
        "title":"Gestão de Multas",
        "embedUrl":"https://app.powerbi.com/view?r=eyJrIjoiNDU4NTdmMjAtNjFiZS00YTJmLTk5NmUtNWNlNDFlYjU5NTY1IiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9"
    },
    {
        "id":"checklist",
        "title":"Acompanhamento de Check List",
        "embedUrl":"https://app.powerbi.com/view?r=eyJrIjoiOTY2MWJhOGQtYTJkNS00ODU1LWE3YzAtZTMxOWI4NzA1MjQ4IiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9"
    }
]

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username in USERS and check_password_hash(USERS[username], password):

            session.permanent = True
            session["user"] = username

            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Usuário ou senha inválidos")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]

    allowed = USER_PERMISSIONS.get(user, [])

    user_reports = [r for r in REPORTS if r["id"] in allowed]

    return render_template("dashboard.html", reports=user_reports)

@app.route("/report/<report_id>")
def report(report_id):

    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]

    allowed = USER_PERMISSIONS.get(user, [])

    if report_id not in allowed:
        return redirect(url_for("dashboard"))

    report = next((r for r in REPORTS if r["id"] == report_id), None)

    if not report:
        return redirect(url_for("dashboard"))

    return render_template("report.html", report=report)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()
