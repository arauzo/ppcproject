#!/bin/bash


for f in ../../examples/*/*.sm; do
#for f in ../../examples/Elmaghraby/e101.sm; do ejecutar un archivo para pruebas
    echo "procesando $f"
    python ../../prueba.py $f 1 >> pruebas_Sha.txt
done

for f in ../../examples/Kolisch/*/*.sm; do
    echo "procesando $f"
    python ../../prueba.py $f 1 >> pruebas_Sha_CohSad.txt
done
