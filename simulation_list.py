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

import fileFormats
import simulation_test_ks
import pert
import zaderenko
import graph
import simulation


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
        
def save (resultados, filename):
    """
    Funcion que guarda el resultado de la simulacion en formato csv

    resultados (valores resultantes de la simulacion)
    filename (nombre del fichero en el que se guardaran los valores) 
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
    Funcion que guarda el resultado de la simulacion de actividades en formato csv

    simulation (valores resultantes de la simulacion de actividades)
    filename (nombre del fichero en el que se guardaran los valores) 
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
    Funcion que realiza la simulacion de las duraciones del proyecto.

    it (numero de iteraciones que se realizaran)
    actividad (vector con las actividades del proyecto y sus duraciones)

    return: duraciones (vector con todas las duraciones resultado de la simulacion)
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
    XXX Main program or test code
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('outfile', nargs='?', default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('outfile2', nargs='?', default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('-i', default=1000,type=int,
                        help='Number of iterations (default: 1000)')

    args = parser.parse_args()

    # Cargamos el proyecto del ppcproject
    act, schedules, recurso, asignacion = load(args.infile)

    # Generamos el vector de resultados
    resultados, simulaciones = vectorDuraciones (args.i, act) #projectSimulation (args.i,act)
    
    # Salvamos un vector con las duraciones simuladas de cada actividad en cada iteracion
    saveSimulation(simulaciones, args.outfile2)

    # Salvamos en formato csv
    save(resultados, args.outfile)  

    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

