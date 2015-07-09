# -*- coding: utf-8 -*-
"""
Algorithm to draw Graph PERT based on algorithm from Syslo with an Optimal solution
"""

import argparse
import fileFormats
import validation
import namedlist
import graph
import pert
import Kahn1962
import syslo_table


def __print_work_table(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %5s %5s %5s %5s %5s" % ('Act', 'Pred', 'Block', 'Dummy', 'Succ', 'start', 'end')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %5s %5s %5s %5s %5s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])


def sysloOptimal(prelations):
    """
    Build a PERT graph using Syslo algorithm

    return p_graph pert.PertMultigraph()
    """
    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)
    
    #Kahn1962.check_cycles(successors)
    prela = successors.copy()

    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                           #   Blocked = (False or Activity with same precedents)  

    alt = graph.successors2precedents(successors)
    #Step 0.
    grafo = {}
    grafo = graph.successors2precedents(syslo_table.syslo(prela, grafo, alt))

    #Step 1.
    work_table = {}
    for act, pre in grafo.items():
        if not act in prelations:
            work_table[act] = Columns(pre, False, True, None, None, None)
        else:
            work_table[act] = Columns(pre, False, False, None, None, None)



    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]

    #print "STEP 2
    #__print_work_table(work_table)
    
    #Step 3. Creating nodes
    node = 0 # instead of 0, can start at 100 to avoid confusion with activities named with numbers when debugging
    for act, columns in work_table.items():
        if not columns.blocked:
            columns.start_node = node
            node += 1
        if columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node

   # print "STEP 3
   # __print_work_table(work_table)
    
    #Step 4. Associate activities with their end nodes
    # (a) find one non-dummy successor for each activity
    for act, columns in work_table.items():
        for suc, suc_columns in work_table.items():
            if  not suc_columns.blocked:
                if act in suc_columns.pre:
                    columns.suc = suc
                    break

    
    #print "STEP 4"
    #__print_work_table(work_table)
    
    
    # (b) find end nodes
    graph_end_node = node # Reserve one node for graph end 
    node += 1
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


    #print "STEP 5"
    #__print_work_table(work_table)
    
    #Step 5 Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table.items():
        _, _, dummy, _, start, end = columns
        pm_graph.add_arc((start, end), (act, dummy))
    p_graph = pm_graph.to_directed_graph()
    
    return p_graph




def main():
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()

    # Open the input file collecting the required information.
    activities, _, _, _ = fileFormats.load_with_some_format(args.infile, [fileFormats.PPCProjectFileFormat(),
                                                                          fileFormats.PSPProjectFileFormat()])
    successors = dict(((act[1], act[2]) for act in activities))

    window = graph.Test()
    
    pert_graph = sysloOptimal(graph.precedents2successors(successors, window))
    window.add_image(graph.pert2image(pert_graph))
    
    graph.gtk.main()
    
    print validation.check_validation(successors, pert_graph)

    return 0 
    
    
    
# If the program is run directly
if __name__ == '__main__': 
    # Imports needed only here
    import sys
    # Run
    sys.exit(main())


