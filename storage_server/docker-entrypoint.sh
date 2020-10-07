#!/usr/bin/env bash

set -ex

cd /application

sleep 5
echo "Register storage"

export PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
export PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
python3 -u register.py > register.log

echo "Start gunicorn"
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile=- main:app
