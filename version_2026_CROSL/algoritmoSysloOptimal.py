#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algorithm to draw Graph PERT based on algorithm from Syslo with Optimal solution
Corregido para Python 3.14
"""

import argparse
import os
import fileFormats
from collections import namedtuple # Usamos namedtuple en lugar de namedlist

import graph
import pert
import syslo_table

def sysloOptimal(prelations):
    """
    Build a PERT graph using Syslo algorithm
    return p_graph pert.PertMultigraph()
    """
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)
    prela = successors.copy()
    
    # Step 0.
    grafo = {}
    alt = graph.successors2precedents(successors)
    # Aquí es donde se llama a syslo_table.py
    syslo_res = syslo_table.syslo(prela, grafo, alt)
    grafo = graph.successors2precedents(syslo_res)

    # Step 1. Save in work table usando diccionarios (más seguro en Python 3)
    work_table = {}
    for act, pre in list(grafo.items()):
        is_dummy = act not in prelations
        work_table[act] = {
            'pre': pre, 
            'blocked': False, 
            'dummy': is_dummy, 
            'suc': None, 
            'start_node': None, 
            'end_node': None
        }

    # Step 2. Identify Identical Precedence
    visited_pred = {}
    for act, col in work_table.items():
        pred = frozenset(col['pre'])
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            col['blocked'] = visited_pred[pred]

    # Step 3. Creating nodes
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
    for act, col in work_table.items():
        suc = col['suc']
        if suc:
            col['end_node'] = work_table[suc]['start_node']
        else:
            if act in end_act:
                col['end_node'] = graph_end_node
            else:
                col['end_node'] = node_count 
                node_count += 1
    
    # Step 4. Remove redundancy
    vis = []
    keys_to_delete = []
    for act, col in work_table.items():
        if not col['dummy']:
            for q in col['pre']:
                for w in col['pre']:
                    if q in work_table and w in work_table:
                        if q != w and work_table[q]['pre'] == work_table[w]['pre'] and \
                           work_table[q]['dummy'] and work_table[w]['dummy']:
                            if w not in vis:
                                keys_to_delete.append(w)
                            vis.append(q)
    
    for k in set(keys_to_delete):
        if k in work_table: del work_table[k]
                     
    # Step 5. Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, col in work_table.items():
        pm_graph.add_arc((col['start_node'], col['end_node']), (act, col['dummy']))

    return pm_graph.to_directed_graph().renumerar()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('reps', type=int, nargs='?', default=1)
    args = parser.parse_args()

    data = fileFormats.load_with_some_format(args.infile, [
        fileFormats.PPCProjectFileFormat(),
        fileFormats.PSPProjectFileFormat()
    ])
    
    if not data:
        print("Error cargando archivo.")
        return

    activities = data[0]
    successors = {str(act[1]): list(map(str, act[2])) for act in activities}
    precedents = graph.successors2precedents(successors)

    # Benchmark
    import time
    itime = os.times()
    g = None
    for _ in range(args.reps):
        g = sysloOptimal(precedents)
    ftime = os.times()

    print("-" * 35)
    print(f"SYSLO OPTIMAL - Archivo: {os.path.basename(args.infile)}")
    print(f"utime: {ftime[0] - itime[0]:.4f}")
    if g:
        print(f"Nodos: {g.number_of_nodes()}")
        print(f"Arcos reales: {g.numArcsReales()}")
    print("-" * 35)

if __name__ == '__main__':
    main()