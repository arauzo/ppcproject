#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algorithm to draw Graph PERT based on algorithm from Syslo in Polynomial time

Copyright 2007-15 University of Cordoba (Spain)
"""

import namedlist

import graph
import pert
import fileFormats
import validation

separator = '-'

           
def sysloPolynomial(prelations):

    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)

    #Step 0. Construct work table with Immediate Predecessors
    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents)


    #Step 1. Create the improper covers
    work_table_pol = makeCover(prelations, successors)
          
   
    # Step 2. Syslo Polynomial algorithm
    final = successors.copy()
    visited = []
       
    for act, pred in prelations.items():
        for v in pred:
            for u in pred:
                if u != v and successors[v] != successors[u] and act not in visited:
                    # Find activity in the improper cover table
                    for key, value in work_table_pol.items():
                        if act in value.w:
                            w = value.w
                          
                    # Find each row that belongs to the predecessors of activity
                    for key, value in work_table_pol.items():
                        if set(value.u).issubset(prelations[act]) and value.u:
                            vertex = set(value.u).pop()
                            # Compare successors of a row with the improper cover of the activity
                            if successors[vertex] != w:
                                for q in value.u: 
                                    if final.has_key(q):
                                        final[q] = list((set(final[q]) - set(w) | set([str(vertex) + separator + str(act)])) - set([act]))       
                                    else:
                                        final[q] = list(set(successors[q]) - set(w) | set([str(vertex) + separator + str(act)]))
                                final[str(vertex) + separator + str(act)] = [act]

                                for l in w:
                                    visited.append(l)
 
        
    final = graph.successors2precedents(final)
    work_table = {}
    
    for act, pred in final.items():
        work_table[act] = Columns(pred, False, False, None, None, None)
        if act not in prelations:
            work_table[act].dummy = True


    #Step 3. Identify Dummy Activities And Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]


    #Step 4. Creating nodes
    # (a) find start nodes
    node = 0 # instead of 0, can start at 100 to avoid confusion with activities named with numbers when debugging
    for act, columns in work_table.items():
        if not columns.blocked:
            columns.start_node = node
            node += 1
        if columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node
            
        # Associate activities with their end nodes
        for suc, suc_columns in work_table.items():
            if not suc_columns.blocked:
                if act in suc_columns.pre:
                    columns.suc = suc
                    break


    
    # (b) find end nodes
    graph_end_node = node # Reserve one node for graph end 
    node += 1
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table.items():
        suc = columns.suc
        if suc:
            columns.end_node = work_table[suc].start_node
        else:
            # Create needed end nodes, avoiding multiple graph end nodes (adaptation)
            if act in end_act:
                columns.end_node = node 
            else:
                columns.end_node = graph_end_node
                node += 1 
        # Generate the graph
        _, _, dummy, _, start, end = columns
        pm_graph.add_arc((start, end), (act, dummy))

    p_graph = pm_graph.to_directed_graph()
    
    return p_graph




def makeCover(prelations, successors):
    """
    prelations = {'activity': ['predecesor1', 'predecesor2'...}
    successors = {'activity': ['successor1', 'successor2'...}

    return a dictionary with the improper covers
    work_table_imp = {index: u(improper covers successors), w(improper covers predecessors)}
    """
    #SConstruct improper cover work table
    MinRev = namedlist.namedlist('MinRev', ['u', 'w'])
                            # [0 Identical successors,   1 Identical Predecessors)
    
    #Group by Identical Successors
    visited_suc = {}
    work_table_imp = {}
    i = 0
    
    for act, columns in successors.items():
        u = set()
        pred = frozenset(columns)
        if pred not in visited_suc:
            visited_suc[pred] = act
            u.add(act)
            for act2, columns2 in successors.items():
                if columns2 == columns:
                    u.add(act2)
                    
        if u:
            work_table_imp[i] = MinRev(list(u), [])
            i+=1
            

    #Group by Identical Predecessors
    visited_pred = {}
    i = 0
    
    for act, columns in prelations.items():
        u.clear()
        pred = frozenset(columns)
        if pred not in visited_pred:
            visited_pred[pred] = act
            u.add(act)
            for act2 in prelations:
                if pred == columns:
                    u.add(act2)
                    
        if u:
            if work_table_imp.has_key(i):
                work_table_imp[i].w = list(u)
            else:
                work_table_imp[i] = MinRev([], list(u))
            i+=1

    return work_table_imp
            
            
            
def main():
    """
    Test Syslo algorithm

    Arguments:
        infile - project file
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()

    # Open the input file collecting the required information.
    activities, _, _, _ = fileFormats.load_with_some_format(args.infile, [fileFormats.PPCProjectFileFormat(),
                                                                          fileFormats.PSPProjectFileFormat()])
    successors = dict(((act[1], act[2]) for act in activities))

    pert_graph = sysloPolynomial(graph.successors2precedents(successors))
    #subgraph = gg1.focus(787, 875) # Error en Large Tavares

    window = graph.Test()
    window.add_image(graph.pert2image(pert_graph))
    graph.gtk.main()
    print pert_graph
    print validation.check_validation(successors, pert_graph)
    return 0



# If the program is run directly
if __name__ == '__main__':
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

