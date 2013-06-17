#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Program to simulate and test distributions
"""
import operator
import math
import os.path

import numpy

import graph
import kolmogorov_smirnov
import fileFormats
import pert
import zaderenko
import simulation
           
def vectorDuraciones(it, actividad):
    """
    Function performing the simulation of the project durations.

    it (number of iterations to be performed)
    actividad (vector with activities of the project and their durations)

    return: duraciones (vector with all durations resulting from the simulation)
    """
    
    # Se simulan las duraciones de las actividades y se genera el grafo del proyecto.    
    simulaciones = simulation.simulacion(it, actividad)
    grafoRenumerado = pert.pertFinal(actividad)
    nodosN = []

    for n in range(len(grafoRenumerado.successors)):
        nodosN.append(n+1)

    # Realizamos la simulacion de la duracion del proyecto aplicando la matriz de Zaderenko.
    duraciones = []
    if simulaciones == None:
        return
    else:
        for s in simulaciones: 
            matrizZad = zaderenko.mZad(actividad, grafoRenumerado.arcs, nodosN, 0, s)
            tearly = zaderenko.early(nodosN, matrizZad)
            duracionProyecto = tearly[-1]
            duraciones.append(duracionProyecto)
            
    return duraciones, simulaciones, grafoRenumerado

        
def main():
    """
    The following program of simulation batch is in charge of uploading a .ppc format file and generating two files 
    from the first one. On the one hand, it generates a file with the result of simulating n times, on the other hand,
    it generates a file resulting from simulating the duration of the activities n times.

    The program shall receive the following parameters for each console:
        infile (name of the file from which data will be uploaded)
        durationsfile (name of the file in which the resulting list with the n simulations of the duration of the project will be saved)
        table_file (name of the file in charge of saving the n simulations of the durations of the activities,
                  the distribution to generate them will be that uploaded from durationsfile)
        -i (number of iterations to be performed)
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser(description='Generates activities and project simulations')
    parser.add_argument('infile', #default=sys.stdin,
                        help='Project file to simulate')
    parser.add_argument('--durations-file', '-d',
                        help='Name of file to store durations list (default: <infile>_simulation.csv)')
    parser.add_argument('--table-file', '-t', default=None,
                        help='Name of file to append test results (default: stdout)')
    parser.add_argument('-i', default=1000, type=int,
                        help='Number of iterations (default: 1000)')
    parser.add_argument('-p', default=90, type=int, 
           help='Percentil de caminos criticos considerados de la simulacion (default: 90)')

    args = parser.parse_args()

    if args.i < 1:
        print 'Number of iterations must be > 0'
        return 1

    if (args.p <= 0):
        print 'The argument p must be greater than 0'
        return 1

    if args.durations_file:
        durations_file = args.durations_file 
    else:
        durations_file = args.infile + '_simulation.csv'

    # Load the project of the ppcproject
    format = fileFormats.PPCProjectFileFormat()
    try:
        data = format.load(args.infile)
        if not data:
            print 'ERROR: Unexpected format for file ', args.infile
            return 1
    except fileFormats.InvalidFileFormatException:
        print 'ERROR: Unexpected format for file ', args.infile
        return 1
    except IOError:
        print 'ERROR: Reading project file\n'
        return 1
    act, schedules, recurso, asignacion = data

    # Simulate project
    durations, simulation_act, graph = vectorDuraciones(args.i, act)

    # Save durations in csv format
    with open(durations_file, 'w') as f:
        simulation_csv = ''
        for dur in durations:
            f.write(str(dur) + '\n')

    # Create the result vector to be saved in the file
    resultados = kolmogorov_smirnov.evaluate_models(act, durations, simulation_act, 
                                                    args.p, pert_graph=graph)

    # Save the results
    if args.table_file:
        if (not os.path.isfile(args.table_file)):
            # Create and write header
            results_table_file = open(args.table_file, 'w')
            header = "'Archivo', " + str( resultados.keys() )[1:-1] + '\n'
            header = header.replace("'", '"')
            results_table_file.write(header)
        else:
            # Append data to the end
            results_table_file = open(args.table_file, 'a')
    else:
        results_table_file = sys.stdout

    # Write values comma separated
    s = str(args.infile) 
    for res in resultados.values():
        s += ',' + res.__repr__().replace("'", '"') # Use doble quote to enclose strings
    s += '\n'

    results_table_file.write(s)
    results_table_file.close()
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

