"""
Algorithm to build a PERT graph based on Malek Mouhoub et. al algorithm
"""
import namedlist
import graph
import pert
import fileFormats
import validation
import argparse
import Zconfiguration
import MouhoubRules


def mouhoub(prelations, window=None):
    """
    Build a PERT graph applying Mouhoub algorithm rules

    return p_graph pert.PertMultigraph()
    """
    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    successors_copy = graph.reversed_prelation_table(prelations.copy())
    end_act = graph.ending_activities(successors)

    complete_bipartite = successors

    #Step 1.Save the prelations in a work table 
    # (a) Build a work table with immediate predecessors
    Columns = namedlist.namedlist('Columns', ['pre', 'su', 'blocked', 'dummy', 'suc', 'start_node', 'end_node', 'aux'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents) 
    
    # (b) Build an auxiliar work table with inmediate predecessors    
    work_table_pred = {}
    for act, pred in prelations.items():
        work_table_pred[act] = Columns(set(pred), None, None, False, None, None, None, None)
   
   # (c) Build an auxiliar work table with inmediate successors
    work_table_suc = {}
    for act, succ in successors_copy.items():
        work_table_suc[act] = Columns(set(succ), None, None, False, None, None, None, None)

        
# PREVIOUS CONDITIONS
    # Previous condition 01. Test Delta Configuration - (Already tested from prueba.py Khan.CheckCycles())
    
    # Previous condition 02.  Remove Z Configuration. Update the prelation table stored in the dict
    complete_bipartite.update(Zconfiguration.zconf(successors))  
    
    
# STEPS TO BUILD THE PERT GRAPH
    #Step 1. Save the prelations in the work table
    complete_bipartite = graph.successors2precedents(complete_bipartite)
    work_table = {}
    for act, sucesores in complete_bipartite.items():
        if act in prelations:
            work_table[act] = Columns(set(sucesores), successors[act], None, False, None, None, None, None)
        else:
            work_table[act] = Columns(set(sucesores), successors[act], None, True, None, None, None, None)
              
           
    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]
                   
            
    #Step 3. Creating nodes
    node = 0
    for act, columns in work_table.items():
        if not columns.blocked:
            columns.start_node = node
            node += 1

    for act, columns in work_table.items():
        if columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node

    
    #Step 4. Associate activities with their end nodes
    # (a) find one non-dummy successor for each activity
    for act, columns in work_table.items():
        for suc, suc_columns in work_table.items():
            if  not suc_columns.blocked:
                if act in suc_columns.pre:
                    columns.suc = suc
                    break


    # (b) Find end nodes
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


    # Step 5. Apply Mouhoub algorithm rules
    # Rule 01
    work_table_G1 = MouhoubRules.rule_1(work_table_pred, work_table, Columns)
    
    # Rule 02
    work_table_G2 = MouhoubRules.rule_2(work_table_suc, work_table, work_table_G1, Columns)
     
    # Rule 03
    work_table_G3 = MouhoubRules.rule_3(work_table_G2, work_table, Columns)

    # Rule 04
    work_table_G4 = MouhoubRules.rule_4(work_table_G3, work_table, Columns)

    # Rule 05 and Rule 06
    work_table_G5_6 = MouhoubRules.rule_5_6(work_table_suc, work_table, work_table_G4, Columns)
    
    # Rule 03
    work_table_G3a = MouhoubRules.rule_3(work_table_G5_6, work_table, Columns)

    # Rule 04
    work_table_G4a = MouhoubRules.rule_4(work_table_G3a, work_table, Columns)

    # Rule 07
    work_table_G7 =  MouhoubRules.rule_7(successors_copy, successors, work_table_G4a, Columns, node)


    # Step 6. Save the output graph after the rules of the Mouhoub algorithm
    work_table_final = {}
    for act, sucesores in work_table_G7.items():
        work_table_final[act] = Columns(sucesores.pre, sucesores.su, sucesores.blocked, sucesores.dummy, sucesores.suc, sucesores.start_node, sucesores.end_node, sucesores.aux)
    

    #Step 7. Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table_final.items():
        _, _, _, dummy, _, start, end, _ = columns
        pm_graph.add_arc((start, end), (act, dummy))
    p_graph = pm_graph.to_directed_graph()
    
    return p_graph




def main():
    """
    Test Mouhoub algorithm

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

    window = graph.Test()
    
    pert_graph = mouhoub(graph.successors2precedents(successors), window)
    window.add_image(graph.pert2image(pert_graph))
    
    graph.gtk.main()
    
    print validation.check_validation(successors, pert_graph)

    return 0   
    _
    
# If the program is run directly
if __name__ == '__main__': 
    # Imports needed only here
    import sys
    # Run
    sys.exit(main())


