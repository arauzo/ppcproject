# -*- coding: utf-8 -*-
"""
Algorithm to draw Graph PERT based on algorithm from Syslo in Polynomial time
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

    #Step 1. Construct work table with Immediate Predecessors
    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents)

    #
    work_table_pol = {}
    improperCover(successors, work_table_pol)
    improperCover(prelations, work_table_pol)       
  

    #
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
                        if set(value.u).issubset(prelations[act]) and len(value.u) > 0:
                            vertex = set(value.u).pop()
                            
                            # Compare successors of a row with the improper cover of the activity
                            if successors[vertex] != w:
                                for q in value.u: 
                                    if final.has_key(q):
                                        final[q] = list(set(final[q]) - set(w) | set([str(vertex) + separator + str(act)]))
                                    else:
                                        final[q] = list(set(successors[q]) - set(w) | set([str(vertex) + separator + str(act)]))
                                final[str(vertex) + separator + str(act)] = set(w) & set(successors[q])
                                
                                for l in w:
                                    visited.append(l)

    
    
    final = graph.successors2precedents(final)
    work_table = {}
    for k, v in final.items():
        work_table[k] = Columns(set(v), False, False, None, None, None)
        
 
    
    #Step 2. Identify Dummy Activities And Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if not prelations.has_key(act):
            columns.dummy = True
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




def improperCover(mydict, work_table_pol):
    """

    """
    #SConstruct work table with Immediate Predecessors
    MinRev = namedlist.namedlist('MinRev', ['u', 'w'])
                            # [0 Identical successors,   1 Identical Predecessors)
    
    #Identify Identical Successor Constraints of Diferent Activities
    visited_pred = {}
    i = 0
    for act, columns in mydict.items():
        u = []
        pred = frozenset(columns)
        if pred not in visited_pred:
            visited_pred[pred] = act
            u.append(act)
            for act2, columns2 in mydict.items():
                if columns2 == columns:
                    u.append(act2)
                    
        if len(u) > 0:
            if not work_table_pol.has_key(i):
                work_table_pol[i] = MinRev(set(u), [])
            if work_table_pol.has_key(i):
                    work_table_pol[i] = MinRev(work_table_pol[i].u, list(set(u)))
            else:
                    work_table_pol[i] = MinRev([], list(set(u)))
            i+=1
            
    return
            
            
            
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

