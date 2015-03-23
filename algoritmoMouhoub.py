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


def mouhoub(prelations):
    """
    Build a PERT graph applying Mouhoub algorithm rules

    return p_graph pert.PertMultigraph()
    """
    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)
    
    successors_copy = graph.reversed_prelation_table(prelations.copy())
    complete_bipartite = successors
    predecessors = graph.reversed_prelation_table(successors_copy.copy())
    #Step 1. Construct work table with Immediate Predecessors in the complete bipartite graph
    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents) 
    
# PREVIOUS CONDITIONS
    # Previous condition 01. Test Delta Configuration - (Already tested)
    
    # Previous condition 02.  Remove Z Configuration
    complete_bipartite.update(Zconfiguration.zconf(successors))  
    
# MOUHOUB RULES
    # Rule 01
    MouhoubRules.rule_1(successors_copy, complete_bipartite)
    
    # Rule 02
    MouhoubRules.rule_2(predecessors, complete_bipartite)
        
    # Contract dummy arcs by iteration of Rule 03 and Rule 04
    MouhoubRules.rule_3_4(complete_bipartite)
    
    #Rule 05 Rule 06
    MouhoubRules.rule_5_6(successors_copy, complete_bipartite)
    
    # Contract dummy arcs by iteration of Rule 03 and Rule 04
    MouhoubRules.rule_3_4(complete_bipartite)

    #RULE 07
    #MouhoubRules.rule_7(complete_bipartite)
    
# STEPS TO BUILD THE PERT GRAPH
     
    #Step 1. Save the prelations in the work table
    complete_bipartite = graph.successors2precedents(complete_bipartite)
    work_table = {}
    for act, sucesores in complete_bipartite.items():
        if act in prelations:
            work_table[act] = Columns(set(sucesores), None, False, None, None, None)
        else:
            work_table[act] = Columns(set(sucesores), None, True, None, None, None)
                
          
    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]
                   
            
    #Step 3. Creating nodes
    node = 0 # instead of 0, can start at 100 to avoid confusion with activities named with numbers when debugging
    for act, columns in work_table.items():
        if not columns.blocked:
            columns.start_node = node
            node += 1

    for act, columns in work_table.items():
        if columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node

    
    #Step 4a. Associate activities with their end nodes
    # (a) find one non-dummy successor for each activity
    for act, columns in work_table.items():
        for suc, suc_columns in work_table.items():
            if  not suc_columns.blocked:
                if act in suc_columns.pre:
                    columns.suc = suc
                    break


    #Step 4b. Find end nodes
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

    
    #Step 5. Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table.items():
        _, _, dummy, _, start, end = columns
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

    pert_graph = mouhoub(graph.successors2precedents(successors))

    window = graph.Test()
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


