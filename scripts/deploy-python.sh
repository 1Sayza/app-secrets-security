#!/bin/sh
set -e

echo "Realizando deploy da aplicação Python..."

docker compose -f python/docker-compose-python.yml config >/dev/null
docker compose -f python/docker-compose-python.yml up -d --build

echo "Deploy da aplicação Python executado com sucesso."
