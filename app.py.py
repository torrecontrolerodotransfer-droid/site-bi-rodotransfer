
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rodotransfer-secret-key-2025'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Usuários com senhas
USERS = {
    'operacional': generate_password_hash('Rodo@2025'),
    'frotas': generate_password_hash('Rodo.2025'),
    'comercial': generate_password_hash('Rodo2025@'),
    'sac': generate_password_hash('Rodo@2025'),
    'financeiro': generate_password_hash('Rodo.2025'),
    'gerencia': generate_password_hash('Rodo2025@'),
    'coordenacao': generate_password_hash('Rodo@2025'),
    'torre_de_controle': generate_password_hash('Rodo.2025'),
    'supervisao': generate_password_hash('Rodo2025@'),
}

# Mapeamento de permissões: usuário → IDs dos relatórios que pode acessar
USER_PERMISSIONS = {
    'frotas': ['monitoramento'],
    'comercial': ['vendas-comissao'],
    'gerencia': ['acompanhamento-entrega', 'vendas-comissao', 'manifestos', 'follow-up', 'coletas', 'monitoramento'],
    'operacional': ['acompanhamento-entrega', 'manifestos', 'coletas'],
    'financeiro': ['follow-up'],
    'coordenacao': ['acompanhamento-entrega', 'manifestos', 'coletas'],
    'supervisao': ['acompanhamento-entrega', 'manifestos', 'coletas'],
    'sac': ['acompanhamento-entrega'],
    'torre_de_controle': ['acompanhamento-entrega', 'vendas-comissao', 'manifestos', 'follow-up', 'coletas', 'monitoramento'],
}

# Relatórios do Power BI
REPORTS = [
    {
        'id': 'acompanhamento-entrega',
        'title': 'Acompanhamento de Entrega',
        'description': 'Monitoramento de entregas em tempo real',
        'embedUrl': 'https://app.powerbi.com/view?r=eyJrIjoiZjYxNGZmYjctMDYzZC00NDk3LTk4ODgtMmQ0MTEzYTEzNTllIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9',
    },
    {
        'id': 'vendas-comissao',
        'title': 'Vendas de Fretes x Comissão',
        'description': 'Análise de vendas e comissões',
        'embedUrl': 'https://app.powerbi.com/view?r=eyJrIjoiMmIyNDI3M2ItNjIwOS00MmZmLWIzZjctZmJiZGFkNzU0Y2VhIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9',
    },
    {
        'id': 'manifestos',
        'title': 'Acompanhamento Manifestos',
        'description': 'Gestão de manifestos de carga',
        'embedUrl': 'https://app.powerbi.com/view?r=eyJrIjoiNmI3ZmFmNzAtM2FmYy00NjdjLWIyMGMtN2FlMjRiMmM3ZThhIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9',
    },
    {
        'id': 'follow-up',
        'title': 'Follow Up',
        'description': 'Acompanhamento de atividades',
        'embedUrl': 'https://app.powerbi.com/view?r=eyJrIjoiYjAxYjQ5YjYtODQzZi00NzhkLThhYzEtOTJmMWVlMjk3ZTNlIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9',
    },
    {
        'id': 'coletas',
        'title': 'Acompanhamento de Coletas',
        'description': 'Gestão de coletas de mercadorias',
        'embedUrl': 'https://app.powerbi.com/view?r=eyJrIjoiZGNkZTllYmUtMzMxOC00MDI4LWE0NDgtZTA2MjZmMTZhYjBlIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9',
    },
    {
        'id': 'monitoramento',
        'title': 'Gestão de Monitoramento e Telemetria',
        'description': 'Monitoramento de frota e telemetria',
        'embedUrl': 'https://app.powerbi.com/view?r=eyJrIjoiOGY1ZGMwZDctMjg5NC00MjE3LWJhMjItN2E1MjM0ZTU4M2FjIiwidCI6IjkyM2UxNzhmLTliMDQtNDRjNy1hNzEzLWE4ODRiMWFiYjk2NCJ9',
    },
]

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and check_password_hash(USERS[username], password):
            session.permanent = True
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Usuário ou senha inválidos')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Filtrar relatórios que o usuário tem permissão de acessar
    user = session['user']
    allowed_report_ids = USER_PERMISSIONS.get(user, [])
    user_reports = [r for r in REPORTS if r['id'] in allowed_report_ids]
    
    return render_template('dashboard.html', user=user, reports=user_reports)

@app.route('/report/<report_id>')
def report(report_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    allowed_report_ids = USER_PERMISSIONS.get(user, [])
    
    # Verificar se o usuário tem permissão de acessar este relatório
    if report_id not in allowed_report_ids:
        return redirect(url_for('dashboard'))
    
    report = next((r for r in REPORTS if r['id'] == report_id), None)
    if not report:
        return redirect(url_for('dashboard'))
    
    # Filtrar relatórios que o usuário tem permissão de acessar
    user_reports = [r for r in REPORTS if r['id'] in allowed_report_ids]
    
    return render_template('report.html', user=user, report=report, reports=user_reports)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 