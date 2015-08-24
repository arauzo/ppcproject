"""
Algorithm to draw Graph PERT based on algorithm from Syslo with Optimal solution
"""

import argparse
import fileFormats
import namedlist

import graph
import pert
import validation
import syslo_table



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

    
    #Step 0.
    grafo = {}
    alt = graph.successors2precedents(successors)
    grafo = graph.successors2precedents(syslo_table.syslo(prela, grafo, alt))

    #Step 1. Save the new prelation table in a work table
    work_table = {}
    for act, pre in grafo.items():
        if not act in prelations:
            work_table[act] = Columns(pre, False, True, None, None, None)
        else:
            work_table[act] = Columns(pre, False, False, None, None, None)


    #Step 2. Identify Dummy Activities And Identical Precedence Constraint of Diferent Activities
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
    for act, columns in work_table.items():
        suc = columns.suc
        if suc:
            columns.end_node = work_table[suc].start_node
        else:
            # Create needed end nodes, avoiding multiple graph end nodes (adaptation)
            if act in end_act:
                columns.end_node = graph_end_node
            else:
                columns.end_node = node 
                node += 1
    
    # Step 4. Remove redundancy of dummy activities
    vis = []
    for act, columns in work_table.items():
        if columns.dummy == False:
            for q in work_table[act].pre:
                    for w in work_table[act].pre:
                        if q in work_table and w in work_table:
                            if q != w and work_table[q].pre == work_table[w].pre and work_table[q].dummy==True and work_table[w].dummy==True:
                                if w not in vis:
                                    del work_table[w]
                                vis.append(q)
                     
    
    #Step 5. Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table.items():
        _, _, dummy, _, start, end = columns
        pm_graph.add_arc((start, end), (act, dummy))

    p_graph = pm_graph.to_directed_graph()
    return p_graph


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


