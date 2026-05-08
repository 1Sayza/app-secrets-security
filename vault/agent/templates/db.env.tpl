{{- with secret "database/creds/app-db" -}}
DB_USER={{ .Data.username }}
DB_PASS={{ .Data.password }}
{{- end -}}
