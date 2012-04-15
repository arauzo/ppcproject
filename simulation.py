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

#import scipy.stats

def calcularFrecuencias(duraciones, dMax, dMin, itTotales, N):
    """
     Cálculo de las F.Absolutas y F.Relativas 

       dMax (duración máxima)
       dMin (duración mímima)
       itTotales (iteraciones totales)
       N (número de intervalos)

     Valor de retorno: fa (frecuencias absolutas)
                       fr (frecuencias relativas)
    """
    fr = []

    # Se inicializa el vector de F.Absolutas
    fa = [0] * N

    # Se calculan las F.Absolutas
    for d in duraciones:
        x = posicion(d, dMax, dMin, N)
        fa[x] += 1

    # Se calculan las F.Relativas
    for a in fa:
        r = '%2.2f' % (float(a) / itTotales)
        fr.append(r)

    return (fa, fr)


def posicion(d, dMax, dMin, N):
    """
     Cálculo de la posición de una duración dentro del 
              vector de F.Absolutas

       d (duración)
       dMax (duración máxima)
       dMin (duración mí­nima)
       N (número de intervalos)

     Valor de retorno: x (posición)
    """
    x = int(((d - dMin) / (dMax - dMin)) * N)
    return x

def nIntervalos (dMax, dMin, N, opcion):
    """
    Cálculo del número de intervalos
    en función de la opción elegida por
    el usuario

    dMax (duración máxima)
    dMin (duración mínima)
    N (número de intervalos o tamaño del intervalo)
    opción (opción seleccionada)
    """

    #print 'Maximo y minimo: ', dMax, dMin, '\n'
    if opcion == 'Number of intervals':
        return int(N)
    elif opcion == 'Size range':
        mini = dMin - (dMin % N)
        cont = mini
        aux = 0
        while cont < dMax:
            cont = cont + N
            aux += 1 
        return int(aux)
 
def duracion(x, dMax, dMin, N):
    """
     Cálculo de la duración correspondiente a una posición 
              (inversa de la Función anterior)

       x (posición)
       dMax (duración máxima)
       dMin (duración mí­nima)
       N (número de intervalos)

     Valor de retorno: d (duración)
    """
    d = (x * (dMax - dMin)) / N + dMin
    return d


def datosSimulacion2csv(duraciones, iteraciones, media, dTipica, modeloCriticidad):
    """
     Prepara los datos de la simulación para ser mostrados
              en formato CSV

       duraciones (lista con las duraciones de la simulación)
       iteraciones (número de iteraciones totales)
       media (duración media)
       dTipica (desviación tí­pica)
       modeloCriticidad (lista de caminos e í­ndice de criticidad)

     Valor de retorno: s (texto a mostrar en formato CSV) 
    """
    s = ''
    s += _('SIMULATION DATA')
    s += '\n'
    s += '\n'
    s += _('N, CRITICALITY INT., PATH')
    s += '\n'
    for n in range(len(modeloCriticidad)):
        s += modeloCriticidad[n][0] + ',' + modeloCriticidad[n][1] + ',' + '"'\
             + modeloCriticidad[n][2] + '"'
        s += '\n'
    s += '\n'
    s += '\n'
    s += _('AVERAGE, TYPICAL DEV.')
    s += '\n'
    s += media + ',' + dTipica
    s += '\n'
    s += '\n'
    s += _('TOTAL SIMULATIONS')
    s += '\n'
    s += iteraciones
    s += '\n'
    s += '\n'
    s += _('DURATIONS')
    s += '\n'
    for d in duraciones:
        s += str(d)
        s += '\n'

    return s


def generaAleatoriosTriangular(op, mode, pes):
    """
    Generates a random number in a triangular distribution in [op, pes]
    with mode

    Preconditions: pes != op
    """
    unif = random.random()  # [0,1]

    if unif <= float(mode - op) / (pes - op):
        aux = (unif * (pes - op)) * (mode - op)
        triang = op + math.sqrt(aux)
    else:
        aux = ((pes - op) * (pes - mode)) * (1 - unif)
        triang = pes - math.sqrt(aux)

    return triang


def simulacion(n, activities):
    """
    Simulate duration of every activity according to its distribution type

     n: number of simulation rows to generate
     activities: list of activities each of them with activity structure
                
     return: [ [simulated_duration_a, simulated_duration_b, ... ], ... ] (list with n rows)
    """
    TOLERANCE = 0.001
    simulacion = []

    for i in range(n):
        sim = []
        for pos, name, follow, opt, mode, pes, mean, std_dev, distribution, start in activities:

            if distribution == 'Uniform':
                if opt == pes:
                    valor = opt
                else:
                    valor = random.uniform(opt, pes)

            elif distribution == 'Beta':
                if opt == pes:
                    valor = opt
#                elif opt == mode:
#                    valor = 10000 # XXX Es necesario poner algo coherente aqui si se cambia a la Beta tradicional
#                elif mode == pes:
#                    valor = 10000 # Idem
                else:
                    mean = (opt + 4 * mode + pes) / 6.0

# incorrecto: stdev = (pes - opt) * math.sqrt(( 5.0 + 8 * (mode-opt) * (pes-mode) / (pes-opt)**2 ) / (36*7))
# stdev innecesaria

#                    stdev = (pes - opt) / 6.0 # Varianza tradicional no valida en extremos
#                    shape_a = (float(mean - opt) / (pes - opt)) * (((mean - opt) * (pes - mean)) / stdev ** 2 - 1)
#                    shape_b = (float(pes - mean) / (mean - opt)) * shape_a
                    shape_a = 1 + 4.0 * (mode - opt) / (pes - opt)
                    shape_b = 1 + 4.0 * (pes - mode) / (pes - opt)
                    valor = random.betavariate(shape_a, shape_b) * (pes - opt) + opt
                    #valor = scipy.stats.beta.rvs(shape_a, shape_b) * (pes - opt) + opt
                    #print "stdev", stdev
                    #print "Scipy VAR:", math.sqrt(scipy.stats.beta.var(shape_a, shape_b, loc=opt, scale=(pes-opt)))


            elif distribution == 'Triangular':
                if opt == pes:
                    valor = opt
                else:
                    valor = generaAleatoriosTriangular(float(opt), float(mode), float(pes))
                                    
            elif distribution == 'Normal':
                if std_dev < TOLERANCE: 
                    valor = mean
                else:
                    valor = random.gauss(mean, std_dev)
            
            else:
                dialogoError(_('S Unknown distribution')) 
                return
                    
            sim.append(float(valor))
            
        simulacion.append(sim)
    
    return simulacion
    

# --- Start running as a program
if __name__ == '__main__':

    # Test of python random number generators
    # ---------------------------------------

    # Generar n aleatorios de cada distribución
    n = 100

    # Para Uniforme, Triangular y Beta:
    op = 2.0
    mode = 5.0
    pes = 10.0

    # Para la Normal
    mean = 5
    stdev = 2

    print '\n *** Uniform(', op, pes, ')'
    for i in range(n):
        print random.uniform(op, pes)

    print '\n *** Beta(', op, mode, pes, ')'
    mean = (op + 4 * mode + pes) / 6.0
    stdev = (pes - op) / 6.0
    shape_a = ((mean - op) / (pes - op)) * (((mean - op) * (pes - mean))
             / stdev ** 2 - 1)
    shape_b = ((pes - mean) / (mean - op)) * shape_a

    print 'Mean=', mean, 'Stdev=', stdev
    print 'shape_a=', shape_a, 'shape_b=', shape_b
    for i in range(n):
        print random.betavariate(shape_a, shape_b) * (pes - op) + op

    print '\n *** Normal(', mean, stdev, ')'
    for i in range(n):
        print random.gauss(mean, stdev)

    print '\n *** Triangle(', op, mode, pes, ')'
    for i in range(n):
        print generaAleatoriosTriangular(op, mode, pes)


