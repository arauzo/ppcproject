#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algorithm to build a PERT graph according to the Salas method

Copyright 2007-15 University of Cordoba (Spain)
"""

import pert
import graph


def salas(prelations):
    """
    Create a PERT graph according to the Lorenzo Salas method
    
    prelations = {'Act': ['Predecessor1','Predecessor2'], ... }
    """
    
    matrix,premat = create_matrix(prelations)
    m, t, af, ai, ami, amiD, amf, amfD = previous(matrix)

    a = len(m)
    b = len(m)                    
    visited = []

    d = {}                    
    for i in range(a):
        d[i] = [0,0]        


    # Initialize a dictionary of activities
    cont = 1                    
    for i in ai:            
        cont = cont + 1
        d[i] = [1, cont]
        visited.append(i)    

    d1 = d.copy() 
    X = 0
    
    while len(visited) < b:
        positions = []                # List that contains the positions of the following activities to the activity X 
                                      # if this activity has end node and beginning node
        if d1[X][0] > 0 and d1[X][1] > 0:    
            cont1 = -1   
 
            for j in m[X]:
                cont1 = cont1 + 1
                if j == 1:
                    positions.append(cont1)

            for k in positions:
                if k not in visited:
                    # If activity 'k' has only one predecesor (only one 1 in the column)
                    if t[k].count(1) == 1:
                        # If activity 'k' is not a key in amfD dictionary (It is not activity with same end), 
                        # cont +1 and set beginning node of activity 'k' the end node of activity X and cont as end node
                        if k not in amfD:
                            cont = cont + 1                
                            d1[k] = [d1[X][1],cont] 
                        # If activity 'k' is key in amfD dictionary
                        else:
                            # If end node of the activity 'k' is 0, 
                            # cont +1 and set beginning node of activity 'k' the end node of activity X and cont as end node
                            if d1[k][1] == 0:
                                cont = cont + 1                
                                d1[k] = [d1[X][1],cont]
                            # If activity 'k' is not 0
                            # cont +1 and set beginning node of activity 'k' the end node of the activity X
                            else:
                                d1[k][0] = d1[X][1]
                            # Find activities with same end that activity 'k' and set the same end node to activity 'k' if its node is 0   
                            for l in amfD[k]:
                                if d1[l][1] == 0:
                                    d1[l][1] = cont
                        visited.append(k)  
                        
                    # If activity 'k' has more than one 1 in the column 
                    elif t[k].count(1) > 1:
                        mi = 0    # mi = 0, it is not an activity with same beginning                        
                        base = []
                        # Find in ami list the activity 'k' and set the activities with same beginning node that 'k' as base
                        for l in ami:
                            if k in l and k not in visited:
                                mi = 1
                                base = l
                        # if mi = 0, insert the activity 'k'
                        if mi == 0:
                            base.append(k)
                        pospre = []                    
                        cont1 = -1
                        # Find in the columns formed by base and if there is some 1 (it is predecessor),
                        # insert in pospre the position of that predecessor activity
                        for n in t[base[0]]:
                            cont1 = cont1 + 1
                            if n == 1:
                                pospre.append(cont1)
                        # in some predecessor activity there are not in visited, continue to the next activity in positions list
                        insert = 1
                        for n in pospre:
                            if n not in visited:
                                insert = 0
                        # If insert = 1, insert into visited the activities that belong to base
                        if insert == 1:
                            if mi == 1:
                                for p in base:
                                    visited.append(p)
                            if mi == 0:
                                visited.append(k)
                            equal = -1        
                            cont1 = -1         
                            equalL = []        
                            
                            # Find the activities of base predecessors and insert into nex_pre these activities
                            for o in pospre:
                                cont1 = -1
                                next_pre = []        
                                for p in m[o]:
                                    cont1 = cont1 + 1
                                    if p == 1:
                                        next_pre.append(cont1)
                                        
                                # Sort next_pre and base
                                next_pre.sort()
                                base.sort()
                                if next_pre == base:
                                    equal = o
                                    equalL.append(o)

                            # If some predecessor activity whose activities are the same               
                            if equal > -1:
                                amfA = []            #  List ofactivities with same end
                                              
                                for p in pospre:
                                    if m[p].count(1) > 1:
                                        if equal != p and p not in amfA:
                                            # Insert dummy activity
                                            d1[a] = [d1[p][1], d1[equal][1]]
                                            a = a + 1
        
                                            if p in amfD:
                                                for u in amfD[p]:
                                                    amfA.append(u)
                                                    
                                # Find on base the same activities
                                for p in base:
                                    # If activity 'p' is not the same end, set node of the activity 'p'  
                                    if p not in amfD:
                                        cont = cont + 1
                                        d1[p] = [d1[equal][1], cont]
                                    # If activity 'p' has the same end
                                    else:
                                        # If the end node of the activity 'p' is not assigned, set 'p' with beginning node, end node
                                        if d1[p][1] == 0:
                                            cont = cont + 1
                                            d1[p] = [d1[equal][1], cont]
                                            
                                        # If the end node of the activity 'p' is assigned, and end node of the equal activity is not assigned. 
                                        # set beginnig node of the activity 'p' into the end node of the equal activity
                                        else:
                                            if d1[equal][1] == 0:
                                                # Find activities that could be equals and they have assigned an end node
                                                for l in equalL:
                                                    if l != equal and d1[l][1] > 0:
                                                        equal = l
                                            d1[p][0] = d1[equal][1]
                                        # Find activities with same end node of the acivity 'p' if its end node is 0
                                        for l in amfD[p]:
                                            if d1[l][1] == 0:
                                                d1[l][1] = cont
                                                
                            # If there are no predecessor activity whose following activities are equal to base         
                            else:
                                path = 0     # If path = 1 it is no necessary dummy activities
                                # Find activities with same end
                                # Sort the lists, and if they are equal to pospre, it is no necessary dummy activities                
                                for l in amf:
                                    l.sort()
                                    if pospre == l:
                                        path = 1
                                # If path=0, predeccesors are not activities with same end
                                # Insert a new node and set predecessors nodes to a new node
                                if path == 0:
                                    cont = cont + 1
                                    ff = cont
                                    for p in pospre:
                                        d1[a] = [d1[p][1], cont]
                                        a = a + 1
                                    for p in base:
                                        cont = cont + 1
                                        d1[p] = [ff, cont]
                                        # Find all activities with same end that activity 'p' and set the same node if its end node is 0 
                                        if p in amfD:
                                            for l in amfD[p]:
                                                d1[l][1] = cont
                                # If path = 1 it is no necessary dummy activities
                                else:
                                    for p in base:
                                        cont = cont + 1
                                        d1[p] = [d1[X][1],cont]
                                        # Find all activities with same end that activity 'p' and set the same node if its end node is 0 
                                        if p in amfD:
                                            for l in amfD[p]:
                                                d1[l][1] = cont
        X = X + 1    
        if X == b:
            X = 0
    
    d2 = d1.copy()
    d2 = settings(d1, cont, a, af, b)
    
    # Build graph

    graph = pert.Pert()

    for i in d2.iteritems():
        tuple = i[1][0], i[1][1]        
        if i[0] < b:
            tuple1 = premat[i[0]], False
            graph.add_arc(tuple, tuple1)
        else:
            if tuple[0] != tuple[1]:
                tuple1 = str(tuple[0]) + '-' + str(tuple[1]), True
                graph.add_arc(tuple, tuple1)

    return graph
    
    

def create_matrix(prelations):
    """
    Create a matrix chain of the prelation table
    
    prelations = {'Act': ['Predecesora1','Predecesora2'], ... }
    
    Return 'm' (matrix chain) and 'premat' (ID for each row of the matrix)
    """
    m = []
    premat = {} 
    cont = 0
    for i in prelations.iteritems():
        premat[cont] = i[0]
        cont = cont + 1
        mf = []
        actividad = i[0]
        for j in prelations.iteritems():
            if actividad in j[1]:
                mf.append(1)
            else:
                mf.append(0)
        m.append(mf)

    return m, premat
    
    

def previous(matrix):
    """
    Make some operation on the matrix to obtain the following variables.
    
    Return:
        - matrix chain
        - traspose matrix
        - ending activities list
        - beginning activities list
        - Lis of lists of the activities with same beginning
        - Dictionary with same beginning
        - Lis of lists of the activities with same end
        - Dictionary with same end
    """

    m = matrix
    a = len(m)    # len of the matrix
    # Store the traspose matrix
    t = []        
    for i in range(a):
        ini = []
        for j in range(a):
            ini.append(m[j][i])
        t.append(ini)

    # Store ending activities
    af = []
    for i in range(a):
        if 1 not in m[i]:
            af.append(i)

    # Store beginning activities
    ai = []
    for i in range(a):
        if 1 not in t[i]:
            ai.append(i)


    amiD = {}       # Dictionary whose keys have same beging node 
                 
    inc = []        
    ami = []
    for i in range(a):
        ci = []
        if i not in inc:
            for j in range(a):
                if j > i and t[i] == t[j] and 1 in t[i]:
                    ci.append(j)
                    inc.append(j)
            if len(ci) > 0:
                ci.append(i)
                ami.append(ci)

        for j in ci:
            amiD[j] = []
            for k in ci:
                if j != k:
                    amiD[j].append(k)

    amfD = {}        # Dictionary whose keys have same ending node 
               
    inc = []       
    amf = []  
      
    for i in range(a):
        fi = []   
        if i not in inc:
            for j in range(a): 
                if j > i and m[i] == m[j]:
                    fi.append(j)
                    inc.append(j)
            if len(fi) > 0:
                fi.append(i)
                amf.append(fi)

        for j in fi:
            amfD[j] = []
            for k in fi:
                if j != k:
                    amfD[j].append(k)
    
    return m, t, af, ai, ami, amiD, amf, amfD


def settings(d, cont, a, af, b):
    """
    Method to make some operations into the dictionary

    Return 'd' (modified dictionary)
    """

    # Set end nodes
    nf = af[0]
    for j in af:    
        if d[nf][1] != d[j][1]:
                d[j][1] = d[nf][1]

    d1 = d.copy()

    # Remove redundancy
    visited = []
    for i in d1.iteritems():
        for j in d1.iteritems():
            if i[0] != j[0] and i[0] >= b and j[0] >= b and i[0] not in visited:
                if d1[i[0]] == d1[j[0]]:
                    visited.append(j[0])
                    del d[j[0]]    
    # Add dummy activities and set activities with same begin node and same en node   
    visited = []
    for i in d1.iteritems():
        for j in d1.iteritems():
            if i[0] != j[0] and i[0] < b and j[0] < b and d1[i[0]] == d1[j[0]] and i[0] not in visited:
                i[0], j[0]
                cont = cont + 1
                d[a]=[d[i[0]][0], cont]
                d[j[0]] = [cont, d[i[0]][1]]
                a = a + 1
                visited.append(j[0])
    return d




# If the program is run directly
window = None

if __name__ == "__main__":

    window = graph.Test() 

    gg = salas(graph.prelations4)
    image1 = graph.pert2image(gg)

    window.images.append(image1)
    graph.gtk.main()

