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
    visited = []
    more_than_once = []
    
    #Step 4. Search standard II(Full) and standard II(Incomplete)
    standard_II = []
    all_successors_visited = []
    more_than_once_all = []
    standard_II_incomplete = []
    
    #Find activities with unique successors and with same successors
    for all_successors in successors.values():
        for element_all_successors in all_successors_visited:
            if len(all_successors) != 0 and set(all_successors) == (set(element_all_successors)):
                if all_successors not in more_than_once_all:
                    more_than_once_all.append(all_successors)
        all_successors_visited.append(all_successors)
        for successor in all_successors:
            if successor in visited and successor not in more_than_once:
                more_than_once.append(successor)
            visited.append(successor)
            
    #For step 3(Standard I) all successor only can appear one time
    for activity, successor in successors.items():
        if not set(more_than_once).intersection(set(successor)) and len(successor) != 0:
            standard_I.append(activity)
    print "standard_I: ", standard_I
    
    #For step 4(Standard II) the same successor for two or more activities
    for activity, successor in successors.items():
        for element_more_than_once_all in more_than_once_all:
            if set(element_more_than_once_all) == set(successor) and activity not in standard_II:
                standard_II.append(activity)
    print "standard_II: ", standard_II
    
    #For step 4.1(Standard II Incomplete)at least one successor of standard II are in other activity not standar II
    for activity, successor in successors.items():
        for suc in more_than_once_all:
            if set(suc).intersection(set(successor)) and activity not in standard_II:
                standard_II_incomplete.append(activity)
    print "standard_II Incompleto: ", standard_II_incomplete
    
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
        'A' : ['D'],
        'B' : ['C', 'D', 'E'],
        'C' : ['F'],
        'D' : ['G'],
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
