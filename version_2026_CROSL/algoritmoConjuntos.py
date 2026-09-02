#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algoritmo N: Generación de PERT basada en conjuntos de dependencias.
Actualizado para Python 3.14 y compatible con el benchmark.
"""

import sys
import os
import argparse
import pert
import graph
import fileFormats

def algoritmoN(prelations):
    """
    Construye el grafo PERT analizando la intersección de conjuntos de precedencia.
    """
    # 1. Identificar Nodos únicos basados en combinaciones de predecesores
    Nodes = []
    for label in prelations:
        node = ['start'] if not prelations[label] else list(prelations[label])
        if node not in Nodes:
            Nodes.append(node)

    # 2. Filtrar nodos contenidos en otros (limpieza de redundancias)
    more_than_one = [n for n in Nodes if len(n) > 1]
    final_more_than_one = []
    for act1 in more_than_one:
        s1 = set(act1)
        is_contained = False
        for act2 in more_than_one:
            if act1 != act2 and s1.issubset(set(act2)):
                is_contained = True
                break
        if not is_contained:
            final_more_than_one.append(act1)

    # 3. Asegurar que las actividades individuales que se repiten sean nodos
    node_list = []
    for activities in final_more_than_one:
        for activity in activities:
            if activity not in node_list:
                node_list.append(activity)
            else:
                if [activity] not in Nodes:
                    Nodes.append([activity])

    if ['end'] not in Nodes:
        Nodes.append(['end'])

    # 4. Crear el grafo y añadir nodos
    gg = pert.Pert()
    def get_node_label(node_list):
        return "-".join(map(str, node_list))

    for node in Nodes:
        gg.add_node(get_node_label(node))

    # 5. Añadir arcos ficticios (Dummies) por contención de conjuntos
    for node in Nodes:
        s_node = set(node)
        for node1 in Nodes:
            if node == node1: continue
            s_node1 = set(node1)
            
            if s_node.issubset(s_node1):
                label_orig = get_node_label(node)
                label_dest = get_node_label(node1)
                gg.add_arc((label_orig, label_dest), ('AA', True))

    # 6. Añadir actividades reales
    for activity, predecessors in prelations.items():
        label_start = get_node_label(predecessors) if predecessors else 'start'
        
        # Buscar el nodo más pequeño que contenga esta actividad
        best_node = None
        min_size = sys.maxsize
        
        for n in Nodes:
            if activity in n:
                if len(n) < min_size:
                    min_size = len(n)
                    best_node = get_node_label(n)
        
        if best_node:
            arc = (label_start, best_node)
            if arc not in gg.arcs:
                gg.add_arc(arc, (str(activity), False))

    return gg

def main():
    parser = argparse.ArgumentParser(description="Benchmark Algoritmo N")
    parser.add_argument('infile', help="Archivo .sm o .ppc")
    parser.add_argument('reps', type=int, nargs='?', default=1, help="Repeticiones")
    args = parser.parse_args()

    data = fileFormats.load_with_some_format(args.infile, [
        fileFormats.PPCProjectFileFormat(),
        fileFormats.PSPProjectFileFormat()
    ])

    if not data:
        print("Error de carga.")
        return 1

    activities = data[0]
    # Diccionario: {Actividad: [Predecesores]}
    precedents = {str(act[1]): list(map(str, act[2])) for act in activities}

    # Benchmark
    g = None
    itime = os.times()
    for _ in range(args.reps):
        g = algoritmoN(precedents)
    ftime = os.times()
    
    print("-" * 35)
    print(f"Algoritmo N - Archivo: {os.path.basename(args.infile)}")
    print(f"utime: {ftime[0] - itime[0]:.4f}")
    if g:
        print(f"Nodos: {len(g.successors)}")
        print(f"Arcos reales: {sum(1 for a in g.arcs.values() if not a[1])}")
    print("-" * 35)

if __name__ == '__main__':
    main()