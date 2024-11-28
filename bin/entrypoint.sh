#!/usr/bin/env bash
#bash
cd /app; python3 manage.py migrate;  python3 manage.py runserver 0.0.0.0:8080
#cd /app/; gunicorn  --workers=8 --threads=4 -b 0.0.0.0:8080 config.wsgi
