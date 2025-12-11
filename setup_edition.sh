#!/usr/bin/env bash
# setup_edition.sh - Configure Odoo edition (CE/EE) - validation only
set -euo pipefail

source .env

echo "Setting up Odoo ${ODOO_VERSION} for ${ODOO_EDITION^^} edition..."

if [ "$ODOO_EDITION" = "ee" ]; then
  if [ ! -d "odoo_enterprise" ]; then
    echo "❌ Error: Enterprise edition selected but odoo_enterprise/ directory not found"
    echo "   - Clone enterprise source, or set ODOO_EDITION=ce in .env"
    exit 1
  fi
  echo "✅ EE detected and odoo_enterprise/ present. (addons_path will include it at runtime)"
else
  echo "✅ CE mode."
fi