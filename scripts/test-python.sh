#!/bin/sh
set -e

echo "Aguardando a aplicação iniciar..."
sleep 10

echo "Testando aplicação Python..."
curl -f http://localhost:3001 || exit 1

echo "Teste concluído com sucesso."
