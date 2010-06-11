import os
import sys
import algoritmoConjuntos
import algoritmoLorenzo
import yuvalCohen
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

itime=os.times()
for i in range(1000):
    g=algoritmoConjuntos.algoritmoN(prelaciones)
ftime=os.times()
utime = ftime[0] - itime[0]
print "Algoritmo Conjuntos"
print "utime %.4f"% (utime)
print "numero de nodos: ",g.numNodes()
print "numero de arcos: ",g.numArcs()
print g.successors
print

itime=os.times()
for i in range(1000):
    g=yuvalCohen.yuvalCohen(prelaciones)
ftime=os.times()
utime = ftime[0] - itime[0]
print "Yuval Cohen"
print "utime %.4f"% (utime)
print "numero de nodos: ",g.numNodes()
print "numero de arcos: ",g.numArcs()
print g.successors
print

itime=os.times()
for i in range(1000):
    g=algoritmoLorenzo.al(prelaciones)
ftime=os.times()
utime = ftime[0] - itime[0]
print "Algoritmo Lorenzo"
print "utime %.4f"% (utime)
print "numero de nodos: ",g.numNodes()
print "numero de arcos: ",g.numArcs()
print g.successors
print

