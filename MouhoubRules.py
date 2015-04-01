"""
MOUHOUB ALGORITHM RULES 
Remove dummy arcs to build a graph with minimum dummy activities according to the Mouhoub algorithm rules
"""
separator = '-'

def rule_1(work_table_pred, work_table, Columns):
    """
    # Rule 1 - For each subgraph with common and uncommon successor activities, contract end vertices in one vertex
     return work_table_G1
   """
    visited = []
    remove = set()
    
    for vertex1, arcs in work_table_pred.items():
        for vertex2, arcs2 in work_table_pred.items():
            common = set(list(arcs.pre)) & set(list(arcs2.pre))
            not_common = set(list(arcs.pre)) ^ set(list(arcs2.pre))
            
            # Join nodes when two activities have common predecessor and uncommon predecessor activities
            if common and not not_common and vertex1 != vertex2:
                if len(common) > 1 and vertex1 not in visited:
                    eliminar = work_table[vertex1].start_node
                    work_table[vertex1].start_node = work_table[vertex2].start_node 
                    visited.append(vertex2)
                    
                    for y in work_table:
                        if work_table[y].end_node == eliminar:
                            remove.add(y)
                            work_table[y].aux = True
                            
    # Save the graph after the modification. Input graph G results graph G1
    work_table_G1 = {}
    for act, sucesores in work_table.items():
        if sucesores.aux != True:
            if sucesores.su != None:
                for u in remove:
                    if u in sucesores.su:
                        sucesores.su =  list(set(sucesores.su) - set([u]))
            work_table_G1[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, sucesores.aux)

    return work_table_G1
    
    
def rule_2(work_table_suc, work_table, work_table_G1, Columns):
    """
    # Rule 2 - For each subgraph with common and uncommon predecessors activities, contract end vertices in one vertex
    """      
    visited = []
    remove = set()
    
    for vertex1, arcs in work_table_suc.items():
        for vertex2, arcs2 in work_table_suc.items():
            common = set(list(arcs.pre)) & set(list(arcs2.pre))
            not_common = set(list(arcs.pre)) ^ set(list(arcs2.pre))
            
            # Join nodes when two activities have common successors and uncommon successors activities
            if common and not not_common and vertex1 != vertex2:
                if len(common) > 1 and vertex1 not in visited:
                    delete = work_table[vertex2].end_node
                    work_table[vertex2].end_node = work_table[vertex1].end_node 
                    visited.append(vertex2)
                    
                    for y in work_table:
                        if work_table[y].start_node == delete:
                            work_table[y].aux = True
                            remove.add(y)
            
    # Save the graph after the modification. Input graph G1 results graph G2
    work_table_G2 = {}
    for act, sucesores in work_table_G1.items():
        if sucesores.aux != True:
            if sucesores.pre != None:
                for u in remove:
                    if u in sucesores.pre:
                        sucesores.pre = set(sucesores.pre) - set([u])
            work_table_G2[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, sucesores.aux)

    return work_table_G2
    

def rule_3(work_table_G2, work_table, Columns):
    """
    # Rule 3 - If a vertex X has one predecessor vertex Y, then contract both vertices in one vertex and delete the resulting loop
    """
    
    for vertex1 in sorted(work_table_G2.keys()):
        if len(work_table_G2[vertex1].pre) == 1:
            extra = set(work_table_G2[vertex1].pre).pop()
            
            # Contract node with only one dummy predecessor
            if work_table[extra].dummy == True:
                v = str(extra).partition(separator)
                if work_table[v[2]].start_node != work_table[v[0]].end_node:
                    work_table[v[2]].start_node = work_table[v[0]].end_node 
                    work_table[extra].aux = True
                    
    # Save the graph after the modification. Input graph G2 results graph G3
    work_table_G3 = {}
    for act, sucesores in work_table.items():
        if sucesores.aux != True:
            work_table_G3[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, sucesores.aux)

    return work_table_G3



def rule_4(work_table_G3, work_table, Columns):
    """
    # Rule 4 - If a vertex X has one successor vertex Y, then contract both vertices in one vertex and delete the resulting loop
    """
    visited = []
    
    for vertex1, arcs in work_table_G3.items():
        if arcs.su != None and vertex1 not in visited:
            if len(arcs.su) == 1:
                extra = set(arcs.su).pop()
                
                # Contract node with only one dummy successor
                if work_table[extra].dummy == True:
                    v = str(extra).partition(separator)
                    if work_table[v[0]].end_node != work_table[v[2]].start_node:
                        work_table[v[0]].end_node = work_table[v[2]].start_node 
                        work_table[extra].aux = True
    
    # Save the graph after the modification. Input graph G3 results graph G4                 
    work_table_G4 = {}
    for act, sucesores in work_table.items():
        if sucesores.aux != True:
            work_table_G4[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, sucesores.aux)

    return work_table_G4


def rule_5_6(work_table_suc, work_table, work_table_G4, Columns):
    """
    # Rule 5 - If the successors of x are a superset of the successors y, then delete common activities and connect with a dummy arc from x to y
    # Rule 6 - 
    """
    visited = []
    new = set()
    remove = set()
    
    for vertex1, arcs1, in reversed(sorted(work_table_suc.items())):
        for vertex2, arcs2, in work_table_suc.items():
            if len(arcs1.pre) > 0:
                
                # Update prelations if a subgraph is a subset 
                if vertex2 not in visited and set(arcs1.pre).issubset(set(arcs2.pre)) and vertex1 != vertex2 and len(arcs1.pre) + 1 == len(arcs2.pre):
                    common = set(arcs1.pre) & set(arcs2.pre)
                    not_common = set(arcs1.pre) ^ set(arcs2.pre)
                    new.clear()
                    new = set(work_table_G4[vertex2].su)
                        
                    for u in common:
                        work_table[d_node(vertex2, u)].aux = True
                        remove.add(d_node(vertex2, u))
                        new.discard(d_node(vertex2, u))

                    for u in not_common:
                        new.add(d_node(vertex2, u))

                    work_table[d_node(vertex2, vertex1)] = Columns(work_table_G4[vertex2].pre, arcs1.pre, vertex1, True, None, work_table_G4[vertex2].end_node, work_table_G4[vertex1].end_node, False)
                    new.add(d_node(vertex2, vertex1))
                    work_table[vertex2].su = list(new)
                    work_table[vertex2].aux = False
                    visited.append(vertex2)

    # Save the graph after the modification. Input graph G4 is concerted in graph G5/G6 
    work_table_G5_G6 = {}
    for act, sucesores in work_table.items():
        if sucesores.aux != True:
            pred = set(sucesores.pre)
            for q in sucesores.pre:
                if q in remove:
                    pred.discard(q)
            work_table_G5_G6[act] = Columns(pred, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, sucesores.aux)
    
    return work_table_G5_G6



    
def rule_7(successors_copy, successors, work_table, Columns, node):
    """
    # Rule 7 - If (A,B) is a maximal partial bipartite subgraph, then build a star with their common dummy arcs
    """
    left = set()

    # Find subgraph with common dummy activities
    for node1, arcs in sorted(successors_copy.items()):
        suc = frozenset(arcs)
        sub = set()
        
        for node2, arcs2 in successors_copy.items():
            common = suc & set(arcs2)
            notcommon = suc ^ set(arcs2)
            
            if work_table[node1].aux != False and work_table[node2].aux != False and len(common) >= 2 and notcommon and node1!=node2 and node1 not in sub and node2 not in sub:
                sub.add(node1)
                sub.add(node2)
 
        if len(sub) >= 2:   
            for q in sub:
                if q != node1:
                    act_common = set(successors_copy[node1]) & set(successors_copy[q])

            # Build a star of dummy arcs with the common activities of the subgraph
            if len(sub) * len(act_common) >= 6: 
                for q in sub:
                    work_table[d_node(q, node)] = Columns([q], None, None, True, str(node), work_table[q].end_node, node, None)
                        
                    for l in act_common:
                        for y in successors[q]:
                            if str(y).find(separator) != -1:
                                re1 = str(y).partition(separator)
                                if re1[2] in act_common:
                                    left.add(y)
                            else:
                                if y in act_common:
                                    left.add(y)

                for t in act_common:
                    work_table[d_node(node, t)] = Columns(None, None, None, True, t, node, work_table[t].start_node, None)
                
                node += 1
    
    # Save the graph after the modification. Input graph G5/G6 results graph G7     
    work_table_G7 = {}
    for act, sucesores in work_table.items():
        if act not in left:
            work_table_G7[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, None)
    
    return work_table_G7
    



def d_node(x, y):
    
    node = str(x) + separator + str(y)
    
    return node