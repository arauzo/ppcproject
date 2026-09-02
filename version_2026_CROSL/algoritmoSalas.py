#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algorithm to build a PERT graph according to the Salas method
Corregido para Python 3.14 
"""

import os
import sys
import argparse
import pert
import graph
import fileFormats

def salas(prelations):
    matrix, premat = create_matrix(prelations)
    m, t, af, ai, ami, amiD, amf, amfD = previous(matrix)

    a = len(m)
    b = len(m)                    
    visited = []
    d = {i: [0, 0] for i in range(a)}                    

    cont = 1                    
    for i in ai:            
        cont += 1
        d[i] = [1, cont]
        visited.append(i)    

    d1 = d.copy() 
    X = 0
    
    # Lógica principal del algoritmo Salas
    while len(visited) < b:
        positions = []                
        if d1[X][0] > 0 and d1[X][1] > 0:    
            cont1 = -1   
            for j in m[X]:
                cont1 += 1
                if j == 1: positions.append(cont1)

            for k in positions:
                if k not in visited:
                    if t[k].count(1) == 1:
                        if k not in amfD:
                            cont += 1                
                            d1[k] = [d1[X][1], cont] 
                        else:
                            if d1[k][1] == 0:
                                cont += 1                
                                d1[k] = [d1[X][1], cont]
                            else:
                                d1[k][0] = d1[X][1]
                            for l in amfD.get(k, []):
                                if d1[l][1] == 0: d1[l][1] = cont
                        visited.append(k)  
                        
                    elif t[k].count(1) > 1:
                        mi = 0
                        base = []
                        for l in ami:
                            if k in l and k not in visited:
                                mi = 1
                                base = l
                        if mi == 0: base = [k]
                        
                        pospre = []                    
                        cont1 = -1
                        for n in t[base[0]]:
                            cont1 += 1
                            if n == 1: pospre.append(cont1)
                        
                        insert = 1
                        for n in pospre:
                            if n not in visited: insert = 0
                        
                        if insert == 1:
                            for p in base:
                                if p not in visited: visited.append(p)
                            equal = -1         
                            equalL = []        
                            
                            for o in pospre:
                                cont1 = -1
                                next_pre = []        
                                for p in m[o]:
                                    cont1 += 1
                                    if p == 1: next_pre.append(cont1)
                                if sorted(next_pre) == sorted(base):
                                    equal = o
                                    equalL.append(o)

                            if equal > -1:
                                amfA = []                                             
                                for p in pospre:
                                    if m[p].count(1) > 1:
                                        if equal != p and p not in amfA:
                                            d1[a] = [d1[p][1], d1[equal][1]]
                                            a += 1
                                            for u in amfD.get(p, []): amfA.append(u)
                                            
                                for p in base:
                                    if p not in amfD:
                                        cont += 1
                                        d1[p] = [d1[equal][1], cont]
                                    else:
                                        if d1[p][1] == 0:
                                            cont += 1
                                            d1[p] = [d1[equal][1], cont]
                                        else:
                                            if d1[equal][1] == 0:
                                                for l in equalL:
                                                    if l != equal and d1[l][1] > 0: equal = l
                                            d1[p][0] = d1[equal][1]
                                        for l in amfD.get(p, []):
                                            if d1[l][1] == 0: d1[l][1] = cont
                            else:
                                path = 0                
                                for l in amf:
                                    if sorted(pospre) == sorted(l): path = 1
                                if path == 0:
                                    cont += 1
                                    ff = cont
                                    for p in pospre:
                                        d1[a] = [d1[p][1], cont]
                                        a += 1
                                    for p in base:
                                        cont += 1
                                        d1[p] = [ff, cont]
                                        for l in amfD.get(p, []): d1[l][1] = cont
                                else:
                                    for p in base:
                                        cont += 1
                                        d1[p] = [d1[X][1], cont]
                                        for l in amfD.get(p, []): d1[l][1] = cont
        X += 1    
        if X == b: X = 0
    
    d2 = settings(d1, cont, a, af, b)
    
    p_graph = pert.PertMultigraph()
    for act_idx, nodes in d2.items():
        if act_idx < b:
            p_graph.add_arc((nodes[0], nodes[1]), (premat[act_idx], False))
        else:
            if nodes[0] != nodes[1]:
                p_graph.add_arc((nodes[0], nodes[1]), (f"f-{nodes[0]}-{nodes[1]}", True))

    return p_graph.to_directed_graph().renumerar()

def create_matrix(prelations):
    m = []
    premat = {} 
    cont = 0
    keys = list(prelations.keys())
    for i, act in enumerate(keys):
        premat[i] = act
        mf = []
        for j, act2 in enumerate(keys):
            mf.append(1 if act in prelations[act2] else 0)
        m.append(mf)
    return m, premat

def previous(matrix):
    m = matrix
    a = len(m)
    t = [[m[j][i] for j in range(a)] for i in range(a)]
    af = [i for i in range(a) if 1 not in m[i]]
    ai = [i for i in range(a) if 1 not in t[i]]

    ami = []
    inc = []
    for i in range(a):
        if i not in inc:
            ci = [j for j in range(a) if j > i and t[i] == t[j] and 1 in t[i]]
            if ci:
                ci.append(i)
                ami.append(ci)
                inc.extend(ci)

    amfD = {}
    amf = []
    inc = []
    for i in range(a):
        if i not in inc:
            fi = [j for j in range(a) if j > i and m[i] == m[j]]
            if fi:
                fi.append(i)
                amf.append(fi)
                inc.extend(fi)
                for x in fi:
                    amfD[x] = [y for y in fi if y != x]
    return m, t, af, ai, ami, None, amf, amfD

def settings(d, cont, a, af, b):
    nf = af[0]
    for j in af:
        d[j][1] = d[nf][1]
    
    d1 = d.copy()
    visited = []
    to_del = []
    items = list(d.items())
    for i_idx, i_val in items:
        for j_idx, j_val in items:
            if i_idx != j_idx and i_idx >= b and j_idx >= b and i_idx not in visited:
                if i_val == j_val:
                    visited.append(j_idx)
                    to_del.append(j_idx)
    for k in to_del:
        if k in d: del d[k]
    return d

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
    # Normalizar a strings para evitar errores de tipo
    successors = {str(act[1]): list(map(str, act[2])) for act in activities}
    precedents = graph.successors2precedents(successors)

    itime = os.times()
    g = None
    for _ in range(args.reps):
        g = salas(precedents)
    ftime = os.times()

    print("-" * 35)
    print(f"SALAS - Archivo: {os.path.basename(args.infile)}")
    print(f"utime: {ftime[0] - itime[0]:.4f}")
    if g:
        print(f"Nodos: {g.number_of_nodes()}")
        print(f"Arcos reales: {g.numArcsReales()}")
    print("-" * 35)

if __name__ == '__main__':
    main()