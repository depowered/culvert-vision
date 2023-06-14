#!/bin/bash

dump_file=$1

if [ $# -ne 1 ]; then
    echo usage: ./load_from_pgsql.sh dump_file
    exit 1
fi

PGPASSWORD=$POSTGRES_PASS psql \
    --username $POSTGRES_USER \
    --host $POSTGRES_HOST \
    --port $POSTGRES_PORT \
    --file=$dump_file \
    $POSTGRES_DB
