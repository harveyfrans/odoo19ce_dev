# Redirect HTTP to HTTPS
server {
  listen 80;
  server_name {{SERVER_NAME}};
  return 301 https://$host$request_uri;
}

# HTTPS server
server {
  listen 443 ssl http2;
  server_name {{SERVER_NAME}};

  ssl_certificate     {{TLS_CERT}};
  ssl_certificate_key {{TLS_KEY}};

  client_max_body_size {{CLIENT_MAX_BODY_SIZE}};

  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

  location /longpolling/ {
    proxy_pass http://odoo:8072/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout {{NGINX_PROXY_READ_TIMEOUT}};
    proxy_buffering off;
  }

  location / {
    proxy_pass http://odoo:8069/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout {{NGINX_PROXY_READ_TIMEOUT}};
  }
}