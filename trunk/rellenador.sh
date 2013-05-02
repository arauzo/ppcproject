#!/bin/bash

FOLDER="$1"
shift 1
DEST="$@"
DEST="${DEST//-/_}" # Quitar -
DEST="${DEST// /}" # Quitar espacios 
DEST="${FOLDER}"/"${DEST}"

mkdir "${DEST}"

for file in "${FOLDER}/"*; do
    if [ -f "$file" ]; then
        base=${file##*/} # Get basename without extension
        base=${base%%.*}
        echo "Creando ${DEST}/${base}.ppc"
        python filler.py $@ "${file}" "${DEST}/${base}.ppc"
    fi
done


