#!/bin/bash

function init() {
  python3 /application/client.py init $@
  DIR="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
  cd "$DIR"
  echo "PS1='"'${PWD#'"$DIR""}/ \$ '" >> /root/.bash_profile
  source /root/.bash_profile
}

function ls() {
  python3 /application/client.py ls $@
}

function push() {
  python3 /application/client.py push $@
}

function pull() {
  python3 /application/client.py pull $@
}

function import() {
  python3 /application/client.py import $@
}

function export() {
  python3 /application/client.py export $@
}
