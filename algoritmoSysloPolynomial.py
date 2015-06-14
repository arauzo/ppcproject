# -*- coding: utf-8 -*-
"""
Algorithm to draw Graph PERT based on algorithm from Syslo in Polynomial time
"""

import namedlist

import graph
import pert
import fileFormats
import validation
import improperCover

def __print_work_table(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %5s %5s %5s %5s %5s" % ('Act', 'Pred', 'Block', 'Dummy', 'Succ', 'start', 'end')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %5s %5s %5s %5s %5s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])



def SysloPolynomial(prelations):

    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)

    #Step 1. Construct work table with Immediate Predecessors
    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents)
    

    
    work_table_pol = improperCover.makeCover(prelations, successors)
    
    uvedoble = []
    visited = []
    final = successors.copy()
            
    for w, pred in prelations.items():
        for v in pred:
            for u in pred:
                if u != v and successors[v] != successors[u] and w not in visited:
                    for key, value in work_table_pol.items():
                        if w in value.w:
                            uvedoble = value.w                

                    for key, value in work_table_pol.items():
                        if set(value.u).issubset(prelations[w]) and len(value.u) > 0:
                            act = set(value.u).pop()
                            if successors[act] != uvedoble:
                                for q in value.u: 
                                    if final.has_key(q):
                                        final[q] = list(set(final[q]) - set(uvedoble) | set([str(act) + '-' + str(w)]))
                                    else:
                                        final[q] = list(set(successors[q]) - set(uvedoble) | set([str(act) + '-' + str(w)]))
                                final[str(act) + '-' + str(w)] = set(uvedoble) & set(successors[q])
                                
                                for l in uvedoble:
                                    visited.append(l)


    final = graph.successors2precedents(final)
    
    
    work_table = {}
    for k, v in final.items():
        if not prelations.has_key(k):
            work_table[k] = Columns(set(v), False, True, None, None, None)
        else:
            work_table[k] = Columns(set(v), False, False, None, None, None)
        
 
    
    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]


        
    #Step 5. Creating nodes
    node = 0 # instead of 0, can start at 100 to avoid confusion with activities named with numbers when debugging
    for act, columns in work_table.items():
        if not columns.blocked:
            columns.start_node = node
            node += 1


    for act, columns in work_table.items():
        if columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node



    #Step 6. Associate activities with their end nodes
    # (a) find one non-dummy successor for each activity
    for act, columns in work_table.items():
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


       
    #Step 8. Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table.items():
        _, _, dummy, _, start, end = columns
        pm_graph.add_arc((start, end), (act, dummy))

    p_graph = pm_graph.to_directed_graph()
    return p_graph



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

    gg1 = SysloPolynomial(graph.successors2precedents(successors))
    #subgraph = gg1.focus(787, 875) # Error en Large Tavares

    window = graph.Test()
    window.add_image(graph.pert2image(gg1))
    graph.gtk.main()
    print gg1
    print validation.check_validation(successors, gg1)
    return 0



# If the program is run directly
if __name__ == '__main__':
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

