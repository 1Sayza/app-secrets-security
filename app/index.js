const express = require("express");
const path = require("path");
const fs = require("fs");
const axios = require("axios");
const https = require("https");
const { Client } = require("pg");

const app = express();

/* =========================
   Middlewares
========================= */
app.use(express.json());
app.use(express.static(path.join(__dirname)));

/* =========================
   Vault Config
========================= */
const VAULT_ADDR = process.env.VAULT_ADDR || "https://vault:8200";
const VAULT_TOKEN_PATH =
  process.env.VAULT_TOKEN_PATH || "/vault/agent/token";

/* =========================
   Helpers
========================= */
function getVaultToken() {
  const token = fs.readFileSync(VAULT_TOKEN_PATH, "utf8").trim();
  console.log("[VAULT] Token lido com sucesso");
  return token;
}

async function getDbCredentials() {
  console.log("[VAULT] Buscando credenciais no Vault...");
  const token = getVaultToken();

  const response = await axios.get(
    `${VAULT_ADDR}/v1/database/creds/app-role`,
    {
      headers: {
        "X-Vault-Token": token
      },
      httpsAgent: new https.Agent({
        rejectUnauthorized: false
      })
    }
  );

  console.log("[VAULT] Credenciais recebidas:", response.data.data.username);
  return response.data.data;
}

/* =========================
   Routes
========================= */
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  console.log("[LOGIN] Tentativa de login:", username);

  let client;

  try {
    const dbCreds = await getDbCredentials();

    console.log("[DB] Conectando no Postgres...");
    client = new Client({
      host: "postgres",
      port: 5432,
      user: dbCreds.username,
      password: dbCreds.password,
      database: "sara_db"
    });

    await client.connect();
    console.log("[DB] Conectado com sucesso");

    const query = `
      SELECT id, username
      FROM users
      WHERE username = $1
        AND password = crypt($2, password)
    `;

    console.log("[DB] Executando query...");
    const result = await client.query(query, [username, password]);

    console.log("[DB] Resultado:", result.rowCount);

    if (result.rowCount === 0) {
      return res.status(401).json({
        error: "Usuário ou senha inválidos"
      });
    }

    return res.json({
      login: "sucesso",
      user: result.rows[0]
    });

  } catch (err) {
    console.error("❌ ERRO REAL:", err.message);

    return res.status(500).json({
      error: "Erro interno",
      details: err.message
    });

  } finally {
    if (client) {
      await client.end();
      console.log("[DB] Conexão encerrada");
    }
  }
});

/* =========================
   Server
========================= */
app.listen(3000, () => {
  console.log("Aplicação segura rodando na porta 3000");
});

