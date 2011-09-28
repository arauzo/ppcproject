#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph

def check_conexos(undirected_graph):
    """
        Check if connected graph
        Return set of visited elements
    """
    visited_elements = set() #Empty set that will contain the visited elements
    aux_random = undirected_graph.iterkeys() #Get iterator over the keys of undirected_graph
    start = set(aux_random.next()) #Create a set with the elements to visit
    iteration=1
    while len(start) > 0 : #While there are elements to visit
        print "\nIteration: ", iteration
        iteration+=1
        print "Start: ", start
        act = start.pop() #Choose last elements from start set to check
        print "Activity: ", act
        visited_elements.add(act) #Add selected elements to visited 
        print "Visited Elements: ", visited_elements
        set_prelations = set(undirected_graph[act]) #Create set of next activities
        print "Set prelations", set_prelations
        start.update(set_prelations.difference(visited_elements)) #Update nexts elements to visit
    print "Activity Undirected Graph:", undirected_graph.keys(), "\n"
    return visited_elements

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
    
def update_dictionary(part_conected, prelations):
    """
        Remove part conected from prelations
        Return new dictionary
    """
    new_dictionary = {}
    for acts,sigs in prelations.items(): #Past through dict of prelations
        if acts not in part_conected: #If activity is not in part conected 
            new_dictionary[acts] = list(sigs) #Copy activities to new dictionary
    return new_dictionary
    
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
        'h' : ['i'],
        'i' : [],
    }
    
    conected = set() #Empty set for recive result of check_conexos
    part_conected = set() #Empty set for all part conected
    list_conected = [] #Empty list for save diferent part conected
    aux_dict = prelations #Auxiliary dictionary to work on 
    while part_conected != set(prelations.keys()): 
        undirected_graph = conected_to_undirected_prelations(aux_dict)
        conected = check_conexos(undirected_graph)
        list_conected.append(conected)
        part_conected.update(conected)
        new_dict = update_dictionary(part_conected, prelations)
        aux_dict = new_dict
    print "List Part Conected: ", list_conected
