#!/usr/bin/python
# -*- coding: utf-8 -*-

# Zaderenko related functions
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


def mZad(mActividad, actividadesGrafo, nodos, control, duracionSim):
    """
     Creación de la matriz de Zaderenko 

     Parámetros: actividadesGrafo (etiquetas actividades, nodo inicio y fí­n)
                 nodos (lista de nodos)
                 control (0: llamada desde Simulación
                          1: llamada desde Zaderenko u Holguras)
                 duracionSim (duración de la simulación)

     Valor de retorno: mZad (matriz de Zaderenko)
     XXX Supone que el grafo esta numerado empezando en 1
    """
    # Se inicializa la matriz
    fila = [''] * len(nodos)
    mZad = [list(fila) for i in range(len(nodos))]

    actividades = []
    for n in range(len(mActividad)):
        actividades.append(mActividad[n][1])

    # Se añaden las duraciones en la posición correspondiente
#    print 'actividadesGrafo', actividadesGrafo
#    print 'actividades', actividades
    for nodes, activity in actividadesGrafo.items():
        i, j = nodes
        if activity[1]: # Dummy?
            mZad[j-1][i-1] = 0
        else:
            if control == 1:  # Si es llamada desde Zaderenko
                for m in range(len(mActividad)):
                    if activity[0] == mActividad[m][1]:
                        mZad[j-1][i-1] = mActividad[m][6]
            else:
                # Si es llamada desde Simulación
                for m in range(len(mActividad)):
                    if activity[0] == mActividad[m][1]:
                        mZad[j-1][i-1] = duracionSim[m]

    # print mZad
    return mZad


def early(nodos, mZad):
    """
     Cálculo de los tiempos early de cada nodo 

     Parámetros: nodos (lista de nodos)
                 mZad (matriz de Zaderenko)

     Valor de retorno: early (lista con los tiempos early)
    """
    early = [0.0] * len(nodos)

    # Se calculan los tiempos early y se van introduciendo a la lista
    for n in range(len(nodos)):
        mayor = 0.0
        for m in range(len(nodos)):
            if m < n and mZad[n][m] != '':
                aux = float(mZad[n][m]) + early[m]
                if aux > mayor:
                    mayor = aux
                aux = 0
        early[n] = mayor

    return early


def last(nodos, early, mZad):
    """
     Cálculo de los tiempos last de cada nodo 

     Parámetros: nodos (lista de nodos)
                 early (lista con los tiempos early)
                 mZad (matriz de Zaderenko)

     Valor de retorno: last (lista con los tiempos last)
    """
    # Se cambian filas por columnas en mZad para usarla en el calculo de los tiempos last
    for n in range(len(nodos)):
        for m in range(len(nodos)):
            if mZad[n][m] != '':
                mZad[n][m] = ''
            else:
                mZad[n][m] = mZad[m][n]

    # Se crea una la lista de tiempos last y se inicializa a 0
    last = [0] * len(nodos)

    # Se calculan los tiempos last y se van introduciendo a la lista
    l = len(nodos) - 1
    aux = early[l]
    last[l] = early[l]
    for m in range(len(nodos)):
        menor = early[l]
        for n in range(len(nodos)):
            if l - m < n and mZad[l - m][n] != '':
                aux = last[n] - float(mZad[l - m][n])
                if aux < menor:
                    menor = aux
                aux = 0
        last[l - m] = menor

    return last


