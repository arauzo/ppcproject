#!/usr/bin/env python
"""
Template for main programs and modules with test code

This template must be used for all programs written in Python and for almost all 
modules (as modules should have test code). 

The comments, specially those marked with XXX, are supposed to be deleted or replaced with your own comments.

It is inspired in the comments from Guido's article[1]. I have not included Usage exception as OptionParser
has the method .error to return when something is wrong on arguments (note that getopt is deprecated).

[1] http://www.artima.com/weblogs/viewpost.jsp?thread=4829
"""
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
    
    s = ''
    if (not checkfile(filename)):
        if filename[-4:] == '.csv':
            f = open (filename, 'w')
        else:
            f = open(filename + '.csv', 'w')
        s += 'Archivo'+ ',' + 'm' + ',' + 'm1' + ',' + 'Media Normal' + ',' + 'Sigma Normal' + ',' + 'Pvalue Normal' + ',' + 'Media Gamma' + ',' + 'Sigma Gamma' + ',' + 'Pvalue Gamma' + ',' + 'Media Valores Extremos' + ',' + 'Sigma Valores Extremos' + ',' + 'Pvalue Valores Extremos' + ',' + 'Media Simulacion' + ',' + 'Sigma Simulacion' + '\n'        
    else:
        f = open(filename, 'a')

    s += str(infile) + ',' + str(resultados[0]) + ',' + str(resultados[1]) + ',' + str(resultados[2]) + ',' + str(resultados[3]) + ',' + str(resultados[4]) + ',' + str(resultados[5]) + ',' + str(resultados[6]) + ',' + str(resultados[7]) + ',' + str(resultados[8]) + ',' + str(resultados[9]) + ',' + str(resultados[10]) + ',' + str(resultados[11]) + ',' + str(resultados[12]) + '\n'

    f.write(s)
    f.close()


def checkfile(archivo):

    import os.path
    if os.path.isfile(archivo):
        return True
    else:
        print False

def test (activity,alfa_test,duracionesTotales):
    

    informacionCaminos = []
    # Get all paths removing 'begin' y 'end' from each path
    successors = dict(((act[1], act[2]) for act in activity))
    g = graph.roy(successors)
    caminos = [c[1:-1]for c in graph.find_all_paths(g, 'Begin', 'End')]

    # Se crea una lista con los caminos, sus duraciones y sus varianzas

    for camino in caminos:   
        media, varianza = pert.mediaYvarianza(camino,activity) 
        info = [camino, float(media), varianza, math.sqrt(float(varianza))]      
        informacionCaminos.append(info)

    #Se ordena la lista en orden creciente por duracion media de los caminos
    informacionCaminos = kolmogorov_smirnov.ordenaCaminos(informacionCaminos)

    #Se calcula el numero de caminos dominantes (segun Dodin y segun nuestro metodo),
    #Se asignan los valores a alfa y beta para poder realizar la funcion gamma
    #Se asignan la media y la sigma estimadas para la gamma
    m, m1, alfa, beta, mediaestimada, sigma = kolmogorov_smirnov.calculoValoresGamma(informacionCaminos)

    #Se asignan la media y la sigma de la normal
    mediaCritico, dTipicaCritico = kolmogorov_smirnov.calculoMcriticoDcriticoNormal(informacionCaminos)

    #Se asignan la media y la sigma de la simulacion
    mediaSimulation = numpy.mean(duracionesTotales)
    sigmaSimulation = numpy.std(duracionesTotales)

    #Si hay mas de un camino candidato a ser critico, se calculan los valores para la funcion de valores extremos
    #Se asignan la media y la sigma de la funcion de valores extremos
    if (m != 1):
        a, b = kolmogorov_smirnov.calculoValoresExtremos (mediaCritico, dTipicaCritico, m)
        mediaVE, sigmaVE = kolmogorov_smirnov.calculoMcriticoDcriticoEV (a, b)

    #Se crea un vector vacio para guardar los resultados
    results = []
    #Se calcula un valor de comparacion para el p-value
    valorComparacion = kolmogorov_smirnov.valorComparacion(alfa_test, len(duracionesTotales))
    
    results.append(m)
    results.append(m1)
    if (m != 1):
        bondadNormal, bondadGamma, bondadVE, pvalueN, pvalueG, pvalueEV = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta, a, b)
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
    else:
        bondadNormal, bondadGamma, bondadVE, pvalueN, pvalueG = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta)
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

    

    return results

# Hacer una funcion que devuelva cual ha sido el mejor resultado :def theBest (results):


def load2 (infile2):

    real_simulation_list= []
    with open(infile2, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            real_simulation_list.append(float(row[0]))
    #f = open(infile2, 'r')
    #real_simulation = f.read()
    #real_simulation_tuple = eval(real_simulation)
    #real_simulation_list = []
    #for n in range(len(real_simulation_tuple)):
    #    real_simulation_list.append (real_simulation_tuple[n])
    #f.close()
    
    return real_simulation_list


def main():
    """
    XXX Main program or test code
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('infile2', nargs='?', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('outfile', nargs='?', default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('-a', default=0.5, type=float, 
                        help='Value of constant to generate the alfa of the test (default: 0.05)')


    args = parser.parse_args()

    act, schedules, recurso, asignacion = load(args.infile)
    simulation_results = load2 (args.infile2)
    #XXX Quitar la a
    resultados = test(act, args.a, simulation_results)
    i = len(simulation_results)
    save(resultados, args.outfile, args.infile)  
    #print 'We will read from', args.infile
    #print 'We will write to', args.outfile
    #print 'Alfa value for the test is ', args.a
    #print 'Number of iterations are', i

    # XXX Use return 1 or any non 0 code to finish with error state
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

