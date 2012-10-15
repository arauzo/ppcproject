#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph

def gento_municio(successors):
    """
    """
    
    #Step 1. Search initials activities
    initials = graph.begining_activities(successors)
    print "Initials:", initials
    
    #Step 2. Search endings activities
    endings = graph.ending_activities(successors)
    print "Endings:", endings
    
    #Step 3. Search standard type I
    standard_I = []
    individual_successors = []
    successor_repetitions = []
    visited = []
    
    for successor in successors.values(): #List individual successors
        for suc in successor:
            individual_successors.append(suc)
    print "individual_successors:", individual_successors 
    
    for successor in individual_successors: #Count successors repetitions
        if successor not in visited:
            aux = [] #List for successor and count
            visited.append(successor) #Avoid repeated analysis
            aux.append(successor)
            aux.append(individual_successors.count(successor)) #Count successor repetitions
            successor_repetitions.append(aux)
    print "successor_repetitions:", successor_repetitions
    
    for activity, successor in successors.items(): #Check unique successors
        print "Activity:", activity, "successor", successor
        check_unique = 0 #Check if all predecessor are unique
        if len(successor) != 0: #Activity have predecessor
            for suc in successor:
                for act, repetition in successor_repetitions:
                    if act == suc and repetition > 1: #Activity not unique
                        check_unique = 1
                        break; #If one predecessor is not unique Activity is not Standard_I
            if check_unique == 0:
                standard_I.append(activity)
    print "Standard_I:", standard_I
    
    #Step 4. Search standard type II Full
    standard_II = []
    repeated_predecessor = []
    d = {}
    l = list(successors.items())
    print "L:", l
    for i in range(len(l)):
        set_i = set(l[i][1]) 
        for j in range(i+1, len(l)):
            set_j = set(l[j][1])
            if set_i == set_j:
                if set_j in d.keys():
                    d[frozenset(set_j)].update(set(l[j][0]))
                else:
                    d[frozenset(set_j)] = set([l[i][0], l[j][0]])
    standard_II = d.values()
    print "Standard II:", standard_II 
    
    #Search standard type II Incomplete
    set_successors = set()
    for activity, successors in successors.items():
        set_successors = set(successors)


        
## --- Start running as a program
if __name__ == '__main__':
    successors = {
        'A' : ['D', 'G'],
        'B' : ['C', 'D', 'E'],
        'C' : ['F'],
        'D' : ['G', 'D'],
        'E' : [],
        'F' : ['C', 'D', 'E'],
        'G' : ['H'],
        'H' : ['G'],
        'I' : ['H'],
        'J' : ['H'],
        'K' : ['G'],
    }

    successors1 = {
        'A' : ['C'],
        'B' : ['C', 'D', 'E'],
        'C' : ['F'],
        'D' : ['F'],
        'E' : [],
        'F' : [],
    }
    
    gento_municio(successors)
