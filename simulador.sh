#!/bin/bash
#
# Llama a simulate.py para simular todos los ficheros de una carpeta
#
#

FOLDER="$1"
shift 1

if [ ! -d "${FOLDER}" ]; then
    echo "Uso:"
    echo "     ./simulador.sh <CARPETA_CON_PROBLEMAS> -i <Iteraciones> -p <Valor de percentil>"
    echo " (para más info de los parametros: python simulate.py -h)"
else
    # Simulate project files
    for file in "${FOLDER}/"*.ppc; do
        if [ -f "$file" ]; then
            echo "Simulando ${file}"
            python simulate.py $@ -t "${FOLDER}/00table.csv" "${file}" 
        fi
    done
fi

