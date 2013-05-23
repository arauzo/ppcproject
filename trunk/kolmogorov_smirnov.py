#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import random
import math
import scipy.stats

def calculoValoresGamma(infoCaminos, dist):
    """
    Funcion que asigna los valores a las datos necesarios para
    la realizacion del test de Kolmogorov-Smirnof con la funcion gamma.
    Asignara el numero de caminos dominantes segun Dodin y segun nosotros,
    la media de la poblacion estimada, la sigma de la poblacion estimada
    y los valores de alfa y beta necesarios para la funcion de distribucion gamma.
    
    infoCaminos (vector con la informacion de cada camino)

    return: m (numero de caminos estimados candidatos de ser criticos segun Dodin)
            m1 (numero de caminos estimados candidatos de ser criticos segun el metodo de Lorenzo Salas)
            alfa (valor de alfa para la gamma)
            beta (valor de beta para la gamma)
            media (media estimada con la distribucion gamma)
            sigma (desviacion tipica estimada con la distribucion gamma)
    """
    m = 0
    m1 = 0
    sigma = 0


    # Calculo de la media y la desviacion tipica del camino critico
    mCritico = infoCaminos[-1][1]
    dCritico = infoCaminos[-1][3]

    # Dentro de los criticos de dodin (desviaciones tipicas)
    sigma_longest_path = dCritico
    sigma_max = None
    sigma_min = None
    
    #Calculo de los caminos dominantes segun Dodin (m) y segun nosotros (m1). Asi como de Sigma.
    for n in range(len(infoCaminos)):
        # Considerado critico por Dodin
        if ((mCritico - infoCaminos[n][1]) < max(0.05*mCritico, 0.02* dCritico)):
            m += 1
            path_stddev = infoCaminos[n][3]
            if sigma_max == None or sigma_max < path_stddev:
                sigma_max = path_stddev
            if sigma_min == None or sigma_min > path_stddev:
                sigma_min = path_stddev

        # Considerado critico por Salas
        if ((float(infoCaminos[n][1]) + 0.5*float(infoCaminos[n][3])) >= (mCritico - 0.25* dCritico)):
            m1 +=1
            aux = float(infoCaminos[n][3])
            if sigma == 0:
                sigma = aux
            elif aux < sigma:
                sigma = aux

    #Calculo de la media de la poblacion estimada, de alfa y de beta 
    #media = mCritico + ((math.pi* math.log(m1))/sigma)
    """media = mCritico + ((math.pi* math.log(m))/sigma)
    beta = (sigma*sigma)/media
    alfa = media/beta"""
    
    #para cada distribucion usamos unas regresiones diferentes
    #logaritmoN = 1.0927284342627
    sigmaMinN = -0.9153232086309
    mediaN = 1.1336004782864
    #logaritmo = 2.96581038327203
    sigmaMin = 0.755017047823797
    media = 0.91263355372917
    
    if dist == 'Normal':
        #media = mCritico + ((math.pi* logaritmoN)/sigmaMinN)
        beta = (sigmaMinN*sigmaMinN)/mediaN
        alfa = mediaN/beta
        media = mediaN
    else :
        #media = mCritico + ((math.pi* logaritmo)/sigmaMin)
        beta = (sigmaMin*sigmaMin)/media
        alfa = media/beta
        
    return m, m1, alfa, beta, media, sigma, sigma_longest_path, sigma_max, sigma_min

def calculoValoresExtremos (media, sigma, m):
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

def calculoMcriticoDcriticoEV (a, b):
    """
    Funcion que devuelve la media y la desviacion tipica
    de la distribucion de valores extremos

    a, b (parametros necesarios para el calculo de la media y la desviacion tipica de la funcion de VE)

    return: media (media estimada de la funcion de valores extremos)
            sigma (desviacion tipica estimada de la funcion de valores extremos)
    """

    media = a + 0.57722/b
    sigma = math.sqrt((math.pi**2)/(6*(b**2)))

    return media, sigma


def testKS (duraciones, mCrit, dCrit, alfa, beta, a=0, b=0, tamanio=0.5):
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
    pvalue = scipy.stats.kstest(duraciones, dNormal.cdf )
    print pvalue, 'Normal'

    dGamma = scipy.stats.gamma(alfa, scale=beta)
    pvalue2 = scipy.stats.kstest(duraciones, dGamma.cdf)
    #print dGamma.cdf(39.55024722), 'valor de gammma'
    
    #Calculo de la funcion de valores extremos acumulativa para cada intervalo
    if (a != 0 and b !=0):
        dGev = scipy.stats.gumbel_r(loc=a, scale=1 / b)
        pvalue3 = scipy.stats.kstest(duraciones, dGev.cdf)
        #print dGev.cdf(), 'valor de gumbel'

    #Devuelve el máximo de los máximos de cada columna de diferencias, en el caso de que la de valores
    #extremos no se pueda realizar devuelve no definido
    if (a != 0 and b != 0):
        return pvalue, pvalue2, pvalue3
    elif (a == 0 and b == 0):
        return pvalue, pvalue2


# If the program is run directly
#if __name__ == '__main__': 

    #testKS (duraciones=[1,2,3], mCrit=36, dCrit=2.45, alfa=0, beta=0, a=0, b=0, tamanio=0.5)
    #testKS (duraciones=[1,2,3], mCrit=0, dCrit=0, alfa=0, beta=0, a=39.58100088, b=0.247050635, tamanio=0.5)
    #testKS (duraciones=[1,2,3], mCrit=0, dCrit=0, alfa=44.66385299, beta=0.89778668, a=0, b=0, tamanio=0.5)

 
    

