"""
MOUHOUB ALGORITHM RULES 
Corregido para Python 3.14
"""

import collections
import collections.abc
from collections import Counter

# --- PARCHE DE COMPATIBILIDAD PARA NAMEDLIST ---
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'Sequence'):
    collections.Sequence = collections.abc.Sequence
if not hasattr(collections, 'MutableSequence'):
    collections.MutableSequence = collections.abc.MutableSequence

import namedlist

separator = '|'
# Definición de la estructura de la tabla de trabajo
Columns = namedlist.namedlist('Columns', ['pre', 'su', 'blocked', 'dummy', 'suc', 'start_node', 'end_node', 'aux'])

def rule_1(work_table_suc, work_table):
    """Regla 1: Contracción de vértices finales para subgrafos con predecesores comunes"""
    visited = []
    remove = set()
    for act, arcs in list(work_table_suc.items()):
        for act2, arcs2 in list(work_table_suc.items()):
            common = set(arcs) & set(arcs2)
            not_common = set(arcs) ^ set(arcs2)
            
            if not not_common and act != act2 and len(common) > 1 and act not in visited:
                delete = work_table[act2].end_node
                work_table[act2].end_node = work_table[act].end_node 
                visited.append(act2)
                    
                for y, pred in list(work_table.items()):
                    if pred.start_node == delete:
                        pred.aux = True
                        work_table[act2].su = work_table[act].su
                        work_table[act2].suc = work_table[act].suc
                        remove.add(y)
                                        
    for act, sucesores in list(work_table.items()):
        if sucesores.aux != True:
            if sucesores.pre != None:
                for u in remove:
                    if u in sucesores.pre:
                        sucesores.pre = set(sucesores.pre) - set([u])
    return 0

def rule_2(work_table_pred, work_table):
    """Regla 2: Contracción de vértices iniciales para subgrafos con sucesores comunes"""
    visited = []
    remove = set()
    for act, arcs in list(work_table_pred.items()):
        for act2, arcs2 in list(work_table_pred.items()):
            common = set(arcs) & set(arcs2)
            not_common = set(arcs) ^ set(arcs2)
            
            if not not_common and act != act2 and len(common) > 1 and act not in visited:
                eliminar = work_table[act].start_node
                work_table[act].start_node = work_table[act2].start_node 
                visited.append(act2)
                
                for y in work_table[act].pre:
                    if work_table[y].end_node == eliminar:
                        remove.add(y)
                        work_table[y].aux = True
                        work_table[y].suc = work_table[act].su
                            
    for act, columns in list(work_table.items()):
        if columns.aux != True and act not in remove:
            if columns.su != None:
                for u in remove:
                    if u in columns.su:
                        columns.su = list(set(columns.su) - set([u]))
    return work_table

def rule_3(work_table_G2, work_table):
    """Regla 3: Contracción de nodos con un solo predecesor ficticio"""
    for act, arcs in list(work_table_G2.items()):
        if len(arcs.pre) == 1:
            extra = list(arcs.pre)[0]
            if work_table[extra].dummy == True:
                v = str(extra).partition(separator)
                work_table[v[2]].start_node = work_table[v[0]].end_node 
                work_table[extra].aux = True
                    
    work_table_G3 = {}
    for act, columns in list(work_table.items()):
        if columns.aux != True:
            work_table_G3[act] = Columns(columns.pre, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, columns.aux)
    return work_table_G3

def rule_4(work_table_G3, work_table):
    """Regla 4: Contracción de nodos con un solo sucesor ficticio"""
    work_table_G4 = work_table
    for act, arcs in list(work_table_G3.items()):
        if arcs.su != None and len(arcs.su) == 1:
            extra = list(arcs.su)[0]
            if work_table[extra].dummy == True:
                v = str(extra).partition(separator)
                work_table[v[0]].end_node = work_table[v[2]].start_node 
                work_table[extra].aux = True
                for act2, arcs2 in list(work_table_G3.items()):
                    if arcs2.su == arcs.su:
                        work_table[act2].end_node = work_table[v[2]].start_node 
    
    work_table_G4 = {}
    for act, columns in list(work_table.items()):
        if columns.aux != True:
            work_table_G4[act] = Columns(columns.pre, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, None)
    return work_table_G4

def rule_5_6(work_table_suc, work_table, work_table_G4):
    """Reglas 5 y 6: Simplificación de superconjuntos de sucesores/predecesores"""
    visited = []
    remove = set()
    svertex = []
    
    for act, arcs1 in reversed(sorted(work_table_suc.items())):
        for act2, arcs2 in list(work_table_suc.items()):
            if len(arcs1) > 0 and act2 not in visited and set(arcs1).issubset(set(arcs2)) and act != act2 and len(arcs1) + 1 == len(arcs2):
                common = set(arcs1) & set(arcs2)
                new = set(work_table_G4[act2].su)
                        
                for u in common:
                    work_table[d_node(act2, u)].aux = True
                    remove.add(d_node(act2, u))
                    new.discard(d_node(act2, u))

                if act not in visited and work_table_G4[act2].end_node not in svertex:
                    work_table[d_node(act2, act)] = Columns(work_table_G4[act2].pre, arcs1, act, True, None, work_table_G4[act2].end_node, work_table_G4[act].end_node, False)
                    new.add(d_node(act2, act))
                    work_table[act2].su = list(new)
                    work_table[act2].aux = False
                    svertex.append(work_table_G4[act2].end_node)
                    visited.append(act2)

    work_table_G5_G6 = {}
    for act, columns in list(work_table.items()):
        if columns.aux != True:
            pred = set(columns.pre)
            for q in columns.pre:
                if q in remove:
                    pred.discard(q)
            work_table_G5_G6[act] = Columns(pred, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, columns.aux)
    return work_table_G5_G6

def rule_7(successors_copy, successors, work_table, node):
    """Regla 7: Construcción de estrellas para subgrafos bipartitos maximales"""
    remove = set()
    visited = [] 
    
    for act, columns in list(work_table.items()):
        snodes = set()
        if columns.dummy == False:
            for r in columns.pre:
                if r in work_table:
                    snodes.add(work_table[r].start_node)
        if snodes:
            work_table[act].aux = list(snodes) 

    for act, columns in list(work_table.items()):
        com_nodes = []
        for act2, columns2 in list(work_table.items()):
            if columns2.aux is not None and columns.aux is not None:
                common = set(columns.aux) & set(columns2.aux)
                if len(common) > 1 and act != act2 and act not in visited:
                    visited.append(act2)
                    for p in common: com_nodes.append(p)
                            
        if com_nodes:     
            most_common = Counter(com_nodes).most_common(1)
            if most_common:
                maximal = most_common[0][1]
                if maximal > 1:
                    a_set = [j for j, va in dict(Counter(com_nodes)).items() if va == maximal]
                    if len(a_set) >= 2:
                        b_set = [act3 for act3, c3 in work_table.items() if c3.end_node in a_set and not c3.dummy]
                        temp_com = set()
                        maxco = False
                        for f in b_set:
                            for g in b_set:
                                if f != g:
                                    common = set(successors_copy[f]) & set(successors_copy[g])
                                    if not maxco:
                                        temp_com = common
                                        maxco = True
                                    else:
                                        temp_com &= common
                        
                        if len(temp_com) + len(a_set) >= 6:
                            for q in b_set:
                                work_table[d_node(q, node)] = Columns([q], None, None, True, str(node), work_table[q].end_node, node, None)
                                for y in successors[q]:
                                    re1 = str(y).partition(separator)
                                    target = re1[2] if re1[1] == separator else y
                                    if target in temp_com: remove.add(y)
                            
                            for t in temp_com:
                                work_table[d_node(node, t)] = Columns(None, None, None, True, t, node, work_table[t].start_node, None)
                            node += 1

    work_table_G7 = {}
    for act, columns in list(work_table.items()):
        if act not in remove:
            work_table_G7[act] = Columns(columns.pre, columns.su, columns.blocked, columns.dummy, columns.suc, columns.start_node, columns.end_node, None)
    return work_table_G7

def d_node(x, y):
    return str(x) + separator + str(y)