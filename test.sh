#!/bin/bash

for f in ../../examples/*/*.sm; do
    echo "procesando $f"
    python ../../prueba.py -cgs $f >> pruebas_algoritmos_todos.txt
done

for f in ../../examples/Kolisch/*/*.sm; do
    echo "procesando $f"
    python ../../prueba.py -cgs $f >> pruebas_algoritmos_todos.txt
done
