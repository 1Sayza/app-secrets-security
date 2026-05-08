# Vault Lab (Vault → Postgres → Role dinâmico → Agent → App)

<img width="1491" height="1055" alt="vault-hashicorp" src="https://github.com/user-attachments/assets/3df69aac-8e1f-4883-b3a0-e4f904bcff81" />


# Vault Lab - Gerenciamento Seguro de Secrets com CI/CD Local

Este projeto apresenta um laboratório local voltado à implementação de uma arquitetura segura para gerenciamento de secrets em aplicações, utilizando credenciais temporárias, autenticação centralizada e integração com pipeline de CI/CD local.

O ambiente foi construído com foco em estudos práticos sobre proteção de credenciais, acesso seguro ao banco de dados e automação de deploy de aplicações, simulando um cenário de laboratório DevSecOps.

---

## Objetivo

O objetivo deste laboratório é demonstrar, de forma prática, como uma aplicação pode acessar um banco de dados sem armazenar credenciais fixas no código-fonte, utilizando um mecanismo de autenticação, geração dinâmica de credenciais e integração com pipeline local de CI/CD.

Além disso, o projeto busca mostrar como separar corretamente:

- a aplicação
- a infraestrutura de secrets
- o banco de dados
- o fluxo de build e deploy

---

## Arquitetura do laboratório

O laboratório é composto por quatro blocos principais:

### 1. Aplicação Web
Aplicação responsável por consumir credenciais temporárias e realizar operações no banco de dados.

### 2. Gerenciador de Secrets
Responsável por controlar autenticação, políticas de acesso e geração de credenciais temporárias.

### 3. Banco de Dados
Responsável por armazenar os dados da aplicação e aceitar conexões autorizadas com permissões limitadas.

### 4. Pipeline de CI/CD local
Responsável por validar, buildar, publicar e testar a aplicação, sem acoplar o gerenciamento de secrets à etapa de build.

---

## Estrutura do projeto

```text

vault-lab/
.
├── LICENSE
├── README.md
├── app
│   ├── Dockerfile
│   ├── index.html
│   ├── index.js
│   └── package.json
├── db
│   └── init.sql
├── docker-compose-gitlab.yml
├── docker-compose-postgres.yml
├── docker-compose-vault-agent.yml
├── docker-compose-vault.yml
├── gitlab-runner
│   └── config
│       └── config.toml
├── python
│   ├── Dockerfile
│   ├── app.py
│   ├── docker-compose-python.yml
│   └── requirements.txt
├── scripts
│   ├── deploy-python.sh
│   ├── test-python.sh
│   └── validate.sh
└── vault
    ├── agent
    │   ├── role_id
    │   ├── secret_id
    │   ├── templates
    │   │   └── db.env.tpl
    │   └── token
    ├── config
    │   ├── vault
    │   │   └── agent
    │   │       ├── secret_id
    │   │       └── templates
    │   │           └── db.env.tpl
    │   ├── vault-agent.hcl
    │   └── vault.hcl
    ├── data [error opening dir]
    ├── tls
    │   ├── ca.crt
    │   ├── ca.key
    │   ├── ca.srl
    │   ├── vault.crt
    │   ├── vault.csr
    │   ├── vault.ext
    │   └── vault.key
    └── vault
        ├── config
        ├── data
        └── tls

```

Componentes do projeto
app/

Contém uma aplicação web em Node.js usada no laboratório.

python/

Contém a aplicação Python, seu Dockerfile, dependências e o docker-compose próprio para deploy da aplicação.

db/

Contém o script de inicialização do banco de dados.

vault/

Contém arquivos de configuração, diretórios de dados, certificados TLS, arquivos do agente e templates de secrets.

scripts/

Contém scripts auxiliares utilizados no pipeline de CI/CD local, como validação, deploy e testes da aplicação Python.

docker-compose-*.yml


## Arquivos separados para orquestração dos serviços do laboratório:

GitLab local
banco de dados
gerenciador de secrets
agente de autenticação
aplicação Python

Tecnologias utilizadas
Docker
Docker Compose
Linux Ubuntu
GitLab CE local
GitLab Runner
Python
PostgreSQL
Gerenciamento seguro de secrets
Bash Script


## Fluxo do laboratório

O funcionamento do laboratório segue, de forma resumida, a seguinte lógica:

A aplicação solicita acesso ao banco de dados.
O mecanismo de autenticação valida a identidade da aplicação.
A solicitação autenticada é encaminhada ao gerenciador de secrets.
A política de acesso é validada.
São geradas credenciais temporárias para acesso ao banco.
O banco cria um usuário temporário com permissões limitadas.
As credenciais são retornadas à aplicação.
A aplicação utiliza essas credenciais para acessar somente os recursos autorizados.
Após o tempo de validade, o acesso temporário pode ser revogado.

## CI/CD local

Neste laboratório, o CI/CD foi projetado para atuar apenas sobre a aplicação, mantendo o banco de dados, o mecanismo de autenticação e o gerenciador de secrets fora da pipeline principal.

A pipeline executa:
validação da configuração da aplicação
build da imagem da aplicação Python
deploy da aplicação
teste da aplicação após o deploy
Infraestrutura mantida fora da pipeline:
banco de dados
gerenciador de secrets
agente de autenticação

Essa separação permite um fluxo mais próximo de ambientes reais, onde a infraestrutura crítica permanece desacoplada da esteira de build da aplicação.

## Scripts do pipeline

scripts/validate.sh

Valida a sintaxe e a estrutura do docker-compose da aplicação Python.

scripts/deploy-python.sh

Executa o deploy da aplicação Python utilizando Docker Compose.

scripts/test-python.sh

Executa testes básicos de disponibilidade da aplicação após o deploy.

## Como executar o laboratório
1. Subir a infraestrutura principal

Suba separadamente os serviços de infraestrutura:

```

docker compose -f docker-compose-vault.yml up -d
docker compose -f docker-compose-vault-agent.yml up -d
docker compose -f docker-compose-postgres.yml up -d

``` 

2. Subir o GitLab local

```
docker compose -f docker-compose-gitlab.yml up -d
```

3. Subir a aplicação Python

```
docker compose -f python/docker-compose-python.yml up -d --build
```
4. Verificar containers em execução
   
```
docker ps
```
## GitLab local

O laboratório também utiliza um GitLab local executando em container para testes de pipeline.

Portas utilizadas
8081: acesso web ao GitLab
8443: acesso HTTPS
2222: acesso SSH


Exemplo de uso do pipeline

Após configurar o GitLab Runner e enviar o projeto ao repositório, a pipeline pode executar automaticamente:

validação do compose da aplicação
build da imagem
deploy atualizado da aplicação Python
teste de disponibilidade da aplicação

Boas práticas adotadas
separação entre aplicação e infraestrutura crítica
não utilização de credenciais fixas diretamente no código
uso de credenciais temporárias
controle de acesso por política
organização modular por serviço
automação local para simular pipeline real

Observações importantes

Este projeto foi desenvolvido com fins educacionais, laboratoriais e de estudo em segurança de aplicações, DevSecOps e gerenciamento seguro de credenciais.

Por se tratar de um ambiente local, algumas configurações podem estar simplificadas em relação a um cenário de produção, especialmente em aspectos como:

hardening do ambiente
rotação avançada de certificados
alta disponibilidade
monitoramento
segregação avançada de rede

Possíveis evoluções do projeto
adicionar testes automatizados mais completos
expandir a pipeline para múltiplos ambientes
integrar análise de segurança no CI/CD
adicionar monitoramento e observabilidade
implementar políticas mais refinadas de acesso
evoluir o fluxo de revogação automática de credenciais


## Autor

Sara Maria
Profissional focada em Segurança da Informação, DevSecOps e proteção de aplicações.




