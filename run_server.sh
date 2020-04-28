#! /bin/sh
source .env/bin/activate
[ -z "$HOST" ] && HOST="127.0.0.1:8000"
gunicorn guineapigs:app -b "$HOST"
