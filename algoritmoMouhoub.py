"""
Algorithm to build a PERT graph based on Mouhoub algorithm
"""
import namedlist
import graph
import pert
import os

import Kahn1962
import Zconfiguration
import MouhoubRules


def mouhoub(successors):
    """
    Build a PERT graph applying Mouhoub algorithm rules

    return p_graph pert.PertMultigraph()
    """
    # Adaptation to avoid multiple end nodes
    reverserd_prelations = graph.reversed_prelation_table(successors)
    end_act = graph.ending_activities(reverserd_prelations)
    
    #Step 1. Construct work table with Immediate Predecessors in the complete bipartite graph
    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents) 
    
# PREVIOUS CONDITIONS
    successors_copy = successors.copy()
    complete_bipartite = successors
    
    # Previous condition 01. Test Delta Configuration
    print "Check Delta Configuration: ", Kahn1962.check_cycles(successors)
    
    # Previous condition 02.  Remove Z Configuration
    complete_bipartite.update(Zconfiguration.zconf(successors))  
    
# MOUHOUB RULES
    # RULE 01, 02 are a special case of RULE 07
    
    #RULE 03
    loop = True
    while loop != False:
        loop = MouhoubRules.rule_3(complete_bipartite)
      
    #RULE 04
    loop = True
    while loop != False:
        loop = MouhoubRules.rule_4(complete_bipartite)
    
    #RULE 05 and 06
    MouhoubRules.rule_5_6(complete_bipartite, successors_copy)
    
    #RULE 07 (RULE 01, RULE 02)
    MouhoubRules.rule_1_2_7(complete_bipartite, successors_copy)

    # Contract dummy arcs by iteration of RULE 03 and RULE 04
    loop = True
    while loop != False:
        loop = MouhoubRules.rule_3(complete_bipartite)
    loop = True
    while loop != False:
        loop = MouhoubRules.rule_4(complete_bipartite)

   
# STEPS TO BUILD THE PERT GRAPH
     
    #Step 1. Save the prelations in the work table
    complete_bipartite = graph.successors2precedents(complete_bipartite)
    work_table = {}
    for act, sucesores in complete_bipartite.items():
        if str(act).find('-') ==-1:
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

    
    #Step 4. Associate activities with their end nodes
    # (a) find one non-dummy successor for each activity
    for act, columns in work_table.items():
        for suc, suc_columns in work_table.items():
            if  not suc_columns.blocked:
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


    #Step 5. Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table.items():
        _, _, dummy, _, start, end = columns
        pm_graph.add_arc((start, end), (act, dummy))
    p_graph = pm_graph.to_directed_graph()
    
    return p_graph


def save_graph2file(pert_graph, name):
    """
    Save PERT graph in a image file
    """
    image_text = graph.pert2image(pert_graph) 
    fsalida = open(os.path.split('mouhoub')[1] + '_' + name + '.svg', 'w')
    fsalida.write(image_text)
    fsalida.close()
    print 'El grafo se ha guardado correctamente: \mouhoub_' , name, '.svg'

    return 0



def main():
    
    ejemplo01 = {
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

    ejemplo02 = {
        'a' : ['d', 'e', 'f'],
        'b' : ['e', 'f'],
        'c' : ['g', 'h'],
        'd' : ['i', 'j'],
        'e' : ['i', 'j'],
        'f' : ['g', 'h'],
        'g' : ['k','l'],
        'h' : ['m'],
        'i' : ['k', 'l'],
        'j' : [],
        'k' : ['n'],
        'l' : ['n'],
        'm' : ['n'],
        'n' : [],    
    }
    
    ejemplo03 = {
        'a' : ['b', 'c', 'g'],
        'b' : ['d', 'e'],
        'c' : ['e', 'f', 'g'],
        'd' : ['h'],
        'e' : ['h'],
        'f' : ['h', 'i'],
        'g' : ['i'],
        'h' : ['j'],
        'i' : ['j'],
        'j' : [],
    }
    
    ejemplo04 = {
        'a' : ['b', 'c'],
        'b' : ['d', 'e'],
        'c' : ['f', 'g'],
        'd' : ['h'],
        'e' : ['h', 'g'],
        'f' : ['h', 'i'],
        'g' : ['i'],
        'h' : ['j'],
        'i' : ['j'],
        'j' : [],
    }
    
    ejemplo05 = {
        'a' : ['c', 'd', 'e', 'f', 'g'],
        'b' : ['c', 'd', 'e', 'f', 'g'],
        'c' : ['d', 'e', 'f', 'g'],
        'd' : ['f', 'g'],
        'e' : ['h', 'g', 'i'],
        'f' : ['h', 'i'],
        'g' : [],
        'h' : ['i'],
        'i' : ['j'],
        'j' : [],
    }
    
    ejemplo06 = {
        'a' : ['b', 'g', 'h'],
        'b' : ['d', 'e'],
        'c' : ['e', 'f', 'g'],
        'd' : ['h'],
        'e' : ['h'],
        'f' : ['h', 'i'],
        'g' : ['i'],
        'h' : ['j'],
        'i' : ['j'],
        'j' : [],
    }
    
    ejemplo07 = {
        'a' : ['d', 'e', 'f'],
        'b' : ['d', 'e', 'f'],
        'c' : ['d', 'e', 'f'],
        'd' : [],
        'e' : [],
        'f' : [],
    }
    
    ejemplo08 = {
        'a' : ['d', 'e', 'f', 'g'],
        'b' : ['e', 'f', 'g'],
        'd' : [],
        'e' : [],
        'f' : [],
        'g' : [],
    }

    ejemplo09 = {
        'a' : ['e'],
        'b' : ['d', 'c', 'e'],
        'c' : [],
        'd' : ['e'],
        'e' : [],
    }
    
    ejemplo10 = {
        'a' : ['c', 'd'],
        'b' : ['d'],
        'c' : [],
        'd' : [],
    }
    
    ejemplo11 = {
        'a' : ['c', 'd'],
        'b' : ['d', 'e'],
        'c' : [],
        'd' : [],
        'e' : [],
    }
    
    ejemplo12 = {
        'a' : ['e', 'g', 'h'],
        'b' : ['f', 'g', 'h'],
        'c' : ['h'],
        'd' : ['h'],
        'e' : [],
        'f' : [],
        'g' : [],
        'h' : [],
    }
    
    ejemplo13 = {
        'a' : ['f', 'g', 'h', 'i', 'j'],
        'b' : [ 'g', 'h', 'i', 'j'],
        'c' : ['h', 'i', 'j'],
        'd' : ['i', 'j'],
        'e' : ['j'],
        'f' : [],
        'g' : [],
        'h' : [],
        'i' : [],
        'j' : [],
    }
    
    ejemplo14 = {
        'a' : ['d'],
        'b' : ['d','e'],
        'c' : ['f','e', 'g'],
        'd' : [],
        'e' : [],
        'f' : [],
        'g' : [],
    }
    
    ejemplo15 = {
        'a' : ['d', 'c'],
        'b' : ['d', 'c'],
        'c' : [],
        'd' : [],
    }
    
    ejemplo16 = {
        'a' : ['c', 'd', 'e', 'f', 'g'],
        'b' : ['e'],
        'c' : [],
        'd' : [],
        'e' : [],
        'f' : [],
        'g' : [],

    }
    
    ejemplo17 = {
        'a' : ['f', 'g', 'h', 'i', 'j'],
        'b' : ['g', 'h', 'i', 'j'],
        'c' : ['h', 'j'],
        'd' : ['i', 'j'],
        'e' : ['j'],
        'f' : [],
        'g' : [],
        'h' : [],
        'i' : [],
        'j' : [],
    }
    
    dict_list = [
                    ('ejemplo01', ejemplo01),
                    ('ejemplo02', ejemplo02),
                    ('ejemplo03', ejemplo03),
                    ('ejemplo04', ejemplo04),
                    ('ejemplo05', ejemplo05),
                    ('ejemplo06', ejemplo06),
                    ('ejemplo07', ejemplo07),
                    ('ejemplo08', ejemplo08),
                    ('ejemplo09', ejemplo09),
                    ('ejemplo10', ejemplo10),
                    ('ejemplo11', ejemplo11),
                    ('ejemplo12', ejemplo12),
                    ('ejemplo13', ejemplo13),
                    ('ejemplo14', ejemplo14),
                    ('ejemplo15', ejemplo15),
                    ('ejemplo16', ejemplo16),
                    ('ejemplo17', ejemplo17),
                ]
    
    for name, dict_i in dict_list:
        print "\n", name
        print dict_i
        prueba = mouhoub(dict_i)
        
        #Save the graph in a file
        save_graph2file(prueba, name)

    return 0   
    
    
# If the program is run directly
if __name__ == '__main__': 
    # Imports needed only here
    import sys
    # Run
    sys.exit(main())


