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

    visited_elements = [] #Empty list that will contain the visited elements
    no_incoming_edges = graph.beginingActivities(prelations) #Set of all nodes with no incoming edges
    print "Datos de Entrada\n", prelations, "\n\n"
    iteracion=1
    while len(no_incoming_edges) > 0: #While no_incoming_edges no empty
        act = no_incoming_edges.pop()
        visited_elements.append(act) #Remove node n from no_incoming_edges and insert n into visited_elements
        print "Iteracion ", iteracion
        iteracion+=1
        print "Prelations: ", prelations
        print "Activity: ", act
        print "noIncomingEdges: ", no_incoming_edges
        print "visitedElements: ", visited_elements, "\n"
        set_prelations = set(prelations[act]) #Get the new set prelations
        del prelations[act] #Delete prelations activity
        no_incoming_edges.update(graph.beginingActivities(prelations, set_prelations)) #Update no_incoming_edges with new begining activities
    if prelations: #if graph has edges
        print "ERROR" #graph has at least one cycle
    else: #graph has no cycles
        print "OK"
        
# --- Start running as a program
if __name__ == '__main__':
    prelations = {
        'a' : ['b','c'],
        'b' : ['d'],
        'c' : ['e'],
        'd' : ['e'],
        'e' : [],
    }
    
    simple_cycle = {
        'a' : ['b','c'],
        'b' : ['c','d'],
        'c' : ['e','b'],
        'd' : ['e'],
        'e' : [],
    }
    
    cycle = {
        'a' : ['b'],
        'b' : ['c','d'],
        'c' : ['e'],
        'd' : ['e'],
        'e' : ['f','h'],
        'f' : ['g'],
        'g' : ['h','i'],
        'h' : ['f','i'],
        'i' : [],
    }
    
    two_cycles = {
        'a' : ['b','c'],
        'b' : ['c','d'],
        'c' : ['e'],
        'd' : ['e'],
        'e' : ['d','c'],
    }
    
#    graph_list = [prelations, simple_cycle, two_cycles]
    
#    for graph in graph_list:
    print check_kahn1962(prelations)


