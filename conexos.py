#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph
import copy

def check_conexos(successors):
    """
    Check if prelations make all activities connected
    """
    undirected_graph = conected_to_undirected_prelations(successors) #Make graph undirected
    visited_activities = set() #Empty set that will contain the visited activities
    aux_random = undirected_graph.iterkeys() #Get iterator over the keys of undirected_graph
    activities_for_visit = set()
    activities_for_visit.add(aux_random.next()) #Create a set with the elements to visit
    activities = set(undirected_graph.keys())
    while len(activities_for_visit) > 0: #While there are elements to visit
        act = activities_for_visit.pop() #Choose last elements from start set to check
        visited_activities.add(act) #Add selected elements to visited
        set_prelations = set(undirected_graph[act]) #Create set of next activities
        activities_for_visit.update(set_prelations.difference(visited_activities)) #Update nexts activities to visit
    if visited_activities != activities:
        return False #Graph is no conected
    else:
        return True #Graph is conected

def conected_to_undirected_prelations(prelations):
    """
    Make undirected the conected prelations
    Return new prelations
    """
    conected = copy.deepcopy(prelations)
    for act, sigs in prelations.items(): #Do undirected the conected prelations
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
