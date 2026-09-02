#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algoritmo de Mouhoub corregido para Python 3.14 y Benchmark.
"""
import os
import sys
import argparse
import collections
import collections.abc

# Parche para namedlist antes de importar nada
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping

import namedlist
import fileFormats
import pert
import graph
import zConfiguration
import mouhoubRules

def mouhoub(prelations):
    # Definición local de Columns para asegurar compatibilidad
    Columns = namedlist.namedlist('Columns', ['pre', 'su', 'blocked', 'dummy', 'suc', 'start_node', 'end_node', 'aux'])

    successors = graph.reversed_prelation_table(prelations)
    successors_copy = graph.reversed_prelation_table(prelations.copy())
    end_act = graph.ending_activities(successors)

    # Step 0. Z Configuration
    z_conf_res = zConfiguration.zconf(successors)
    complete_bipartite = successors.copy()
    complete_bipartite.update(z_conf_res)
    
    # Step 1. Work Table
    precedents_table = graph.successors2precedents(complete_bipartite)
    work_table = {}
    for act, preds in list(precedents_table.items()):
        is_dummy = act not in prelations
        work_table[act] = Columns(set(preds), successors.get(act, []), None, is_dummy, None, None, None, None)
    
    # Step 2. Identical Precedence
    visited_pred = {}
    for act, columns in list(work_table.items()):
        pred_set = frozenset(columns.pre)
        if pred_set not in visited_pred:
            visited_pred[pred_set] = act
        else:
            columns.blocked = visited_pred[pred_set]
    
    # Step 3. Creating nodes
    node_count = 0
    for act, columns in list(work_table.items()):
        if not columns.blocked:
            columns.start_node = node_count
            node_count += 1
        else:
            columns.start_node = work_table[columns.blocked].start_node
            
    for act, columns in list(work_table.items()):
        for suc_name, suc_cols in list(work_table.items()):
            if not suc_cols.blocked and act in suc_cols.pre:
                columns.suc = suc_name
                break

    graph_end_node = node_count
    node_count += 1
    for act, columns in list(work_table.items()):
        if columns.suc:
            columns.end_node = work_table[columns.suc].start_node
        else:
            if act in end_act:
                columns.end_node = graph_end_node
            else:
                columns.end_node = node_count
                node_count += 1

    # Step 4. Rules
    mouhoubRules.rule_1(successors_copy, work_table)
    G2 = mouhoubRules.rule_2(prelations, work_table)
    G3 = mouhoubRules.rule_3(G2, work_table)
    G4 = mouhoubRules.rule_4(G3, work_table)
    G5_6 = mouhoubRules.rule_5_6(successors_copy, work_table, G4)
    G3a = mouhoubRules.rule_3(G5_6, work_table)
    G4a = mouhoubRules.rule_4(G3a, work_table)
    # Pasamos el contador de nodos actual
    G7 = mouhoubRules.rule_7(successors_copy, successors, G4a, node_count)
    
    # Step 5 & 6. Cleanup and Graph generation
    pm_graph = pert.PertMultigraph()
    for act, cols in list(G7.items()):
        pm_graph.add_arc((cols.start_node, cols.end_node), (act, cols.dummy))
    
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
    if not data: return

    activities = data[0]
    successors_dict = {str(act[1]): list(map(str, act[2])) for act in activities}
    precedents_dict = graph.successors2precedents(successors_dict)

    itime = os.times()
    g = None
    for _ in range(args.reps):
        g = mouhoub(precedents_dict)
    ftime = os.times()

    print("-" * 35)
    print(f"Mouhoub - Archivo: {os.path.basename(args.infile)}")
    print(f"utime: {ftime[0] - itime[0]:.4f}")
    if g:
        print(f"Nodos: {g.number_of_nodes()}")
        print(f"Arcos reales: {g.numArcsReales()}")
    print("-" * 35)

if __name__ == '__main__':
    main()