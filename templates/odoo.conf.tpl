[options]
admin_passwd = {{ADMIN_PASS}}

# Database
db_host = {{POSTGRES_HOST}}
db_port = 5432
db_user = {{POSTGRES_USER}}
db_password = {{PASSWORD}}

# Addons
addons_path = {{ADDONS_PATH}}

# Logging & runtime
log_level = {{LOG_LEVEL}}
logfile = /var/log/odoo/odoo.log
proxy_mode = {{PROXY_MODE}}
limit_time_cpu = 0
limit_time_real = 0
limit_time_real_cron = 0
workers = {{WORKERS}}
list_db = True
# admin_passwd_insecure = True