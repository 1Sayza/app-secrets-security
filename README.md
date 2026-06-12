# Vault Lab (Vault → Postgres → Role dinâmico → Agent → App)

<img width="1491" height="1055" alt="vault-hashicorp" src="https://github.com/user-attachments/assets/3df69aac-8e1f-4883-b3a0-e4f904bcff81" />


# Vault Lab - Gerenciamento Seguro de Secrets com CI/CD Local

Este projeto apresenta um laboratório local voltado à implementação de uma arquitetura segura para gerenciamento de secrets em aplicações, utilizando credenciais temporárias, autenticação centralizada e integração com pipeline de CI/CD local.

O ambiente foi construído com foco em estudos práticos sobre proteção de credenciais, acesso seguro ao banco de dados e automação de deploy de aplicações, simulando um cenário de laboratório DevSecOps.

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


## RESUMO DA PREPARAÇÃO DO AMBIENTE

A estrutura do projeto foi organizada no diretório vault-lab, contendo os arquivos de composição dos serviços, a aplicação Python, os scripts de automação do pipeline, as configurações do Vault, os dados utilizados pelo Vault Agent e os arquivos do GitLab Runner. Entre os principais componentes do projeto estão os arquivos docker-compose-postgres.yml, docker-compose-vault.yml, docker-compose-vault-agent.yml e docker-compose-gitlab.yml, além dos diretórios python, scripts, vault e gitlab-runner. Essa organização permitiu separar as responsabilidades de cada serviço e facilitar a reprodução do ambiente.

Inicialmente, foi criada uma rede Docker compartilhada para os contêineres do laboratório. Essa rede permite que a aplicação, o Vault, o Vault Agent, o PostgreSQL, o GitLab e o GitLab Runner se comuniquem internamente por nome de serviço, reduzindo a necessidade de exposição direta entre componentes. A rede utilizada no ambiente foi denominada vaultlab-net, sendo referenciada tanto no Docker Compose da aplicação Python quanto na configuração do GitLab Runner.

Em seguida, foi iniciado o banco de dados PostgreSQL por meio do arquivo docker-compose-postgres.yml. Esse serviço é responsável por hospedar a base sara-db, utilizada pela aplicação para realizar consultas e autenticação de usuários. Durante a inicialização do banco, o ambiente utiliza um script de bootstrap localizado no diretório db, responsável por preparar as estruturas necessárias para o funcionamento da aplicação.

Após a subida do banco de dados, foi iniciado o HashiCorp Vault utilizando o arquivo docker-compose-vault.yml. O Vault foi configurado com armazenamento local e comunicação via TLS, utilizando certificados presentes no diretório vault/tls. Os arquivos principais de configuração ficam no diretório vault/config, onde estão localizados os arquivos vault.hcl e vault-agent.hcl.

Com o Vault em execução, foram configurados os mecanismos de segurança necessários para o laboratório. O Database Secrets Engine foi habilitado para permitir a geração dinâmica de credenciais de acesso ao PostgreSQL. Nesse processo, foram criadas roles de banco responsáveis por emitir usuários temporários com permissões restritas, tempo de vida controlado e revogação após o término do TTL.

Além disso, foi configurado o método de autenticação AppRole, utilizado pelo Vault Agent para autenticar a aplicação no Vault. No ambiente, a role de autenticação foi associada à política app-policy e configurada com token periódico de 10 minutos. Esse token é renovável e permite que a aplicação solicite credenciais dinâmicas ao Vault sem armazenar credenciais administrativas no código-fonte.

Depois da configuração do Vault, foi iniciado o Vault Agent por meio do arquivo docker-compose-vault-agent.yml. O Vault Agent utiliza os arquivos role-id e secret-id, armazenados no diretório vault/agent, para autenticação via AppRole. Como resultado, o agente gera um token renovável e o disponibiliza no caminho /vault/agent/token. Na estrutura atual, o diretório vault/agent contém os arquivos role-id, secret-id, templates e token, não sendo mais utilizado o arquivo db.env para expor usuário e senha do banco.

A aplicação Python foi desenvolvida no diretório python, contendo os arquivos Dockerfile, app.py, docker-compose-python.yml e requirements.txt. A aplicação utiliza Flask para disponibilizar as rotas web, requests para comunicação com a API do Vault, psycopg2 para conexão com o PostgreSQL e bcrypt para validação de senhas armazenadas em formato de hash. Essas dependências foram declaradas no arquivo requirements.txt.

Na versão aprimorada do laboratório, a aplicação deixou de utilizar o arquivo db.env. O arquivo docker-compose-python.yml passou a declarar apenas variáveis não sensíveis, como o endereço do Vault, o caminho do token, o caminho da role de credenciais dinâmicas, o certificado da CA e os dados básicos de conexão com o banco. Entre as variáveis utilizadas estão VAULT-ADDR, VAULT-TOKEN-PATH, VAULT-DB-CREDS-PATH, REQUESTS-A-BUNDLE, PGHOST, PGDATABASE e PGPORT.

O arquivo docker-compose-python.yml também é responsável por montar, no contêiner da aplicação, o certificado da autoridade certificadora do Vault e o token disponibilizado pelo Vault Agent, ambos em modo somente leitura. Essa configuração permite que a aplicação estabeleça uma comunicação HTTPS confiável com o Vault e utilize o token de autenticação sem armazenar credenciais sensíveis em arquivos locais.

Durante a execução, a aplicação lê o token disponível em /vault/agent/token e realiza uma chamada HTTP ao endpoint database/creds/app-db do Vault. Como resposta, são obtidos um usuário e uma senha temporários, empregados exclusivamente em memória para o estabelecimento da conexão com o PostgreSQL. Esse comportamento foi implementado no arquivo app.py, por meio das funções responsáveis pela leitura do token, pela solicitação das credenciais dinâmicas e pela abertura da conexão com o banco de dados.

Embora o serviço do Vault possua seus próprios volumes para configuração, certificados e persistência de dados, a aplicação Python precisa declarar montagens específicas em seu próprio arquivo Docker Compose, uma vez que os volumes não são compartilhados automaticamente entre contêineres. Nesse contexto, o certificado da CA é montado para permitir a validação da conexão HTTPS com o Vault, enquanto o token gerado pelo Vault Agent é disponibilizado à aplicação em modo somente leitura, impedindo sua modificação. Dessa forma, a aplicação consegue autenticar suas requisições ao Vault e solicitar credenciais dinâmicas para acesso ao banco de dados, preservando o isolamento entre os serviços e reduzindo a exposição de segredos persistentes no ambiente da aplicação.

O fluxo de funcionamento da aplicação ocorre da seguinte forma: inicialmente, a aplicação recebe uma requisição do usuário; em seguida, lê o token renovável gerado pelo Vault Agent; posteriormente, consulta o Vault para solicitar credenciais temporárias; na sequência, utiliza essas credenciais em memória para estabelecer a conexão com o PostgreSQL; por fim, executa a consulta necessária e encerra a conexão com o banco. Com isso, DB-USER e DB-PASS deixam de ser armazenados em arquivos, não são declarados diretamente no Docker Compose como segredos e não permanecem persistidos no ambiente da aplicação.

Além da integração com o Vault, o laboratório também foi ampliado com a implantação de um GitLab local e de um GitLab Runner, com o objetivo de representar o processo de integração e entrega contínua da aplicação. O GitLab é iniciado por meio do arquivo docker-compose-gitlab.yml, enquanto o Runner utiliza o diretório gitlab-runner/config, no qual se encontra o arquivo config.toml. O Runner foi configurado com executor Docker, imagem docker:24, modo privilegiado, acesso ao Docker socket e conexão com a rede vaultlab-net, permitindo que os jobs executem comandos Docker e acessem os serviços internos do laboratório.

O pipeline da aplicação utiliza scripts armazenados no diretório scripts. Foram criados três scripts principais: validate.sh, deploy-python.sh e test-python.sh. O script validate.sh é responsável por validar os arquivos Docker Compose principais do projeto. O script deploy-python.sh realiza o deploy da aplicação Python, executando a validação da configuração e iniciando o contêiner com processo de build. Por sua vez, o script test-python.sh aguarda a inicialização da aplicação e realiza um teste HTTP para verificar se o serviço respondeu corretamente.

Essa automação permite que o GitLab CI/CD valide a estrutura do ambiente, construa a aplicação, realize o deploy e execute testes básicos de disponibilidade. Dessa forma, o laboratório passa a representar não apenas o uso seguro de credenciais dinâmicas, mas também a integração dessas práticas a um fluxo DevSecOps, aproximando o experimento de um cenário real de desenvolvimento e entrega contínua de aplicações.


## Autor

Sara Maria
Profissional focada em Segurança da Informação, DevSecOps e proteção de aplicações.




