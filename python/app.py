import os
import logging
import traceback
from pathlib import Path
from typing import Dict, Tuple, Optional

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

APP_DEBUG = env_true("APP_DEBUG", "0")                   # mostra detalhe do erro na tela (lab)
ALLOW_PASSWORDLESS = env_true("ALLOW_PASSWORDLESS", "0")  # permite senha vazia (lab)
ENV_FILE_PATH = os.getenv("DB_ENV_FILE", "/vault/agent/db.env")

logging.basicConfig(
    level=logging.DEBUG if APP_DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# ---------- helpers ----------
def parse_env_file(path: str) -> Dict[str, str]:
    """
    Lê arquivo estilo KEY=VALUE e retorna dict.
    Ex: /vault/agent/db.env com DB_USER e DB_PASS.
    """
    p = Path(path)
    if not p.exists():
        return {}

    out: Dict[str, str] = {}
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def get_db_creds() -> Tuple[str, str]:
    """
    Preferência:
    1) /vault/agent/db.env (atualiza sem precisar recriar container)
    2) env vars (DB_USER/DB_PASS ou PGUSER/PGPASSWORD)
    """
    d = parse_env_file(ENV_FILE_PATH)

    user = d.get("DB_USER") or d.get("PGUSER") or os.getenv("DB_USER") or os.getenv("PGUSER")
    pwd = d.get("DB_PASS") or d.get("PGPASSWORD") or os.getenv("DB_PASS") or os.getenv("PGPASSWORD")

    if not user or not pwd:
        raise RuntimeError(
            "Credenciais do Postgres não encontradas. "
            "Esperado DB_USER/DB_PASS (ou PGUSER/PGPASSWORD) no /vault/agent/db.env ou env vars."
        )
    return user, pwd

def get_pg_conn():
    db_user, db_pass = get_db_creds()

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

def verify_password(stored_hash: Optional[str], provided_password: str) -> bool:
    """
    stored_hash no banco está em bcrypt ($2a$ / $2b$ / $2y$...)
    """
    if stored_hash is None:
        return False

    # senha vazia: só permite se ALLOW_PASSWORDLESS=1 e stored_hash está vazio
    if provided_password == "":
        return ALLOW_PASSWORDLESS and (stored_hash.strip() == "")

    # bcrypt
    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        return bcrypt.checkpw(
            provided_password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )

    # fallback (não recomendado): comparação direta
    return stored_hash == provided_password

def check_login(username: str, password: str) -> Tuple[bool, str]:
    """
    Retorna (ok, motivo)
    motivo:
      - "ok"
      - "no_user"
      - "bad_pass"
    """
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
    return {"status": "ok"}, 200

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = (request.form.get("username") or "").strip()
        p = request.form.get("password") or ""

        if not u:
            return render_template_string(
                LOGIN_HTML, msg="Informe o usuário.", color="red", debug_detail=None
            ), 400

        try:
            ok, why = check_login(u, p)
        except Exception:
            logging.exception("Erro no login")
            debug_detail = traceback.format_exc() if APP_DEBUG else None
            return render_template_string(
                LOGIN_HTML,
                msg="Erro interno (veja docker logs).",
                color="red",
                debug_detail=debug_detail
            ), 500

        if ok:
            return f"<h2>Seja bem-vindo, {u}!</h2>", 200

        if why == "no_user":
            return render_template_string(
                LOGIN_HTML, msg="Login não existe", color="red", debug_detail=None
            ), 401

        return render_template_string(
            LOGIN_HTML, msg="Senha incorreta", color="red", debug_detail=None
        ), 401

    return render_template_string(LOGIN_HTML, msg=None, color="black", debug_detail=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

