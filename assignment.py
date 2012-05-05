#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filling data for simulation
"""
import random
import math

def datosBetaMedia(mean, k):
    """
    Returns the parameters of the beta basing only on the average
    and proportionality value of the typical deviation

    mean (average duration of activity)
    k (proportionality constant of the typical deviation)

    return: (average, typical deviation, shape factor a, shape factor b)
    """
    stdev = (k*mean) 
    mode = random.uniform(mean*(1-k),mean*(1+k))
    op = ((3*mean*(1-k))-(2*mode))
    pes = (op+(6*k*mean))

    return (op, mode, pes, stdev)

def datosTriangularMedia(mean,k):
    """
    Generates a random number in a triangular distribution in [op,pes]
    with mean
    """
    stdev = (k*mean)
    mode = random.uniform(mean*(1-(k*math.sqrt(2))),mean*(1+(k*math.sqrt(2))))
    op = ((3*mean-mode)-math.sqrt(pow((3*mean-mode),2)-4*(-3*mean*mode+pow(mode,2)+6*pow(mean,2)*(0.5-pow(0.2,2)))))/2
    pes = 3*mean-op-mode

    return (op, mode, pes, stdev)

def datosUniformeMedia(mean,k):
    """
    Data for a Uniform distribution having only the mean.
    """
    stdev = (k*mean)
    op = mean * (1-(k* math.sqrt(3)))
    pes = mean * (1+(k* math.sqrt(3)))
    mode = (op + pes) / 2

    return (op, pes, stdev, mode)

def actualizarInterfaz (modelo, k, dist,actividad):
    """
    A function that updates the interface of the program according to the distribution we want to be used.

    modelo ( chart of the graphical interface in which each activity data is shown)
    k ( proportionality value of the typical deviation)
    dist ( distribution used to ascribe missing parameters)
    actividad (vector with activity data)

    return: modelo (updated chart of the interface)
            actividad (updated vector of activities)
    """
    for m in range(len(actividad)):
        actividad [m][8] = dist
        modelo [m][8] = str(dist)
    
    # The type of distribution is checked and values are ascribed
    if dist == 'Uniform':
        for m in range(len(actividad)):                
            actividad [m][3], actividad[m][5],actividad[m][7], actividad [m][4] = datosUniformeMedia(actividad[m][6], k)
            modelo [m][3], modelo[m][5],modelo[m][7], modelo[m][4] = actividad [m][3], actividad[m][5], actividad[m][7], actividad[m][4]
    elif dist == 'Beta':
        for m in range(len(actividad)):
            actividad [m][3], actividad [m][4], actividad[m][5], actividad[m][7] = datosBetaMedia(actividad[m] [6], k)
            modelo [m][3], modelo[m][4],modelo[m][5],modelo[m][7] = actividad [m][3], actividad[m][4], actividad[m][5], actividad[m][7]
    elif dist == 'Triangular':
        for m in range(len(actividad)):
            actividad[m][3], actividad[m][4], actividad[m][5], actividad[m][7] = datosTriangularMedia(actividad[m][6], k)
            modelo [m][3], modelo[m][4],modelo[m][5],modelo[m][7] = actividad [m][3], actividad[m][4], actividad[m][5], actividad[m][7]
    elif dist == 'Normal':
        for m in range(len(actividad)):
            actividad[m][7] = actividad[m][6] * k # Mean * k
            modelo[m][7] = actividad[m][7]
        if (actividad[m][3] != '' or actividad[m][4] != '' or actividad[m][5] !=''):
            for m in range(len(actividad)):
                actividad[m][3] = actividad[m][4] = actividad[m][5] = ''
                modelo[m][3] = modelo[m][4] = modelo[m][5] = ''
    else:
        raise Exception('Distribution not expected')

    return modelo, actividad

def actualizarActividadesFichero(k, dist, actividad):
    """
    Updates the activities according to the distribution to be used.

    k ( proportionality value of the typical deviation)
    dist ( distribution used to ascribe missing parameters)
    actividad (vector with activity data)

    return: actividad (updated vector of activities)
    """
    for m in range(len(actividad)):
        actividad [m][8] = dist
    
    # The type of distribution is checked and values are ascribed
    if dist == 'Uniform':
        for m in range(len(actividad)):                
            actividad [m][3], actividad[m][5],actividad[m][7], actividad [m][4] = datosUniformeMedia(actividad[m][6], k)
    elif dist == 'Beta':
        for m in range(len(actividad)):
            actividad [m][3], actividad [m][4], actividad[m][5], actividad[m][7] = datosBetaMedia(actividad[m] [6], k)
    elif dist == 'Triangular':
        for m in range(len(actividad)):
            actividad[m][3], actividad[m][4], actividad[m][5], actividad[m][7] = datosTriangularMedia(actividad[m][6], k)
    elif dist == 'Normal':
        for m in range(len(actividad)):
            actividad[m][7] = actividad[m][6] * k # Mean * k
    else:
        raise Exception('Distribution not expected')

    return actividad
        
        
