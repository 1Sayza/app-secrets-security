import os
import logging
import traceback
from typing import Tuple, Optional

import requests
import psycopg2
from flask import Flask, request, render_template_string
import bcrypt

app = Flask(__name__)

LOGIN_HTML = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Login</title></head>
<body style="font-family: Arial; max-width: 360px; margin: 80px auto;">
  <h2>Login Seguro</h2>
  <form method="post">
    <input name="username" placeholder="usuario" style="width:100%;padding:10px;margin:8px 0" required>
    <input name="password" type="password" placeholder="senha" style="width:100%;padding:10px;margin:8px 0">
    <button style="width:100%;padding:10px">Entrar</button>
  </form>
  {% if msg %}<p style="color: {{color}}">{{msg}}</p>{% endif %}
  {% if debug_detail %}<pre style="white-space: pre-wrap; background:#f7f7f7; padding:10px; border:1px solid #ddd;">{{debug_detail}}</pre>{% endif %}
</body>
</html>
"""

# ---------- config ----------
def env_true(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


APP_DEBUG = env_true("APP_DEBUG", "0")
ALLOW_PASSWORDLESS = env_true("ALLOW_PASSWORDLESS", "0")

VAULT_ADDR = os.getenv("VAULT_ADDR", "https://vault:8200")
VAULT_TOKEN_PATH = os.getenv("VAULT_TOKEN_PATH", "/vault/agent/token")
VAULT_DB_CREDS_PATH = os.getenv("VAULT_DB_CREDS_PATH", "database/creds/app-db")

logging.basicConfig(
    level=logging.DEBUG if APP_DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


# ---------- Vault helpers ----------
def get_vault_token() -> str:
    """
    Lê apenas o token renovável gerado pelo Vault Agent.
    A aplicação não lê mais /vault/agent/db.env.
    """
    if not os.path.exists(VAULT_TOKEN_PATH):
        raise RuntimeError(
            f"Token do Vault não encontrado em {VAULT_TOKEN_PATH}. "
            "Verifique se o Vault Agent está rodando e montado no container da aplicação."
        )

    with open(VAULT_TOKEN_PATH, "r", encoding="utf-8") as file:
        return file.read().strip()


def get_dynamic_db_credentials() -> Tuple[str, str]:
    """
    Busca credenciais dinâmicas diretamente no Vault.
    As credenciais ficam apenas em memória durante a execução da requisição.
    """
    token = get_vault_token()
    url = f"{VAULT_ADDR}/v1/{VAULT_DB_CREDS_PATH}"

    response = requests.get(
        url,
        headers={"X-Vault-Token": token},
        timeout=10,
        verify=os.getenv("REQUESTS_CA_BUNDLE", True)
    )

    response.raise_for_status()

    data = response.json()["data"]

    return data["username"], data["password"]


# ---------- Database ----------
def get_pg_conn():
    db_user, db_pass = get_dynamic_db_credentials()

    pg_host = os.getenv("PGHOST", "postgres")
    pg_port = int(os.getenv("PGPORT", "5432"))
    pg_db = os.getenv("PGDATABASE", "sara_db")

    return psycopg2.connect(
        host=pg_host,
        port=pg_port,
        dbname=pg_db,
        user=db_user,
        password=db_pass,
        connect_timeout=5,
    )


# ---------- Auth helpers ----------
def verify_password(stored_hash: Optional[str], provided_password: str) -> bool:
    """
    O campo password no banco está em bcrypt: $2a$, $2b$ ou $2y$.
    """
    if stored_hash is None:
        return False

    if provided_password == "":
        return ALLOW_PASSWORDLESS and (stored_hash.strip() == "")

    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        return bcrypt.checkpw(
            provided_password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )

    return stored_hash == provided_password


def check_login(username: str, password: str) -> Tuple[bool, str]:
    conn = get_pg_conn()

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password FROM public.users WHERE username = %s LIMIT 1;",
                (username,)
            )

            row = cur.fetchone()

            if not row:
                return False, "no_user"

            stored_hash = row[0]

            if verify_password(stored_hash, password):
                return True, "ok"

            return False, "bad_pass"

    finally:
        conn.close()


# ---------- routes ----------
@app.route("/health", methods=["GET"])
def health():
    conn = get_pg_conn()
    conn.close()

    return {
        "status": "ok",
        "message": "Aplicação conectou ao banco usando credenciais dinâmicas do Vault"
    }, 200


@app.route("/users", methods=["GET"])
def users():
    conn = get_pg_conn()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username FROM public.users ORDER BY id;")
            rows = cur.fetchall()

        result = []

        for row in rows:
            result.append({
                "id": row[0],
                "username": row[1]
            })

        return result, 200

    finally:
        conn.close()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = (request.form.get("username") or "").strip()
        p = request.form.get("password") or ""

        if not u:
            return render_template_string(
                LOGIN_HTML,
                msg="Informe o usuário.",
                color="red",
                debug_detail=None
            ), 400

        try:
            ok, why = check_login(u, p)

        except Exception:
            logging.exception("Erro no login")

            debug_detail = traceback.format_exc() if APP_DEBUG else None

            return render_template_string(
                LOGIN_HTML,
                msg="Erro interno ao autenticar. Veja os logs do container.",
                color="red",
                debug_detail=debug_detail
            ), 500

        if ok:
            return f"<h2>Seja bem-vindo, {u}!</h2>", 200

        if why == "no_user":
            return render_template_string(
                LOGIN_HTML,
                msg="Login não existe",
                color="red",
                debug_detail=None
            ), 401

        return render_template_string(
            LOGIN_HTML,
            msg="Senha incorreta",
            color="red",
            debug_detail=None
        ), 401

    return render_template_string(
        LOGIN_HTML,
        msg=None,
        color="black",
        debug_detail=None
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
