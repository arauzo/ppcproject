#!/bin/bash
#file=e802.sm
a=relleno
b=listaSimulacion
c=tablaSalidas
f=.ppc
g=.csv

#cd Elmaghraby2
for file in `find * -name "*.sm"`;
do
echo -n .
python /home/felipe/ppcproject/filler.py "$file" "${file%%.*}$a" -d $1 -k $2
echo -n .
python /home/felipe/ppcproject/simulation_list.py "${file%%.*}$a$f" "${file%%.*}$b" -i $3
echo -n .
python /home/felipe/ppcproject/simulation_test_ks.py "${file%%.*}$a$f" "${file%%.*}$b$g" Tablasalidas2.csv -a 0.05
echo -n .
done
echo .
