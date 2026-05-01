#!/bin/sh
set -e

echo "Realizando deploy da aplicação Python..."

mkdir -p vault/agent

if [ ! -f vault/agent/db.env ]; then
  echo "Criando db.env temporário para execução no CI..."
  cat > vault/agent/db.env <<EOF
DB_USER=ci_user
DB_PASS=ci_password
DB_HOST=postgres
DB_NAME=sara_db
DB_PORT=5432
EOF
fi

docker compose -f python/docker-compose-python.yml config >/dev/null

echo "Deploy da aplicação Python validado com sucesso."
