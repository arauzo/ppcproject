#!/usr/bin/python
# -*- coding: utf-8 -*-

# Functions for simulation of project duration
# -----------------------------------------------------------------------
# PPC-PROJECT
#   Multiplatform software tool for education and research in
#   project management
#
# Copyright 2007-8 Universidad de Córdoba
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

# Internationalization

import gettext
APP = 'PPC-Project'  # Program name
DIR = 'po'  # Directory containing translations, usually /usr/share/locale
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)


def calcularFrecuencias(duraciones, dMax, dMin, itTotales, N):
    """
     Cálculo de las F.Absolutas y F.Relativas 

     Parámetros: dMax (duración máxima)
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

     Parámetros: d (duración)
                 dMax (duración máxima)
                 dMin (duración mí­nima)
                 N (número de intervalos)

     Valor de retorno: x (posición)
    """

    x = int(((d - dMin) / (dMax - dMin)) * N)
    return x


def duracion(x, dMax, dMin, N):
    """
     Cálculo de la duración correspondiente a una posición 
              (inversa de la Función anterior)

     Parámetros: x (posición)
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

     Parámetros: duraciones (lista con las duraciones de la simulación)
                 iteraciones (número de iteraciones totales)
                 media (duración media)
                 dTipica (desviación tí­pica)
                 modeloCriticidad (lista de caminos e í­ndice de criticidad)

     Valor de retorno: s (texto a mostrar en formato CSV) 
    """

    s = ''
    s += gettext.gettext('SIMULATION DATA')
    s += '\n'
    s += '\n'
    s += gettext.gettext('N, I.CRITICIDAD, PATH')
    s += '\n'
    for n in range(len(modeloCriticidad)):
        s += modeloCriticidad[n][0] + ',' + modeloCriticidad[n][1] + ',' + '"'\
             + modeloCriticidad[n][2] + '"'
        s += '\n'
    s += '\n'
    s += '\n'
    s += gettext.gettext('AVERAGE, TYPICAL DEV.')
    s += '\n'
    s += media + ',' + dTipica
    s += '\n'
    s += '\n'
    s += gettext.gettext('TOTAL SIMULATIONS')
    s += '\n'
    s += iteraciones
    s += '\n'
    s += '\n'
    s += gettext.gettext('DURATIONS')
    s += '\n'
    for d in duraciones:
        s += str(d)
        s += '\n'

    return s


def datosBeta(op, mode, pes):
    """
    Returns the parameters of a general Beta random variate from those of
    PERT method

    op (optimistic)
    mode (most likely)
    pes (pesimist)

    Returned value: (mean, std deviation, shape factor a, shape factor b)
    """

    mean = (op + 4 * mode + pes) / 6.0
    stdev = (pes - op) / 6.0
    shape_a = ((mean - op) / (pes - op)) * (((mean - op) * (pes - mean)) / stdev ** 2 - 1)
    shape_b = ((pes - mean) / (mean - op)) * shape_a

    return (mean, stdev, shape_a, shape_b)


def generaAleatoriosUniforme(op, pes):
    """
    Generates a random number in a Uniform distribution in [op, pes]
    """

    unif = random.uniform(op, pes)
    return unif


def generaAleatoriosBeta(op, pes, shape_a, shape_b):
    """
    Generates a random number in a Beta distribution in [op, pes]
    """

    beta = random.betavariate(shape_a, shape_b) * (pes - op) + op
    return beta


def generaAleatoriosTriangular(op, mode, pes):
    """
    Generates a random number in a triangular distribution in [op, pes]
    with mode
    """

    unif = random.random()  # [0,1]

    if unif <= (mode - op) / (pes - op):
        aux = (unif * (pes - op)) * (mode - op)
        triang = op + math.sqrt(aux)
    else:
        aux = ((pes - op) * (pes - mode)) * (1 - unif)
        triang = pes - math.sqrt(aux)

    return triang


def generaAleatoriosNormal(mean, stdev):
    """
    Generates a number from a Normal random variate with mean and stdev
    """
    
    norm = random.gauss(mean, stdev)
    return norm


