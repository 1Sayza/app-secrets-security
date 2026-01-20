# Vault Lab (PostgreSQL + Vault + Apps)

Laboratório com PostgreSQL, HashiCorp Vault (TLS) e duas aplicações:

- App Node (web) em app/

- App Python (Flask) em python/ (testada no ambiente)

O objetivo é demonstrar um fluxo seguro onde a aplicação obtém credenciais dinâmicas do banco via Vault (Database Secrets Engine), evitando credenciais fixas no código.

## Estrutura do projeto


```bash
vault-lab/
├── docker-compose.yml
├── vault/
│   ├── config/
│   │   └── vault.hcl
│   ├── scripts/
│   │   └── init-vault.sh
│   ├── data/
│   └── tls/
├── db/
│   └── init.sql
├── app/                       # aplicação Node (web)
│   ├── Dockerfile
│   ├── package.json
│   ├── index.js
│   └── index.html
└── python/                    # aplicação Python (Flask)
    ├── Dockerfile
    ├── requirements.txt
    └── app.py
```
- Observação: dentro de vault/ eu mantenho composes separados (DB, Vault e App). A ordem de subida é sempre DB → Vault → App(s).

## Pré-requisitos

Docker e Docker Compose (plugin docker compose)

OpenSSL (para gerar certificados TLS do Vault)

## 1) Subir o PostgreSQL (primeiro)

## 1.1 Subir o compose do banco

Se você tem compose separado do Postgres:

```bash
docker compose -f vault/docker-compose.postgres.yml up -d
```

Se o docker-compose.yml na raiz já contém o serviço:
```bash
docker compose up -d postgres
```
## 1.2 Verificar saúde do Postgres






