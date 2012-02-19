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

    """
    Funcion que guarda los resultados del test y la simulacion en una tabla.

    resultados (valores resultado de la simulacion y aplicacion del test de kolmogorov_smirnov)
    filename (nombre del archivo en el que vamos a guardar los resultados)
    infile (nombre del archivo del que hemos leido los datos)
    """
    
    # Comprobamos si existe el fichero, si no existe creamos la cabecera y lo abrimos en modo escritura; si existe lo abrimos en modo relleno
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
    Funcion que comprueba la existencia de un archivo.

    archivo (nombre del archivo que queremos comprobar si existe)

    return: bool (devuelve un booleano en funcion de si el archivo existe o no)
    """

    import os.path
    if os.path.isfile(archivo):
        return True
    else:
        return False

def test (activity, duracionesTotales, simulaciones, porcentaje):
    """
    Funcion que realiza el test de kolmogorov_smirnov y calcula los parametros necesarios para comprobar que parametros
    estimados se han acercado mas a los obtenidos en la simulacion.

    activity (actividades del proyecto)
    duracionesTotales (vector con las duraciones resultado de la simulacion)
    simulaciones (vector con las simulaciones de cada actividad en cada iteracion)
    porcentaje (cota que queremos poner para saber cuantos caminos han salido criticos)

    return: results( vector con los resultados que nos interesa guardar en la tabla de salidas)
    """

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

    # Creamos un vector aparicion que contara el numero de veces que un camino ha salido critico
    aparicion = []

    # Se inicializa
    for n in range(len(informacionCaminos)):
        aparicion.append(0)
    
    # Bucle encargado de contar las vaces que ha salido critico cada camino
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

    # Asignamos el valor de m2 en funcion del porcentaje elegido
    m2 = caminosCriticosCalculados (aparicion, porcentaje, len(simulaciones))

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

    # Se agrega al vector de resultados el numero de caminos estimados candidatos a ser criticos, segun Dodin y segun nuestro metodo.    
    results.append(m)
    results.append(m1)

    # En funcion de si se aplica la distribucion de valores extremos se agregan los resultados que se mostraran en el archivo de salida.
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

def theBest (results):
    """
    Funcion que comprueba cual de las tres distribuciones ha obtenido el mejor resultado comparandolo con la simulacion

    results (resultados obtenidos tras realizar el test)

    return: devuelve cual ha sido la mejor distribucion en formato string.
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
    Funcion que devuelve el numero total de caminos que han sido criticos mas veces, en funcion de un porcentaje dado

    aparicion(vector con el numero de veces que ha sido critico cada camino)
    porcentaje(porcentaje en el que pondremos el limite, ej:90 , nos dara el numero de caminos que han sido criticos el 90% de las veces)
    it (numero de iteraciones totales)

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
    Calcula cual ha sido la aproximacion mas cercana
    a la real en cuanto a caminos se refiere

    m (caminos estimados candidatos a ser criticos segun Dodin)
    m1 (caminos estimados candidatos a ser criticos segun Lorenzo Salas)
    m2 (caminos calculados que han salido criticos mas del un % de las veces)

    return: Un strin con la mejor opcion
    """
    aux1 = abs(m2-m)
    aux2 = abs(m2-m1)
    if (aux1<aux2):
        return 'Dodin'
    elif (aux1>aux2):
        return 'Lorenzo'
    else:
        return 'Iguales'
        


def load2 (infile2):
    """
    Funcion que carga el archivo con la lista de los resultados de la simulacion.

    infile2 (nombre del archivo en el que esta guardada la lista de la simulacion)

    return: real_simulation_list (vector de float con los resultados de la simulacion)
    """
    activity_simulation_list= []
    with open(infile2, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            activity_simulation_list.append(float(row[0]))

    return activity_simulation_list

def load3 (infile3):
    """
    Funcion que carga el archivo con la lista de los resultados de la simulacion
    de actividades.

    infile3 (nombre del archivo en el que esta guardada la lista de la simulacion)

    return 
    """
    real_simulation_list= []
    f = open(infile3)
    for s in f:
        real_simulation_list.append(eval(s))

    #eval(real_simulation_list)
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
    parser.add_argument('infile3', nargs='?', default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('outfile', nargs='?', default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('-p', default=90, type=int, 
                        help='Porcentaje por que pondra el limite de caminos criticos de la simulacion')


    args = parser.parse_args()
    
    # Cargamos el archivo con las actividades rellenas
    act, schedules, recurso, asignacion = load(args.infile)

    # Cargamos el archivo con los resultados de la simulacion
    simulation_results = load2 (args.infile2)

    simulation_activities_results = load3 (args.infile3)
    
    # Creamos el vector resultados que queremos guardar en el fichero
    resultados = test(act, simulation_results, simulation_activities_results, args.p)

    # Salvamos los resultados en el fichero
    save(resultados, args.outfile, args.infile)  
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

