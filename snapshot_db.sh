#!/usr/bin/env bash
# snapshot_db.sh - Database Backup and Restore Management
set -euo pipefail

source .env
source .env.secrets

DC="docker compose"
SNAPDIR=./snapshots
mkdir -p "$SNAPDIR"

DB_NAME="${DB_PREFIX}_$(date +%Y%m%d)"

show_help() {
  cat <<EOF
Database Snapshot Management Tool

Usage: $0 [command] [name]

Commands:
  dump [name]     Create snapshot (default: LATEST)
  restore [name]  Restore snapshot (default: LATEST)
  list            List available snapshots

Examples:
  $0 dump                 # Create LATEST.dump
  $0 dump golden          # Create named snapshot
  $0 restore LATEST       # Restore from LATEST.dump
EOF
}

dump_database() {
  local snapshot_name="${1:-LATEST}"
  local output_file="$SNAPDIR/${snapshot_name}.dump"
  echo "Creating snapshot: $DB_NAME -> $output_file"
  $DC exec -T db pg_dump -U "$POSTGRES_USER" -Fc --compress=9 --no-owner --no-privileges "$DB_NAME" > "$output_file"
  local file_size=$(du -h "$output_file" | cut -f1)
  echo "✅ Snapshot created: $output_file ($file_size)"
}

restore_database() {
  local snapshot_name="${1:-LATEST}"
  local input_file="$SNAPDIR/${snapshot_name}.dump"
  [ -f "$input_file" ] || { echo "Error: Snapshot not found: $input_file"; exit 1; }
  local new_db="${DB_PREFIX}_$(date +%Y%m%d_%H%M)"
  echo "Restoring snapshot to: $new_db"
  $DC exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "DROP DATABASE IF EXISTS \"${new_db}\";" >/dev/null
  $DC exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE DATABASE \"${new_db}\" ENCODING 'UTF8' TEMPLATE template0;" >/dev/null
  cat "$input_file" | $DC exec -T db pg_restore -U "$POSTGRES_USER" -d "$new_db" --no-owner --no-privileges
  echo "✅ Database restored: $new_db"
  echo "  Access: http://localhost:${ODOO_HTTP_PORT}"
}

list_snapshots() {
  echo "Available Snapshots:"
  echo "======================================"
  if [ ! -d "$SNAPDIR" ] || [ -z "$(ls -A $SNAPDIR/*.dump 2>/dev/null)" ]; then
    echo "No snapshots found in $SNAPDIR"
    return
  fi
  for dump_file in "$SNAPDIR"/*.dump; do
    local basename=$(basename "$dump_file" .dump)
    local size=$(du -h "$dump_file" | cut -f1)
    echo "  $basename ($size)"
  done
}

case "${1:-help}" in
  dump)    dump_database "${2:-}" ;;
  restore) restore_database "${2:-}" ;;
  list)    list_snapshots ;;
  help|-h|--help) show_help ;;
  *) echo "Unknown command: ${1:-help}"; show_help; exit 1;;
esac