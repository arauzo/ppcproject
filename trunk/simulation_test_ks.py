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

import assignment
import graph
import kolmogorov_smirnov
import math
import fileFormats
import ppcproject
import numpy
import pert
import csv

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
        

def save (resultados, filename, infile):

    """
    Function that saves the test results and the simulation in a table.

    resultados (values resulting from the simulation and application of the kolmogorov_smirnov test)
    filename (name of the file in which the results will be saved)
    infile (name of the file whose data has been read)
    """
    
    # We check if the file already exists, or else we create the header and open it in writing mode; if it exists, we open it in filler mode
    s = ''
    if (not checkfile(filename)):
        if filename[-4:] == '.csv':
            f = open (filename, 'w')
        else:
            f = open(filename + '.csv', 'w')
        s += 'Archivo'+ ',' + 'm' + ',' + 'm1' + ',' + 'M.Norm' + ',' + 'S.Norm' + ',' + 'P.Norm' + ',' + 'M.Gamm' + ',' + 'S.Gamm' + ',' + 'P.Gamm' + ',' + 'M.VE' + ',' + 'S.VE' + ',' + 'P.VE' + ',' + 'M.Simu' + ',' + 'S.Simu' + ',' + 'Mas cercana' + ',' + 'mS'+','+'mCercana'+ '\n'        
    else:
        f = open(filename, 'a')

    s += str(infile) + ',' + str(resultados[0]) + ',' + str(resultados[1]) + ',' + str(resultados[2]) + ',' + str(resultados[3]) + ',' + str(resultados[4]) + ',' + str(resultados[5]) + ',' + str(resultados[6]) + ',' + str(resultados[7]) + ',' + str(resultados[8]) + ',' + str(resultados[9]) + ',' + str(resultados[10]) + ',' + str(resultados[11]) + ',' + str(resultados[12]) + ',' + str(resultados[13]) + ',' + str(resultados[14]) + ',' + str(resultados[15]) + '\n'

    f.write(s)
    f.close()


def checkfile(archivo):
    """
    Function that checks the existence of a file.

    archivo (name of the file whose existence is to be checked)

    return: bool (it returns a boolean based on the existence or non-existence of the file)
    """

    import os.path
    if os.path.isfile(archivo):
        return True
    else:
        return False

def test (activity, duracionesTotales, simulaciones, porcentaje):
    """
    Function that performs the kolmogorov_smirnov test and calculates the parameters required to check which
    estimated parameters most approximates to those obtained during the simulation.

    activity (project activities)
    duracionesTotales (vector with the duration resulting from the simulation)
    simulaciones (vector with the simulations of each activity in each iteration)
    porcentaje (the mark we want to establish to determine how many paths have turned out critical)

    return: results( vector with the results we should save in the output table)
    """

    informacionCaminos = []
    # Get all paths removing 'begin' y 'end' from each path
    successors = dict(((act[1], act[2]) for act in activity))
    g = graph.roy(successors)
    caminos = [c[1:-1]for c in graph.find_all_paths(g, 'Begin', 'End')]


    # A list is created with the paths, their duration and variances    
    for camino in caminos:   
        media, varianza = pert.mediaYvarianza(camino,activity) 
        info = [camino, float(media), varianza, math.sqrt(float(varianza))]      
        informacionCaminos.append(info)

    #The list is arranged in order of increasing according to the average duration of the paths
    informacionCaminos = kolmogorov_smirnov.ordenaCaminos(informacionCaminos)

    # We create an apparition vector that will count all the times a path has turned out critical
    aparicion = numeroCriticos (informacionCaminos, duracionesTotales, simulaciones, caminos)
    
    # We ascribe the value m2 according to the selected percentage
    m2 = caminosCriticosCalculados (aparicion, porcentaje, len(simulaciones))

    #The number of predominant paths is calculated (according to Dodin and to our method),
    #Values are assign to alpha and beta in order to perform the gamma function
    #The average and sigma estimated for the gamma are assigned
    m, m1, alfa, beta, mediaestimada, sigma = kolmogorov_smirnov.calculoValoresGamma(informacionCaminos)

    #The average and the sigma of the normal are assigned
    mediaCritico, dTipicaCritico = kolmogorov_smirnov.calculoMcriticoDcriticoNormal(informacionCaminos)

    #The average and the sigma of the simulation are assigned
    mediaSimulation = numpy.mean(duracionesTotales)
    sigmaSimulation = numpy.std(duracionesTotales)

    #If there were more than one path candidate to be critical, the values for the function of extreme values are calculated
    #The average and the sigma of the extreme values function are calculated
    if (m != 1):
        a, b = kolmogorov_smirnov.calculoValoresExtremos (mediaCritico, dTipicaCritico, m)
        mediaVE, sigmaVE = kolmogorov_smirnov.calculoMcriticoDcriticoEV (a, b)

    #An empty vector is created to save the results
    results = []

    # The number of estimated paths candidate to be critical, according to Dodin and to our method is added to the vector of results.   
    results.append(m)
    results.append(m1)

    # Depending on whether the distribution of extreme values is applied, the results displaying in the output file will be added.
    if (m != 1):
        pvalueN, pvalueG, pvalueEV = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta, a, b)
        results.append(round(mediaCritico,6))
        results.append(round(dTipicaCritico,6))
        results.append(round(pvalueN[0],6))
        results.append(round(mediaestimada,6))
        results.append(round(sigma,6))
        results.append(round(pvalueG[0],6))
        results.append(round(mediaVE,6))
        results.append(round(sigmaVE,6))
        results.append(round(pvalueEV[0],6))
        results.append(round(mediaSimulation,6))
        results.append(round(sigmaSimulation,6))
        results.append(theBest(results))
        results.append(m2)
        results.append(theBestm(m,m1,m2))
    else:
        pvalueN, pvalueG = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta)
        results.append(round(mediaCritico,6))
        results.append(round(dTipicaCritico,6))
        results.append(round(pvalueN[0],6))
        results.append(round(mediaestimada,6))
        results.append(round(sigma,6))
        results.append(round(pvalueG[0],6))
        results.append('Not defined')
        results.append('Not defined')
        results.append('Not defined')
        results.append(round(mediaSimulation,6))
        results.append(round(sigmaSimulation,6))
        results.append(theBest(results))
        results.append(m2)
        results.append(theBestm(m,m1,m2))

    

    return results

def numeroCriticos (informacionCaminos, duracionesTotales, simulaciones, caminos):
    """
    Funcion que genera un vector con las veces que ha salido critico cada camino.

    infoCaminos (informacion referente a los caminos)
    duracionesTotales (vector de la simulacion de duraciones del proyecto)
    simulaciones (vector con la simulacion de las duraciones de las actividades)
    caminos (caminos posibles del proyecto)
    """
    # We create an apparition vector that will count all the times a path has turned out critical
    aparicion = []

    # It is initialized
    for n in range(len(informacionCaminos)):
        aparicion.append(0)
    
    # Loop in charge of counting the times each path has turned out critical
    for i in range(len(duracionesTotales)):
        longitud = len(informacionCaminos)
        
        for j in caminos: 
            critico = informacionCaminos [longitud-1][0]
            
            for n in range(len(critico)):
                critico[n] = int(critico[n])

            duracion = 0 
            
            for x in critico:                
                duracion += simulaciones[i][x - 2]
                
            if ((duracion - 0.015 <= duracionesTotales[i]) and (duracionesTotales[i] <= duracion + 0.015)):
                aparicion [longitud - 1] += 1 
                break 
            else: 
                longitud -= 1

    return aparicion

def theBest (results):
    """
    Function that checks which one of the three distributions has obtained the best result comparing it with the simulation

    results (results obtained after the performance of the test)

    return: it returns which one has been the best distribution in string format.
    """
    if (results[10] != 'Not defined'):
        if (min(results[4], results[7], results[10]) == results[4]):
            return 'Normal'
        elif (min(results[4], results[7], results[10]) == results[7]):
            return 'Gamma'
        else:
            return 'Extreme Values'
    else:
        if (min(results[4], results[7]) == results[4]):
            return 'Normal'
        elif (min(results[4], results[7]) == results[7]):
            return 'Gamma'
        else:
            return 'Extreme Values'

def caminosCriticosCalculados (aparicion , porcentaje, it):
    """
    Function that returns the final count of those paths which turned out critical more times according to a given percentage

    aparicion(vector with the number os times each path has turned out critical)
    porcentaje(percentage in which the limit will be established, e.g.:90 will come to the number of paths which turned out critical 90% of the times)
    it (final count of the iterations)

    return: total (numero de caminos criticos)
    """
    aux = int(round((porcentaje * it)/100))
    ncaminos = len(aparicion) - 1
    total = 0
    aux2 = 0

    for i in range(len(aparicion)):
        if (aparicion[ncaminos] != 0):
            aux2 += aparicion[ncaminos]
            if (aux2 >= aux):
                return total + 1
            else:
                total += 1
                ncaminos -= 1
        else:
            ncaminos -= 1

def theBestm (m,m1,m2):
    """
    Calculate which one was the closest approximation
    to the real one as far as paths is concerned

    m (estimated paths candidate to be critical according to Dodin)
    m1 (estimated paths candidate to be critical according to Lorenzo Salas)
    m2 (calculated paths which turned out critical more than a % times)

    return: Un strin con la mejor opcion
    """
    aux1 = abs(m2-m)
    aux2 = abs(m2-m1)
    if (aux1<aux2):
        return 'Dodin'
    elif (aux1>aux2):
        return 'Salas'
    else:
        return 'Iguales'
        


def load2 (infile2):
    """
    Function that uploads the file with the list of the results of the simulation.

    infile2 (name of the file in which the list of the simulation is saved)

    return: real_simulation_list (float vector with the results of the simulation)
    """
    real_simulation_list = []
    with open(infile2, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            real_simulation_list.append(float(row[0]))

    return real_simulation_list

def load3 (infile3):
    """
    Function that uploads the file with the list of the results of the simulation
    of activities.

    infile3 (name of the file in which the list of the simulation is saved)

    return 
    """
    activity_simulation_list= []
    f = open(infile3)
    for s in f:
        activity_simulation_list.append(eval(s))


    return activity_simulation_list

def main():
    """
    The following program is in charge of generating a table with the results of the Kolmogorov-smirnov test,
    as well as a series of data required to carry out our research project.

    It is necessary to give it the arguments below:
        infile (ppc file from which we will take the information needed to perform the required calculations
                for our research)
        infile2 (file with the data of the simulation of the duration of the project)
        infile3 (file with the data of the simulation of the activities)
        outfile (.csv file in which the output data will be saved)
        p (mark percentage for the numebr of critical paths)
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('infile2', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('infile3', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('outfile', default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('-p', default=90, type=int, 
                        help='Porcentaje por que pondra el limite de caminos criticos de la simulacion')


    args = parser.parse_args()
    
    # We upload the file with the activities filled in
    act, schedules, recurso, asignacion = load(args.infile)

    # We upload the file with the results of the simulation
    simulation_results = load2 (args.infile2)

    simulation_activities_results = load3 (args.infile3)
    if (args.p <= 0):
        raise Exception ('The argument p must be greater than 0')
    else:
        # We create the result vector to be saved in the file
        resultados = test(act, simulation_results, simulation_activities_results, args.p)

        # We save the results in the file
        save(resultados, args.outfile, args.infile)  
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

