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
    relation.sort() # XXX Quitar en version definitiva para eficiencia
    print "RELATION: ", relation
    #Put one each relationship
    for activity, successor in successors.items():
        for suc in successor:
            matrix[relation.index(activity)][relation.index(suc)] = 1
    print "MATRIX filled: ", matrix
    #Sum each column
    sum_predecessors = scipy.sum(matrix, axis=0)
    print "SUM_SUCCESSORS: ", sum_predecessors
    #Sum each row
    sum_successors = scipy.sum(matrix, axis=1)
    print "SUM_PREDECCESSORS: ", sum_successors
    #Step 1. Search initials activities (have no predecessors)
    for num_predecessors in sum_predecessors:
        if num_predecessors == 0:
            beginning, = numpy.where(sum_predecessors == 0)
            
    print "Beginning: ", beginning
    #Step 2. Search endings activities (have no successors)
    for num_successors in sum_successors:
        if num_successors == 0:
            ending, = numpy.where(sum_successors == 0)
            
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
                    stI.append([num_successors, predecessor])
                
    print "stI: ", stI
    #Step 4. Search standard II(Full) and standard II(Incomplete)
    print "matrix: ", matrix
    stII_complete = []
    stII_complete_final = []
    stII_incomplete = []
    stII_incomplete_final = []
    predecessor_stII = []
    iguales = []
    for num_successors in range(len(sum_successors)):
        same_predecessors = [num_successors]
        for num_predecessors in range(num_successors+1, len(sum_predecessors)):
            if (matrix[num_successors] == matrix[num_predecessors]).all() and num_predecessors not in iguales:
                iguales.append(num_predecessors)
                same_predecessors.append(num_predecessors)
                sum_pre = matrix[num_predecessors] + matrix[num_successors]
        if len(same_predecessors) > 1:
            print "same_predecessors: ", same_predecessors
            if numpy.dot(numpy.array(sum_predecessors), numpy.array(matrix[same_predecessors[0]])) == \
               len(same_predecessors) * numpy.sum(matrix[same_predecessors[0]]): 
                stII_complete.append(same_predecessors)
            else:
                stII_incomplete.append(same_predecessors)
    for i in range(len(stII_complete)):
        stII_complete_final.append((stII_complete[i], numpy.nonzero(matrix[stII_complete[i][0]])))
    
    for i in range(len(stII_incomplete)):
        stII_incomplete_final.append( (stII_incomplete[i], numpy.nonzero(matrix[stII_incomplete[i][0]])[0] ) )
    print "STII COMPLETO: ", stII_complete, "###ERROR### STII Incompleto", stII_incomplete
    print "STII COMPLETO FINAL: ", stII_complete_final
    print "STII INCOMPLETO FINAL: ", stII_incomplete_final
    
    #Step 5. Search for matches

    
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
        'E' : ['G'],
        'F' : [],
        'G' : ['F'],
    }
    
    gento_municio(successors1)
    
##ACLARACION FUNCIONAMIENTO##
#Para el tipo II incompleto. Si una o varias actividades tienen las mismas siguientes, pero alguna o algunas de las siguientes son precededidas por alguna más, entonces es seguro que: 

#El nudo inicio de las que no tienen otra precedente es el mismo nudo de fin de las que tienen las mismas siguientes... y.
#Del nudo fin de las que tienen las mismas siguientes sale al menos una ficticia que va al nudo inicio de las que tienen más precedentes. Ahora habría que analizar si las que tienen otras precedentes tienen precedentes comunes o no comunes y sería como el tipo I (o no).


#El patrón coincidencias sirve para saber seguro cuándo hay ficticias. Una vez que se sabe eso, el patrón tipo II incompleto y el de cadenas, te ayuda a optimizar.
