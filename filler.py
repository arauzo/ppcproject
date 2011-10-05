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
# Imports from Python standard library

# Imports from other external libraries

# Imports from our libraries
import assignment
import graph
import kolmogorov_smirnov
import math
import pert
import zaderenko
import simulation
import fileFormats
import ppcproject
# XXX Here functions and classes...

miObjeto = ppcproject.PPCproject()

def load (filename, distribucion, k):

    format = fileFormats.PSPProjectFileFormat()
    activities, none, none1, none2 = format.load(filename)
    activity = assignment.actualizarActividadesFichero(k,distribucion,activities)
    return activity

def save (actividades, filename):

    f = open(filename,"w")
    for line in actividades:
        f.write(str(line))
        f.write('\n')

    f.close()
   

def test (it,activity):
    

    informacionCaminos = []
    # Get all paths removing 'begin' y 'end' from each path
    successors = dict(((act[1], act[2]) for act in activity))
    g = graph.roy(successors)
    caminos = [c[1:-1]for c in graph.find_all_paths(g, 'Begin', 'End')]

    # Se crea una lista con los caminos, sus duraciones y sus varianzas
#    miObjeto2 = ppcproject.PPCproject()
    for camino in caminos:   
        media, varianza = miObjeto.mediaYvarianza(camino,activity) 
        info = [camino, float(media), varianza, math.sqrt(float(varianza))]      
        informacionCaminos.append(info)

    #Se ordena la lista en orden creciente por duracion media de los caminos
    informacionCaminos = kolmogorov_smirnov.ordenaCaminos(informacionCaminos)

    #Se calcula el numero de caminos dominantes (segun Dodin y segun nuestro metodo),
    #Se asignan los valores a alfa y beta para poder realizar la funcion gamma
    m, m1, alfa, beta, mediaestimada, sigma = kolmogorov_smirnov.calculoValoresGamma(informacionCaminos)
    print m, m1, alfa, beta , mediaestimada, sigma, '\n'

    mediaCritico, dTipicaCritico = kolmogorov_smirnov.calculoMcriticoDcriticoNormal(informacionCaminos)
    print mediaCritico, dTipicaCritico ,m,'\n'

    if (m != 1):
        a, b = kolmogorov_smirnov.calculoValoresExtremos (mediaCritico, dTipicaCritico, m)
    #Creamos un vector con las duraciones totales para pasarselo al test
    duracionesTotales = vectorDuraciones(it,activity)

    valorComparacion = kolmogorov_smirnov.valorComparacion(0.05, len(duracionesTotales)) 
    if (m != 1):
        bondadNormal, bondadGamma, bondadVE = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta, a, b)
        print bondadNormal, bondadGamma , bondadVE, '\n'
    else:
        bondadNormal, bondadGamma, bondadVE = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta)
        print bondadNormal, bondadGamma, bondadVE, '\n'

    
    print 'El valor de comparacion es: ', valorComparacion, '\n'  
    print 'La media y la varianza que selecciona es: ', mediaCritico, dTipicaCritico, '\n'
    if (m != 1):
        print 'Los valores de a y b son respectivamente', a, b, '\n'


def vectorDuraciones(it,actividad):
    
    simulaciones = simulation.simulacion(it, actividad)
 #   miObjeto = ppcproject.PPCproject()
    grafoRenumerado = miObjeto.pertFinal(actividad)

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
    parser.add_argument('-d', '--distribution', default='Beta', 
                        choices=['Beta', 'Normal', 'Uniform', 'Triangular'],
                        help='Statistical distribution (default: Beta)')
    parser.add_argument('-k', default=0.2, type=float, 
                        help='Value of constant to generate missing values (default: 0.2)')

    args = parser.parse_args()

    act = load(args.infile,args.distribution,args.k)
    test(1000,act)
    save(act,args.outfile)  

    # XXX Place here the code for test or main program
    print 'We will read from', args.infile
    print 'We will write to', args.outfile
    print 'Distribution will be', args.distribution
    print 'and constant', args.k

    # XXX Use return 1 or any non 0 code to finish with error state
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

