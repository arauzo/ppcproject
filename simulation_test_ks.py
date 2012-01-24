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
import pert
import zaderenko
import simulation
import fileFormats
import ppcproject
import numpy

def load (filename):

    formatos = [fileFormats.PPCProjectFileFormat(),fileFormats.PSPProjectFileFormat()]
    print filename
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
        

def save (resultados, filename, inputfile, i):

    f = open(filename,"a")
    f.write('Nombre del archivo de entrada: ')
    f.write(str(inputfile))
    f.write('\n')
    f.write('Numero de iteraciones realizadas: ')
    f.write(str(i))
    f.write('\n')
    f.write('El valor de comparacion es: ')
    f.write(str(resultados[0]))
    f.write('\t' + 'Para un alfa = ' + str(resultados[1]))
    f.write('\n')
    f.write('Valor para la normal' + '\t' + 'Valor para la gamma' + '\t'+'\t' + 'Valor para VE')
    f.write('\n')
    f.write(str(resultados[2]) + '\t'+'\t'+'\t' + str(resultados[3]) + '\t' + '\t'+'\t' + str(resultados[4]))
    f.write('\n')
    distribuciones = ['Normal', 'Gamma', 'Extreme Values']
    cont = 0
    for n in range(2,5):
        if resultados[n] <= resultados [0]:
            cont += 1
            f.write('TEST SUPERADO!! La distribucion ' + distribuciones[n-2] + ' ha pasado el test' + '\n')
    if (cont == 0):
        f.write('NINGUNA DISTRIBUCION HA PASADO EL TEST' + '\n')
    f.write('El valor del test usando scipy con la normal es: ' + str(resultados[5]) + '\n')
    f.write('El valor del test usando scipy con la gamma es: ' + str(resultados[6]) + '\n')
    f.write('El valor del test usando scipy con la de valores extremos es: ' + str(resultados[7]) + '\n')
    f.write('\n' + '\n')
    
    f.close()
   

def test (it,activity,alfa_test):
    

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
    m, m1, alfa, beta, mediaestimada, sigma = kolmogorov_smirnov.calculoValoresGamma(informacionCaminos)
    print 'Media Gamma: ', mediaestimada, '\n'
    print 'Sigma Gamma: ', sigma, '\n'

    mediaCritico, dTipicaCritico = kolmogorov_smirnov.calculoMcriticoDcriticoNormal(informacionCaminos)
    print 'Media Critico: ', mediaCritico, '\n'
    print 'Sigma Critico: ', dTipicaCritico, '\n'


    if (m != 1):
        a, b = kolmogorov_smirnov.calculoValoresExtremos (mediaCritico, dTipicaCritico, m)
        mediaVE, sigmaVE = kolmogorov_smirnov.calculoMcriticoDcriticoEV (a, b)
        print 'Media VE: ', mediaVE, '\n'
        print 'Sigma VE: ', sigmaVE, '\n'
    #Creamos un vector con las duraciones totales para pasarselo al test
    duracionesTotales = vectorDuraciones(it,activity)
    print 'Media Simulacion: ', numpy.mean(duracionesTotales), '\n'
    print 'Sigma Simulacion: ', numpy.std(duracionesTotales), '\n'
    results = []
    print alfa_test
    valorComparacion = kolmogorov_smirnov.valorComparacion(alfa_test, len(duracionesTotales))
    print valorComparacion
    results.append(valorComparacion)
    results.append(alfa_test)
    if (m != 1):
        bondadNormal, bondadGamma, bondadVE, pvalueN, pvalueG, pvalueEV = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta, a, b)
        results.append(bondadNormal)
        results.append(bondadGamma)
        results.append(bondadVE)
        results.append(pvalueN)
        results.append(pvalueG)
        results.append(pvalueEV)
    else:
        bondadNormal, bondadGamma, bondadVE, pvalueN, pvalueG = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta)
        results.append(bondadNormal)
        results.append(bondadGamma)
        results.append(bondadVE)
        results.append(pvalueN)
        results.append(pvalueG)
        results.append('No definido')

    

    return results



def vectorDuraciones(it,actividad):
   
    simulaciones = simulation.simulacion(it, actividad)
    grafoRenumerado = pert.pertFinal(actividad)

    nodosN=[]
    for n in range(len(grafoRenumerado.successors)):
        nodosN.append(n+1)

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
    
    
    return duraciones

def main():
    """
    XXX Main program or test code
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('outfile', nargs='?', default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('-a', default=0.5, type=float, 
                        help='Value of constant to generate the alfa of the test (default: 0.05)')
    parser.add_argument('-i', default=1000,type=int,
                        help='Number of iterations (default: 1000)')

    args = parser.parse_args()

    act, schedules, recurso, asignacion = load(args.infile)
    resultados = test(args.i,act, args.a)
    save(resultados, args.outfile, args.infile, args.i)  
    print 'We will read from', args.infile
    print 'We will write to', args.outfile
    print 'Alfa value for the test is ', args.a
    print 'Number of iterations are', args.i

    # XXX Use return 1 or any non 0 code to finish with error state
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

