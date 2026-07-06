#!/bin/sh
set -e
if [ -f /dumps/latest.sql.gz ]; then
  echo "[svinopass] Restoring database from /dumps/latest.sql.gz"
  gunzip -c /dumps/latest.sql.gz | psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
elif [ -f /dumps/latest.sql ]; then
  echo "[svinopass] Restoring database from /dumps/latest.sql"
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /dumps/latest.sql
else
  echo "[svinopass] No dump found, starting with empty database"
fi