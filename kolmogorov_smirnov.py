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
from scipy.stats import norm
from scipy.stats import gamma
from scipy.stats import gumbel_r
from scipy.stats import kstest

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
        beta = (sigmaMinN*sigmaMinN)/media
        alfa = media/beta
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


def testKS (duraciones, mCrit, dCrit, alfa, beta, a=0, b=0, tamanio=0.5, save=0):
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
    save (opcion por si queremos guardar el resultado del test)
    
    return: p-values (en el caso de que la opcion de guardar no se active)
            intervalos, frecuencias, distribuciones y p-values (en el caso de que se active la opcion de guardado)

    Nota: La funcionalidad de este modulo se decidio cambiar al encontrar unas librerias capaces de realizar la
          parte que necesitabamos del test, no obstante puede servir en un futuro.
          Todo el codigo que se hizo en un principio se ha dejado comentado para que no consuma recursos para el programa,
          pero puede ser de utilidad para futuras actualizaciones.
    """

    #Obtenemos el primer valor del intervalo
    #x = min(duraciones) - (min(duraciones) % tamanio)
    #inicio = x + tamanio

    #Obtenemos el numero de intervalos
    #cont = nIntervalos(duraciones,tamanio)

    #Creacion de una lista con los intervalos en funcion del tamanio
    #intervalos = [inicio]
    #for n in range(cont-1):
        #intervalos.append(intervalos[n] + tamanio)
    
    #Se ordenan las duraciones
    #duraciones.sort()

    #Calculo de las frecuencias
    #frecuencia = []
    #for n in range(len(intervalos)):
        #cont2 = 0
        #for x in range(len(duraciones)):
            #if float(duraciones[x]) <= float(intervalos[n]):
                #cont2 = cont2 + 1
            #else:
                #continue
        #frecuencia.append(float(cont2)/len(duraciones))

    #Calculo de la funcion normal acumulativa para cada intervalo
    #normal = []
    dNormal = norm (loc = mCrit, scale = dCrit)
    
    #for n in range(len(intervalos)):
        #normal.append(dNormal.cdf(intervalos[n]))
    
    pvalue = kstest (duraciones, dNormal.cdf )
    

    #Calculo de la diferencia por la izquierda y por la derecha de la funcion normal con respecto a los datos obtenidos de simular
    #normalD = diferencias (normal, intervalos, frecuencia)

    #Calculo de la funcion gamma acumulativa para cada intervalo
    #gammaV = []
    dGamma = gamma(alfa, scale=beta)
    #for n in range(len(intervalos)):
        #gammaV.append(dGamma.cdf(intervalos[n]))

    pvalue2 = kstest (duraciones,dGamma.cdf)
    

    #Calculo de la diferencia por la izquierda y por la derecha de la funcion normal con respecto a los datos obtenidos de simular
    #gammaD = diferencias (gammaV, intervalos, frecuencia)

    #Calculo de la funcion de valores extremos acumulativa para cada intervalo
    if (a != 0 and b !=0):
        #gev = []
        dGev = gumbel_r (loc = a, scale = 1/b)
        #for n in range(len(intervalos)):
            #gev.append(dGev.cdf(intervalos[n]))

        pvalue3 = kstest (duraciones, dGev.cdf)
        
        
        #gevD = diferencias (gev, intervalos, frecuencia)


    #Maximos de las columnas de diferencias y maximo de los máximos
    #maxNormal = max(max(normalD[0]), max(normalD[1]))
    #maxGamma = max(max(gammaD[0]), max(gammaD[1]))
    #if (a != 0 and b != 0):
        #maxVE = max(max(gevD[0]), max(gevD[1]))

    #Devuelve el máximo de los máximos de cada columna de diferencias, en el caso de que la de valores
    #extremos no se pueda realizar devuelve no definido
    if (a != 0 and b != 0 and save == 0):
        return pvalue, pvalue2, pvalue3
    elif (a == 0 and b == 0 and save == 0):
        return pvalue, pvalue2
    #elif (a != 0 and b != 0 and save == 1):
        #return intervalos, frecuencia, normal, normalD, gammaV, gammaD, gev, gevD, maxNormal, maxGamma, maxVE, cont, pvalue, pvalue2, pvalue3
    #elif (a == 0 and b == 0 and save == 1):
        #return intervalos, frecuencia, normal, normalD, gammaV, gammaD, maxNormal, maxGamma, cont, pvalue, pvalue2
  

"""
Las siguientes dos funciones tambien se decidio prescindir de ellas en un estado ya avanzado del proyecto,
no obstante, al igual que las anteriores se dejaran comentadas para posibles actualizaciones futuras

def valorComparacion(precision, totalIteraciones):

    Funcion que un p-value con la precision definida por el usuario

    precision (valor de ajuste para la comparacion)
    totalIteraciones (numero total de iteraciones que se han realizado)

    return: valor (p-value)

    valor = ((-math.log(precision/2)/(2*totalIteraciones))**0.5)
    return valor

def diferencias (distribucion, intervalos, frecuencia):

    Devuelve un vector con las diferencias por la
    izquierda y por la derecha con respecto a la funcion de
    distribucion seleccionada y a las frecuencias obtenidas
    de la similuacion

    distribucion (tipo de distribucion utilizada)
    intervalos (vector con los intervalos en los que vamos a aplicar las diferecias)
    frecuencia (frecuencia de la simulacion en el intervalo)

    return: distribucionD (vector de diferencias)

    for n in range(len(intervalos)):
        if (n == 0):
            distribucionD = [[distribucion[0]],[abs(distribucion[0] - frecuencia[0])]]
        else:
            distribucionD[0].append(abs(distribucion[n] - frecuencia [n-1]))
            distribucionD[1].append(abs(distribucion[n] - frecuencia [n]))

    return distribucionD

def nIntervalos(duraciones, tamanio=0.5):
    
    Funcion que devuelve el número de intervalos que tendrá
    el test de Kolmogorov-Smirnov

    duraciones (vector de duraciones del proyecto)
    tamanio (tamanio del intervalo deseado)

    return: cont (numero de intervalos que tendra el el test)
   
    #Asigna el maximo y el minimo de las duraciones simuladas del proyecto

    mini,maxi = min(duraciones), max(duraciones)
    #Asignamos el valor de inico de los intervalos y contamos el numero de intervalos necesarios para el test
    x = mini - (mini % tamanio)
    inicio = x + tamanio
    cont = 0
    aux = inicio
    while aux < maxi + tamanio:
        aux = aux + tamanio
        cont += 1

    return cont

"""    
    
    

