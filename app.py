
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "avia-chave-demonstracao")

# Configurações
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Perfis do sistema
ROLES = {
    "recebimento": "Operador de recebimento",
    "qualidade": "Inspetor de qualidade",
    "loja": "Gerente da loja",
    "compras": "Gestor de compras",
    "admin": "Administrador do sistema",
    "cliente": "Cliente"
}

# Permissões demonstrativas
PERMISSIONS = {
    "recebimento": ["upload_recebimento"],
    "qualidade": ["upload_qualidade"],
    "loja": ["produtos", "estoque", "compras"],
    "compras": ["produtos", "compras"],
    "admin": [
        "produtos", "estoque", "compras",
        "upload_recebimento", "upload_qualidade"
    ],
    "cliente": ["produtos"]
}

# Usuários demonstrativos
USERS = {
    "admin@avia.com": {
        "password": "avia123",
        "role": "admin"
    },
    "recebimento@avia.com": {
        "password": "123",
        "role": "recebimento"
    },
    "qualidade@avia.com": {
        "password": "123",
        "role": "qualidade"
    },
    "loja@avia.com": {
        "password": "123",
        "role": "loja"
    },
    "compras@avia.com": {
        "password": "123",
        "role": "compras"
    }
}

# Página inicial
@app.route("/")
def home():
    return render_template("index.html")


# Login
@app.route("/login/<role>", methods=["GET", "POST"])
def login(role):

    if role not in ROLES:
        return render_template("acesso_negado.html"), 404

    if request.method == "POST":

        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")

        user = USERS.get(email)

        if user and user["password"] == password:

            if user["role"] != role:
                flash("Este usuário não pertence ao perfil selecionado.", "error")
                return redirect(url_for("login", role=role))

            session["email"] = email
            session["role"] = role

            return redirect(url_for("dashboard"))

        flash("E-mail ou senha incorretos.", "error")

    return render_template(
        "login.html",
        role=role,
        role_name=ROLES[role]
    )


# Cadastro de clientes
@app.route("/cadastro", methods=["GET", "POST"])
def register_client():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Preencha todos os campos.", "error")

        elif email in USERS:
            flash("Este e-mail já está cadastrado.", "error")

        else:
            USERS[email] = {
                "password": password,
                "role": "cliente",
                "name": name
            }

            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("login", role="cliente"))

    return render_template("cadastro.html")


# Recuperação de senha
@app.route("/recuperar", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        session["recovery_email"] = email

        return redirect(url_for("verification"))

    return render_template("recuperar.html")


# Verificação simulada
@app.route("/verificacao")
def verification():

    email = session.get("recovery_email")

    if not email:
        return redirect(url_for("forgot_password"))

    return render_template(
        "verificacao.html",
        email=email
    )


# Painel
@app.route("/painel")
def dashboard():

    if "email" not in session:
        return redirect(url_for("home"))

    role = session["role"]

    return render_template(
        "painel.html",
        email=session["email"],
        role=role,
        role_name=ROLES[role],
        permissions=PERMISSIONS[role]
    )


# Controle de permissões
def authorized(permission):

    if "email" not in session:
        return False

    role = session.get("role")

    return permission in PERMISSIONS.get(role, [])


# Produtos
@app.route("/produtos")
def products():

    if not authorized("produtos"):
        return render_template("acesso_negado.html"), 403

    return render_template("produtos.html")


# Estoque
@app.route("/estoque")
def inventory():

    if not authorized("estoque"):
        return render_template("acesso_negado.html"), 403

    return render_template("estoque.html")


# Compras
@app.route("/compras")
def purchases():

    if not authorized("compras"):
        return render_template("acesso_negado.html"), 403

    return render_template("compras.html")


# Verificação de imagem
def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# Upload de recebimento
@app.route("/recebimento", methods=["GET", "POST"])
def upload_receiving():

    if not authorized("upload_recebimento"):
        return render_template("acesso_negado.html"), 403

    if request.method == "POST":

        file = request.files.get("image")

        if not file or file.filename == "":
            flash("Selecione uma imagem.", "error")

        elif not allowed_file(file.filename):
            flash("Formato de imagem não permitido.", "error")

        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            flash("Imagem enviada com sucesso!", "success")

    return render_template("recebimento.html")

@app.route('/documentacao')
def documentacao():
    return render_template('documentacao.html')

# Upload de qualidade
@app.route("/qualidade", methods=["GET", "POST"])
def upload_quality():

    if not authorized("upload_qualidade"):
        return render_template("acesso_negado.html"), 403

    if request.method == "POST":

        file = request.files.get("image")

        if not file or file.filename == "":
            flash("Selecione uma imagem.", "error")

        elif not allowed_file(file.filename):
            flash("Formato de imagem não permitido.", "error")

        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            flash("Imagem enviada com sucesso!", "success")

    return render_template("qualidade.html")



# Encerrar sessão
@app.route("/logout")
def logout():

    session.clear()

    flash("Você saiu do sistema.", "success")

    return redirect(url_for("home"))


# Inicialização
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
