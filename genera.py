#!/usr/bin/python
# -*- coding: utf-8 -*-

# Test of python random number generators
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
import math

# Generar n aleatorios de cada distribución

n = 100

# Para Uniforme, Triangular y Beta:

op = 2.0
mode = 5.0
pes = 10.0

# Para la Normal

mean = 5
stdev = 2


def trianglevariate(op, mode, pes):
    """
   Generates a random number in a triangular distribution in [op, pes]
   with mode
   """

    unif = random.random()  # [0,1]

    if unif <= (mode - op) / (pes - op):
        aux = (unif * (pes - op)) * (mode - op)
        triangularDist = op + math.sqrt(aux)
    else:
        aux = ((pes - op) * (pes - mode)) * (1 - unif)
        triangularDist = pes - math.sqrt(aux)

    return triangularDist


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
    print trianglevariate(op, mode, pes)

