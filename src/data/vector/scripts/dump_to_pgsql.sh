#!/bin/bash

dump_file=$1
source_file=$2
layer=$3
to_table=$4

if [ $# -ne 4 ]; then
    echo usage: ./dump_to_pgsql.sh dump_file source_file layer to_table
    exit 1
fi

ogr2ogr --config PG_USE_COPY YES -f PGDump $dump_file $source_file \
    -sql "SELECT * FROM $layer" \
    -nln $to_table \
    -nlt PROMOTE_TO_MULTI \
    -lco GEOMETRY_NAME=geom \
    -lco DIM=2 \
    -lco SCHEMA=raw \
    -lco CREATE_SCHEMA=ON \
    -lco DROP_TABLE=IF_EXISTS \
    -lco SPATIAL_INDEX=GIST