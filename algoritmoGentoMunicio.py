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
    
    #Step 4. Search standard type II
    standard_II = []
    d = {} #Dictionary for similar successors(key) and activities with similar successors(values)
    l = list(successors.items()) #List actvity succesors
    print "L:", l
    for i in range(len(l)):
        set_i = set(l[i][1]) #Set of successors i
        for j in range(i+1, len(l)):
            set_j = set(l[j][1]) #Set of successors j
            if set_i == set_j: #If successors i and succesors j have same successors
                if set_j in d.keys(): #If set j analyzed, update
                    d[frozenset(set_j)].update(set(l[j][0]))
                else: #Add news sets similar successors(key) and activities with similar successors(values)
                    d[frozenset(set_j)] = set([l[i][0], l[j][0]])
    print "D:", d
#    standard_II = d.values()
    incomplete = []
    complete = []
    for sig, act in d.items():
        for auxact, auxsig in successors.items():
            if sig.intersection(auxsig) and auxact not in act:
                print "AUXSIG:", auxsig
                if act not in incomplete:
                    incomplete.append(auxact)
                    incomplete.append(act)
    for act in d:
        if len(act) != 0:
            complete.append(act)
#                    print "CHECKsig, act, auxact, auxsig:", sig, act, auxact, auxsig
#                    if auxact in act:
#                        print "####CHECKsig, act, auxact, auxsig:", sig, act, auxact, auxsig
    print "Complete:", complete
    print "Incomplete:", incomplete
    #Search standard type II Incomplete
##    standard_II_incomplete = []
##    di = {}
##    for s2, act2 in d.items():
##        for auxs2, auxact2 in successors.items():
##            print "S2:", s2, "ACT2:", act2
##            print "AUXS2:", auxs2, "AUXACT2:", auxact2
##            if s2.intersection(auxact2) and act2.isdisjoint(auxs2):
##                print "OK"
##                if act2 not in standard_II_incomplete:
##                    standard_II_incomplete.append(act2)
#    for a in standard_II_incomplete:
#        print "A:", a
##    standard_II_full = []
##    for sII in d.values():
##        print "SII:", sII
##        if sII not in standard_II_incomplete:
##            standard_II_full.append(sII)
##    print "SIIfull:", standard_II_full
#            if not a.intersection(sII):
#                print "AOK:", a 
#    print "Standard II:", standard_II
#    l = list(successors.items())
#    for i in range(len(l)):
#        set_i = set(l[i][1])
#        print "SET_I:", set_i
#        for j in range(i+1, len(l)):
#            set_j = set(l[j][1])
#            print "SET_J:", set_j
#            if set_i.intersection(set_j):
#                print "OK"
##                print "set_i, set_j:", set_i, set_j
##                if set_i == set_j:
##                    if set_j in d.keys():
##                        d[frozenset(set_j)].update(set(l[j][0]))
##                    else:
##                        d[frozenset(set_j)] = set([l[i][0], l[j][0]])
#                if set_j in di.keys():
#                    print "###IF DI:", di
#                    di[frozenset(set_j)].update(set(l[j][0]))
#                else:
#                    print "DI ELSE&&&:", di
#                    di[frozenset(set_j)] = set([l[i][0], l[j][0]])
##    standard_II = d.values()
##    print "Standard IIFINAL:", standard_II
##    print "DI:", di
#    standard_II_incomplete = di.values()
##    print "Standard II incomplete:", standard_II_incomplete
#        
## --- Start running as a program
if __name__ == '__main__':
    successors = {
        'A' : ['G', 'D'],
        'B' : ['C', 'E'],
        'C' : ['F'],
        'D' : ['G', 'A'],
        'E' : [],
        'F' : ['C', 'D', 'E'],
        'G' : ['H'],
        'H' : ['G'],
        'I' : ['H'],
        'J' : ['H'],
    }

    successors1 = {
        'A' : ['C'],
        'B' : ['C', 'D', 'E'],
        'C' : ['F'],
        'D' : ['F'],
        'E' : [],
        'F' : [],
        'G' : ['F', 'E'],
    }
    
    gento_municio(successors1)
