import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'chave-secreta-cartorio-afetivo'
DATABASE = 'date_agendor.db'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # Create dates table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS dates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seu_nome TEXT NOT NULL,
                nome_donzela TEXT NOT NULL,
                whatsapp_donzela TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                quem_paga TEXT NOT NULL,
                comida TEXT NOT NULL,
                assunto TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                invitation_id INTEGER
            )
        ''')

        # Create custom_invitations table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS custom_invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_pretendente TEXT NOT NULL,
                whatsapp_pretendente TEXT,
                titulo TEXT NOT NULL,
                subtitulo TEXT NOT NULL,
                opcao_comida_1 TEXT NOT NULL,
                opcao_comida_2 TEXT NOT NULL,
                opcao_comida_3 TEXT NOT NULL,
                opcao_comida_4 TEXT NOT NULL,
                opcao_paga_1 TEXT NOT NULL,
                opcao_paga_2 TEXT NOT NULL,
                opcao_paga_3 TEXT NOT NULL,
                opcao_paga_4 TEXT NOT NULL,
                opcao_assunto_1 TEXT NOT NULL,
                opcao_assunto_2 TEXT NOT NULL,
                opcao_assunto_3 TEXT NOT NULL,
                opcao_assunto_4 TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Ensure invitation_id column exists in dates (for backward compatibility if DB exists)
        try:
            conn.execute('ALTER TABLE dates ADD COLUMN invitation_id INTEGER')
        except sqlite3.OperationalError:
            pass

        conn.commit()

@app.route('/')
def index():
    # Renderiza página principal que contém o Quiz interativo
    invite_id = request.args.get('c')
    invite = None
    if invite_id:
        try:
            with get_db() as conn:
                invite = conn.execute('SELECT * FROM custom_invitations WHERE id = ?', (invite_id,)).fetchone()
        except Exception:
            pass
    return render_template('index.html', invite=invite)

@app.route('/convite/<int:invite_id>')
def convite(invite_id):
    invite = None
    try:
        with get_db() as conn:
            invite = conn.execute('SELECT * FROM custom_invitations WHERE id = ?', (invite_id,)).fetchone()
    except Exception:
        pass
    if not invite:
        return "Convite não encontrado no cartório afetivo!", 404
    return render_template('index.html', invite=invite)

@app.route('/agendar_post', methods=['POST'])
def agendar_post():
    # Coleta todas informações do Quiz e formulário final
    seu_nome = request.form.get('seu_nome', 'Candidato a date')
    nome_donzela = request.form.get('nome_donzela', 'Donzela de honra')
    whatsapp_donzela = request.form.get('whatsapp_donzela', 'Sem whatsapp')
    data_hora = request.form.get('data_hora', 'No futuro')
    quem_paga = request.form.get('quem_paga', 'Não definido')
    comida = request.form.get('comida', 'Copo d\'água')
    assunto = request.form.get('assunto', 'Fofocas')
    invitation_id = request.form.get('invitation_id')

    if not invitation_id or invitation_id == '':
        invitation_id = None
    else:
        try:
            invitation_id = int(invitation_id)
        except ValueError:
            invitation_id = None

    # Formatação amigável de data e hora
    try:
        if 'T' in data_hora:
            data, hora = data_hora.split('T')
            ano, mes, dia = data.split('-')
            data_formatada = f"{dia}/{mes}/{ano} {hora}"
        else:
            data_formatada = data_hora
    except Exception:
        data_formatada = data_hora

    # Insere informações no banco de dados SQLite
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO dates (seu_nome, nome_donzela, whatsapp_donzela, data_hora, quem_paga, comida, assunto, invitation_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (seu_nome, nome_donzela, whatsapp_donzela, data_formatada, quem_paga, comida, assunto, invitation_id))
        conn.commit()
        last_id = cursor.lastrowid

    # Redireciona para o certificado permanente gerado por ID
    return redirect(url_for('certificado', date_id=last_id))

@app.route('/certificado/<int:date_id>')
def certificado(date_id):
    # Procura o date correspondente no banco de dados
    with get_db() as conn:
        row = conn.execute('SELECT * FROM dates WHERE id = ?', (date_id,)).fetchone()

    if not row:
        return "Contrato de date não encontrado no cartório afetivo!", 404

    return render_template('certificado.html', date=row)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('painel'))
        else:
            flash('Credenciais inválidas no Cartório Afetivo!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/painel')
@login_required
def painel():
    # Recupera todos os dates salvos
    with get_db() as conn:
        all_dates = conn.execute('SELECT * FROM dates ORDER BY id DESC').fetchall()
        try:
            all_invites = conn.execute('SELECT * FROM custom_invitations ORDER BY id DESC').fetchall()
        except sqlite3.OperationalError:
            all_invites = []

    # Estatísticas básicas para o painel
    total_dates = len(all_dates)
    confirmados = len([d for d in all_dates if d['status'] == 'Confirmado'])
    pendentes = len([d for d in all_dates if d['status'] == 'Pendente'])
    recusados = len([d for d in all_dates if d['status'] == 'Recusado'])

    # Captura mensagem de sucesso se houver
    novo_link = request.args.get('novo_link')

    return render_template(
        'painel.html',
        dates=all_dates,
        invites=all_invites,
        total_dates=total_dates,
        confirmados=confirmados,
        pendentes=pendentes,
        recusados=recusados,
        novo_link=novo_link
    )

@app.route('/painel/criar_convite', methods=['POST'])
@login_required
def criar_convite():
    nome_pretendente = request.form.get('nome_pretendente', 'Cupido')
    whatsapp_pretendente = request.form.get('whatsapp_pretendente', '')
    titulo = request.form.get('titulo', 'Você recebeu um convite especial')
    subtitulo = request.form.get('subtitulo', 'Valide sua compatibilidade emocional')

    opcao_comida_1 = request.form.get('opcao_comida_1', 'Pizza Clássica')
    opcao_comida_2 = request.form.get('opcao_comida_2', 'Restaurante Chique')
    opcao_comida_3 = request.form.get('opcao_comida_3', 'Dogão Duplo')
    opcao_comida_4 = request.form.get('opcao_comida_4', 'Presença Minimalista')

    opcao_paga_1 = request.form.get('opcao_paga_1', 'Você Paga Tudo')
    opcao_paga_2 = request.form.get('opcao_paga_2', 'Dividimos 12x')
    opcao_paga_3 = request.form.get('opcao_paga_3', 'Eu Pago Tudo')
    opcao_paga_4 = request.form.get('opcao_paga_4', 'Quem comer por último')

    opcao_assunto_1 = request.form.get('opcao_assunto_1', 'Fofocas Aleatórias')
    opcao_assunto_2 = request.form.get('opcao_assunto_2', 'Teorias da Conspiração')
    opcao_assunto_3 = request.form.get('opcao_assunto_3', 'Doutrina Miojo')
    opcao_assunto_4 = request.form.get('opcao_assunto_4', 'Mega-Sena Projetada')

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO custom_invitations (
                nome_pretendente, whatsapp_pretendente, titulo, subtitulo,
                opcao_comida_1, opcao_comida_2, opcao_comida_3, opcao_comida_4,
                opcao_paga_1, opcao_paga_2, opcao_paga_3, opcao_paga_4,
                opcao_assunto_1, opcao_assunto_2, opcao_assunto_3, opcao_assunto_4
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nome_pretendente, whatsapp_pretendente, titulo, subtitulo,
            opcao_comida_1, opcao_comida_2, opcao_comida_3, opcao_comida_4,
            opcao_paga_1, opcao_paga_2, opcao_paga_3, opcao_paga_4,
            opcao_assunto_1, opcao_assunto_2, opcao_assunto_3, opcao_assunto_4
        ))
        conn.commit()
        last_id = cursor.lastrowid

    novo_link = url_for('convite', invite_id=last_id, _external=True)
    return redirect(url_for('painel', novo_link=novo_link))

@app.route('/painel/status/<int:date_id>', methods=['POST'])
@login_required
def alterar_status(date_id):
    novo_status = request.form.get('status')
    if novo_status in ['Pendente', 'Confirmado', 'Recusado']:
        with get_db() as conn:
            conn.execute('UPDATE dates SET status = ? WHERE id = ?', (novo_status, date_id))
            conn.commit()
    return redirect(url_for('painel'))

@app.route('/painel/excluir/<int:date_id>', methods=['POST'])
@login_required
def excluir_date(date_id):
    with get_db() as conn:
        conn.execute('DELETE FROM dates WHERE id = ?', (date_id,))
        conn.commit()
    return redirect(url_for('painel'))

@app.route('/painel/excluir_convite/<int:invite_id>', methods=['POST'])
@login_required
def excluir_convite(invite_id):
    with get_db() as conn:
        conn.execute('DELETE FROM custom_invitations WHERE id = ?', (invite_id,))
        conn.commit()
    return redirect(url_for('painel'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
