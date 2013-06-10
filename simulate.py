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
            
    return duraciones, simulaciones
   
   
#def test(activity, duracionesTotales, simulaciones, porcentaje):
#    """
#    Performs the kolmogorov_smirnov test and calculates the parameters required to check which
#    estimated parameters most approximates to those obtained during the simulation.

#    activity (project activities)
#    duracionesTotales (vector with the duration resulting from the simulation)
#    simulaciones (vector with the simulations of each activity in each iteration)
#    porcentaje (the mark we want to establish to determine how many paths have turned out critical)

#    return: results( vector with the results we should save in the output table)
#    """
#    # Get all paths removing 'begin' y 'end' from each path
#    successors = dict(((act[1], act[2]) for act in activity))
#    g = graph.roy(successors)
#    caminos = [c[1:-1] for c in graph.find_all_paths(g, 'Begin', 'End')]

#    # A list is created with the paths, their duration and variances    
#    informacionCaminos = []
#    for camino in caminos:   
#        media, varianza = pert.mediaYvarianza(camino, activity) 
#        info = [camino, float(media), float(varianza), math.sqrt(float(varianza))]      
#        informacionCaminos.append(info)

#    # Paths in order of increasing duration and stdev
#    informacionCaminos.sort(key=operator.itemgetter(1,3))

#    # Create an apparition vector that will count all the times a path has turned out critical
#    aparicion = numeroCriticos(informacionCaminos, duracionesTotales, simulaciones, caminos)
#    
#    # Value m2 according to the selected percentage
#    m2 = caminosCriticosCalculados(aparicion, porcentaje, len(simulaciones))

#    #The number of predominant paths is calculated (according to Dodin and to our method),
#    #Values are assign to alpha and beta in order to perform the gamma function
#    #The average and sigma estimated for the gamma are assigned
#    m, m1, alfa, beta, mediaestimada, sigma, sigma_longest_path, sigma_max, sigma_min \
#        = kolmogorov_smirnov.calculoValoresGamma(informacionCaminos, 'Normal')

#    #The average and the sigma of the normal are assigned
#    mediaCritico = float(informacionCaminos[-1][1])
#    dTipicaCritico = float(informacionCaminos[-1][3]) 

#    #The average and the sigma of the simulation are assigned
#    mediaSimulation = numpy.mean(duracionesTotales)
#    sigmaSimulation = numpy.std(duracionesTotales)

#    #If there were more than one path candidate to be critical
#    #The average and the sigma of the extreme values function are calculated
#    mediaVE = sigmaVE = a = b = None
#    if (m != 1):
#        a, b = kolmogorov_smirnov.calculoValoresExtremos (mediaCritico, dTipicaCritico, m)
#        mediaVE, sigmaVE = kolmogorov_smirnov.calculoMcriticoDcriticoEV (a, b)

#    #An empty vector is created to save the results
#    results = []

#    # The number of estimated paths candidate to be critical, 
#    # according to Dodin and to our method is added to the vector of results.   
#    results.append(m)
#    results.append(m1)

#    # Depending on whether the distribution of extreme values is applied
#    if (m != 1):
#        pvalueN, pvalueG, pvalueEV \
#            = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, 
#                                        dTipicaCritico, alfa, beta, a, b)
#    else:
#        pvalueN, pvalueG = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico,
#                                                     dTipicaCritico, alfa, beta)
#        pvalueEV = [None]
#        
#    results.append(mediaCritico)
#    results.append(dTipicaCritico)
#    results.append(pvalueN[0])
#    results.append(mediaestimada)
#    results.append(sigma)
#    results.append(pvalueG[0])
#    results.append(mediaVE)
#    results.append(sigmaVE)
#    results.append(pvalueEV[0])
#    results.append(mediaSimulation)
#    results.append(sigmaSimulation)
#    results.append(theBest(results))
#    results.append(m2)
#    results.append(theBestm(m, m1, m2))
#    results.append(sigma_longest_path)
#    results.append(sigma_max)
#    results.append(sigma_min)
#    return results

        
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
    durations, simulation_act = vectorDuraciones(args.i, act)

    # Save durations in csv format
    with open(durations_file, 'w') as f:
        simulation_csv = ''
        for dur in durations:
            f.write(str(dur) + '\n')

    # Create the result vector to be saved in the file
    resultados = kolmogorov_smirnov.evaluate_models(act, durations, simulation_act, args.p)

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

