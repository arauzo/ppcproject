"""
Algorithm to draw Graph PERT based on algorithm from Syslo with an Optimal solution
"""

import argparse
import fileFormats
import validation
import namedlist

import graph
import pert
import syslo_table


def sysloOptimal(successors):
    """
    Build a PERT graph using Syslo algorithm

    return p_graph pert.PertMultigraph()
    """
    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_succ_copytion_table(successors)
    end_act = graph.ending_activities(successors)

    succ_copy = successors.copy()

    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                           #   Blocked = (False or Activity with same precedents)  


    #Step 0. Syslo Optimal algorithm
    grafo = graph.successors2precedents(syslo_table.syslo(succ_copy, successors))

    #Step 1. Save the prelations with dummy activities in a work_table 
    work_table = {}
    for act, pre in grafo.items():
        work_table[act] = Columns(pre, False, False, None, None, None)
        if act not in successors:
            pre.dummy = True


    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]

    
    #Step 3. Creating nodes
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


