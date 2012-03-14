#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Functions for simulation of project duration
# -----------------------------------------------------------------------
# PPC-PROJECT
#   Multiplatform software tool for education and research in
#   project management
#
# Copyright 2007-9 Universidad de Córdoba
# This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published
#   by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import fileFormats
import simulation_test_ks
import pert
import zaderenko
import graph
import simulation


def load (filename):
    """
    Function in charge of uploading ppcproject-compatible files; that is to say .ppc files & .sm files

    filename (name of the file to be uploaded)

    return: data (file info)
    """

    formatos = [fileFormats.PPCProjectFileFormat(),fileFormats.PSPProjectFileFormat()]
    #print filename
    try:
        # Tries to load file with formats that match its extension in format order
        data = None
        extension = filename[filename.rfind('.')+1:]

        for format in formatos:
            if extension in format.filenameExtensions:
                try:
                    data = format.load(filename)
                    break
                except fileFormats.InvalidFileFormatException:
                    pass

        # If load by extension failed, try to load files in any format independently of their extension
        if not data:
            for format in fileFormats:
                try:
                    data = format.load(filename)
                    break
                except fileFormats.InvalidFileFormatException:
                    pass
        
        #Data successfully loaded
        if data:
            actividad, schedules, recurso, asignacion = data
            return actividad, schedules, recurso, asignacion
        else:
            raise Exception('ERROR: Formato del archivo origen no reconocido')

    except IOError:
        print 'ERROR: Formato del archivo origen no reconocido', '\n'
        
def save (resultados, filename):
    """
    Function that saves the results of the simulation in csv format

    resultados (values resulting from the simulation)
    filename (name of the file in which the values will be saved) 
    """
    
    # Comprobamos que el nombre del archivo termine en csv, de lo contrario le daremos esta extension.
    if filename[-4:] == '.csv':
        f = open(filename, 'w')
    else:
        f = open(filename + '.csv', 'w')

    # Se inicializa una cadena
    simulation_csv = ' '

    # Se rellena la cadena con los resultados de la simulacion
    for n in range(len(resultados)):
        simulation_csv += str(resultados[n])
        simulation_csv += '\n'

    # Se escribe en el fichero el resultado y se cierra.
    f.write(simulation_csv)
    f.close()

def saveSimulation (simulation, filename):    
    """
    Function that saves the results of the simulation of activities in csv format

    simulation (values resulting from the simulation of activities)
    filename (name of the file in which the values will be saved) 
    """
    
    # Comprobamos que el nombre del archivo termine en csv, de lo contrario le daremos esta extension.
    if filename[-4:] == '.csv':
        f = open(filename, 'w')
    else:
        f = open(filename + '.csv', 'w')

    # Se inicializa una cadena
    simulation_csv = ' '

    # Se rellena la cadena con los resultados de la simulacion
    for n in range(len(simulation)):
        simulation_csv += str(simulation[n])
        simulation_csv += '\n'

    # Se escribe en el fichero el resultado y se cierra.
    f.write(simulation_csv)
    f.close()
   
def vectorDuraciones(it,actividad):
    """
    Function performing the simulation of the project durations.

    it (number of iterations to be performed)
    actividad (vector with activities of the project and their durations)

    return: duraciones (vector with all durations resulting from the simulation)
    """
    
    # Se simulan las duraciones de las actividades y se genera el grafo del proyecto.    
    simulaciones = simulation.simulacion(it, actividad)
    grafoRenumerado = pert.pertFinal(actividad)
    nodosN=[]

    for n in range(len(grafoRenumerado.successors)):
        nodosN.append(n+1)

    # Realizamos la simulacion de la duracion del proyecto aplicando la matriz de Zaderenko.
    duraciones = []
    if simulaciones == None:
            return
    else:
        for s in simulaciones: 
            matrizZad = zaderenko.mZad(actividad,grafoRenumerado.arcs, nodosN, 0, s)
            tearly = zaderenko.early(nodosN, matrizZad)
            tlast = zaderenko.last(nodosN, tearly, matrizZad)
            tam = len(tearly)
            duracionProyecto = tearly[tam-1]
            duraciones.append(duracionProyecto)
            
            
    
    
    return duraciones, simulaciones
   

def main():
    """
    The following program of simulation batch is in charge of uploading a .ppc format file and generating two files 
    from the first one. On the one hand, it generates a file with the result of simulating n times, on the other hand,
    it generates a file resulting from simulating the duration of the activities n times.

    The program shall receive the following parameters for each console:
        infile (name of the file from which data will be uploaded)
        outfile (name of the file in which the resulting list with the n simulations of the duration of the project will be saved)
        outfile2 (name of the file in charge of saving the n simulations of the durations of the activities,
                  the distribution to generate them will be that uploaded from outfile)
        -i (number of iterations to be performed)
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser(description = 'Generates activities and project simulations')
    parser.add_argument('infile', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('outfile', default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('outfile2', default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('-i', default=1000,type=int,
                        help='Number of iterations (default: 1000)')

    args = parser.parse_args()

    # We upload the project of the ppcproject
    act, schedules, recurso, asignacion = load(args.infile)

    # We generate the vector of results
    if (args.i < 1):
        raise Exception ('At least one simulation must be done & the number of iterations can not be negative')
    else:
        resultados, simulaciones = vectorDuraciones (args.i, act) #projectSimulation (args.i,act)
    
        # We save a vector with the simulated duration of each activity in each iteration
        saveSimulation(simulaciones, args.outfile2)

        # We save it in csv format
        save(resultados, args.outfile)  

    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

