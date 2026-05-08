# Vault Lab (Vault → Postgres → Role dinâmico → Agent → App)

<img width="1196" height="447" alt="image" src="https://github.com/user-attachments/assets/f1d0fa4c-6f9b-465a-a811-b479b3a196f7" />


Laboratório com PostgreSQL, HashiCorp Vault (TLS) e uma aplicação:

- App Python (Flask) em python/ (testada no ambiente)

O objetivo é demonstrar um fluxo seguro onde a aplicação obtém credenciais dinâmicas do banco via Vault (Database Secrets Engine), evitando credenciais fixas no código.

## Estrutura do projeto


```bash
vault-lab/
├── app/                          # Aplicação Web (Node.js)
│   ├── Dockerfile
│   ├── index.html
│   ├── index.js
│   └── package.json
│
├── python/                       # Aplicação Python (Flask)
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── docker-compose-python.yml
│
├── db/                           # Bootstrap do banco (PostgreSQL)
│   └── init.sql
│
├── vault/                        # Vault (config, dados, TLS e scripts)
│   ├── config/
│   │   ├── vault.hcl             # Config do Vault (listener TLS + storage)
│   │   └── vault-agent.hcl       # Config do Vault Agent (AppRole + CA)
│   │
│   ├── scripts/
│   │   └── init-vault.sh         # Script de bootstrap (mount database, role, policy, approle)
│   │
│   ├── tls/                      # Certificados TLS (CA + cert do Vault)
│   │   ├── ca.crt
│   │   ├── ca.key
│   │   ├── ca.srl
│   │   ├── vault.crt
│   │   ├── vault.csr
│   │   ├── vault.ext
│   │   └── vault.key
│   │
│   ├── agent/                    # Arquivos do AppRole + token gerado pelo agent
│   │   ├── role_id               # AppRole RoleID
│   │   ├── secret_id             # AppRole SecretID
│   │   └── token                 # Token gerado (sink) para a aplicação ler
│   │
│   └── data/                     # Storage persistente do Vault (não versionar)
│
├── docker-compose-postgres.yml   # Compose do PostgreSQL
├── docker-compose-vault.yml      # Compose do Vault
├── docker-compose-vault-agent.yml# Compose do Vault Agent
├── docker-compose-web.yml        # Compose da aplicação Node (web)
└── docker-compose.yml            # (opcional) Compose raiz (se você usar tudo em um só)

```
- Observação: dentro de vault/ eu mantenho composes separados (DB, Vault e App). A ordem de subida é sempre DB → Vault → App(s).

## Pré-requisitos

Docker e Docker Compose (plugin docker compose)

OpenSSL (para gerar certificados TLS do Vault)

Curl para Teste

## 1) Clonar e entrar no projeto

```bash
git clone <SEU_REPO>
cd vault-lab
```

## 2) Criar a rede Docker (padronizada)

Todos os containers devem estar na mesma rede para resolver vault, vault-agfent, aplicação e postgres por nome.

```bash
docker network create vaultlab-net 2>/dev/null || true
```

 ## 4) Gerar TLS do Vault (CA + certificado do servidor)

 Os arquivos ficam em vault/tls/.

```bash
 mkdir -p vault/tls
cd vault/tls

# CA
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
  -subj "/C=BR/ST=RN/L=Natal/O=VaultLab/OU=DevSecOps/CN=VaultLab-CA" \
  -out ca.crt

# Cert do Vault (com SAN)
openssl genrsa -out vault.key 2048
openssl req -new -key vault.key -subj "/CN=vault" -out vault.csr

cat > vault.ext <<'EOF'
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=@alt_names

[alt_names]
DNS.1=vault
DNS.2=localhost
IP.1=127.0.0.1
EOF

openssl x509 -req -in vault.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out vault.crt -days 825 -sha256 -extfile vault.ext

sudo chmod 600 ca.key vault.key
sudo chmod 644 ca.crt vault.crt vault.ext vault.csr ca.srl

cd ../../

```
```bash
openssl x509 -in vault/tls/vault.crt -noout -text | grep -n "Subject Alternative Name" -A2
```
5) Subir o PostgreSQL (primeiro)
   
```bash 
docker compose -f docker-compose-postgres.yml up -d
```
## 6) Conferir se o init.sql foi aplicado:
```bash
docker exec -it postgres psql -U postgres -d sara_db -c "\dt"
```
## 7) Subir o Vault (segundo)
```bash
docker compose -f docker-compose-vault.yml up -d
```
## 8) Testar health com CA:
```bash
curl --cacert vault/tls/ca.crt https://127.0.0.1:8200/v1/sys/health
```
## 9) Inicializar/configurar o Vault (Database Engine + roles)

O script vault/scripts/init-vault.sh prepara:

database/ secrets engine

conexão do Vault com Postgres

role app-db para credenciais dinâmicas

policy e AppRole do vault-agent

```bash
vault/scripts/init-vault.sh
```
Ou também podemos configurar manualmente dentro do container do vault 

 Inicializar/Configurar Vault

- unseal (quando aplicável)

- database/ secrets engine

- conexão com Postgres e role app-db

- policy/approle (se usado por vault-agent)

## PASSO A PASSO CONFIGURANDO MANUALMENTE O VAULT

- SEGUE OS PRINTS

- OBS: OS TOKENS QUE APARECE SÃO APENAS DE LABORATÓRIO. 

<img width="522" height="593" alt="image" src="https://github.com/user-attachments/assets/f4dc6469-ffe9-4b98-8b9b-9aecfa651ae8" />

<img width="691" height="573" alt="image" src="https://github.com/user-attachments/assets/b6633392-ffa2-4f59-bed7-b6043855d41e" />

<img width="789" height="667" alt="image" src="https://github.com/user-attachments/assets/ee6f8195-c6c6-4b9c-b4e0-3edf7d61f98c" />

Se precisa desbloquear o vault usando os tokens que é gerado de início quando sobe o ambiente. No caso Unseal Key 1, 2, 3 e até o 5 gera. Guardar esses tokens gerados para quando necessitar subir o ambiente novamente. E também gera o Root token que é essencial para entrar
no ambiente e realiza login via web. 



## 10) Subir o Vault Agent (terceiro)

O vault-agent autentica no Vault via AppRole e grava um token em vault/agent/token, que a aplicação lê em runtime.

```bash
docker compose -f docker-compose-vault-agent.yml up -d
```

```bash
docker ps --filter "name=vault-agent"
docker logs --tail 80 vault-agent
docker exec -it vault-agent sh -lc 'ls -l /vault/agent/token && head -c 20 /vault/agent/token; echo'
```

## 11) Subir a aplicação Python (Flask) – opcional

Entre na pasta python/ e suba com o compose específico:

```bash
docker compose -f docker-compose-python.yml up -d --build
```
- Python: http://localhost:3001/ (ou a porta definida no compose)

## 12) Testes do fluxo (App → Vault → DB)

Testar se a app consegue buscar credenciais dinâmicas

```bash
docker exec -it simple-python-app sh -lc 'python - <<PY
import os, requests
addr=os.environ.get("VAULT_ADDR", "https://vault:8200")
tok=open("/vault/agent/token").read().strip()
r=requests.get(f"{addr}/v1/database/creds/app-db", headers={"X-Vault-Token": tok}, timeout=5)
print("status:", r.status_code)
print(r.text[:200])
PY'
```

## 13) Testar login via terminal (exemplo)

Observação que precisa criar dentro do banco um usuário e senha para validar a busca dos objetos do banco e validar a funcionalidade da aplicação do banckend se comunicar com o vualt agent > vault > banco. 
```bash
curl -i -X POST http://localhost:3001/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=<SEU_USUARIO>&password=<SUA_SENHA>"
```






