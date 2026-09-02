#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filling data for simulation
"""

import math
import random


class InvalidK(Exception):
    pass


def _to_model_text(value):
    if value == '':
        return ''
    return str(value)


def datosBetaMedia(mean, k):
    """
    Returns the parameters of the beta basing only on the average
    and proportionality value of the typical deviation

    mean (average duration of activity)
    k (proportionality constant of the typical deviation)
    Precondition: 0 <= k <= 1

    return: (average, typical deviation, shape factor a, shape factor b)
    """
    stdev = (k * mean)

    low_mode_limit = mean * (1 - k)
    high_mode_limit = min(mean * (1 + k), (3 * mean / 2.0) * (1 - k))
    mode = random.uniform(low_mode_limit, high_mode_limit)
    op = ((3 * mean * (1 - k)) - (2 * mode))
    pes = (op + (6 * k * mean))

    return (op, mode, pes, stdev)


def datosTriangularMedia(mean, k):
    """
    Generates a random number in a triangular distribution in [op,pes]
    with mean
    """
    a = mean * (1 - (k * math.sqrt(2)))
    b = mean * (1 + (k * math.sqrt(2)))
    c = (3 * mean + math.sqrt(pow((3 * mean), 2) - 24 * (pow(mean, 2)) * (0.5 - pow(k, 2)))) / 2
    d = (3 * mean - math.sqrt(pow((3 * mean), 2) - 24 * (pow(mean, 2)) * (0.5 - pow(k, 2)))) / 2

    dif1 = d - a
    dif2 = b - c

    stdev = (k * mean)

    if a < d < c < b:
        r = random.uniform(0, dif1 + dif2)
        if r < dif1:
            mode = a + r
        else:
            mode = c + r - dif1
    elif d < a < c < b:
        mode = random.uniform(c, b)
    elif a < d < b < c:
        mode = random.uniform(a, d)
    elif d < a < b < c:
        raise InvalidK()
    else:
        mode = 0

    op = (
        (3 * mean - mode)
        - math.sqrt(
            pow((3 * mean - mode), 2)
            - 4 * (-3 * mean * mode + pow(mode, 2) + 6 * pow(mean, 2) * (0.5 - pow(k, 2)))
        )
    ) / 2
    pes = 3 * mean - op - mode

    return (op, mode, pes, stdev)


def datosUniformeMedia(mean, k):
    """
    Data for a Uniform distribution having only the mean.
    """
    stdev = (k * mean)
    op = mean * (1 - (k * math.sqrt(3)))
    pes = mean * (1 + (k * math.sqrt(3)))
    mode = (op + pes) / 2

    return (op, pes, stdev, mode)


def actualizarInterfaz(modelo, k, dist, actividad):
    """
    Update the interface according to the selected distribution.
    """
    for m in range(len(actividad)):
        actividad[m][8] = dist
        modelo[m][8] = _to_model_text(dist)

    if dist == 'Uniform':
        for m in range(len(actividad)):
            actividad[m][3], actividad[m][5], actividad[m][7], actividad[m][4] = datosUniformeMedia(
                actividad[m][6], k
            )

            modelo[m][3] = _to_model_text(actividad[m][3])
            modelo[m][5] = _to_model_text(actividad[m][5])
            modelo[m][7] = _to_model_text(actividad[m][7])
            modelo[m][4] = _to_model_text(actividad[m][4])

            actividad[m][4] = ''
            modelo[m][4] = ''

    elif dist == 'Beta':
        for m in range(len(actividad)):
            actividad[m][3], actividad[m][4], actividad[m][5], actividad[m][7] = datosBetaMedia(
                actividad[m][6], k
            )

            modelo[m][3] = _to_model_text(actividad[m][3])
            modelo[m][4] = _to_model_text(actividad[m][4])
            modelo[m][5] = _to_model_text(actividad[m][5])
            modelo[m][7] = _to_model_text(actividad[m][7])

    elif dist == 'Triangular':
        for m in range(len(actividad)):
            actividad[m][3], actividad[m][4], actividad[m][5], actividad[m][7] = datosTriangularMedia(
                actividad[m][6], k
            )

            modelo[m][3] = _to_model_text(actividad[m][3])
            modelo[m][4] = _to_model_text(actividad[m][4])
            modelo[m][5] = _to_model_text(actividad[m][5])
            modelo[m][7] = _to_model_text(actividad[m][7])

    elif dist == 'Normal':
        for m in range(len(actividad)):
            actividad[m][7] = actividad[m][6] * k
            modelo[m][7] = _to_model_text(actividad[m][7])

        for m in range(len(actividad)):
            if actividad[m][3] != '' or actividad[m][4] != '' or actividad[m][5] != '':
                actividad[m][3] = ''
                actividad[m][4] = ''
                actividad[m][5] = ''
                modelo[m][3] = ''
                modelo[m][4] = ''
                modelo[m][5] = ''
    else:
        raise Exception('Distribution not expected')

    return modelo, actividad


def actualizarActividadesFichero(k, dist, actividad):
    """
    Updates the activities according to the distribution to be used.
    """
    for m in range(len(actividad)):
        actividad[m][8] = dist

    if dist == 'Uniform':
        for m in range(len(actividad)):
            actividad[m][3], actividad[m][5], actividad[m][7], actividad[m][4] = datosUniformeMedia(
                actividad[m][6], k
            )
    elif dist == 'Beta':
        for m in range(len(actividad)):
            actividad[m][3], actividad[m][4], actividad[m][5], actividad[m][7] = datosBetaMedia(
                actividad[m][6], k
            )
    elif dist == 'Triangular':
        for m in range(len(actividad)):
            actividad[m][3], actividad[m][4], actividad[m][5], actividad[m][7] = datosTriangularMedia(
                actividad[m][6], k
            )
    elif dist == 'Normal':
        for m in range(len(actividad)):
            actividad[m][7] = actividad[m][6] * k
    else:
        raise Exception('Distribution not expected')

    return actividad
