"""
MOUHOUB ALGORITHM RULES 
Remove dummy arcs to build a graph with minimal dummy activities according to the Mouhoub algorithm rules
"""

from collections import Counter

separator = '|'

    
def rule_1(work_table_suc, work_table, Columns):
    """
    # Rule 1 - For each subgraph with common and uncommon predecessors activities, contract end vertices in one vertex

   """      
    visited = []
    remove = set()
    for act, arcs in work_table_suc.items():
        for act2, arcs2 in work_table_suc.items():
            common = set(arcs) & set(arcs2)
            not_common = set(arcs) ^ set(arcs2)
            
            # Join nodes when two activities have common successors and uncommon successors activities
            if not not_common and act != act2 and len(common) > 1 and act not in visited:
                delete = work_table[act2].end_node
                work_table[act2].end_node = work_table[act].end_node 
                visited.append(act2)
                    
                for y, pred in work_table.items():
                    if pred.start_node == delete:
                        pred.aux = True
                        work_table[act2].su = work_table[act].su
                        work_table[act2].suc = work_table[act].suc
                        
                        remove.add(y)
                                       
    # Save the graph after the modification. Input graph G1 results graph G2
    work_table_G1 = {}
    for act, sucesores in work_table.items():
        if sucesores.aux != True:
            if sucesores.pre != None:
                for u in remove:
                    if u in sucesores.pre:
                        sucesores.pre = set(sucesores.pre) - set([u])
            work_table_G1[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, sucesores.aux)

    return work_table_G1
    
   
    
    
def rule_2(work_table_pred, work_table, work_table_G1, Columns):
    """
    # Rule 2 - For each subgraph with common and uncommon successor activities, contract end vertices in one vertex
     return work_table_G2
   """
    visited = []
    remove = set()
    
    for act, arcs in work_table_pred.items():
        for act2, arcs2 in work_table_pred.items():
            common = set(arcs) & set(arcs2)
            not_common = set(arcs) ^ set(arcs2)
            
            # Join nodes when two activities have common predecessor and uncommon predecessor activities
            if not not_common and act != act2 and len(common) > 1 and act not in visited:
                eliminar = work_table[act].start_node
                work_table[act].start_node = work_table[act2].start_node 
                visited.append(act2)
                
                for y in work_table[act].pre:
                    if work_table[y].end_node == eliminar:
                        remove.add(y)
                        work_table[y].aux = True
                        work_table[y].suc = work_table[act].su
                            
    # Save the graph after the modification. Input graph G results graph G1
    work_table_G2 = {}
    for act, columns in work_table_G1.items():
        if columns.aux != True and act not in remove:
            if columns.su != None:
                for u in remove:
                    if u in columns.su:
                        columns.su =  list(set(columns.su) - set([u]))
                        
            work_table_G2[act] = Columns(columns.pre, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, columns.aux)

    return work_table_G2
    


def rule_3(work_table_G2, work_table, Columns):
    """
    # Rule 3 - If a vertex X has one predecessor vertex Y, then contract both vertices in one vertex and delete the resulting loop
      return work_table_G3
    """
    
    for act, arcs in work_table_G2.items():
        if len(arcs.pre) == 1:
            extra = set(arcs.pre).pop()
            
            # Contract node with only one dummy predecessor
            if work_table[extra].dummy == True:
                v = str(extra).partition(separator)
                work_table[v[2]].start_node = work_table[v[0]].end_node 
                work_table[extra].aux = True
                    
    # Save the graph after the modification. Input graph G2 results graph G3
    work_table_G3 = {}
    for act, columns in work_table.items():
        if columns.aux != True:
            work_table_G3[act] = Columns(columns.pre, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, columns.aux)

    return work_table_G3



def rule_4(work_table_G3, work_table, Columns):
    """
    # Rule 4 - If a vertex X has one successor vertex Y, then contract both vertices in one vertex and delete the resulting loop
      return work_table_G4
    """
    work_table_G4 = work_table
    for act, arcs in work_table_G3.items():
        if arcs.su != None and len(arcs.su) == 1:
            extra = set(arcs.su).pop()
                
            # Contract node with only one dummy successor
            if work_table[extra].dummy == True:
                
                    v = str(extra).partition(separator)
                    
                    work_table[v[0]].end_node = work_table[v[2]].start_node 
                    work_table_G4[extra].aux = True

                    
                    for act2, arcs2 in work_table_G3.items():
                        if arcs2.su == arcs.su:
                            work_table[act2].end_node = work_table[v[2]].start_node 
    
    # Save the graph after the modification. Input graph G3 results graph G4                 
    work_table_G4 = {}
    for act, columns in work_table.items():
        if columns.aux != True:
            work_table_G4[act] = Columns(columns.pre, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, None)

    return work_table_G4


def rule_5_6(work_table_suc, work_table, work_table_G4, Columns):
    """
    # Rule 5 - If successors of x are a superset of successors of y, then delete common activities and connect with a dummy arc from x to y
    # Rule 6 - If predecessors of x are a superset of predecessors of y, then delete common activities and connect with a dummy arc from x to y
      return work_table_G5_G6
    """
    visited = []
    new = set()
    remove = set()
    snode = []
    svertex = []
    
    for act, arcs1, in reversed(sorted(work_table_suc.items())):
        for act2, arcs2, in work_table_suc.items():
            
            # Update prelations if a subgraph is a subset 
            if len(arcs1) > 0 and act2 not in visited and set(arcs1).issubset(set(arcs2)) and act != act2 and len(arcs1) + 1 == len(arcs2):
                common = set(arcs1) & set(arcs2)
                not_common = set(arcs1) ^ set(arcs2)
                new = set(work_table_G4[act2].su)
                        
                for u in common:
                    work_table[d_node(act2, u)].aux = True
                    remove.add(d_node(act2, u))
                    new.discard(d_node(act2, u))

                for u in not_common:
                    new.add(d_node(act2, u))    
                    
                if act not in snode and work_table_G4[act2].end_node not in svertex:
                    work_table[d_node(act2, act)] = Columns(work_table_G4[act2].pre, arcs1, act, True, None, work_table_G4[act2].end_node, work_table_G4[act].end_node, False)
                    new.add(d_node(act2, act))
                    work_table[act2].su = list(new)
                    work_table[act2].aux = False
                    svertex.append(work_table_G4[act2].end_node)
                    visited.append(act2)

    # Save the graph after the modification. Input graph G4 is concerted in graph G5/G6 
    work_table_G5_G6 = {}
    for act, columns in work_table.items():
        if columns.aux != True:
            pred = set(columns.pre)
            for q in columns.pre:
                if q in remove:
                    pred.discard(q)
            work_table_G5_G6[act] = Columns(pred, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, columns.aux)
    
    return work_table_G5_G6



    
def rule_7(successors_copy, successors, work_table, Columns, node):
    """
    # Rule 7 - If (A,B) is a maximal partial bipartite subgraph, then build a star with their common dummy arcs
      return work_table_G7
    """
    left = set()
    visited = [] 
    
    #Store start node numbers of ecg predecssor in column aux
    for act, columns in work_table.items():
        snodes = set()
        
        if columns.dummy == False:
            for r in columns.pre:
                if r in r in work_table:
                    snodes.add(work_table[r].start_node)

        if snodes:
            work_table[act].aux = list(snodes) 

    #
    for act, columns in work_table.items():
        com_nodes = []
        for act2, columns2 in work_table.items():
            if columns2.aux != None and columns.aux != None:
                common = set(columns.aux) & set(columns2.aux)
                    
                if len(common) > 1 and act != act2 and act not in visited:
                    visited.append(act2)
                    
                    for p in common:
                        com_nodes.append(p)
                            
        if com_nodes != []:     
                maximal = list(Counter(com_nodes).most_common(1)[0]).pop()
                
                if maximal > 1:
                    a_set = []
                    diccy = Counter(com_nodes)
                    
                    for j, va in dict(diccy).items():
                        if va == maximal:
                            a_set.append(j)
                    
                    #
                    if len(a_set) >= 2:
                        b_set = []
                        maxco = False
                        temp_com = set()
                        
                        for act3, columns3 in work_table.items():
                            if columns3.end_node in a_set and columns3.dummy != True:
                                b_set.append(act3)
                       
                        for f in b_set:
                            for g in b_set:
                                if f != g:
                                    common = set(successors_copy[f]) & set(successors_copy[g])
                                    
                                    if temp_com.issuperset(common):
                                        temp_com = temp_com
                                        if len(temp_com) > len(common):
                                            temp_com = temp_com & common
                                    elif maxco == False:
                                        temp_com = common
                                        maxco = True
                                    else:
                                        temp_com = temp_com & common
                        
                        #
                        if len(temp_com) + len(common) >= 6:
                            for q in b_set:
                                work_table[d_node(q, node)] = Columns([q], None, None, True, str(node), work_table[q].end_node, node, None)
                                    
                                for l in temp_com:
                                    for y in successors[q]:
                                        if str(y).find(separator) != -1:
                                            re1 = str(y).partition(separator)
                                            
                                            if re1[2] in temp_com:
                                                left.add(y)
                                        else:
                                            if y in temp_com:
                                                left.add(y)
                            
                            #
                            for t in temp_com:
                                work_table[d_node(node, t)] = Columns(None, None, None, True, t, node, work_table[t].start_node, None)
                            
                            node += 1

    # Save the graph after the modification. Input graph G5/G6 results graph G7     
    work_table_G7 = {}
    for act, columns in work_table.items():
        if act not in left:
            work_table_G7[act] = Columns(columns.pre, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, None)
    
    return work_table_G7
    



def d_node(x, y):
    node = str(x) + separator + str(y)
    
    return node