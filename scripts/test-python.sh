#!/bin/sh
set -e

echo "Aguardando a aplicação iniciar..."
sleep 10

echo "Testando aplicação Python..."

curl -f http://simple-python-app:3000

echo "Aplicação Python respondeu com sucesso."
