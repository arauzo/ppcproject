# -*- coding: utf-8 -*-
"""
Algorithm to draw Graph PERT based on algorithm from Syslo
"""
import namedlist
import graph
import pert
import os
import Kahn1962
import syslo_table

global i

def __print_work_table(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %5s %5s %5s %5s %5s" % ('Act', 'Pred', 'Block', 'Dummy', 'Succ', 'start', 'end')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %5s %5s %5s %5s %5s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])



def SysloPolynomial(prelations):
    """
    Build a PERT graph using Syslo algorithm

    return p_graph pert.PertMultigraph()
    """
    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)

    Kahn1962.check_cycles(successors)
    prela = prelations.copy()

    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents)  


    grafo = {}
    endnodes = 0
    

    for t, r in prela.items():
        if len(r) == 0:
            endnodes += 1
            
    while len(prela) - endnodes > 1:
        temp = subgraph(prela)

        tempgrafo = syslo_table.syslo(temp, grafo)
        #print "TEMPGRAFO: ", tempgrafo
        for q, values in tempgrafo.items():
            if len(values) != 0:
                grafo[q] = values
            if q == max(prelations):
                grafo[q] = values
            
        for d in prela.keys():
                if d in temp.keys():
                    del prela[d]
                
        #print "----", grafo
        #raw_input('-->')        
        
    for c, d in prelations.items():
        if c not in grafo.keys():
            grafo[c] = d
    
   
    
    grafo = graph.successors2precedents(grafo)
    
    work_table = {}
    for act, pre in grafo.items():
        work_table[act] = Columns(set(pre), False, None, None, None, None)


    #Step 6. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]


    #Step 7. Creating nodes
    node = 0 # instead of 0, can start at 100 to avoid confusion with activities named with numbers when debugging
    for act, columns in work_table.items():
        if not columns.dummy and not columns.blocked:
            columns.start_node = node
            node += 1

    for act, columns in work_table.items():
        if not columns.dummy and columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node


    #Step 8. Associate activities with their end nodes
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
                columns.end_node = node 
            else:
                columns.end_node = graph_end_node
                node += 1 


    # Step  . Set dummies activities
    work_table_final = {}
    for act, predecessors in work_table.items():
        if not act in prelations:
            work_table_final[act] = Columns(work_table[act].pre, work_table[act].blocked, True, work_table[act].suc, work_table[act].start_node, work_table[act].end_node)
        else:
            work_table_final[act] = Columns(work_table[act].pre,  work_table[act].blocked, False, work_table[act].suc, work_table[act].start_node, work_table[act].end_node)


    print "STEP FINAL"
    __print_work_table(work_table_final)
    
    #Step 5 Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table_final.items():
        _, _, dummy, _, start, end = columns
        pm_graph.add_arc((start, end), (act, dummy))
    p_graph = pm_graph.to_directed_graph()
    
    return p_graph
 
 
 

        

def subgraph(prela):
    
    # Step 0. Agupar por dependencias ordenado topologicamente
    mul = []
    temp = {}
    
    for act, predecessors in sorted(prela.items()):
        pre = frozenset(predecessors)
        if len(mul) == 0:
            if pre & set(predecessors):
                for r in pre:
                    mul.append(r)
                for r in predecessors:
                    mul.append(r)
                #print act, predecessors, set(mul)
                temp[act] = predecessors
        else:
            if set(mul) & set(predecessors):
                for r in pre:
                    mul.append(r)
                for r in predecessors:
                    mul.append(r)
                #print act, predecessors, set(mul)
                temp[act] = predecessors 
                
    return temp

def save_graph2file(pert_graph, name):

    image_text = graph.pert2image(pert_graph) 
    fsalida = open(os.path.split('SysloPolynomial')[1] + '_' + name + '.svg', 'w')
    fsalida.write(image_text)
    fsalida.close()
    print 'El grafo se ha guardado correctamente: SysloPolynomial' , name, '.svg'
    
    return 0
      
      
      
        
def main():
    ejemplo01 = {
        '1' : ['5','6', '7'],
        '2' : ['6','7'],
        '3' : ['6'],
        '4' : ['7'],
        '5' : [],
        '6' : [],
        '7' : [],
    }

    ejemplo02 = {

        'a' : ['k','h', 'f', 'g'],
        'b' : ['k','g'],
        'c' : ['h', 'f', 'g'],
        'd' : ['f', 'g'],
        'e' : ['h', 'i', 'g'],
        'f' : ['i', 'l', 'j'],
        'g' : ['l', 'j'],   
        'h' : ['j'], 
        'i' : [], 
        'j' : [], 
        'k' : [],
        'l' : [],
    }
    
    
    ejemplo04 = {
        'b' : ['g','e', 'f'],
        'c' : ['f', 'g', 'h'],
        'd' : ['f', 'g', 'h'],
        'e' : [],
        'f' : [],   
        'g' : [],
        'h' : [], 
    }
    
    ejemplo05 = {
        'a' : ['c','d'],
        'b' : ['c','d', 'e'],
        'c' : ['i', 'j'],
        'd' : ['f', 'g', 'h'],
        'e' : ['h'],
        'f' : ['i', 'j'],
        'g' : ['j', 'k'],
        'h' : ['k'],
        'i' : [],
        'j' : ['l'],
        'k' : ['l'],
        'l' : [],
    }
    
    
    dict_list = [
                    #('ejemplo01', ejemplo01),
                    ('ejemplo02', ejemplo02),
                    #('ejemplo04', ejemplo04),
                    ('ejemplo05', ejemplo05),
                ]
    
    for name, dict_i in dict_list:
        print "\n", name
        print dict_i
        prueba = SysloPolynomial(dict_i)
        
        #Save the graph in a file
        save_graph2file(prueba, name)

    return 0   
    
    
# If the program is run directly
if __name__ == '__main__': 
    # Imports needed only here
    import sys
    # Run
    sys.exit(main())


