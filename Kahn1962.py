#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph

def check_kahn1962(prelations):
    """
    """
    #L ← Empty list that will contain the sorted elements
    #S ← Set of all nodes with no incoming edges
    #while S is non-empty do
    #    remove a node n from S
    #    insert n into L
    #    for each node m with an edge e from n to m do
    #        remove edge e from the graph
    #        if m has no other incoming edges then
    #            insert m into S
    #if graph has edges then
    #    output error message (graph has at least one cycle)
    #else 
    #    output message (proposed topologically sorted order: L)

    visitedElements = [] #Empty list that will contain the visited elements
    noIncomingEdges = graph.beginingActivities(prelations) #Set of all nodes with no incoming edges
    print prelations
    print noIncomingEdges

    while len(noIncomingEdges) > 0: #While noIncomingEdges no empty
        act = noIncomingEdges.pop()
        visitedElements.append(act) #Remove node n from noIncomingEdges and insert n into visitedElements
        print "act = " + act
        print "noIncomingEdges = "
        print noIncomingEdges
        print "visitedElements"
        print visitedElements
        setPrelations = set(prelations[act])
        del prelations [act]
        print prelations
        b = graph.beginingActivities(prelations, setPrelations)
        noIncomingEdges.update(b)
        print 'B:', b #if m has no other incoming edges 
        print "noIncomingEdges1 = "
        print noIncomingEdges
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

    print check_kahn1962(prelations)


