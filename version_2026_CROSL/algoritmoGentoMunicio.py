#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algoritmo de Gento-Municio para la generación de grafos PERT.
Actualizado para Python 3.14 y SciPy/NumPy moderno.
"""

import scipy
import numpy as np  # Usamos np por convención
import collections
import itertools
import os
import sys
import argparse

import graph
import pert
import fileFormats

class NodeList(object):
    """Gestión de nodos y actividades para el grafo PERT"""
    def __init__(self, activity_names):
        self.activity_names = list(activity_names)
        self.num_real_activities = len(activity_names)
        self.next_dummy = 0
        self.node_list = [[None, None] for i in range(self.num_real_activities)]
        self.last_node_created = -1

    def next_node(self):
        self.last_node_created += 1
        return self.last_node_created

    def append_dummy(self, begin, end):
        self.activity_names.append(f'dummy{self.next_dummy}')
        self.next_dummy += 1
        self.node_list.append([begin, end])

    def to_pert_graph(self):
        pm_graph = pert.PertMultigraph()
        for i in range(self.num_real_activities):
            pm_graph.add_arc((self.node_list[i][0], self.node_list[i][1]), (self.activity_names[i], False))
        for i in range(self.num_real_activities, len(self.node_list)):
            pm_graph.add_arc((self.node_list[i][0], self.node_list[i][1]), (self.activity_names[i], True))
        return pm_graph.to_directed_graph()

def gento_municio(predecessors):
    nodes = NodeList(predecessors.keys())
    successors_dict = graph.reversed_prelation_table(predecessors)

    # CORRECCIÓN: Usar np.zeros y np.sum (SciPy ya no los incluye)
    matrix = np.zeros([nodes.num_real_activities, nodes.num_real_activities], dtype=int)
    
    for activity, successors in successors_dict.items():
        if activity in nodes.activity_names:
            idx_i = nodes.activity_names.index(activity)
            for suc in successors:
                if suc in nodes.activity_names:
                    idx_j = nodes.activity_names.index(suc)
                    matrix[idx_i][idx_j] = 1

    sum_predecessors = np.sum(matrix, axis=0)
    sum_successors = np.sum(matrix, axis=1)

    # Paso 1: Inicio
    beginning = np.nonzero(sum_predecessors == 0)[0]
    begin_node = nodes.next_node()
    for act_idx in beginning:
        nodes.node_list[act_idx][0] = begin_node

    # Paso 2: Final
    ending = np.nonzero(sum_successors == 0)[0]
    end_node = nodes.next_node()
    for act_idx in ending:
        nodes.node_list[act_idx][1] = end_node

    # Paso 3: Estándar Tipo I
    act_one_pred = np.nonzero(sum_predecessors == 1)[0]
    stI = collections.defaultdict(list)
    for i in act_one_pred:
        pred = np.nonzero(matrix[:, i])[0][0]
        if sum_successors[pred] == 1 or sum_successors[pred] == np.sum(matrix[:, np.nonzero(matrix[pred])[0]]):
            stI[pred].append(i)

    for node_act, succs in stI.items():
        node_id = nodes.next_node()
        nodes.node_list[node_act][1] = node_id
        for s in succs:
            nodes.node_list[s][0] = node_id

    # Paso 4: Estándar Tipo II
    stII = collections.defaultdict(list)
    for act in range(nodes.num_real_activities):
        nz = np.nonzero(matrix[act])[0]
        if len(nz) > 0:
            stII[frozenset(nz)].append(act)

    mark_complete = []
    for succs, preds in list(stII.items()):
        u = len(preds)
        is_complete = True
        for s in succs:
            if sum_predecessors[s] != u:
                is_complete = False
                break
        
        if is_complete:
            mark_complete.append(succs)
            node_id = nodes.next_node()
            for p in preds: nodes.node_list[p][1] = node_id
            for s in succs: nodes.node_list[s][0] = node_id
        else:
            node_id = nodes.next_node()
            for p in preds: nodes.node_list[p][1] = node_id

    # Limpieza para MASC
    for s_set in mark_complete:
        if s_set in stII: del stII[s_set]
    
    masc = stII
    npc = np.zeros([nodes.num_real_activities], dtype=int)
    for succs, preds in masc.items():
        for s in succs: npc[s] += len(preds)

    # Paso 6: Coincidencias
    act_no_init = [i for i in range(nodes.num_real_activities) if nodes.node_list[i][0] is None]
    if act_no_init:
        mra = np.zeros([len(act_no_init), len(act_no_init)], dtype=int)
        for succs, preds in masc.items():
            for act_i, act_j in itertools.combinations(succs, 2):
                if act_i in act_no_init and act_j in act_no_init:
                    ii, jj = act_no_init.index(act_i), act_no_init.index(act_j)
                    mra[ii, jj] += len(preds)
                    mra[jj, ii] += len(preds)

        for i in range(len(act_no_init)):
            for j in range(i+1, len(act_no_init)):
                if mra[i,j] > 0 and mra[i,j] == npc[act_no_init[i]] and mra[i,j] == npc[act_no_init[j]]:
                    node_id = nodes.node_list[act_no_init[i]][0] or nodes.next_node()
                    nodes.node_list[act_no_init[i]][0] = node_id
                    nodes.node_list[act_no_init[j]][0] = node_id

    for n in nodes.node_list:
        if n[0] is None: n[0] = nodes.next_node()
        if n[1] is None: n[1] = nodes.next_node()

    return nodes.to_pert_graph().renumerar()

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
    precedents = {str(act[1]): list(map(str, act[2])) for act in activities}

    g = None
    itime = os.times()
    for _ in range(args.reps):
        g = gento_municio(precedents)
    ftime = os.times()

    print("-" * 35)
    print(f"Gento-Municio - Archivo: {os.path.basename(args.infile)}")
    print(f"utime: {ftime[0] - itime[0]:.4f}")
    if g:
        print(f"Nodos: {g.number_of_nodes()}")
        print(f"Arcos reales: {g.numArcsReales()}")
    print("-" * 35)

if __name__ == '__main__':
    main()