"""
MOUHOUB ALGORITHM RULES 
Remove dummy arcs to build a graph with minimum dummy activities according to the Mouhoub algorithm rules
"""

from collections import Counter

separator = '-'

    
def rule_1(work_table_suc, work_table, Columns):
    """
    # Rule 1 - For each subgraph with common and uncommon predecessors activities, contract end vertices in one vertex
      return work_table_G1
   """      
    visited = []
    remove = set()
    
    for vertex1, arcs in work_table_suc.items():
        for vertex2, arcs2 in work_table_suc.items():
            common = set(list(arcs)) & set(list(arcs2))
            not_common = set(arcs) ^ set(arcs2)
            
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
    
    for vertex1, arcs in work_table_pred.items():
        for vertex2, arcs2 in work_table_pred.items():
            common = set(arcs) & set(arcs2)
            not_common = set(arcs) ^ set(arcs2)
            
            # Join nodes when two activities have common predecessor and uncommon predecessor activities
            if common and not not_common and vertex1 != vertex2:
                if len(common) > 1 and vertex1 not in visited:
                    eliminar = work_table[vertex1].start_node
                    work_table[vertex1].start_node = work_table[vertex2].start_node 
                    visited.append(vertex2)
                    #print vertex1, vertex2, work_table[vertex1].start_node, " = ", work_table[vertex1].start_node, work_table[vertex1].end_node, eliminar
                    for y in work_table[vertex1].pre:
                        if work_table[y].end_node == eliminar:
                            remove.add(y)
                            #print "DEL: ", y
                            work_table[y].aux = True
                            
    # Save the graph after the modification. Input graph G results graph G1
    work_table_G2 = {}
    for act, sucesores in work_table.items():
        if sucesores.aux != True:
            if sucesores.su != None:
                for u in remove:
                    if u in sucesores.su:
                        sucesores.su =  list(set(sucesores.su) - set([u]))
            work_table_G2[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, sucesores.aux)

    return work_table_G2
    


def rule_3(work_table_G2, work_table, Columns):
    """
    # Rule 3 - If a vertex X has one predecessor vertex Y, then contract both vertices in one vertex and delete the resulting loop
      return work_table_G3
    """
    
    for vertex1, arcs in work_table_G2.items():
        if len(work_table_G2[vertex1].pre) == 1:
            extra = set(work_table_G2[vertex1].pre).pop()
            
            # Contract node with only one dummy predecessor
            if work_table[extra].dummy == True:
                v = str(extra).partition(separator)
                print v[2], v[0], vertex1
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
      return work_table_G4
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
            work_table_G4[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, None)

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
    for vertex1, arcs1, in reversed(sorted(work_table_suc.items())):
        
        for vertex2, arcs2, in work_table_suc.items():
            if len(arcs1) > 0:
                
                # Update prelations if a subgraph is a subset 
                if vertex2 not in visited and set(arcs1).issubset(set(arcs2)) and vertex1 != vertex2 and len(arcs1) + 1 == len(arcs2):
                    common = set(arcs1) & set(arcs2)
                    not_common = set(arcs1) ^ set(arcs2)
                    new.clear()
                    new = set(work_table_G4[vertex2].su)
                        
                    for u in common:
                        work_table[d_node(vertex2, u)].aux = True
                        remove.add(d_node(vertex2, u))
                        new.discard(d_node(vertex2, u))

                    for u in not_common:
                        new.add(d_node(vertex2, u))    
                    
                    if vertex1 not in snode and work_table_G4[vertex2].end_node not in svertex:
                        work_table[d_node(vertex2, vertex1)] = Columns(work_table_G4[vertex2].pre, arcs1, vertex1, True, None, work_table_G4[vertex2].end_node, work_table_G4[vertex1].end_node, False)
                        new.add(d_node(vertex2, vertex1))
                        work_table[vertex2].su = list(new)
                        work_table[vertex2].aux = False
                        visited.append(vertex2)
                        svertex.append(work_table_G4[vertex2].end_node)

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



    
def rule_7(successors, work_table, Columns, node):
    """
    # Rule 7 - If (A,B) is a maximal partial bipartite subgraph, then build a star with their common dummy arcs
      return work_table_G7
    """
    left = set()
    visi = [] 
    
    for k, v in work_table.items():
        snodes = []
        if v.dummy == False:
            for r in v.pre:
                if r in r in work_table:
                    snodes.append(work_table[r].start_node)

        if snodes != []:
            work_table[k].aux = snodes 


    for k, v in work_table.items():
        if v.aux != None:
            nodoscomunes = []
            for k2, v2 in work_table.items():
                if v2.aux != None:
                    common = set(v.aux) & set(v2.aux)
                    
                    if len(common) > 1 and k != k2 and k not in visi:
                        visi.append(k2)
                        
                        for p in common:
                            nodoscomunes.append(p)
                            
            if len(nodoscomunes) > 0:     
                maximo = list(Counter(nodoscomunes).most_common(1)[0]).pop()
                
                if maximo > 1:
                    final = []
                    diccy = Counter(nodoscomunes)
                    
                    for j, va in dict(diccy).items():
                        if va == maximo:
                            final.append(j)
                            
                    if len(final) >= 2:
                        #print "------------------------------"
                        iniciales = []
                        vi = 0
                        finalcommon = set()
                        
                        for k3, v3 in work_table.items():
                            if v3.end_node in final and v3.dummy != True:
                                iniciales.append(k3)
                       
                        #print iniciales
                        for f in iniciales:
                            for g in iniciales:
                                if f != g:
                                    common = set(successors[f]) & set(successors[g])
                                    #print "---", common, finalcommon
                                    if finalcommon.issuperset(common):
                                        finalcommon = finalcommon
                                        if len(finalcommon) > len(common):
                                            finalcommon = finalcommon & common
                                    elif vi == 0:
                                        finalcommon = common
                                        vi = 1
                                    else:
                                        finalcommon = finalcommon & common
                       
                        #print "-_",  finalcommon
                        if len(finalcommon) + len(common) >= 6:
                            for q in iniciales:
                                work_table[d_node(q, node)] = Columns([q], None, None, True, str(node), work_table[q].end_node, node, None)
                                    
                                for l in finalcommon:
                                    for y in successors[q]:
                                        if str(y).find(separator) != -1:
                                            re1 = str(y).partition(separator)
                                            if re1[2] in finalcommon:
                                                left.add(y)
                                        else:
                                            if y in finalcommon:
                                                left.add(y)
            
                            for t in finalcommon:
                                work_table[d_node(node, t)] = Columns(None, None, None, True, t, node, work_table[t].start_node, None)
                                #raw_input()
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