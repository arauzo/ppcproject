#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph

def check_cycles(prelations):
    """
    Algorithm based on Kahn 1962 to check if dict has cycles
    """
    #L ← Empty list that will contain the sorted elements
    #S ← Set of all nodes with no incoming edges
    #while S is non-empty do
    #    remove a node n from S
    #    insert n into L
    #    for each node m with an edge e from n to m do
    #        remove edge e from dict
    #        if m has no other incoming edges then
    #            insert m into S
    #if dict has edges then
    #    output error message (graph has at least one cycle)
    #else 
    #    output message (proposed topologically sorted order: L)
#    print "Prelations:", prelations
    check_prelations = dict.copy(prelations) #Work with a copy because it changes
#    print "check_Prelations:", check_prelations
    visited_elements = [] #Empty list that will contain the visited elements
    no_incoming_edges = graph.begining_activities(check_prelations) #Set of all nodes with no incoming edges
#    print "Datos de Entrada\n", prelations, "\n\n"
    iteracion=1
    while len(no_incoming_edges) > 0: #While no_incoming_edges no empty
        act = no_incoming_edges.pop()
        visited_elements.append(act) #Remove node n from no_incoming_edges and insert n into visited_elements
        iteracion+=1
        set_prelations = set(check_prelations[act]) #Get the new set prelations
        del check_prelations[act] #Delete prelations activity
        no_incoming_edges.update(graph.begining_activities(check_prelations, set_prelations)) #Update no_incoming_edges with new begining activities
    if check_prelations: #if graph has edges
        print "ERROR Graph has at least one cycle" #graph has at least one cycle
    else: #graph has no cycles
        print "OK Graph no have cycles"
        print 'hoy'
        
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
    
    small_cycle = {
        'a' : ['b'],
        'b' : ['a'],
    }
    
    dict_list = [prelations, simple_cycle, cycle, two_cycles, small_cycle]
    
    for dict_i in dict_list:
        print check_cycles(dict_i)


