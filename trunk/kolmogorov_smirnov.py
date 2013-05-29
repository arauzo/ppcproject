#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 Models to estimate project duration and test the distribution estimated

 PPC-PROJECT
   Multiplatform software tool for education and research in
   project management

 Copyright 2007-13 Universidad de Córdoba
 This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published
   by the Free Software Foundation, either version 3 of the License,
   or (at your option) any later version.
 This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import random
import math
import operator
import collections

import scipy.stats
import numpy

import graph
import pert


def evaluate_models(activity, duracionesTotales, simulaciones, porcentaje=90):
    """
    Using the data from a simulation compare the results with those achieved by the several models 
    defined. The comparison is done by testing the fitting of the distribution with the 
    kolmogorov_smirnov test 

    activity (project activities)
    duracionesTotales (vector with the duration resulting from the simulation)
    simulaciones (vector with the simulations of each activity in each iteration)
    porcentaje (the mark we want to establish to determine how many paths have turned out critical)

    return: results( vector with the results we should save in the output table)
    """
    # Get all paths removing 'begin' y 'end' from each path
    successors = dict(((act[1], act[2]) for act in activity))
    g = graph.roy(successors)
    caminos = [c[1:-1] for c in graph.find_all_paths(g, 'Begin', 'End')]

    # List with the paths, their duration and variance (ordered by increasing duration and variance)
    informacionCaminos = []
    for camino in caminos:   
        media, varianza = pert.mediaYvarianza(camino, activity) 
        informacionCaminos.append([camino, float(media), float(varianza)])
    informacionCaminos.sort(key=operator.itemgetter(1,2))

    # Vector with the times a path has turned out critical
    #aparicion = numeroCriticos(informacionCaminos, duracionesTotales, simulaciones, caminos)
    
    # Value m2 according to the selected percentage
    #m2 = caminosCriticosCalculados(aparicion, porcentaje, len(simulaciones))

    # Critical path average and std deviation (according to PERT Normal estimate)
    crit_path_avg = float(informacionCaminos[-1][1])
    crit_path_stdev = math.sqrt(informacionCaminos[-1][2]) 

    #The number of predominant paths is calculated (according to Dodin and to our method),
    # Dentro de los criticos de dodin (desviaciones tipicas)
    sigma_longest_path = crit_path_stdev
    sigma_max = None
    sigma_min = None
    
    #Calculo de los caminos dominantes segun Dodin (m) y segun nosotros (m1). Asi como de Sigma.
    m_dodin = 0
    m1 = 0
    sigma = 0
    for n in range(len(informacionCaminos)):
        # Considerado critico por Dodin
        if ((crit_path_avg - informacionCaminos[n][1]) < max(0.05*crit_path_avg, 0.02* crit_path_stdev)):
            m_dodin += 1
            path_stddev = math.sqrt(informacionCaminos[n][2])
            if sigma_max == None or sigma_max < path_stddev:
                sigma_max = path_stddev
            if sigma_min == None or sigma_min > path_stddev:
                sigma_min = path_stddev

        # Considerado critico por Salas
        if ((float(informacionCaminos[n][1]) + 0.5*math.sqrt(informacionCaminos[n][2])) >= (crit_path_avg - 0.25* crit_path_stdev)):
            m1 +=1
            aux = math.sqrt(informacionCaminos[n][2])
            if sigma == 0:
                sigma = aux
            elif aux < sigma:
                sigma = aux

    # Gamma estimated distribution
    distribucion = activity[1][8]
    print distribucion, 'distribucion que estamos utilizando para el test'
    alfa, beta, mediaestimada, sigmaestimada = calculoValoresGamma(crit_path_avg, sigma_min,
                                                                   m_dodin, distribucion)

    #The average and the sigma of the simulation are assigned
    mediaSimulation = numpy.mean(duracionesTotales)
    sigmaSimulation = numpy.std(duracionesTotales)

    #If there were more than one path candidate to be critical
    #The average and the sigma of the extreme values function are calculated
    mediaVE = sigmaVE = a = b = None
    if (m_dodin != 1):
        a, b = calculoValoresExtremos (crit_path_avg, crit_path_stdev, m_dodin)
        mediaVE, sigmaVE = calculoMcriticoDcriticoEV (a, b)

    # Depending on whether the distribution of extreme values is applied
    if (m_dodin != 1):
        ks_testN, ks_testG, ks_testEV = testKS(duracionesTotales, crit_path_avg, 
                                               crit_path_stdev, alfa, beta, a, b)
    else:
        ks_testN, ks_testG = testKS(duracionesTotales, crit_path_avg,
                                    crit_path_stdev, alfa, beta)
        ks_testEV = [None, None]
        
    # Results
    results = collections.OrderedDict()
    results['m_dodin'] = m_dodin
    results['m1'] = m1
    results['mediaCritico'] = crit_path_avg
    results['dTipicaCritico'] = crit_path_stdev
    results['statisticN'] = ks_testN[0]
    results['pvalueN'] = ks_testN[1]
    results['mediaestimada'] = mediaestimada
    results['sigma'] = sigma
    results['statisticG'] = ks_testG[0]
    results['pvalueG'] = ks_testG[1]
    results['mediaVE'] = mediaVE
    results['sigmaVE'] = sigmaVE
    results['statisticEV'] = ks_testEV[0]
    results['pvalueEV'] = ks_testEV[1]
    results['mediaSimulation'] = mediaSimulation
    results['sigmaSimulation'] = sigmaSimulation
#    results['theBest'] = theBest(results)
#    results['m2'] = m2
#    results['theBestm'] = theBestm(m, m1, m2)
    results['sigma_longest_path'] = sigma_longest_path
    results['sigma_max'] = sigma_max
    results['sigma_min'] = sigma_min
    return results

#def numeroCriticos(informacionCaminos, duracionesTotales, simulaciones, caminos):
#    """
#    Create an apparition vector that will count all the times a path has turned out critical

#    informacionCaminos (informacion referente a los caminos)
#    duracionesTotales (vector de la simulacion de duraciones del proyecto)
#    simulaciones (vector con la simulacion de las duraciones de las actividades)
#    caminos (caminos posibles del proyecto)
#    """
#    aparicion = [0] * len(informacionCaminos)
#    
#    # Count the times each path has turned out critical
#    for i in range(len(duracionesTotales)):
#        longitud = len(informacionCaminos)
#        
#        for j in caminos: 
#            critico = informacionCaminos[longitud-1][0]
#            
#            for n in range(len(critico)):
#                critico[n] = int(critico[n])

#            duracion = 0 
#            for x in critico:      
#                duracion += simulaciones[i][x - 2]
#                
#            if ((duracion - 0.015 <= duracionesTotales[i]) and 
#                (duracionesTotales[i] <= duracion + 0.015)):
#                aparicion[longitud - 1] += 1 
#                break 
#            else: 
#                longitud -= 1

#    return aparicion

#def theBest (results):
#    """
#    Checks which one of the three distributions has obtained the best result comparing it with the simulation

#    results (results obtained after the performance of the test)

#    return: it returns which one has been the best distribution in string format.
#    """
#    if (results[10] != 'Not defined'):
#        if (min(results[4], results[7], results[10]) == results[4]):
#            return 'Normal'
#        elif (min(results[4], results[7], results[10]) == results[7]):
#            return 'Gamma'
#        else:
#            return 'Extreme Values'
#    else:
#        if (min(results[4], results[7]) == results[4]):
#            return 'Normal'
#        elif (min(results[4], results[7]) == results[7]):
#            return 'Gamma'
#        else:
#            return 'Extreme Values'

#def caminosCriticosCalculados (aparicion , porcentaje, it):
#    """
#    Returns the final count of those paths which turned out critical more times than a given percentage

#    aparicion(vector with the number of times each path has turned out critical)
#    porcentaje(percentage in which the limit will be established, e.g.:90 will come to the number of paths which turned out critical 90% of the times)
#    it (final count of the iterations)

#    return: total (numero de caminos criticos)
#    """
#    aux = int(round((porcentaje * it)/100))
#    ncaminos = len(aparicion) - 1
#    total = 0
#    aux2 = 0

#    for i in range(len(aparicion)):
#        if (aparicion[ncaminos] != 0):
#            aux2 += aparicion[ncaminos]
#            if (aux2 >= aux):
#                return total + 1
#            else:
#                total += 1
#                ncaminos -= 1
#        else:
#            ncaminos -= 1
#    return total

#def theBestm(m, m1, m2):
#    """
#    Calculate which one was the closest approximation
#    to the real one as far as paths is concerned

#    m (estimated paths candidate to be critical according to Dodin)
#    m1 (estimated paths candidate to be critical according to Lorenzo Salas)
#    m2 (calculated paths which turned out critical more than a % times)

#    return: Un strin con la mejor opcion
#    """
#    #print m, m1, m2
#    aux1 = abs(m2-m)
#    aux2 = abs(m2-m1)
#    if (aux1<aux2):
#        return 'Dodin'
#    elif (aux1>aux2):
#        return 'Salas'
#    else:
#        return 'Iguales'



def calculoValoresGamma(crit_path_avg, sigma_min, m_dodin, dist):
    """
    Estimate the duration random variable of a project with a Gamma distribution using a model 
    created by Salas et al.
    
    return: alfa (valor de alfa para la gamma)
            beta (valor de beta para la gamma)
            media (media estimada con la distribucion gamma)
            sigma (desviacion tipica estimada con la distribucion gamma)
    """
    sigma = 0.91154134766017  * sigma_min
    
    if dist == 'Normal':
        media = (  1.1336004782864 * crit_path_avg 
                 - 0.9153232086309 * sigma_min 
                 + 1.0927284342627 * math.log(m_dodin) )
    else :
        media = (  0.91263355372917 * crit_path_avg 
                 + 0.75501704782379 * sigma_min 
                 + 2.96581038327203 * math.log(m_dodin) )

    beta = sigma**2 / media
    alfa = media / beta
        
    return alfa, beta, media, sigma

def calculoValoresExtremos(media, sigma, m):
    """
    Funcion que nos devuelve los valores necesarios para
    realizar la distribucion de valores extremos

    media (duracion media del camino critico)
    sigma (desviacion tipica del camino critico)

    return: a, b (parametros necesarios para realizar la funcion de valores extremos)
    """
    a = media + sigma * ((2*math.log(m))**0.5 - 0.5 * (math.log(math.log(m)) + math.log(4*math.pi)) / (2* math.log(m))**0.5)
    b = ((2 * math.log(m))**0.5) / sigma

    return a, b

def calculoMcriticoDcriticoEV(a, b):
    """
    Funcion que devuelve la media y la desviacion tipica
    de la distribucion de valores extremos

    a, b (parametros necesarios para el calculo de la media y la desviacion tipica de la funcion de VE)

    return: media (media estimada de la funcion de valores extremos)
            sigma (desviacion tipica estimada de la funcion de valores extremos)
    """
    media = a + 0.57722 / b
    sigma = math.sqrt((math.pi**2) / (6*(b**2)))

    return media, sigma


def testKS(duraciones, mCrit, dCrit, alfa, beta, a=0, b=0, tamanio=0.5):
    """
    Funcion que realiza el test de kolmogorv_smirnoff y
    devuelve el p-value para cada distribucion

    duraciones (vector con las duraciones simuladas del proyecto)
    mCrit (media del camino critico)
    dCrit (desviacion tipica del camino critico)
    alfa (alfa de la funcion gamma)
    beta (beta de la funcion gamma)
    a (parametro de la funcion de valores extremos)
    b (parametro de la funcion de valores extremos)
    tamanio (tamanio del intervalo en el que queremos realizar el test)
    
    return: p-values (en el caso de que la opcion de guardar no se active)
            intervalos, frecuencias, distribuciones y p-values (en el caso de que se active la opcion de guardado)

    Nota: La funcionalidad de este modulo se decidio cambiar al encontrar unas librerias capaces de realizar la
          parte que necesitabamos del test, no obstante puede servir en un futuro.
          Todo el codigo que se hizo en un principio se ha dejado comentado para que no consuma recursos para el programa,
          pero puede ser de utilidad para futuras actualizaciones.
    """
    dNormal = scipy.stats.norm(loc=mCrit, scale=dCrit)
    ks_test = scipy.stats.kstest(duraciones, dNormal.cdf )
    print ks_test, 'Normal'

    dGamma = scipy.stats.gamma(alfa, scale=beta)
    ks_test2 = scipy.stats.kstest(duraciones, dGamma.cdf)
    #print dGamma.cdf(39.55024722), 'valor de gammma'
    
    #Calculo de la funcion de valores extremos acumulativa para cada intervalo
    if (a != 0 and b !=0):
        dGev = scipy.stats.gumbel_r(loc=a, scale=1 / b)
        ks_test3 = scipy.stats.kstest(duraciones, dGev.cdf)
        #print dGev.cdf(), 'valor de gumbel'

    #Devuelve el máximo de los máximos de cada columna de diferencias, en el caso de que la de valores
    #extremos no se pueda realizar devuelve no definido
    if (a != 0 and b != 0):
        return ks_test, ks_test2, ks_test3
    elif (a == 0 and b == 0):
        return ks_test, ks_test2


# If the program is run directly, test cases
if __name__ == '__main__': 
    testKS (duraciones=[1,2,3], mCrit=36, dCrit=2.45, alfa=0, beta=0, a=0, b=0, tamanio=0.5)
    testKS (duraciones=[1,2,3], mCrit=0, dCrit=0, alfa=0, beta=0, a=39.58100088, b=0.247050635, tamanio=0.5)
    testKS (duraciones=[1,2,3], mCrit=0, dCrit=0, alfa=44.66385299, beta=0.89778668, a=0, b=0, tamanio=0.5)

 
    

