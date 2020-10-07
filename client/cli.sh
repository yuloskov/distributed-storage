#!/bin/bash

function help() {
  python3 /application/client.py --help
}

function init() {
  python3 /application/client.py init $@
  if [ $? == 0 ]; then
    DIR="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
    cd "$DIR"
    echo "PS1='"'${PWD#'"$DIR""}/ \$ '" >> /root/.bash_profile
    source /root/.bash_profile
  fi
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

# init dfs --force
