# Implementação de Gestão de Segredos de Aplicações

Este repositório apresenta uma prova de conceito desenvolvida para o Trabalho de Conclusão de Curso intitulado:

**Implementação de Gestão de Segredos de Aplicações: Uma Prova de Conceito Usando a Solução HashiCorp Vault Integrada a Pipeline de Implantação de Sistemas Web Distribuídos**

O objetivo deste projeto é demonstrar, de forma prática, como uma aplicação web pode acessar um banco de dados sem manter credenciais fixas no código-fonte, em arquivos de configuração ou em variáveis de ambiente expostas.

Para isso, a solução utiliza o **HashiCorp Vault** como gerenciador centralizado de segredos, integrado ao **Vault Agent**, ao banco de dados **PostgreSQL**, a uma aplicação web e a uma estrutura de **pipeline CI/CD com GitLab e GitLab Runner**. O Vault é responsável por gerar credenciais dinâmicas e temporárias para acesso ao banco, enquanto a pipeline automatiza etapas de validação, implantação e testes da aplicação.

---

## Objetivo do laboratório

Este laboratório foi desenvolvido para validar uma abordagem segura de gerenciamento de segredos em aplicações web distribuídas.

A proposta demonstra o seguinte fluxo:

1. O desenvolvedor envia o código-fonte para o GitLab.
2. A pipeline de CI/CD é acionada automaticamente.
3. A pipeline executa etapas de validação, implantação e testes.
4. A aplicação é implantada sem armazenar usuário e senha fixos do banco de dados.
5. O Vault Agent autentica no HashiCorp Vault utilizando AppRole.
6. A aplicação utiliza um token controlado para solicitar credenciais ao Vault.
7. O Vault gera credenciais dinâmicas e temporárias no PostgreSQL.
8. A aplicação utiliza essas credenciais para acessar o banco.
9. Após o tempo de vida configurado, as credenciais expiram automaticamente.

Com isso, o projeto demonstra a substituição do modelo tradicional baseado em credenciais estáticas por um modelo mais seguro, baseado em credenciais temporárias, automação e controle de acesso.

---

## Tecnologias utilizadas

* HashiCorp Vault
* Vault Agent
* PostgreSQL
* Docker
* Docker Compose
* GitLab
* GitLab Runner
* Pipeline CI/CD
* Python Flask
* OpenSSL
* Linux/WSL

---

## Arquitetura da solução

A arquitetura do laboratório é composta pelos seguintes elementos:

* **GitLab:** utilizado como repositório de código-fonte e ponto de acionamento da pipeline.
* **GitLab Runner:** responsável por executar os estágios definidos na pipeline.
* **Pipeline CI/CD:** realiza as etapas de validação, implantação e teste da aplicação.
* **Aplicação Web:** simula o consumo de dados protegidos no banco.
* **Vault Agent:** realiza a autenticação automática no Vault utilizando AppRole.
* **HashiCorp Vault:** gerencia políticas, autenticação e geração de credenciais dinâmicas.
* **PostgreSQL:** banco de dados utilizado para validar o acesso com credenciais temporárias.
* **Docker Compose:** utilizado para orquestrar os serviços do laboratório.

Fluxo resumido da solução:

```text
Desenvolvedor
      |
      | Push do código
      v
GitLab
      |
      | Aciona pipeline
      v
GitLab Runner
      |
      | Validação / Deploy / Testes
      v
Aplicação Web
      |
      | Solicita credenciais
      v
Vault Agent
      |
      | Autentica via AppRole
      v
HashiCorp Vault
      |
      | Gera credenciais temporárias
      v
PostgreSQL
```

---

## Estrutura do projeto

```text
vault-lab/
├── LICENSE
├── README.md
├── app/
│   ├── Dockerfile
│   ├── index.html
│   ├── index.js
│   └── package.json
│
├── db/
│   └── init.sql
│
├── docker-compose-gitlab.yml
├── docker-compose-postgres.yml
├── docker-compose-vault-agent.yml
├── docker-compose-vault.yml
│
├── gitlab-runner/
│   └── config/
│       └── config.toml
│
├── python/
│   ├── Dockerfile
│   ├── app.py
│   ├── docker-compose-python.yml
│   └── requirements.txt
│
├── scripts/
│   ├── deploy-python.sh
│   ├── test-python.sh
│   └── validate.sh
│
└── vault/
    ├── agent/
    │   ├── role_id
    │   ├── secret_id
    │   ├── token
    │   └── templates/
    │       └── db.env.tpl
    │
    ├── config/
    │   ├── vault-agent.hcl
    │   └── vault.hcl
    │
    ├── data/
    └── tls/
        ├── ca.crt
        ├── ca.key
        ├── ca.srl
        ├── vault.crt
        ├── vault.csr
        ├── vault.ext
        └── vault.key
```

---

## Descrição dos principais diretórios

### `app/`

Contém uma aplicação web em Node.js utilizada nas etapas iniciais do laboratório. Essa aplicação representa um serviço web que pode ser implantado em ambiente distribuído.

### `python/`

Contém a aplicação principal em Python Flask. Essa aplicação utiliza o token disponibilizado pelo Vault Agent para solicitar credenciais dinâmicas ao HashiCorp Vault e acessar o banco PostgreSQL.

### `db/`

Contém o script `init.sql`, responsável pela criação inicial da base de dados, tabelas e permissões necessárias para o funcionamento do laboratório.

### `vault/`

Contém os arquivos relacionados ao HashiCorp Vault, incluindo configurações, certificados TLS, dados persistentes e arquivos utilizados pelo Vault Agent.

### `gitlab-runner/`

Contém a configuração do GitLab Runner, responsável por executar os jobs da pipeline CI/CD.

### `scripts/`

Contém scripts auxiliares utilizados pela pipeline:

* `validate.sh`: realiza validações iniciais do ambiente e dos arquivos necessários.
* `deploy-python.sh`: executa o processo de implantação da aplicação Python.
* `test-python.sh`: realiza testes para validar se a aplicação foi implantada corretamente.

---

## Pipeline CI/CD

A pipeline de CI/CD tem como objetivo automatizar o processo de validação, implantação e teste da aplicação.

Ela representa uma etapa importante da prova de conceito, pois demonstra que a aplicação pode ser implantada de forma automatizada sem expor credenciais sensíveis diretamente no código-fonte ou nos arquivos da pipeline.

O fluxo da pipeline contempla três etapas principais:

```text
validate → deploy → test
```

### Etapa `validate`

Responsável por verificar se os arquivos necessários para a implantação estão presentes e se o ambiente possui a estrutura esperada.

Exemplo de validações:

* presença dos arquivos da aplicação;
* presença dos arquivos Docker;
* presença dos scripts de implantação;
* verificação básica da estrutura do projeto.

### Etapa `deploy`

Responsável por realizar a implantação da aplicação Python utilizando Docker Compose.

Nessa etapa, a aplicação é publicada ou atualizada no ambiente, mantendo a lógica de acesso seguro aos segredos por meio do Vault.

### Etapa `test`

Responsável por validar se a aplicação está em execução corretamente após a implantação.

Essa etapa pode incluir testes de disponibilidade, verificação de health check e validação do funcionamento básico da aplicação.

---

## Pré-requisitos

Antes de executar o laboratório, é necessário possuir:

* Docker instalado
* Docker Compose instalado
* OpenSSL instalado
* Curl instalado
* Git instalado
* Ambiente Linux ou WSL no Windows

---

## Como executar o laboratório

Esta seção apresenta o passo a passo para subir o ambiente do laboratório utilizando Docker, HashiCorp Vault, PostgreSQL, Vault Agent, aplicação Python e GitLab CI/CD.

---

### 1. Clonar o repositório

Clone o repositório do projeto e acesse o diretório principal:

```bash
git clone https://github.com/1Sayza/app-secrets-security.git
cd app-secrets-security
```

---

### 2. Criar a rede Docker

Antes de subir os containers, crie a rede Docker utilizada pelos serviços do laboratório:

```bash
docker network create vaultlab-net
```

Caso a rede já exista, você pode seguir para o próximo passo.

---

### 3. Subir o banco PostgreSQL

O PostgreSQL será utilizado como banco de dados da aplicação.

```bash
docker compose -f docker-compose-postgres.yml up -d
```

Verifique se o container está em execução:

```bash
docker ps
```

Se tudo estiver correto, o container do PostgreSQL será exibido na lista.

---

### 4. Subir o HashiCorp Vault

Agora suba o container do HashiCorp Vault:

```bash
docker compose -f docker-compose-vault.yml up -d
```

Verifique se o container foi iniciado:

```bash
docker ps
```

Também é possível acompanhar os logs do Vault:

```bash
docker logs vault
```

---

### 5. Inicializar e desbloquear o Vault

Após iniciar o container do Vault, acesse o container:

```bash
docker exec -it vault sh
```

Configure as variáveis de ambiente dentro do container:

```bash
export VAULT_ADDR=https://127.0.0.1:8200
export VAULT_CACERT=/vault/tls/ca.crt
```

Inicialize o Vault:

```bash
vault operator init
```

Esse comando irá gerar as **chaves de unseal** e o **token root**.

> Guarde essas informações, pois elas serão necessárias para desbloquear e configurar o Vault.

Agora desbloqueie o Vault utilizando três chaves de unseal:

```bash
vault operator unseal
```

Repita o comando três vezes, informando uma chave diferente em cada execução.

Depois, faça login com o token root:

```bash
vault login
```

---

### 6. Configurar o Vault para gerar credenciais do banco

Habilite o mecanismo de segredos de banco de dados:

```bash
vault secrets enable database
```

Configure a conexão do Vault com o PostgreSQL:

```bash
vault write database/config/sara-db \
  plugin_name=postgresql-database-plugin \
  allowed_roles="app-db" \
  connection_url="postgresql://{{username}}:{{password}}@postgres:5432/sara_db?sslmode=disable" \
  username="vault_admin" \
  password="vault_admin"
```

Crie a role responsável por gerar credenciais temporárias:

```bash
vault write database/roles/app-db \
  db_name=sara-db \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT CONNECT ON DATABASE sara_db TO \"{{name}}\"; GRANT USAGE ON SCHEMA app TO \"{{name}}\"; GRANT SELECT ON ALL TABLES IN SCHEMA app TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"
```

Teste se o Vault consegue gerar credenciais dinâmicas:

```bash
vault read database/creds/app-db
```

Se tudo estiver correto, o Vault irá retornar um usuário e uma senha temporários para acesso ao PostgreSQL.

---

### 7. Configurar autenticação AppRole

Habilite o método de autenticação AppRole:

```bash
vault auth enable approle
```

Crie uma policy para permitir que a aplicação leia as credenciais dinâmicas:

```bash
vault policy write app-policy - <<EOF
path "database/creds/app-db" {
  capabilities = ["read"]
}
EOF
```

Crie a role da aplicação:

```bash
vault write auth/approle/role/app \
  token_policies="app-policy" \
  token_ttl="1h" \
  token_max_ttl="4h"
```

Gere o `role_id`:

```bash
vault read -field=role_id auth/approle/role/app/role-id > /vault/agent/role_id
```

Gere o `secret_id`:

```bash
vault write -field=secret_id -f auth/approle/role/app/secret-id > /vault/agent/secret_id
```

Saia do container do Vault:

```bash
exit
```

---

### 8. Subir o Vault Agent

O Vault Agent será responsável por autenticar no Vault usando AppRole e gerar um token para a aplicação.

```bash
docker compose -f docker-compose-vault-agent.yml up -d
```

Verifique os logs do Vault Agent:

```bash
docker logs vault-agent
```

Verifique se o token foi criado:

```bash
docker exec -it vault-agent sh -c "ls -l /vault/agent/token"
```

Se o arquivo `token` existir, significa que o Vault Agent conseguiu autenticar corretamente no Vault.

---

### 9. Subir a aplicação Python

Acesse o diretório da aplicação Python:

```bash
cd python
```

Suba a aplicação:

```bash
docker compose -f docker-compose-python.yml up -d --build
```

Verifique se o container está em execução:

```bash
docker ps
```

Acesse a aplicação no navegador:

```text
http://localhost:3001
```

---

### 10. Testar a aplicação

Teste o endpoint de saúde da aplicação:

```bash
curl http://localhost:3001/health
```

Se a aplicação estiver funcionando corretamente, ela deverá retornar uma resposta de sucesso.

Também é possível testar se a aplicação consegue solicitar credenciais ao Vault:

```bash
docker exec -it simple-python-app sh -lc 'python - <<PY
import requests

tok = open("/vault/agent/token").read().strip()

r = requests.get(
    "https://vault:8200/v1/database/creds/app-db",
    headers={"X-Vault-Token": tok},
    verify="/vault/tls/ca.crt"
)

print(r.status_code)
print(r.text)
PY'
```

Se o retorno for `200`, significa que a aplicação conseguiu acessar o Vault e solicitar credenciais dinâmicas.

---

## Subindo o GitLab e executando a pipeline

Além do ambiente com Vault, PostgreSQL e aplicação Python, o laboratório também possui integração com GitLab CI/CD.

---

### 1. Subir o GitLab

Na raiz do projeto, execute:

```bash
docker compose -f docker-compose-gitlab.yml up -d
```

Aguarde o GitLab iniciar completamente.

Depois acesse no navegador:

```text
http://localhost:8081
```

---

### 2. Acessar o GitLab

No primeiro acesso, configure a senha do usuário administrador.

Usuário padrão:

```text
root
```

Depois, crie um novo projeto ou importe este repositório para dentro do GitLab local.

---

### 3. Registrar o GitLab Runner

O GitLab Runner é responsável por executar os jobs da pipeline.

A configuração do Runner fica no diretório:

```text
gitlab-runner/config/config.toml
```

Após registrar o Runner no GitLab, verifique se ele aparece como disponível no projeto.

---

### 4. Executar a pipeline

A pipeline utiliza os scripts presentes na pasta `scripts/`:

```text
scripts/
├── validate.sh
├── deploy-python.sh
└── test-python.sh
```

O fluxo esperado da pipeline é:

```text
validate → deploy → test
```

#### Etapa de validação

Verifica se os arquivos necessários existem e se a estrutura básica do projeto está correta.

#### Etapa de deploy

Realiza a implantação da aplicação Python usando Docker Compose.

#### Etapa de teste

Valida se a aplicação subiu corretamente após o deploy.



```bash
curl -i http://localhost:3001/health
```

Ou acessar pelo navegador:

```text
http://localhost:3001
```

---

## Resultado esperado

Ao final da execução, espera-se que:

* a aplicação não possua credenciais fixas do banco de dados;
* o Vault Agent consiga autenticar no Vault via AppRole;
* a aplicação consiga solicitar credenciais temporárias ao Vault;
* o Vault gere usuários dinâmicos no PostgreSQL;
* o acesso ao banco seja limitado por tempo de vida;
* as credenciais expirem automaticamente após o TTL configurado;
* a pipeline consiga validar, implantar e testar a aplicação;
* o processo de implantação ocorra sem exposição direta de senhas do banco.

Esse comportamento demonstra a aplicação prática de uma arquitetura segura para gerenciamento de segredos em aplicações web distribuídas.

---

## Relação com o TCC

Este repositório representa a implementação prática da prova de conceito apresentada no Trabalho de Conclusão de Curso.

A solução demonstra, de forma integrada, o uso do HashiCorp Vault para gerenciamento seguro de segredos em aplicações, considerando:

* armazenamento centralizado de segredos;
* geração dinâmica de credenciais;
* redução da exposição de senhas fixas;
* autenticação automatizada com Vault Agent;
* integração entre aplicação, Vault, Vault Agent e banco de dados;
* automação do processo de implantação com GitLab CI/CD;
* aplicação do princípio do menor privilégio;
* limitação do tempo de vida das credenciais.

Dessa forma, o laboratório contribui para demonstrar como práticas de segurança podem ser incorporadas ao ciclo de implantação de aplicações, reduzindo riscos associados ao uso de credenciais estáticas em ambientes distribuídos.

---

## Aviso de segurança

Este projeto foi desenvolvido exclusivamente para fins acadêmicos e de demonstração.

Não é recomendado utilizar os tokens, certificados, senhas ou configurações deste laboratório diretamente em ambientes de produção.

Em ambientes reais, recomenda-se:

* não versionar tokens, chaves privadas ou arquivos sensíveis;
* proteger `role_id`, `secret_id` e tokens do Vault Agent;
* restringir permissões de acesso aos arquivos sensíveis;
* utilizar certificados emitidos por uma autoridade confiável;
* habilitar auditoria no Vault;
* aplicar políticas de menor privilégio;
* limitar o tempo de vida das credenciais;
* proteger os dados persistentes do Vault;
* restringir o acesso administrativo ao GitLab e ao GitLab Runner.

---

## Licença

Este projeto está licenciado sob a licença MIT.

---

## Autora

Desenvolvido por **Sara Maria** como parte do Trabalho de Conclusão de Curso no Instituto Federal do Rio Grande do Norte.

Repositório: https://github.com/1Sayza/app-secrets-security
