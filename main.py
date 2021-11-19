import sqlite3    
import smtplib
from flask import Flask, render_template, request
app = Flask(__name__)

def conectar():
    return sqlite3.connect('emcomendas.db')
    
def criaTabelas():
    conexao = conectar()
    sql = """CREATE TABLE IF NOT EXISTS ENCOMENDAS(
    id integer PRIMARY KEY,
    description text
    destinatario text, 
    ramal integer, 
    email text,
    retirada integer ); """

    conexao.cursor().execute(sql)
    conexao.commit()
    conexao.close()
    return

def cadastraEncomenda(description, destinatario, ramal, email):
    conexao = conectar()
    encomenda = (description, destinatario, ramal, email, 0);
    sql = "INSERT INTO ENCOMENDAS(description, destinatario, ramal, email, retirada) VALUES (?, ?, ?, ?, ?)";
    conexao.cursor().execute(sql, encomenda)
    conexao.commit()
    conexao.close()
    return

def listarEncomendas():
    conexao = conectar();
    cursor = conexao.cursor();
    cursor.execute("SELECT id, destinatario, ramal, email, description, retirada FROM ENCOMENDAS ORDER BY retirada ASC")
    lista = cursor.fetchall()
    conexao.close()
    return lista


def encomendaRetirada(idEncomenda):
    conexao = conectar()
    sql ="UPDATE ENCOMENDAS SET retirada = 1 WHERE ID = ?";
    conexao.cursor().execute(sql, (idEncomenda))
    conexao.commit()
    conexao.close()
    return

def limaparTabela():
    conexao = conectar()
    sql ="DELETE FROM  ENCOMENDAS";
    conexao.cursor().execute(sql)
    conexao.commit()
    conexao.close()
    return
    
def notificarMorador(emailMorador, destinatario):
    usuarioGmail="";
    senhaGmail=""
    enderecoGmail=""
   
    try:
        if usuarioGmail and senhaGmail and enderecoGmail:
            corpoEmail = """\
            From: %s
            To: %s
            Subject: Retirar Encomenda
            
            Sr(a) %s, favor retirar encomenda na portaria.
            """ % (enderecoGmail, emailMorador, destinatario)

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(usuarioGmail, senhaGmail)
            server.sendmail(enderecoGmail, email, corpoEmail)
            server.close()
    except:
        return
    return
   
@app.route('/', methods=['GET','POST'])
def index():
    destinatario = request.form.get("destinatario")
    ramal = request.form.get("ramal")    
    description = request.form.get("description")
    idEncomenda = request.form.get("id")
    email = request.form.get("email")

    if request.method == 'POST':
        if destinatario and ramal and description:
            cadastraEncomenda(description, destinatario, ramal, email)
            notificarMorador(email, destinatario)
        if idEncomenda:
            encomendaRetirada(idEncomenda)
    
    encomendas = listarEncomendas()
    return render_template("index.html", encomendas=encomendas)
    
@app.route('/criar')
def criar():
    criaTabelas()
    return "<h1>Tabelas criadas</h1>"
    
@app.route('/limpar')
def limpar():
    limaparTabela()
    return "<h1>Tabela limpa</h1>"
