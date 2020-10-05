#!/usr/bin/env bash

set -ex

cd /application

sleep 5
echo "Register storage"
python3 -u register.py > register.log

echo "Start gunicorn"
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile=- main:app
