import os
import sys
import algoritmoConjuntos
import algoritmoLorenzo
import yuvalCohen
import openProject
filename="j901_1.sm"
data=openProject.openProject(filename)
successors={}
for i in data:
    successors[i[1]]=i[2]

prelaciones1 = openProject.reversedGraph(successors)
prelaciones = {
    'B': [], 
    'A': [], 
    'D': ['B'], 
    'C': [], 
    'F': ['C'], 
    'E': ['D'], 
    'H': ['B'], 
    'G': ['F'], 
    'J': ['F'], 
    'I': ['A'], 
    'L': ['C', 'E'], 
    'K': ['I'], 
    'N': ['B'], 
    'M': ['H'], 
    'P': ['D'], 
    'O': ['E'], 
    'R': ['F'], 
    'Q': ['E'], 
    'S': ['O'], 
    'T': ['J', 'N', 'P'], 
    'U': ['I'], 
    'V': ['Q'], 
    'W': ['K'],
    'X': ['L', 'M', 'R'], 
    'Y': ['J', 'P', 'O'], 
    'Z': ['Y', 'U', 'G'], 
    'AB': ['H'], 
    'AC': ['W', 'U', 'P'],
    'AD': ['X', 'Z', 'AB'],
    'AE': ['S', 'T', 'V']
    }
print "Sucesores"
print successors
print "Prelaciones"
print prelaciones1
itime=os.times()
for i in range(1000):
    g=algoritmoConjuntos.algoritmoN(prelaciones1)
ftime=os.times()
utime = ftime[0] - itime[0]
print "Algoritmo Conjuntos"
print "utime %.4f"% (utime)
print "numero de nodos: ",g.numNodes()
print "numero de arcos: ",g.numArcs()
print "numero de arcos reales: ",g.numArcsReales()
print "numero de arcos ficticios: ",g.numArcsFicticios()
print g.successors
print

itime=os.times()
for i in range(1000):
    g=yuvalCohen.yuvalCohen(prelaciones1)
ftime=os.times()
utime = ftime[0] - itime[0]
print "Yuval Cohen"
print "utime %.4f"% (utime)
print "numero de nodos: ",g.numNodes()
print "numero de arcos: ",g.numArcs()
print "numero de arcos reales: ",g.numArcsReales()
print "numero de arcos ficticios: ",g.numArcsFicticios()
print g.successors
print

itime=os.times()
for i in range(1000):
    g=algoritmoLorenzo.al(prelaciones1)
ftime=os.times()
utime = ftime[0] - itime[0]
print "Algoritmo Lorenzo"
print "utime %.4f"% (utime)
print "numero de nodos: ",g.numNodes()
print "numero de arcos: ",g.numArcs()
print "numero de arcos reales: ",g.numArcsReales()
print "numero de arcos ficticios: ",g.numArcsFicticios()
print g.successors
print

