#!/bin/bash
file=e802.sm
a=relleno
b=listaSimulacion
c=tabla

python filler.py e802.sm e802relleno -d 'Beta' -k 0.2
python simulation_list.py e802relleno.ppc e802lista -i 1000
python simulation_test_ks.py e802relleno.ppc e802lista.csv TablaSalidas.csv -a 0.05 

