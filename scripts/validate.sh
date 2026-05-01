#!/bin/sh
set -e

echo "Validando arquivos docker-compose do projeto..."

docker compose -f docker-compose-postgres.yml config >/dev/null
docker compose -f docker-compose-vault.yml config >/dev/null
docker compose -f docker-compose-vault-agent.yml config >/dev/null

echo "Arquivos docker-compose principais validados com sucesso."
