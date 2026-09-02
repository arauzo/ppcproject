#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algorithm to draw Graph PERT based on algorithm from Syslo in Polynomial time
Corregido para Python 3.14
"""

import os
import sys
import argparse
import graph
import pert
import fileFormats
import validation

separator = '-'

# Clase auxiliar para sustituir namedlist
class MinRev:
    def __init__(self, u, w):
        self.u = u
        self.w = w

def sysloPolynomial(prelations):
    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)

    # Step 1. Create the improper covers
    work_table_pol = makeCover(prelations, successors)
    
    # Step 2. Syslo Polynomial algorithm
    final = successors.copy()
    visited = []
       
    for act, pred in list(prelations.items()):
        for v in pred:
            for u in pred:
                if u != v and successors[v] != successors[u] and act not in visited:
                    w = []
                    # Find activity in the improper cover table
                    for key, value in list(work_table_pol.items()):
                        if act in value.w:
                            w = value.w
                          
                    # Find each row that belongs to the predecessors of activity
                    for key, value in list(work_table_pol.items()):
                        if value.u and set(value.u).issubset(set(prelations[act])):
                            vertex = list(value.u)[0]
                            # Compare successors of a row with the improper cover of the activity
                            if successors[vertex] != w:
                                for q in value.u: 
                                    if q in final:
                                        final[q] = list((set(final[q]) - set(w) | set([str(vertex) + separator + str(act)])) - set([act]))       
                                    else:
                                        final[q] = list(set(successors[q]) - set(w) | set([str(vertex) + separator + str(act)]))
                                final[str(vertex) + separator + str(act)] = [act]

                                for l in w:
                                    visited.append(l)
 
    final_precedents = graph.successors2precedents(final)
    work_table = {}
    
    # Step 3. Identify Dummy Activities
    for act, pred in list(final_precedents.items()):
        work_table[act] = {
            'pre': pred,
            'blocked': False,
            'dummy': act not in prelations,
            'suc': None,
            'start_node': None,
            'end_node': None
        }

    # Identical Precedence Constraint
    visited_pred = {}
    for act, col in work_table.items():
        pred = frozenset(col['pre'])
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            col['blocked'] = visited_pred[pred]

    # Step 4. Creating nodes
    node_count = 0 
    for act, col in work_table.items():
        if not col['blocked']:
            col['start_node'] = node_count
            node_count += 1
        else:
            col['start_node'] = work_table[col['blocked']]['start_node']
            
        for suc_name, suc_col in work_table.items():
            if not suc_col['blocked']:
                if act in suc_col['pre']:
                    col['suc'] = suc_name
                    break

    graph_end_node = node_count
    node_count += 1
    pm_graph = pert.PertMultigraph()
    
    for act, col in work_table.items():
        suc = col['suc']
        if suc:
            col['end_node'] = work_table[suc]['start_node']
        else:
            if act in end_act:
                col['end_node'] = node_count 
                node_count += 1
            else:
                col['end_node'] = graph_end_node
        
        pm_graph.add_arc((col['start_node'], col['end_node']), (act, col['dummy']))

    return pm_graph.to_directed_graph().renumerar()

def makeCover(prelations, successors):
    visited_suc = {}
    work_table_imp = {}
    i = 0
    
    # Group by Identical Successors
    for act, cols in list(successors.items()):
        u = set()
        pred_fs = frozenset(cols)
        if pred_fs not in visited_suc:
            visited_suc[pred_fs] = act
            u.add(act)
            for act2, cols2 in list(successors.items()):
                if cols2 == cols:
                    u.add(act2)
        if u:
            work_table_imp[i] = MinRev(list(u), [])
            i += 1

    # Group by Identical Predecessors
    visited_pred = {}
    # Reiniciamos i o seguimos, según lógica original suele ser independiente
    curr_i = 0
    for act, cols in list(prelations.items()):
        u_pred = set()
        pred_fs = frozenset(cols)
        if pred_fs not in visited_pred:
            visited_pred[pred_fs] = act
            u_pred.add(act)
            for act2, cols2 in list(prelations.items()):
                if cols2 == cols:
                    u_pred.add(act2)
        if u_pred:
            if curr_i in work_table_imp:
                work_table_imp[curr_i].w = list(u_pred)
            else:
                work_table_imp[curr_i] = MinRev([], list(u_pred))
            curr_i += 1

    return work_table_imp

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('reps', type=int, nargs='?', default=1)
    args = parser.parse_args()

    data = fileFormats.load_with_some_format(args.infile, [
        fileFormats.PPCProjectFileFormat(),
        fileFormats.PSPProjectFileFormat()
    ])
    if not data: return

    activities = data[0]
    successors = {str(act[1]): list(map(str, act[2])) for act in activities}
    precedents = graph.successors2precedents(successors)

    # Benchmark
    itime = os.times()
    g = None
    for _ in range(args.reps):
        g = sysloPolynomial(precedents)
    ftime = os.times()

    print("-" * 35)
    print(f"SYSLO POLYNOMIAL - Archivo: {os.path.basename(args.infile)}")
    print(f"utime: {ftime[0] - itime[0]:.4f}")
    if g:
        print(f"Nodos: {g.number_of_nodes()}")
        print(f"Arcos reales: {g.numArcsReales()}")
    print("-" * 35)

if __name__ == '__main__':
    main()