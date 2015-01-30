#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scipy
import numpy
import collections
import itertools

import graph
import pert
import Kahn1962

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

    def __len__(self):
        return len(self.node_list)
    
    def __getitem__(self, key):
        return self.node_list[key]
    
    def next_node(self):
        """Creates a new node number"""
        self.last_node_created += 1
        return self.last_node_created

    def append_dummy(self, begin, end):
        self.node_list.append( [begin, end] )

    def new_dummy(self):# XXX are we usign this?
        """Creates a new dummy activity and return its index"""
        self.node_list.append( [None, None] )
        return len(self.node_list) - 1

def gento_municio(predecessors):
    """
    """
    successors = graph.reversed_prelation_table(predecessors)
    #Generate precedences/successors matrix
    num_real_activities = len(successors.keys())
    matrix = scipy.zeros([num_real_activities, num_real_activities], dtype = int)
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
    # Step 1. Search initial activities (have no predecessors) [3.1] 
    beginning, = numpy.nonzero(sum_predecessors == 0)
    print "Beginning: ", beginning
    
    # add begin node to activities that begin at initial node
    begin_node = nodes.next_node()
    for node_activity in beginning:
        nodes[node_activity][0] = begin_node
    
    # Step 2. Search endings activities (have no successors) [3.2]
    ending, = numpy.nonzero(sum_successors == 0)
    print "Ending: ", ending
    #XXX Igual a STII si mas de una actividad (no es necesario este paso) stI no lo considera???
    #Add end node to activities that end in final node
    end_node = nodes.next_node()
    for node_activity in ending:
        nodes[node_activity][1] = end_node
    print nodes

    # Step 3. Search standard type I (Activity have unique successors) [3.3]
    act_one_predeccessor, = numpy.nonzero(sum_predecessors == 1)
    stI = collections.defaultdict(list)
    for i in act_one_predeccessor:
        pred = numpy.nonzero((matrix[:,i]))[0][0]
        if (sum_successors[pred] == 1 # this condition is redundant but faster than the following check
            or sum_successors[pred] == scipy.sum(matrix[:,numpy.nonzero(matrix[pred])]) ):
            stI[pred].append(i)
            # XXX This may be faster if first pred introduced on dict and then remove those pred that have more successors in sum_successors than values in this dict
    print "stI: ", stI
    #Add the same end node of activities to the begin node of its successors activities
    for node_activity in stI:
        stI_node = nodes.next_node()
        nodes[node_activity][1] = stI_node
        for successor in stI[node_activity]:
            nodes[successor][0] = stI_node
    print nodes


    #Step 4. Search standard II(Full) and standard II(Incomplete) [3.4]
    print "--- Step 4 ---"
    # dictionary with key: equal successors; value: mother activities
    stII = collections.defaultdict(list)

    for act in range(num_real_activities):
        stII[frozenset(matrix[act].nonzero()[0])].append(act) 

    # remove ending activities and those included in type I
    del(stII[ frozenset([]) ]) 
    for pred, succs in stI.items():
        del(stII[ frozenset(succs) ])

    # assigns nodes to type II as indicated in figure 8
    mark_complete = []
    for succs, preds in stII.items():
        u = len(preds)
        # if NP[succs] != u (complete)
        print preds, '->', succs,
        if not [ i for i in succs if sum_predecessors[i] != u ]:
            print 'complete'
            mark_complete.append(succs)
            node = nodes.next_node()
            for act in preds:
                nodes[act][1] = node
            for act in succs:
                nodes[act][0] = node
        else: # (incomplete)
            print 'incomplete'
            node = nodes.next_node()
            for act in preds:
                nodes[act][1] = node
    print nodes

    # Step 5. Search for matching successors [3.5]
    print "--- Step 5 ---"
    # remove type II complete so that stII becomes MASC
    for succs in mark_complete:
        del stII[succs]
    masc = stII

    print "MASC"
    for succs, preds in stII.items():
        print preds, succs

    npc = collections.defaultdict(int)  # XXX Puede usarse un vector mejor
    for succs, preds in masc.items():
        num_preds = len(preds)
        for succ in succs:
            npc[succ] += num_preds
    print npc

    # Step 6. Identifying start nodes on matching successors
    print "--- Step 6 ---"
    act_no_initial = [i for i in range(num_real_activities) if nodes[i][0] == None]
    print act_no_initial, "<- No initial node"
    num_no_initial = len(act_no_initial)

    mra = scipy.zeros([num_no_initial, num_no_initial], dtype = int)
    for succs, preds in masc.items():
        num_preds = len(preds)
        for act_i, act_j in itertools.combinations(succs, 2):
            mra[act_no_initial.index(act_i), act_no_initial.index(act_j)] += num_preds
            mra[act_no_initial.index(act_j), act_no_initial.index(act_i)] += num_preds # Symmetry, any succ order
    print 'MRA'
    print mra

    # check matching successors and assign them initial nodes
    for i in range(num_no_initial):
        for j in range(i+1, num_no_initial):
            if mra[i,j] == npc[act_no_initial[i]] and mra[i,j] == npc[act_no_initial[j]]: 
                print 'coincidencia', i, j, "(", act_no_initial[i], act_no_initial[j], ")"
                if nodes[act_no_initial[i]][0] != None:
                    node = nodes[act_no_initial[i]][0]
                else:
                    node = nodes.next_node()
                    nodes[act_no_initial[i]][0] = node
                nodes[act_no_initial[j]][0] = node               

    # assign initial node to the remaining activities (they must be alone, interpreted, not clear on paper)
    for node in nodes:
        if node[0] == None:
            node[0] = nodes.next_node()

    print nodes

    # Step 7. String search
    # create MNS (to avoid counting matching successors twice)
    mns = {}
    unconnected = set() # all nodes in MNS
    for succs, preds in masc.items():
        succ_nodes = set([nodes[succ][0] for succ in succs])
        mns[ nodes[preds[0]][1] ] = succ_nodes  # as all preds have same successors they will be usign just one node
        unconnected.update(succ_nodes)

    print 'MNS'
    for pred, succs in mns.items():
        print pred, '-', succs

    # create MRN
    unconnected = list(unconnected)
    num_unconnected = len(unconnected)
    print unconnected, '<-Unconnected'

    appear = scipy.zeros([num_unconnected], dtype=int)
    mrn = scipy.zeros([num_unconnected, num_unconnected], dtype=int)    
    for pred, u_nodes in mns.items():
        for node in u_nodes:
            appear[ unconnected.index(node) ] += 1
        for node_a, node_b in itertools.combinations(u_nodes, 2):
            mrn[unconnected.index(node_a), unconnected.index(node_b)] += 1
            mrn[unconnected.index(node_b), unconnected.index(node_a)] += 1
    print 'MRN'
    print mrn
    print 'Appear'
    print appear

    # create MC
    mc = []
    for i in range(num_unconnected):
        mc.append([j for j in range(num_unconnected) if mrn[i,j] == appear[i] ])

    print 'MC'
    for i in range(num_unconnected):
        print i, '-', mc[i]

    # use strings to connect nodes
    next_dummy = 0
    for i in range(num_unconnected):
        following_nodes = sorted([ (len(mc[j]), j) for j in mc[i] ])
        while following_nodes:
            print following_nodes
            num, follower = following_nodes.pop()
            if num == 0: pass

            # Create dummy i -> follower (unconnected to real)
            relation.append('dummy' + str(next_dummy))            
            next_dummy += 1
            nodes.append_dummy(unconnected[i], unconnected[follower])
            for fol_follower in mc[follower]:
                following_nodes.remove( (len(mc[fol_follower]), fol_follower) )
                
    print nodes

    # Step 8. Final nodes and dummies
    # (note: contrary to what paper says, we have already set final nodes for all
    #  activities in step 4 as indicated in figure 8. Nevertheless, these nodes are
    #  unconnected so we replace them here if necessary. Not assigning nodes in step 4
    #  would break step 7)
    for succs, preds in masc.items():
        print "Studying:", preds, '->', succs
        if len(succs) == 1: # Case I
            print "Case I"
            for pred in preds:
                nodes[pred][1] = nodes[next(iter(succs))][0]
        else:
            # Get follower with lower npc
            min_follower = None
            min_npc = None
            for succ in succs:
                if min_npc == None or min_npc > npc[succ]:
                    min_follower = succ
                    min_npc = npc[succ]
            print min_follower, 'npc:', min_npc

            # Count the number of masc rows containing our successor activities
            count = 0
            for others in masc:
                if succs.issubset(others):
                    count += len(masc[others])  # XXX o hay que tener en cuenta len(preds)???
                    
            if count >= min_npc: # Case II (if min_npc==1) and Case III             
                print "Case II or III"
                for pred in preds:
                    nodes[pred][1] = nodes[min_follower][0]
                


    # Step 9. Final nodes for type II incomplete
    # (note: they have already been assigned in step 8. We do not understand section 3.9
    #  of the paper)



    # Build PertGraph (creating dummy activities for parallel activities)
    pm_graph = pert.PertMultigraph()
    for i in range(num_real_activities):
        pm_graph.add_arc((nodes[i][0], nodes[i][1]), (relation[i], False))

    for i in range(num_real_activities, len(nodes)):
        pm_graph.add_arc((nodes[i][0], nodes[i][1]), (relation[i], True))

    p_graph = pm_graph.to_directed_graph()
    return p_graph#.renumerar()



# --- Start running as a program
if __name__ == '__main__': 
    
    successors = { # with redundancy
        'A' : ['D'],
        'B' : ['C', 'E'],
        'C' : ['F'],
        'D' : ['G'],
        'E' : [],
        'F' : ['D', 'E'],
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
    # Datos con coincidencias
    successors2 = {
        'A' : ['C'],
        'B' : ['G', 'D', 'F', 'E'],
        'C' : ['G', 'D', 'F', 'E'],#G, D
        'D' : [],
        'E' : [],#G
        'F' : [],
        'G' : [],
        'H' : ['D']#Analizar D, F, E
    }
    
    # Datos con multiples stI
    successors3 = {
        'A' : ['C', 'E'],
        'B' : ['G', 'D'],
        'C' : ['G', 'D'],
        'D' : ['F'],
        'E' : ['G'],
        'F' : ['B'],
        'G' : ['F'],
    }
    
    # Datos con un stI de 3 actividades y dos casos casi stI (dos predecesores) y (pred compartido)
    successors4 = {
        'A' : ['B', 'C', 'D'],
        'B' : [],
        'C' : [],
        'D' : [],
        'E' : ['F'],
        'F' : [],
        'G' : ['F', 'H'],
        'H' : [],
    }

    # Coincidencias successors2 sin E en B
    successors5 = {
        'A' : ['C'],
        'B' : ['G', 'D', 'F'],
        'C' : ['G', 'D', 'F', 'E'],#G, D
        'D' : [],
        'E' : [],#G
        'F' : [],
        'G' : [],
        'H' : ['D']#Analizar D, F, E
    }

    # Coincidencias successors2 con R
    successors6 = {
        'A' : ['C'],
        'B' : ['G', 'D', 'F', 'E'],
        'C' : ['G', 'D', 'F', 'E'],#G, D
        'D' : [],
        'E' : [],#G
        'F' : [],
        'G' : [],
        'H' : ['D','R'],#Analizar D, F, E
        'R'  : [],
    }

    # Ejemplo con las cadenas del articulo
    successors7 = {
        'Ai' : ['C'],
        'Aj' : ['D'],
        'Ak' : ['B', 'C', 'D'],
        'Al' : ['A', 'B', 'C', 'D'],
        'A' : [],
        'B' : [],
        'C' : [],
        'D' : ['R'],
        'R'  : [],

    }

    successors8 = { # similar to 0 without redundancy
        'A' : ['D'],
        'B' : ['C', 'E'],
        'C' : ['F'],
        'D' : ['G'],
        'E' : [],
        'F' : ['D', 'L'],
        'G' : ['H'],
        'H' : ['E'],
        'I' : ['H'],
        'J' : ['H'],
        'K' : ['A', 'B', 'I', 'J'],
        'L' : [],
    }


    tab = successors8
    if Kahn1962.check_cycles(tab):
        gg1 = gento_municio(tab)
        import graph
        import validation
        window = graph.Test()
        window.add_image(graph.pert2image(gg1))
        graph.gtk.main()
        print gg1
        print validation.check_validation(tab, gg1)
    else:
        print "Example contains cicles!!"



    
##ACLARACION FUNCIONAMIENTO##
#Para el tipo II incompleto. Si una o varias actividades tienen las mismas siguientes, pero alguna o algunas de las siguientes son precededidas por alguna más, entonces es seguro que: 

#El nudo inicio de las que no tienen otra precedente es el mismo nudo de fin de las que tienen las mismas siguientes... y.
#Del nudo fin de las que tienen las mismas siguientes sale al menos una ficticia que va al nudo inicio de las que tienen más precedentes. Ahora habría que analizar si las que tienen otras precedentes tienen precedentes comunes o no comunes y sería como el tipo I (o no).


#El patrón coincidencias sirve para saber seguro cuándo hay ficticias. Una vez que se sabe eso, el patrón tipo II incompleto y el de cadenas, te ayuda a optimizar.
