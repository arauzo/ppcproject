#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algoritmo de Cohen-Sadeh para la generación de grafos PERT (AOA).
Incluye exportación visual automática a formato DOT y SVG.
"""

import collections
import collections.abc
import os
import sys
import argparse
import subprocess

# --- PARCHE INTEGRAL PARA PYTHON 3.10 - 3.14 ---
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence
collections.MutableSequence = collections.abc.MutableSequence
# -----------------------------------------------

import namedlist
import graph
import pert
import fileFormats

def cohen_sadeh(prelations):
    """
    Construye un grafo PERT utilizando el algoritmo de Cohen-Sadeh.
    """
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)

    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
    work_table = {}
    for act, predecessors in list(prelations.items()):
        work_table[str(act)] = Columns(set(map(str, predecessors)), False, False, None, None, None)

    # Identificar restricciones idénticas
    visited_pred = {}
    for act, columns in list(work_table.items()):
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]

    # Identificar Arcos Dummy
    dups = set()
    visited_act = set()
    for columns in list(work_table.values()):
        if not columns.blocked:
            for act in columns.pre:
                if act in visited_act:
                    dups.add(act)
                visited_act.add(act)

    # Crear filas para Arcos Dummy
    dummy_counter = collections.Counter()
    for act_key in list(work_table.keys()):
        columns = work_table[act_key]
        if not columns.blocked:
            predecessors = columns.pre
            if len(predecessors) > 1:
                for pre in list(predecessors):
                    if pre in dups:
                        predecessors.remove(pre)
                        dummy_name = f"{pre}-d{dummy_counter[pre]}"
                        dummy_counter[pre] += 1
                        predecessors.add(dummy_name)
                        work_table[dummy_name] = Columns(set([pre]), False, True, None, None, None)

    # Creación de nodos
    node = 0
    for act, columns in list(work_table.items()):
        if not columns.dummy and not columns.blocked:
            columns.start_node = node
            node += 1

    for act, columns in list(work_table.items()):
        if not columns.dummy and columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node

    # Asociar nodos finales
    for act, columns in list(work_table.items()):
        for suc, suc_columns in list(work_table.items()):
            if not suc_columns.dummy and not suc_columns.blocked:
                if act in suc_columns.pre:
                    columns.suc = suc
                    break

    graph_end_node = node
    node += 1
    for act, columns in list(work_table.items()):
        suc = columns.suc
        if suc:
            columns.end_node = work_table[suc].start_node
        else:
            if act in map(str, end_act):
                columns.end_node = graph_end_node
            else:
                columns.end_node = node 
                node += 1

    for act, columns in list(work_table.items()):
        if columns.dummy:
            pred = next(iter(columns.pre))
            columns.start_node = work_table[pred].end_node

    pm_graph = pert.PertMultigraph()
    for act, columns in list(work_table.items()):
        pm_graph.add_arc((columns.start_node, columns.end_node), (act, columns.dummy))

    p_graph = pm_graph.to_directed_graph()
    return p_graph.renumerar()

def main():
    parser = argparse.ArgumentParser(description="Algoritmo Cohen-Sadeh con salida gráfica.")
    parser.add_argument('infile', help="Archivo del proyecto (.sm o .ppc)")
    parser.add_argument('reps', type=int, nargs='?', default=1, help="Repeticiones")
    args = parser.parse_args()

    data = fileFormats.load_with_some_format(args.infile, [
        fileFormats.PPCProjectFileFormat(),
        fileFormats.PSPProjectFileFormat()
    ])

    if not data:
        print(f"Error al cargar: {args.infile}")
        return 1

    activities = data[0]
    precedents = {str(act[1]): list(map(str, act[2])) for act in activities}

    # Ejecución
    g = None
    itime = os.times()
    for _ in range(args.reps):
        g = cohen_sadeh(precedents)
    ftime = os.times()
    
    utime = ftime[0] - itime[0]

    # --- SALIDA DE DATOS ---
    print("\n" + "="*40)
    print(f"RESULTADOS: {os.path.basename(args.infile)}")
    print(f"Tiempo total: {utime:.4f}s")
    if g:
        print(f"Nodos: {g.number_of_nodes()} | Reales: {g.numArcsReales()} | Ficticios: {g.numArcsFicticios()}")
    print("="*40)

    # --- GENERACIÓN GRÁFICA ---
    if g:
        dot_file = "resultado_grafo.dot"
        svg_file = "resultado_grafo.svg"
        
        # 1. Guardar archivo DOT (Texto)
        with open(dot_file, "w") as f:
            f.write(graph.pert2dot(g))
        print(f"[*] Archivo DOT generado: {dot_file}")

        # 2. Intentar generar SVG usando Graphviz instalado
        try:
            # Usamos la función que ya existe en tu graph.py
            img_data = graph.pert2image(g, 'svg')
            with open(svg_file, "wb") as f:
                f.write(img_data)
            print(f"[*] ¡Imagen SVG creada con éxito!: {svg_file}")
        except Exception as e:
            print("[!] No se pudo generar el SVG automáticamente (¿Tienes instalado Graphviz?)")
            print("    Puedes visualizar el archivo .dot en: https://edavis.github.io/gviz/")

    return 0

if __name__ == '__main__':
    sys.exit(main())