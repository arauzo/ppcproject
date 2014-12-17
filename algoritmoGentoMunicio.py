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

def gento_municio(successors): # XXX Lo que se le pasa son predecesores ?no?
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
    
    #Add begin node to activities that begin at initial node
    begin_node = nodes.next_node()
    for node_activity in beginning:
        nodes[node_activity][0] = begin_node
    
    #Step 2. Search endings activities (have no successors)
    ending, = numpy.nonzero(sum_successors == 0)
    print "Ending: ", ending
    #XXX Igual a STII si mas de una actividad (no es necesario este paso) stI no lo considera
    #Add end node to activities that end in final node
    end_node = nodes.next_node()
    for node_activity in ending:
        nodes[node_activity][1] = end_node
    
    print nodes
    #Step 3. Search standard type I (Activity have unique successors)
    indice, = numpy.nonzero(sum_predecessors == 1)
    stI = collections.defaultdict(list)
    for i in indice:
        activity = numpy.nonzero((matrix[:,i]))[0][0]
        if sum_successors[activity] == 1 or scipy.sum(matrix[:,numpy.nonzero(matrix[activity])]) == sum_successors[activity]:
            stI[activity].append(i)
    print "stI: ", stI
    #Add the same end node of activities to the begin node of its successors activities
    for node_activity in stI:
        print "node_activity: ", node_activity
        stI_node = nodes.next_node()
        print "stI_node: ", stI_node
        nodes[node_activity][1] = stI_node
        for successor in stI[node_activity]:
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
    equal = [] #XXX Deberia ser conjunto por eficiencia o cambiar estructura para simplificar lo siguiente
    for act in range(num_real_activities):
        same_successors = [act]
        for aux_act in range(act+1, num_real_activities):
            if (matrix[act] == matrix[aux_act]).all() and aux_act not in equal:
                equal.append(aux_act)
                same_successors.append(aux_act)
        if len(same_successors) > 1:
            print "SAME SUCCESSORS: ", same_successors
            if numpy.dot(numpy.array(sum_predecessors), numpy.array(matrix[same_successors[0]])) == \
               len(same_successors) * numpy.sum(matrix[same_successors[0]]): 
                stII_complete.append(same_successors)
            else:
                stII_incomplete.append(same_successors)
                num_same_pred = len(same_successors)
                stII_incomplete_node = nodes.next_node()
                for node_activity_incomplete in same_successors:
                    nodes[node_activity_incomplete][1] = stII_incomplete_node
    print nodes
    if len(stII_incomplete) > 0:
        print "stII_incomplete: ", stII_incomplete
        for pre in stII_incomplete:
            print "PRE: ", pre
            index = numpy.nonzero(matrix[pre[0]]) #matrix[stII_incomplete[0][0]])
        print "INDEX: ", index
        for ind in index[0]:
            print "IND", ind
            if sum_predecessors[ind] > num_same_pred:
                activities_stII_incomplete, = numpy.nonzero(matrix[:,ind])
                print "###ERROR### STII Incompleto", activities_stII_incomplete
    print "STII COMPLETO: ", stII_complete
    
    for node_activity in stII_complete:
        stII_node = nodes.next_node()
        stII_complete_successors = numpy.nonzero(matrix[node_activity[0]])
        for activity in node_activity:
            nodes[activity][1] = stII_node
        for successor in stII_complete_successors[0]:
            nodes[successor][0] = stII_node
    
    print nodes
    
    #Step 5. Search for matches
    print "MATRIX: ", matrix
    
#    print "SUCCESSORS: ", successors
#    incomplete_sig = [successors[activity] for act in activities_stII_incomplete]
#    print "INCOMPLETE SIG: ", incomplete_sig
    
    #XXX (Eficiencia) guardar numpy.nonzero(matrix[activity])[0] en una variable en vez de llamar 3 veces?
    if len(stII_incomplete) > 0:
        print "STII INCOMPLETE: ", activities_stII_incomplete
        masc = []
        for activity in activities_stII_incomplete:
            masc.append(numpy.nonzero(matrix[activity])[0])
            if len(numpy.nonzero(matrix[activity])[0]) == 1:
                stII_incomplete_node = nodes.next_node()
                nodes[activity][1] = stII_incomplete_node
                nodes[numpy.nonzero(matrix[activity])[0]][0] = stII_incomplete_node 
                print "ACT: ", activity
                print "LEN numpy.nonzero: ", len(numpy.nonzero(matrix[activity])[0])
        print "MASC: ", masc
        
        print nodes
        npc = []
        incomplete_index = set()
        for m in masc:
            for i_m in m:
                print "i_m: ", i_m
                npc.append(i_m)
                incomplete_index.add(i_m)
        list_incomplete_index = list(incomplete_index)
        print "list_incomplete_index: ", list_incomplete_index
        
        MRA = scipy.zeros([len(list_incomplete_index), len(list_incomplete_index)], dtype = int)
        print "MRA: \n", MRA
        print "npc: ", npc
        print "masc: ", masc
        incomplete_same_node = []
        for l in masc:
            print "L: ", l
            for i in range(0, len(l)):
                print "l[i]FOR[I]: ", l[i]
                for j in range(0, len(l)):
                    if not i == j:
                        MRA[list_incomplete_index.index(l[i])][list_incomplete_index.index(l[j])] += 1
                        print "npc.count(li): ", npc.count(list_incomplete_index[i])
                        print "npc.count(lj): ", npc.count(list_incomplete_index[j])
                        print "MRA[i, j]: ", MRA[i, j]
                        if npc.count(list_incomplete_index[i]) == MRA[i, j] and npc.count(list_incomplete_index[j]) == MRA[i, j]:
                            print "l[i]: ", l[i], "l[j]: ", l[j]
                            print "list_incomplete_index[i]: ", list_incomplete_index.index(l[i])
                            print "list_incomplete_index[j]: ", list_incomplete_index.index(l[j])
                            print "list_incomplete_index[i]OK CUMPLE LAS CONDICIONES: ", list_incomplete_index[i]
                            print "nodes [i][0]: ", nodes[list_incomplete_index[i]][0]
                            if nodes[list_incomplete_index[i]][0] == None:
                                matches_node = nodes.next_node()
                                nodes[list_incomplete_index[i]][0] = matches_node
                                nodes[list_incomplete_index[j]][0] = matches_node
                                print "Pasada IF"
                            else:
                                nodes[list_incomplete_index[j]][0] = matches_node
                                print "Pasada ELSE"
                            incomplete_same_node.append([list_incomplete_index[i], list_incomplete_index[j]])
#                            stII_incomplete_same_node = nodes.next_node()
#                            nodes[list_incomplete_index[i]][0] = stII_incomplete_same_node
#                            nodes[list_incomplete_index[j]][0] = stII_incomplete_same_node
            print "MRA: \n", MRA
            print "incomplete_same_node: ", incomplete_same_node
    print nodes
        
    #Step 6. Search for strings
##    Matrix
##    MNS = scipy.zeros([len(list_incomplete_index), len(list_incomplete_index)], dtype = int)
##    print "MNS: ", MNS
    MNS = {}
    for i in list_incomplete_index:
        print "i: ", i
        MNS[i] = nodes[i][0]
    print "MNS: ", MNS
    MRN = scipy.zeros([len(list_incomplete_index), len(list_incomplete_index)], dtype = int)
    for i in MNS.keys():
        print "i: ", i
    print "MRN: \n", MRN
    print "list incomplete index: ", list_incomplete_index
#    for i in range(0, len(list_incomplete_index)):
#        for j in range(0, len(list_incomplete_index)):
#            if not i == j:
#                print "i,j: ", i, j
#                print "l[i]: ", list_incomplete_index[i]
#                print "list_incomplete_index[i]: ", list_incomplete_index[i]
##                print "list_incomplete_index[j]: ", list_incomplete_index.index(l[j])
#                print "MRA[list_incomplete_index.index([l[i]])]: ", MRA[i, j]
##                print "MRA[list_incomplete_index.index([l[j]])]: ", MRA[list_incomplete_index.index([l[j]])]
#                print "npc.count(l[i]): ", npc.count(list_incomplete_index[i])
##                print "npc.count(lj): ", npc.count(l[j])
#                if npc.count(list_incomplete_index[i]) == MRA[i, j]:
#                    print "list_incomplete_index[i]OK CUMPLE LAS CONDICIONES: ", list_incomplete_index[i]
#    #Contamos las apariciones de cada actividad y comparamos con su valor en MRA
#    for l1 in list_incomplete_index:
#        print "#####"
#        print "npc.count(l1): ", npc.count(l1)
#        print "l1: ", l1
##        print "list_incomplete_index.index(l1): ", list_incomplete_index.index(l1)
#        print "#####"
##        if npc.count(l1) == 
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
        'C' : ['G', 'D'],#G, D
        'D' : ['F'],
        'E' : ['G'],#G
        'F' : [],
        'G' : ['F'],
    }
#    Datos con coincidencias
#    successors1 = {
#        'A' : ['C'],
#        'B' : ['G', 'D', 'F', 'E'],
#        'C' : ['G', 'D', 'F', 'E'],#G, D
#        'D' : [],
#        'E' : [],#G
#        'F' : [],
#        'G' : [],
#        'H' : ['D']#Analizar D, F, E
#    }
    
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
