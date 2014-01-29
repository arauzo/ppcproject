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
    no_standard_I = []
    individual_successors = []
    successor_repetitions = []
    visited = [] #List of visited activities
    more_than_once = [] #List of activities that appear more than once
    for predecessors in successors.values():
        for activity in predecessors:
            if activity in visited and activity not in more_than_once: #If activity visited
                more_than_once.append(activity) #Add activity duplicate
            visited.append(activity) #Add activity to list of visited
    print "visited: ", visited
    print "more than once: ", more_than_once
    
    for activity, successors in successors.items():
        if set(more_than_once).intersection(set(successors)):
            no_standard_I.append(activity)
        elif len(successors) != 0:
            standard_I.append(activity)
    print "standard_I: ", standard_I
    print "no_standard_I: ", no_standard_I
#    #List individual successors
#    print "Successors_values: ", successors.values()
#    for successor in successors.values():
#        for suc in successor:
#            individual_successors.append(suc)
#    print "individual_successors:", individual_successors 
#    #Count successors repetitions
#    #aux = List for successor and count
#    for successor in individual_successors:
#        if successor not in visited:
#            aux = [] 
#            visited.append(successor)
#            aux.append(successor)
#            aux.append(individual_successors.count(successor))
#            successor_repetitions.append(aux)
#    print "successor_repetitions:", successor_repetitions
#    for a, b in successor_repetitions:
#        print "a, b:", a, b
#    #Check unique successors
#    #If one predecessor is not unique Activity is not Standard_I
#    for activity, successor in successors.items():
#        print "Activity:", activity, "successor", successor
#        check_unique = 0
#        if len(successor) != 0:
#            for suc in successor:
#                for act, repetition in successor_repetitions:
#                    if act == suc and repetition > 1:
#                        check_unique = 1
#                        break;
#            if check_unique == 0:
#                standard_I.append(activity)
#    print "Standard_I:", standard_I
    
    #Step 4. Search standard type II
    #d = Dictionary for similar successors(key) and activities with similar successors(values)
    standard_II = []
    d = {}
    aux_successors = successors.copy()
    aux_suc = []
    print "Successors", successors
    for act, suc in aux_successors.items():
        for act1, suc1 in aux_successors.items():
            if len(act) != 0:
                if act != act1 and suc and set(suc) == set(suc1):
                    print "ACT: ", act, "act: ", act1
                    print "SUC: ", suc, "suc: ", suc1
                    if suc not in aux_suc:
                        aux_suc.append(suc)
    print "aux_suc: ", aux_suc
    print aux_successors is successors
    print "aux_successors", aux_successors
    l = list(aux_successors.items())
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
    print "D:", d
    print "sucessors:", successors
    coincidencias = []
    for similar_set, act in d.items():
        for activity, successor in successors.items():
            if set(similar_set) == set(successor):
                print "1 similar_set>activities", similar_set, "suc", successor
            elif set(similar_set) < set(successor) and activity not in set(act):
                coincidencias.append(activity)
                for i in act:
                    coincidencias.append(i)
                print "2 similar_set<activities", similar_set, "suc", successor
    print "coincidencias:", coincidencias
    complete = []
    for aux_set, act in d.items():
        if len(act) != 0:
            for a in act:
                if a not in coincidencias:
                    complete.append(a)
    print "Successors:", successors
#    standard_II = d.values()
    incomplete = []
    for sig, act in d.items():
        for auxact, auxsig in successors.items():
            if sig.intersection(auxsig) and auxact not in act:
                print "AUXSIG:", auxsig
                print "act:", act
                print "incomplete:", incomplete
                print "complete:", complete
                if act not in incomplete and act not in complete:
                    incomplete.append(auxact)
                    incomplete.append(act)

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
        'D' : ['G', 'D'],
        'E' : [],
        'F' : ['G', 'D', 'E'],
        'G' : ['H'],
        'H' : ['E'],
        'I' : ['H'],
        'J' : ['H'],
        'K' : ['A', 'B', 'I', 'J'],
    }

    successors1 = {
        'A' : ['C'],
        'B' : ['C', 'D', 'E'],
        'C' : ['F'],
        'D' : ['F'],
        'E' : [],
        'F' : [],
        'G' : ['F'],
    }
    
    gento_municio(successors1)
    
##ACLARACION FUNCIONAMIENTO##
#Para el tipo II incompleto. Si una o varias actividades tienen las mismas siguientes, pero alguna o algunas de las siguientes son precededidas por alguna más, entonces es seguro que: 

#El nudo inicio de las que no tienen otra precedente es el mismo nudo de fin de las que tienen las mismas siguientes... y.
#Del nudo fin de las que tienen las mismas siguientes sale al menos una ficticia que va al nudo inicio de las que tienen más precedentes. Ahora habría que analizar si las que tienen otras precedentes tienen precedentes comunes o no comunes y sería como el tipo I (o no).


#El patrón coincidencias sirve para saber seguro cuándo hay ficticias. Una vez que se sabe eso, el patrón tipo II incompleto y el de cadenas, te ayuda a optimizar.
