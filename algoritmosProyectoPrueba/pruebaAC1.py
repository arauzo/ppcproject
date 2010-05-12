import os
import sys
import algoritmoConjuntos
import yuvalCohen
import time
prelaciones = {
    'A' : [],
    'B' : [],
    'C' : ['A','B'],
    'D' : ['A'],
    'E' : ['B'],
    'F' : ['A','B'],
    'G' : ['C'],
    'H' : ['D','E'],
    'I' : ['D','E','F'],
    'J' : ['D','E','F'],
    'K' : ['D','F','L'],
    'L' : ['A'],
}
itiempo=time.time()
g=algoritmoConjuntos.algoritmoN(prelaciones)
ftiempo=time.time()
ttiempo=ftiempo-itiempo
print ttiempo

itiempo=time.time()
g=yuvalCohen.yuvalCohen(prelaciones)
ftiempo=time.time()
ttiempo=ftiempo-itiempo
print ttiempo
g
