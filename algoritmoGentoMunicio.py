#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph
import scipy
import numpy

def gento_municio(successors):
    """
    """
    #Generate precedences/successors matrix
    matrix = scipy.zeros([len(successors.keys()), len(successors.keys())], dtype = int)
    print "MATRIX: ", matrix
    #Assign number to letters of activity
    relation = successors.keys()
    print "RELATION: ", relation
    #Put one each relationship
    for activity, successor in successors.items():
        for suc in successor:
            matrix[relation.index(activity)][relation.index(suc)] = 1
    print "MATRIX filled: ", matrix
    #Sum each column
    sum_predecessors = scipy.sum(matrix, axis=0)
    print "SUM_PREDECESSORS: ", sum_predecessors
    #Sum each row
    sum_successors = scipy.sum(matrix, axis=1)
    print "SUM_SUCCESSORS: ", sum_successors
    #Step 1. Search initials activities (have no predecessors)
    for num_predecessors in sum_predecessors:
        if num_predecessors == 0:
            beginning = numpy.where(sum_predecessors == 0)
            
    print "Beginning: ", beginning
    #Step 2. Search endings activities (have no successors)
    for num_successors in sum_successors:
        if num_successors == 0:
            ending = numpy.where(sum_successors == 0)
            
    print "Ending: ", ending
    #Step 3. Search standard type I (Activity have unique successors)
    stI = []
    for num_successors in range(len(sum_predecessors)):
        print "matrix[i]: ", matrix[num_successors]
        ok = True
        unique_successors = []
        for predecessor in range(len(matrix[num_successors])):
            if matrix[num_successors][predecessor] == 1 and ok == True:
                print "matrix['%d']['%d']: " % (num_successors, predecessor), matrix[num_successors][predecessor]
                print "sum_predecessors[predecessor]: ", sum_predecessors[predecessor]
                if (sum_predecessors[predecessor] > 1): #More than one not unique successor activity 
                    ok = False
                elif sum_predecessors[predecessor] == 1: #
                    unique_successors.append(predecessor)
                    print "unique_successors: ", unique_successors
                    print "%s : %s" % (relation[num_successors], unique_successors)
                    print "OKOKOKOKActivity: successorOKOKOKOK", num_successors, predecessor
                    stI.append([num_successors, predecessor])
                
    print "stI: ", stI
    #Step 4. Search standard II(Full) and standard II(Incomplete)
    print "matrix: ", matrix
    stII_complete = []
    stII_incomplete = []
    iguales = []
    for num_successors in range(len(sum_successors)):
        same_predecessors = [num_successors]
        for num_predecessors in range(num_successors+1, len(sum_predecessors)):
            if (matrix[num_successors] == matrix[num_predecessors]).all() and num_predecessors not in iguales:
                iguales.append(num_predecessors)
                same_predecessors.append(num_predecessors)
                sum_pre = matrix[num_predecessors] + matrix[num_successors]
                print "##sum_preIN: ", sum_pre
                print "(i, j): ", num_successors, num_predecessors
                print "matrix[i]: ", matrix[num_successors]
                print "matrix[j]: ", matrix[num_predecessors]
        if len(same_predecessors) > 1:
            print "same_predecessors: ", same_predecessors
            print "same_predecessors[0]: ", same_predecessors[0]
            print "sum_predecessors: ", sum_predecessors
            print "matrix[same_predecessors[0]]: ", matrix[same_predecessors[0]]
            a = numpy.array(sum_predecessors)
            b = numpy.array(matrix[same_predecessors[0]])
            print "MULTIPLICACION MATRICIALnp.dot: ", numpy.dot(a, b)
            print "len(same_predeccessors): ", len(same_predecessors)
            print "sum(Matrix[i]): ", numpy.sum(matrix[same_predecessors[0]])
            for i in range(len(matrix[same_predecessors[0]])):
                print "i: ", i
                print "matrix[same_predecessors[0][i]]: ", matrix[same_predecessors[0],[i]]
                if matrix[same_predecessors[0],[i]] != 0:
                    print "matrix[same_predecessors[0][i]]: ", matrix[same_predecessors[0],[i]]
    print "STII COMPLETO: ",  stII_complete, "###ERROR### STII Incompleto", stII_incomplete
#    for i in same_predecessors:
#        print "sum_pre before: ", sum_pre
#        sum_pre += matrix[i]
#        print "sum_pre after: ", sum_pre
    print "same_predecessors FINAL: ", same_predecessors
    print "sum_pre: ", sum_pre
##    for p in range(len(sum_pre)):
##        if sum_pre[p] > 0:
##            print "p: ", p
##            print "sum_pre[p]: ", sum_pre[p]
##            print "same_predecessors[0]: ", same_predecessors[0]
##            print "sum_predecessors[p]: ", sum_predecessors[p]
##            if sum_pre[p] == sum_predecessors[p]:
##                print "stII Completo"
##                print "same_predecessors: ", same_predecessors
##                print "p: ", p
##            else:
##                print "stII Incompleto"
##                print "same_predecessors: ", same_predecessors
##                print "p: ", p
##                for i in range(len(matrix[:, p])):
##                    if matrix[i,p] == 1 and i not in same_predecessors:
##                        print "i: ", i
##                        same_predecessors.append(i)
##                        print "same_predecessors: ", same_predecessors
##                        
#                print "matrix[same_predecessors[0]]: ", matrix[same_predecessors[0][p]
#    for i in matrix.flat:
#            print "Matrix[i,j]: ", i
    

#    
#    #node array for activity, begin and end
#    node_array = {}
#    print "Successors: ", successors
#    #Step 1. Search initials activities
#    initials = graph.begining_activities(successors)
#    for ini in initials:
#        node_array[ini] = ([0, None])
#    print "Node Array: ", node_array
#    print "Initials:", initials
#    

#    endings = graph.ending_activities(successors)
#    for end in endings:
#       node_array[end] = ([None, 1])
#    print "Node Array: ", node_array
#    print "Endings:", endings
#    

#    ##Matrix Predeccessors
###    precedence_matrix = []
###    
###    for rows in range(len(successors.keys())):
###        precedence_matrix.append([0]*len(successors.values()))
###        precedence_matrix[rows][rows] = "-"
###    print "Matrix: ", precedence_matrix
#    act_not_unique = []
#    suc_not_unique = []
#    same_sucs = []
#    for activity, successor in successors.items():
#        for act, suc in successors.items():
#            if activity != act and set(successor).intersection(set(suc)):
#                if act not in act_not_unique:
#                    act_not_unique.append(activity)
#                    act_not_unique.append(act)
#                    for s in suc:
#                        if s not in suc_not_unique:
#                            suc_not_unique.append(s)
#            if activity != act and set(successor) == set(suc):
#                if successor not in same_sucs: 
#                    same_sucs.append(successor)
#    print "same sucs: ", same_sucs
##    print "activity, successor, act, suc: ", activity, successor, act, suc
#    print "act_not_unique: ", act_not_unique
#    print "suc_not_unique: ", suc_not_unique
#    
#    standard_I = []
#    for activity, successor in successors.items():
#        if activity not in act_not_unique:
#            for suc in successor:
#                if suc not in suc_not_unique and len(suc) > 0:
#                    if activity not in standard_I:
#                        standard_I.append(activity)
#                        node_array[activity] = ([0, 1])
#        for same_suc in same_sucs:
##            print "s, same_sucs: ", same_suc, same_sucs
###            print "activity, successor, act, suc: ", activity, successor, act, s
##            print "len s, len successor: ", len(same_suc), len(successor)
#            if set(same_suc).intersection(set(successor)):
#                if len(same_suc) == len(successor):
#                    print "Standard II Completo"
#                    print "###***INactivity, successor, suc: ", activity, successor, same_suc
#                else:
#                    print "Standard II INCompleto"
#                    print "###***INactivity, successor, suc: ", activity, successor, same_suc
#    print "Standard I: ", standard_I
#    print "node_array: ", node_array
#    
##    standard_II = []
##    for activity, successor in successors.items():
#        
##    matrix_predeccessors = []
##    list_act_countpredecessors = [[0]]
##    vis = []
##    for act, suc in successors.items():
##            for s in suc:
##                if s in vis
##                if s not in vis:
##                    vis.append(s)
###                print "Successors values: ", successors.values()
###                print "suc: ", suc
###                integer = successors.values().count(suc)
###                print "act, s, integer: ", a, s, integer
###            matrix_predeccessors[act] = integer
##    print "MATRIX_PREDECCESSORS: ", matrix_predeccessors
##    
##    standard_I = []
##    visited = []
##    more_than_once = []
##    
##    standard_II = []
##    all_successors_visited = []
##    more_than_once_all = []
##    standard_II_incomplete = []
##    
#    #Find activities with unique successors and with same successors
#    #XXX
##    for activity, successor in successors.items():
##        for act, suc in successors.items():
##            if activity != act and set(successor) == set(suc):
##                standard_I.append([activity, successor])
##            if activity != act and set(successor).intersection(set(suc)):
##                print "Activity, successors, suc", activity, successor, suc
##                visited.extend([activity, act])
##                if activity not in visited:
##                    standard_II_incomplete.append([[activity, successor], [act, suc]])
##                if suc == successor:
##                    print "SUC==SUCCESSORActivity, successors, suc", activity, successor, suc
##    print "visited: ", visited
##    print "standard_I: ", standard_I
##    print "standard_II_incomplete: ", standard_II_incomplete
#    #XXX
##    for all_successors in successors.values():
##        for element_all_successors in all_successors_visited:
##            if len(all_successors) != 0 and set(all_successors) == (set(element_all_successors)):
##                if all_successors not in more_than_once_all:
##                    more_than_once_all.append(all_successors)
##        all_successors_visited.append(all_successors)
##        for successor in all_successors:
##            if successor in visited and successor not in more_than_once:
##                more_than_once.append(successor)
##            visited.append(successor)
##            
##    #For step 3(Standard I) all successor only can appear one time
##    for activity, successor in successors.items():
##        if not set(more_than_once).intersection(set(successor)) and len(successor) != 0:
##            standard_I.append([activity, successor])
##    print "standard_I: ", standard_I
##    print "MORE TAN ONCE ALL: ", more_than_once_all
##    #For step 4(Standard II) the same successor for two or more activities
##    
##    for element_more_than_once_all in more_than_once_all:
##        for activity, successor in successors.items():
###            print "Element mtoa: ", element_more_than_once_all
###            print "successors: ", successor
##            if set(element_more_than_once_all) == ((set(successor))):
##                standard_II.append(activity)
##    print "standard_II: ", standard_II
##    
##    for activity, successor in successors.items():
##        for suc in successor:
##            if [suc] in more_than_once_all and activity not in standard_II:
##                standard_II_incomplete.append([activity, successor])
##                print "Activity, successor: ", activity, successor
##            elif activity in standard_II:
##                print "Activity, successor ELSE: ", activity, successor
##    #For step 4.1(Standard II Incomplete)at least one successor of standard II are in other activity not standar II
###    for activity, successor in successors.items():
###        for suc in more_than_once_all:
###            if set(suc).intersection(set(successor)):
###                standard_II_incomplete.append(activity)
##            
##    print "standard_II Incompleto: ", standard_II_incomplete
    
# --- Start running as a program
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
        'B' : ['G', 'D'],
        'C' : ['G', 'D'],
        'D' : ['F'],
        'E' : ['G', 'D'],
        'F' : [],
        'G' : ['F'],
    }
    
    gento_municio(successors1)
    
##ACLARACION FUNCIONAMIENTO##
#Para el tipo II incompleto. Si una o varias actividades tienen las mismas siguientes, pero alguna o algunas de las siguientes son precededidas por alguna más, entonces es seguro que: 

#El nudo inicio de las que no tienen otra precedente es el mismo nudo de fin de las que tienen las mismas siguientes... y.
#Del nudo fin de las que tienen las mismas siguientes sale al menos una ficticia que va al nudo inicio de las que tienen más precedentes. Ahora habría que analizar si las que tienen otras precedentes tienen precedentes comunes o no comunes y sería como el tipo I (o no).


#El patrón coincidencias sirve para saber seguro cuándo hay ficticias. Una vez que se sabe eso, el patrón tipo II incompleto y el de cadenas, te ayuda a optimizar.
