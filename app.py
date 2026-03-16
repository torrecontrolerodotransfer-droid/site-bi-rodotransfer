from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "rodotransfer-secret"

# Usuários
USERS = {
    "operacional": generate_password_hash("123"),
    "gerencia": generate_password_hash("123"),
    "comercial": generate_password_hash("123")
}

# Permissões
USER_PERMISSIONS = {
    "operacional": ["manifestos","coletas"],
    "gerencia": ["manifestos","coletas","vendas"],
    "comercial": ["vendas"]
}

# Relatórios
REPORTS = [

{
"id":"manifestos",
"title":"Acompanhamento Manifestos",
"embedUrl":"https://app.powerbi.com/view?r=SEU_LINK_AQUI"
},

{
"id":"coletas",
"title":"Acompanhamento de Coletas",
"embedUrl":"https://app.powerbi.com/view?r=SEU_LINK_AQUI"
},

{
"id":"vendas",
"title":"Vendas x Comissão",
"embedUrl":"https://app.powerbi.com/view?r=SEU_LINK_AQUI"
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

        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and check_password_hash(USERS[username], password):

            session["user"] = username

            return redirect(url_for("dashboard"))

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

    report = next((r for r in REPORTS if r["id"] == report_id), None)

    return render_template("report.html", report=report)


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()