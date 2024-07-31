from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Diretório para salvar os arquivos CSV
if not os.path.exists('data'):
    os.makedirs('data')

CSV_FILE = 'data/calls.csv'

# Cria o arquivo CSV com o cabeçalho se não existir
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Nome', 'Departamento', 'Unidade', 'Telefone', 'Descrição', 'Status', 'Data de Abertura', 'Prioridade'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    departamento = request.form['departamento']
    unidade = request.form['unidade']
    telefone = request.form['telefone']
    descricao = request.form['descricao']
    data_abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Calcula a prioridade baseada na hora
    abertura = datetime.now()
    hora_atual = abertura.hour
    if hora_atual < 8:
        prioridade = 'Baixa'
    elif 8 <= hora_atual < 17:
        prioridade = 'Média'
    else:
        prioridade = 'Alta'

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nome, departamento, unidade, telefone, descricao, 'Aberto', data_abertura, prioridade])

    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':  # Alterar as credenciais aqui
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return "Credenciais inválidas. Tente novamente."

    return render_template('admin.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        # Atualiza o status do chamado
        status = request.form.get('status')
        row_id = int(request.form.get('row_id'))

        rows = []
        with open(CSV_FILE, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header
            rows = list(reader)
        
        if 0 <= row_id < len(rows):
            rows[row_id][5] = status  # Atualiza o status na coluna apropriada
        
            with open(CSV_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)  # Reescreve o cabeçalho
                writer.writerows(rows)
        
        return redirect(url_for('dashboard'))

    calls = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip header
        calls = list(reader)

    return render_template('dashboard.html', calls=calls)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('admin'))

#Descomentar para rodar somente no servidor
#if __name__ == '__main__':
#    app.run(debug=True)

#Roda na rede interna.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
