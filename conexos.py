#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph

def check_conexos(prelations):
    """
    """
    visitedElements = [] #Empty list that will contain the visited elements
    noIncomingEdges = graph.beginingActivities(prelations) #Set of all nodes with no incoming edges
    print prelations
    print noIncomingEdges

    while len(noIncomingEdges) > 0: #While noIncomingEdges no empty
        act = noIncomingEdges.pop()
        visitedElements.append(act) #Remove node n from noIncomingEdges and insert n into visitedElements
        
        setPrelations = set(prelations[act])
        del prelations [act]
        noIncomingEdges.update(setPrelations)
    if prelations: #if graph has edges
        print "error" #graph has at least one cycle
    else:
        print "OK"
        
# --- Start running as a program
if __name__ == '__main__':
    prelations = {
        'a' : ['b','c'],
        'b' : ['e'],
        'c' : ['e'],
        'd' : ['f'],
        'e' : ['d','f'],
        'f' : [],
    }

    print check_conexos(prelations)


