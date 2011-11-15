#!/usr/bin/python
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

import random
import math

from operator import itemgetter
from scipy.stats import norm
from scipy.stats import gamma
from scipy.stats import gumbel_r
from scipy.stats import kstest

def ordenaCaminos (infoCaminos):
    """
    Funcion de ordenacion de los caminos por el campo
    de tiempo medio de cada camino
    """
    infoCaminos.sort(key=itemgetter(1))
    #print 'Caminos      Duracion media      Varianza        Desviacion Tipica'

    #for n in range(len(infoCaminos)):
     #   s=''
      #  for c in infoCaminos[n][0]:
       #     if s!='':
        #        s+=' -> '
         #       s+=str(c)
          #  else:
           #     s+=str(c)
        #print s,'       ',infoCaminos[n][1],'        ',infoCaminos[n][2],'        ',infoCaminos[n][3]

    return infoCaminos

def calculoValoresGamma (infoCaminos):
    """
    Funcion que asigna los valores a las datos necesarios para
    la realizacion del test de Kolmogorov-Smirnof con la funcion gamma.
    Asignara el numero de caminos dominantes segun Dodin y segun nosotros,
    la media de la poblacion estimada, la sigma de la poblacion estimada
    y los valores de alfa y beta necesarios para la funcion de distribucion gamma.
    Devuelve todos estos valores ya asignados.
    """

    m = 0
    m1 = 0
    sigma = 0
    mCritico = float(infoCaminos[len(infoCaminos)-1][1])
    dCritico = float(infoCaminos[len(infoCaminos)-1][3])
    #Caluculo de los caminos dominantes segun Dodin (m) y segun nosotros (m1). Asi como de Sigma.
    for n in range(len(infoCaminos)):
        if ((mCritico - float(infoCaminos[n][1])) < max(0.05*mCritico, 0.02* dCritico)):
            m += 1
        if ((float(infoCaminos[n][1]) + 0.5*float(infoCaminos[n][3])) >= (mCritico - 0.25* dCritico)):
            m1 +=1
            aux = float(infoCaminos[n][3])
            if sigma == 0:
                sigma = aux
            elif aux < sigma:
                sigma = aux

    #Calculo de la media de la poblacion estimada, de alfa y de beta
    media = mCritico + ((math.pi* math.log(m1))/sigma)
    beta = (sigma*sigma)/media
    alfa = media/beta

    return m, m1, alfa, beta, media, sigma

def calculoMcriticoDcriticoNormal (infoCaminos):
    """
    Funcion que devuelve la media del camino critico
    y la desviacion tipica del mismo
    """

    return float(infoCaminos[len(infoCaminos)-1][1]), float(infoCaminos[len(infoCaminos)-1][3])

def calculoValoresExtremos (media, sigma, m):
    """
    Funcion que nos devuelve los valores necesarios para
    realizar la distribucion de valores extremos
    """
    a = media + sigma * ((2*math.log(m))**0.5 - 0.5 * (math.log(math.log(m)) + math.log(4*math.pi)) / (2* math.log(m))**0.5)
    b = ((2 * math.log(m))**0.5) / sigma

    return a, b

def nIntervalos(duraciones, tamanio=0.5):
    
    #Funcion que devuelve el número de intervalos que tendrá
    #el test de Kolmogorov-Smirnov
    
    #Ordenamos las duraciones de la simulacion
    #duraciones.sort()
    #Obtenemos el tiempo maximo y minimo
    mini,maxi = min(duraciones), max(duraciones)
    x = mini - (mini % tamanio)
    inicio = x + tamanio
    cont = 0
    aux = inicio
    while aux < maxi + tamanio:
        aux = aux + tamanio
        cont += 1

    return cont

def testKS (duraciones, mCrit, dCrit, alfa, beta, a=0, b=0, tamanio=0.5, save=0):
    """
    Funcion que realiza el test de kolmogorv_smirnoff y
    devuelve la bondad de cada distribucion
    """

    #Obtenemos el primer valor del intervalo
    x = min(duraciones) - (min(duraciones) % tamanio)
    inicio = x + tamanio
    #Obtenemos el numero de intervalos
    cont = nIntervalos(duraciones,tamanio)
    #Creacion de una lista con los intervalos de 0.5 en 0.5
    intervalos = [inicio]
    for n in range(cont-1):
        intervalos.append(intervalos[n] + tamanio)

    duraciones.sort()
    #Calculo de las frecuencias
    frecuencia = []
    for n in range(len(intervalos)):
        cont2 = 0
        for x in range(len(duraciones)):
            if float(duraciones[x]) <= float(intervalos[n]):
                cont2 = cont2 + 1
            else:
                continue
        frecuencia.append(float(cont2)/len(duraciones))
    #Calculo de la funcion normal acumulativa para cada intervalo

    normal = []
    dNormal = norm (loc = mCrit, scale = dCrit)
    for n in range(len(intervalos)):
        normal.append(dNormal.cdf(intervalos[n]))
    pvalue = kstest (duraciones, dNormal.cdf )
    #print pvalue

    #Calculo de la diferencia por la izquierda y por la derecha de la funcion normal con respecto a los datos obtenidos de simular
    normalD = diferencias (normal, intervalos, frecuencia)

    #Calculo de la funcion gamma acumulativa para cada intervalo
    gammaV = []
    dGamma = gamma(alfa, scale=beta)
    for n in range(len(intervalos)):
        gammaV.append(dGamma.cdf(intervalos[n]))

    pvalue2 = kstest (duraciones,dGamma.cdf)
    #print pvalue2

    #Calculo de la diferencia por la izquierda y por la derecha de la funcion normal con respecto a los datos obtenidos de simular
    gammaD = diferencias (gammaV, intervalos, frecuencia)

    #Calculo de la funcion de valores extremos para cada intervalo
    if (a != 0 and b !=0):
        gev = []
        dGev = gumbel_r (loc = a, scale = 1/b)
        for n in range(len(intervalos)):
            gev.append(dGev.cdf(intervalos[n]))

        pvalue3 = kstest (duraciones, dGev.cdf)
        #print pvalue3
        
        gevD = diferencias (gev, intervalos, frecuencia)


    #Maximos de las columnas de diferencias y maximo de los máximos
    maxNormal = max(max(normalD[0]), max(normalD[1]))
    maxGamma = max(max(gammaD[0]), max(gammaD[1]))
    if (a != 0 and b != 0):
        maxVE = max(max(gevD[0]), max(gevD[1]))

    #Devuelve el máximo de los máximos de cada columna de diferencias, en el caso de que la de valores
    #extremos no se pueda realizar devuelve no definido
    if (a != 0 and b != 0 and save == 0):
        return maxNormal, maxGamma, maxVE, pvalue, pvalue2, pvalue3
    elif (a == 0 and b == 0 and save == 0):
        return maxNormal, maxGamma, 'No definido', pvalue, pvalue2
    elif (a != 0 and b != 0 and save == 1):
        return intervalos, frecuencia, normal, normalD, gammaV, gammaD, gev, gevD, maxNormal, maxGamma, maxVE, cont, pvalue, pvalue2, pvalue3
    elif (a == 0 and b == 0 and save == 1):
        return intervalos, frecuencia, normal, normalD, gammaV, gammaD, maxNormal, maxGamma, cont, pvalue, pvalue2
  

def valorComparacion(precision, totalIteraciones):
    """
    Funcion que comprueba que los valores obtenidos se
    aproximan a los reales
    """
    aux = ((-math.log(precision/2)/(2*totalIteraciones))**0.5)
    return aux

def diferencias (distribucion, intervalos, frecuencia):
    """
    Devuelve dos vecotres con las diferencias por la
    izquierda y por la derecha con respecto a la funcion de
    distribucion seleccionada y a las frecuencias obtenidas
    de la similuacion
    """
    for n in range(len(intervalos)):
        if (n == 0):
            distribucionD = [[distribucion[0]],[abs(distribucion[0] - frecuencia[0])]]
        else:
            distribucionD[0].append(abs(distribucion[n] - frecuencia [n-1]))
            distribucionD[1].append(abs(distribucion[n] - frecuencia [n]))

    return distribucionD
    
    
    

