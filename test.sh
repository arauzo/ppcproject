#!/bin/bash


for f in ../../examples/*/*.sm; do
#for f in ../../examples/Elmaghraby/e101.sm; do #ejecutar un archivo para pruebas
    echo "procesando $f"
    python ../../prueba.py -cgs $f >> pruebas_algoritmos_todos.txt
done

for f in ../../examples/Kolisch/*/*.sm; do
    echo "procesando $f"
    python ../../prueba.py -cgs $f >> pruebas_algoritmos_todos.txt
done
