#!/bin/bash

#The following script is in charge of sequentially performing the group of tests that we need to
#carry out our project.

#It receives 4 parameters:
#        1. Type of distribution for the simulation of the activities
#        2. Proporcionality constant of the typical deviation
#        3. Number of iterations to be performed to simulate the duracion of the project
#        4. Mark percentage for the calculation of critical paths
#
#    For each file with extension .sm placed in the current directory, it will operate as follows:
#
#       1. It will upload a file from the PSPLIB libraries.
#        2. It will fill it out with the values required to perform the simulation.
#        3. It will generate a .ppc file filled with the preious data, and two .csv: one with the data resulting
#           from simulate the activities and another one with the data resulting from simulate the duration of the project.
#        4. It will generate an output table with the data required to carry out our study.
#
#    The files will be saved within the same directories the .sm files were located,
#    except for the output table, that will be generated in the current directory.
#


a=relleno
b=listaSimulacion
c=tablaSalidas
f=.ppc
g=.csv
h=simact


for file in `find * -name "*.sm"`;
do
echo -n .
python /home/felipe/ppcproject/filler.py "$file" "${file%%.*}$a" -d $1 -k $2
echo -n .
python /home/felipe/ppcproject/simulation_list.py "${file%%.*}$a$f" "${file%%.*}$b" "${file%%.*}$h" -i $3
echo -n .
python /home/felipe/ppcproject/simulation_test_ks.py "${file%%.*}$a$f" "${file%%.*}$b$g" "${file%%.*}$h$g" TablaSalidas.csv -p $4
echo -n .
done
echo .
