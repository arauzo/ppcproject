#!/usr/bin/env python
# -*- coding: utf-8 -*-
import graph
import scipy
import numpy
import collections

class NodeList(object):
    """List of nodes for each activity to create PERT graph"""

    def __init__(self, num_real_activities):
        #List of nodes for each activity [0, n-1] real activities, [n, n+m-1] the dummy activities )
        self.node_list = [ [None, None] for i in range(num_real_activities) ]
        self.last_node_created = 99 #-1 para la version definitiva XXX

    def __str__(self):
        """String for debuging"""
        s = ''
        for act in range(len(self.node_list)):
            s += str(act) + ' ' + str(self.node_list[act]) + '\n'
        s += "Last_node_created: " + str(self.last_node_created) + '\n'
        return s
    
    def __getitem__(self, key):
        return self.node_list[key]
    
    def next_node(self):
        """Creates a new node number"""
        self.last_node_created += 1
        return self.last_node_created

    def new_dummy(self):
        """Creates a new dummy activity and return its index"""
        self.node_list.append( [None, None] )
        return len(self.node_list) - 1

def gento_municio(successors):
    """
    """
    #Generate precedences/successors matrix
    num_real_activities = len(successors.keys())
    matrix = scipy.zeros([num_real_activities, num_real_activities], dtype = int)
    print "MATRIX: \n", matrix
    #Assign number to letters of activity
    relation = successors.keys()
    relation.sort() # XXX Quitar en version definitiva para eficiencia
    print "RELATION: ", relation
    #Put one each relationship
    for activity, successor in successors.items():
        for suc in successor:
            matrix[relation.index(activity)][relation.index(suc)] = 1
    print "MATRIX filled: \n", matrix
    #Sum each column
    sum_predecessors = scipy.sum(matrix, axis=0)
    print "SUM_PREDECESSORS: ", sum_predecessors
    #Sum each row
    sum_successors = scipy.sum(matrix, axis=1)
    print "SUM_SUCCCESSORS: ", sum_successors
        
    nodes = NodeList(num_real_activities)
    print nodes
    #Step 1. Search initials activities (have no predecessors)
    beginning, = numpy.nonzero(sum_predecessors == 0)
    print "Beginning: ", beginning
    
    begin_node = nodes.next_node()
    for node_activity in beginning:
        nodes[node_activity][0] = begin_node
    
    #Step 2. Search endings activities (have no successors)
    ending, = numpy.nonzero(sum_successors == 0)
    print "Ending: ", ending
    
    end_node = nodes.next_node()
    for node_activity in ending:
        nodes[node_activity][1] = end_node
    
    print nodes
    #Step 3. Search standard type I (Activity have unique successors)
    indice, = numpy.nonzero(sum_predecessors == 1)
    prueba_stI = collections.defaultdict(list)
    print "indice: ", indice
    print "suma matrix \"indices\":", scipy.sum(matrix[:,indice])
    for i in indice:
        print "i: ", i
        print "matrix[:,i]: ", matrix[:,i]
        activity = numpy.nonzero((matrix[:,i]))[0][0]
        if sum_successors[activity] == 1 or scipy.sum(matrix[:,numpy.nonzero(matrix[activity])]) == sum_successors[activity]:
            print "activity: ", activity
            prueba_stI[activity].append(i)
    print "prueba_stI: ", prueba_stI
    
    for node_activity in prueba_stI:
        print "node_activity: ", node_activity
        stI_node = nodes.next_node()
        print "stI_node: ", stI_node
        nodes[node_activity][1] = stI_node
        for successor in prueba_stI[node_activity]:
            nodes[successor][0] = stI_node
    
    print nodes
#    stI = []
#    for num_successors in range(len(sum_predecessors)):
#        ok = True
#        unique_successors = []
#        for predecessor in range(len(matrix[num_successors])):
#            if matrix[num_successors][predecessor] == 1 and ok == True:
#                if (sum_predecessors[predecessor] > 1): #More than one not unique successor activity 
#                    ok = False
#                elif sum_predecessors[predecessor] == 1:
#                    unique_successors.append(predecessor)
#                    stI.append([num_successors, predecessor])
#    print "stI: ", stI
    #Step 4. Search standard II(Full) and standard II(Incomplete)
    print "matrix: \n", matrix
    stII_complete = []
    stII_complete_final = []
    stII_incomplete = []
    stII_incomplete_final = []
    predecessor_stII = []
    equal = []
    for num_successors in range(len(sum_successors)):
        same_predecessors = [num_successors]
        for num_predecessors in range(num_successors+1, len(sum_predecessors)):
            if (matrix[num_successors] == matrix[num_predecessors]).all() and num_predecessors not in equal:
                equal.append(num_predecessors)
                same_predecessors.append(num_predecessors)
                sum_pre = matrix[num_predecessors] + matrix[num_successors]
        if len(same_predecessors) > 1:
            print "same_predecessors: ", same_predecessors
            prueba_same_pred = same_predecessors #same predecesor change
            print "numpy.dot(numpy.array(sum_predecessors), numpy.array(matrix[same_predecessors[0]]))", \
               numpy.dot(numpy.array(sum_predecessors), numpy.array(matrix[same_predecessors[0]]))
            print "len(same_predecessors) * numpy.sum(matrix[same_predecessors[0]])", \
                len(same_predecessors) * numpy.sum(matrix[same_predecessors[0]])
            if numpy.dot(numpy.array(sum_predecessors), numpy.array(matrix[same_predecessors[0]])) == \
               len(same_predecessors) * numpy.sum(matrix[same_predecessors[0]]): 
                stII_complete.append(same_predecessors)
            else:
                stII_incomplete.append(same_predecessors)
                
    print "stII_incomplete[0][0]: ", stII_incomplete
    indices = numpy.nonzero(matrix[stII_incomplete[0][0]])
    print "indices: ", indices
    print "same predecessors: ", same_predecessors
    print "len(same_predecessors)", len(same_predecessors)
    print "sum_predecessors: ", sum_predecessors
    print "sum_predecessors[ind]", sum_predecessors[indices[0]]
    print "sum_predecessors[ind]2", sum_predecessors[indices[0][1]]
    for ind in indices[0]:
        if sum_predecessors[ind] > len(prueba_same_pred):
            print "ind: ", ind
            print "OK"
            print "matrix[0][ind]", matrix[:,ind]
            columna = numpy.nonzero(matrix[:,ind])
            print "columna: ", columna

    print "stII_incomplete: ", stII_incomplete
            
    for i in range(len(stII_complete)):
        stII_complete_final.append((stII_complete[i], numpy.nonzero(matrix[stII_complete[i][0]])))
    
    for i in range(len(stII_incomplete)):
        stII_incomplete_final.append( (stII_incomplete[i], numpy.nonzero(matrix[stII_incomplete[i][0]])[0] ) )
    print "STII COMPLETO: ", stII_complete, "###ERROR### STII Incompleto", stII_incomplete
    print "STII COMPLETO FINAL: ", stII_complete_final
    print "STII INCOMPLETO FINAL: ", stII_incomplete_final
    
    #Step 5. Search for matches
    npc = []
    print "stII incomplete final: ", stII_incomplete_final
    for activity, sucessor in stII_incomplete_final:
        ocurrencia = 0
        for s in sucessor:
            npc.append((s,ocurrencia+len(activity)))
            print "npc: ", npc
            print "activity, sucessor: ", activity, sucessor
    #Step 5.1 Know initial nodes of activities of matches standar
#    for activity, matches in npc:
#        if matches > 1:
#            print "1"
#            else:
#                print "OKKO"
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
    
#    Datos con multiples stI
#    successors1 = {
#        'A' : ['C', 'E'],
#        'B' : ['G', 'D'],
#        'C' : ['G', 'D'],
#        'D' : ['F'],
#        'E' : ['G'],
#        'F' : ['B'],
#        'G' : ['F'],
#    }
    
    gento_municio(successors1)
    
##ACLARACION FUNCIONAMIENTO##
#Para el tipo II incompleto. Si una o varias actividades tienen las mismas siguientes, pero alguna o algunas de las siguientes son precededidas por alguna más, entonces es seguro que: 

#El nudo inicio de las que no tienen otra precedente es el mismo nudo de fin de las que tienen las mismas siguientes... y.
#Del nudo fin de las que tienen las mismas siguientes sale al menos una ficticia que va al nudo inicio de las que tienen más precedentes. Ahora habría que analizar si las que tienen otras precedentes tienen precedentes comunes o no comunes y sería como el tipo I (o no).


#El patrón coincidencias sirve para saber seguro cuándo hay ficticias. Una vez que se sabe eso, el patrón tipo II incompleto y el de cadenas, te ayuda a optimizar.
