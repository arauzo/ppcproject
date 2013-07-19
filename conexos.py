#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph

def check_conexos(successors):
    """
    Check if connected graph, graph must be undirected
    Return set of visited elements
    """
    undirected_graph = conected_to_undirected_prelations(successors)
    visited_elements = set() #Empty set that will contain the visited elements
    aux_random = undirected_graph.iterkeys() #Get iterator over the keys of undirected_graph
    start = set(aux_random.next()) #Create a set with the elements to visit
    activities = set(undirected_graph.keys())
    while len(start) > 0 : #While there are elements to visit
        act = start.pop() #Choose last elements from start set to check
        visited_elements.add(act) #Add selected elements to visited
        set_prelations = set(undirected_graph[act]) #Create set of next activities
        start.update(set_prelations.difference(visited_elements)) #Update nexts elements to visit
    if visited_elements != activities:
        return False
    else:
        return True

def conected_to_undirected_prelations(prelations):
    """
        Make undirected the conected prelations
        Return new prelations
    """
    conected = {} #New Dictionary
    for act,sigs in prelations.items(): #Copy the Dictionary
        conected[act] = list(sigs)
    
    for act,sigs in prelations.items(): #Do undirected the conected prelations
        for sig in sigs:
            conected[sig].append(act) #Add activity to their next activity
    return conected
    
#def update_dictionary(part_conected, prelations):
#    """
#        Remove part conected from prelations
#        Return new dictionary
#    """
#    new_dictionary = {}
#    for acts,sigs in prelations.items(): #Past through dict of prelations
#        if acts not in part_conected: #If activity is not in part conected 
#            new_dictionary[acts] = list(sigs) #Copy activities to new dictionary
#    return new_dictionary
    
##--- Start running as a program
#if __name__ == '__main__':
#    successors = {
#        'a' : ['b','c'],
#        'b' : ['c','d'],
#        'c' : ['d'],
#        'd' : ['e'],
#        'e' : [],
#        'f' : [],
#        'g' : [],
#        'h' : ['i'],
#        'i' : [],
#    }
    
#    conected = set() #Empty set for recive result of check_conexos
#    part_conected = set() #Empty set for all part conected
#    list_conected = [] #Empty list for save diferent part conected
#    aux_dict = prelations #Auxiliary dictionary to work on 
#    while part_conected != set(prelations.keys()): 
##    undirected_graph = conected_to_undirected_prelations(prelations)
##    print "Check_Conexos: ", check_conexos(successors)
#        list_conected.append(conected)
#        part_conected.update(conected)
#        new_dict = update_dictionary(part_conected, prelations)
#        aux_dict = new_dict
#    print "List Part Conected: ", list_conected
