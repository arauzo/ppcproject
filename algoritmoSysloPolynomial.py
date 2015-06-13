# -*- coding: utf-8 -*-
"""
Algorithm to draw Graph PERT based on algorithm from Syslo in Polynomial time
"""

import namedlist

import graph
import pert
import fileFormats
import validation

def __print_work_table(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %5s %5s %5s %5s %5s" % ('Act', 'Pred', 'Block', 'Dummy', 'Succ', 'start', 'end')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %5s %5s %5s %5s %5s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])

def __print_work_pol(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %30s %5s %5s %5s %5s" % ('i', 'Ui', 'Wi', 'Dummy', 'Succ', 'start', 'end')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %30s %5s %5s %5s %5s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])



def SysloPolynomial(prelations):

    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)

    #Step 1. Construct work table with Immediate Predecessors
    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents)
    
    #Step 1. Construct work table with Immediate Predecessors
    MinRev = namedlist.namedlist('MinRev', ['u', 'w', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents)
    

    #################
    #################


    work_table_pol = {}
    work_table = {}
    
    #Step 2. Identify Identical Successor Constraint of Diferent Activities
    visited_pred = {}
    i = 0
    for act, columns in successors.items():
        u = []
        pred = frozenset(columns)
        if pred not in visited_pred:
            visited_pred[pred] = act
            u.append(act)
            for act2, columns2 in successors.items():
                if columns2 == columns:
                    u.append(act2)
                    
        if len(u) > 0:
            work_table_pol[i] = MinRev(set(u), False, False, None, None, None)
            i+=1
            
        
    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    i = 0
    for act, columns in prelations.items():
        u = []
        pred = frozenset(columns)
        if pred not in visited_pred:
            visited_pred[pred] = act
            u.append(act)
            for act2, columns2 in prelations.items():
                if columns2 == columns:
                    u.append(act2)
                    
        if len(u) > 0:
            if work_table_pol.has_key(i):
                work_table_pol[i] = MinRev(work_table_pol[i].u, list(set(u)) , False, None, None, None)
                i+=1
            else:
                work_table_pol[i] = MinRev([], list(set(u)), False, None, None, None)
                i+=1
        
    for k, v in work_table_pol.items():      
        if v.w == False:
            v.w = []
            

    #################
    #################

    final = {}
    uvedoble = []
    visited = []
    
    x = 0
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
                                #print w, " : ", prelations[w],  successors[w], "____________________", u, v, visited
                                #print "COMPARA: ", successors[pipo], " - ", uvedoble, " // ", successors[u], successors[v]
                                for q in value.u: 
                                    if final.has_key(q):
                                        final[q] = list(set(final[q]) - set(uvedoble) | set(['z' + str(x)]))
                                    else:
                                        final[q] = list(set(successors[q]) - set(uvedoble) | set(['z' + str(x)]))
                                final['z' + str(x)] = set(uvedoble) & set(successors[q])
                                
                                for l in uvedoble:
                                    visited.append(l)
                                x += 1

    
    for w, suc in successors.items():
        if not final.has_key(w):
            final[w] = suc
    
    final = graph.successors2precedents(final)
    
    for k, v in final.items():
        if not prelations.has_key(k):
            work_table[k] = Columns(set(v), False, True, None, None, None)
        else:
            work_table[k] = Columns(set(v), False, False, None, None, None)
        

    
    #print "\n--- Step 1 ---"
    #__print_work_table(work_table)   
    
    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]

    #print "\n--- Step 2 ---"
    #__print_work_table(work_table)

        
    #Step 5. Creating nodes
    node = 0 # instead of 0, can start at 100 to avoid confusion with activities named with numbers when debugging
    for act, columns in work_table.items():
        if not columns.blocked:
            columns.start_node = node
            node += 1

    #print "\n--- Step 5a ---"
    #__print_work_table(work_table)

    for act, columns in work_table.items():
        if columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node

    #print "\n--- Step 5b ---"
    #__print_work_table(work_table)


    #Step 6. Associate activities with their end nodes
    # (a) find one non-dummy successor for each activity
    for act, columns in work_table.items():
        for suc, suc_columns in work_table.items():
            if not suc_columns.blocked:
                if act in suc_columns.pre:
                    columns.suc = suc
                    break

#    print "\n--- Step 6a ---"
#    __print_work_table(work_table)

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

