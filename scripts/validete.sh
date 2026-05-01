#!/bin/bash
set -e

docker compose -f python/docker-compose-python.yml config >/dev/null

echo "Arquivo docker-compose da aplicação Python validado com sucesso."
