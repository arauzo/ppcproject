#!/bin/bash


for f in ../../examples/*/*.sm; do 
    echo "procesando $f"
    python ../../prueba.py $f 1; >pruebas_Sha.txt 
done 
