# Vault Lab (PostgreSQL + Vault + Apps)

Laboratório com PostgreSQL, HashiCorp Vault (TLS) e duas aplicações:

- App Node (web) em app/

- App Python (Flask) em python/ (testada no ambiente)

O objetivo é demonstrar um fluxo seguro onde a aplicação obtém credenciais dinâmicas do banco via Vault (Database Secrets Engine), evitando credenciais fixas no código.

## Estrutura do projeto


```bash
vault-lab/
├── docker-compose.yml docker-compose-postgres.yml docker-compose-app.yml
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

```bash
docker ps
docker logs --tail 100 postgres
```
## 1.3 Validar se o init.sql rodou

```bash
docker exec -it postgres psql -U postgres -d postgres -c "\l"
docker exec -it postgres psql -U postgres -d sara_db -c "\dt app.*"
```

## 2) Subir e configurar o Vault com TLS (segundo)

## 2.1 Gerar certificados TLS (CA + cert do Vault)

Crie/entre na pasta:

- mkdir -p vault/tls
- cd vault/tls

Gere a CA:

```bash
openssl genrsa -out ca.key 4096 openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
-subj "/C=BR/ST=RN/L=Natal/O=VaultLab/OU=DevSecOps/CN=VaultLab-CA" \
-out ca.crt
```

Gere o cert do Vault com SAN para vault e 127.0.0.1:

```bash
openssl genrsa -out vault.key 2048
openssl req -new -key vault.key -subj "/CN=vault" -out vault.csr

cat > vault.ext <<'EOF'
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth subjectAltName=@alt_names

[alt_names]
DNS.1=vault
DNS.2=localhost
IP.1=127.0.0.1
EOF

openssl x509 -req -in vault.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
-out vault.crt -days 825 -sha256 -extfile vault.ext
```
Permissões recomendadas:
```bash
sudo chmod 600 vault.key ca.key
sudo chmod 644 vault.crt ca.crt
```

Volte para a raiz:

cd ../../

## 2.2 Subir o Vault

Se você tem compose separado do Vault:

```bash
docker compose -f vault/docker-compose.vault.yml up -d
```
Se está na raiz:

```bash
docker compose up -d vault
```
## 3) Inicializar/Configurar Vault

- unseal (quando aplicável)

- database/ secrets engine

- conexão com Postgres e role app-db

- policy/approle (se usado por vault-agent)

## 4) Subir as aplicações (terceiro)

## 4.1 Aplicação Node (pasta app/)

Compose separado:

```bash
docker compose -f vault/docker-compose.app.yml up -d --build
```

Ou pela raiz:

```bash
docker compose up -d --build app
```

Acesso: http://localhost:<porta_publicada_no_compose>/

## 4.2 Aplicação Python (pasta python/)

Build e run manual (exemplo padrão do lab):

```bash
cd python
docker build -t simple-python-app:1 .
docker rm -f simple-python-app 2>/dev/null

docker run -d --name simple-python-app --network vaultlab-net -p 3001:3000 \
  -e VAULT_ADDR="https://vault:8200" \
  -e REQUESTS_CA_BUNDLE="/etc/ssl/certs/vault-ca.crt" \
  -v "$HOME/vault-lab/vault/tls/ca.crt:/etc/ssl/certs/vault-ca.crt:ro" \
  -v "$HOME/vault-lab/vault/agent:/vault/agent:ro" \
  -e PGHOST="postgres" \
  -e PGDATABASE="sara_db" \
  simple-python-app:1

Acesso: http://localhost:3001/

Teste login via terminal:

curl -i -X POST http://localhost:3001/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=<user>&password=<SUA_SENHA_CADASTRADA>"

``` 


