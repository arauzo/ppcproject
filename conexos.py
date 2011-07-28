#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph

def check_conexos(undirected_graph):
    """
        Check if connected graph
    """
    visited_elements = set() #Empty set that will contain the visited elements
    aux_random = undirected_graph.iterkeys() #Get iterator over the keys of undirected_graph
    start = set(aux_random.next()) #Create a set with the elements to visit
    iteration=1
    while len(start) > 0 : #While there are elements to visit
        print "\nIteration: ", iteration
        iteration+=1
        print "Start: ", start
        act = start.pop() #Choose the last elements of start set to check
        print "Activity: ", act
        visited_elements.add(act) #Add the selected elements to visited 
        print "Visited Elements: ", visited_elements
        set_prelations = set(undirected_graph[act]) #Create de set of next activities
        print "Set prelations", set_prelations
        start.update(set_prelations.difference(visited_elements)) #Update the nexts elements to visit
    print "Activity Undirected Graph:", undirected_graph.keys(), "\n"
    for act in undirected_graph.keys(): #Get keys of undirected_graph
        if act not in visited_elements: #If the activity has not been visit
            print "ERROR"
            break
        else:
            print "OK"

def conected_to_undirected_prelations(prelations):
    """
        Make undirected the conected prelations
        Return new prelations
    """
    print "Datos de Entrada(No conexas): ", prelations
    conected = {} #New Dictionary
    for act,sigs in prelations.items(): #Copy the Dictionary
        conected[act] = list(sigs)
    
    for act,sigs in prelations.items(): #Do undirected the conected prelations
        for sig in sigs:
            conected[sig].append(act) #Add activity to their next activity
    print "Prelaciones conexas: ", conected
    return conected
# --- Start running as a program
if __name__ == '__main__':
    prelations = {
        'a' : ['b','c'],
        'b' : ['c','d'],
        'c' : ['e'],
        'd' : ['g'],
        'e' : [],
        'f' : [],
        'g' : [],
    }
    
    undirected_graph = conected_to_undirected_prelations(prelations)
    check_conexos(undirected_graph)
