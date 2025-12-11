#!/usr/bin/env bash
# reset_dev_db.sh - Fresh Odoo Database Creation (CE/EE)
set -euo pipefail

[ -f .env ] || { echo "Error: .env file not found"; exit 1; }
[ -f .env.secrets ] || { echo "Error: .env.secrets file not found"; exit 1; }
source .env
source .env.secrets

./setup_edition.sh
DC="docker compose"

echo "Starting containers..."
$DC up -d --wait

DB_NAME="${DB_PREFIX}_$(date +%Y%m%d)"
echo "Creating fresh database: $DB_NAME"

# terminate/drop if exists
$DC exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid != pg_backend_pid();" >/dev/null || true
$DC exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 \
  -c "DROP DATABASE IF EXISTS \"${DB_NAME}\";" >/dev/null

# create
$DC exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 \
  -c "CREATE DATABASE \"${DB_NAME}\" ENCODING 'UTF8' TEMPLATE template0 LC_COLLATE='C' LC_CTYPE='C';" >/dev/null

echo "Database created successfully"

# module list
if [ "${ODOO_EDITION}" = "ee" ]; then
  INSTALL_MODULES="${MODULES_CE},${MODULES_EE}"
  echo "Installing modules for Enterprise Edition..."
else
  INSTALL_MODULES="${MODULES_CE}"
  echo "Installing modules for Community Edition..."
fi

DEMO_FLAG=""
if [ "${WITH_DEMO,,}" = "false" ]; then
  DEMO_FLAG="--without-demo=all"
fi

echo "Installing Odoo modules: $INSTALL_MODULES"
$DC exec -T odoo odoo -c /etc/odoo/odoo.conf -d "$DB_NAME" -i "$INSTALL_MODULES" $DEMO_FLAG --stop-after-init

echo "✅ Fresh Odoo 19 ${ODOO_EDITION^^} database ready!"
echo "  Edition: ${ODOO_EDITION^^}"
echo "  Database: $DB_NAME"
echo "  URL: http://localhost:${ODOO_HTTP_PORT}"
echo "  Note: Set admin password on first login"