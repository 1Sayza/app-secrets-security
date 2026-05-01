#!/bin/bash
set -e

echo "Realizando deploy da aplicação Python..."
docker compose -f python/docker-compose-python.yml up -d --build

echo "Containers em execução:"
docker ps

echo "Deploy concluído com sucesso."
