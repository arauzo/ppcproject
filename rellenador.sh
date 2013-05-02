#!/bin/bash
#
# Llama a filler para rellenar todos los ficheros de una carpeta
#
#

FOLDER="$1"
shift 1

if [ ! -d "${FOLDER}" ]; then
    echo "Uso:"
    echo "     ./rellenador.sh <CARPETA_CON_PROBLEMAS> -d <Distribucion> -k <Valor de k>"
    echo " (para más info de los parametros: python filler.py -h)"
else
    # Destination directory is created
    DEST="$@"
    DEST="${DEST//-/_}" # Remove '-'
    DEST="${DEST// /}"  # Remove spaces 
    DEST="${FOLDER}"/"${DEST}"
    mkdir "${DEST}"

    # Create filled project files
    for file in "${FOLDER}/"*; do
        if [ -f "$file" ]; then
            base=${file##*/} # Get basename without extension
            base=${base%%.*}
            echo "Creando ${DEST}/${base}.ppc"
            python filler.py $@ "${file}" "${DEST}/${base}.ppc"
        fi
    done
fi

