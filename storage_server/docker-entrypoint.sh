#!/usr/bin/env bash

set -e

cd /application

sleep 5
echo "Register storage"
python3 -u register.py > register.log

echo "Run Flask"
python3 -u main.py > flask.log



