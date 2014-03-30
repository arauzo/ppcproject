"""
Algorithm to draw Graph PERT based on Algorithm Yuval Cohen and Arick Sadeh
"""
import copy
import collections
import operator

import graph
import pert
import fileFormats
import validation

def cohen_sadeh(prelations):
    """
    Build graph PERT using Cohen-Sadeh algorithm
    Note: the original algorithm does not consider parallel activities (creates a multigraph)
    
    prelations = {'activity': ['prelations1', 'prelations2'...}
    
    return graph pert.Pert()
    """
    #Step 1. Construct Immediate Predecessors Table
    work_table = {}
    for act, predecessors in prelations.items():
                          # [Predecesors,     Blocked, Dummy, Successors, Start node, End node]
        work_table[act] = [set(predecessors), False,   False, None,       None,       None]

    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = set()
    for act, columns in work_table.items():
        pred = columns[0] 
        if pred not in visited_pred:
            visited_pred.add( frozenset(pred) )
        else:
            columns[1] = True

    #Step 3. Identify Necessary Dummy Arcs
    dups = set()
    visited_act = set()
    for columns in work_table.values():
        pred = columns[0]
        if not columns[1]: # not blocked
            for act in pred:
                if act in visited_act:
                    dups.add(act)
                visited_act.add(act)                        

    #Step 3.2, 3.3 and 4. Create rows and information for Dummy Arcs
    dummy_counter = collections.Counter()
    for act, columns in work_table.items():
        # Avoid blocked
        if not columns[1]:
            predecessors = columns[0]
            if len(predecessors) > 1:
                for act in predecessors:
                    if act in dups:
                        predecessors.remove(act)
                        dummy_name = act + '-d' + str(dummy_counter[act])
                        dummy_counter[act] += 1
                        predecessors.add(dummy_name)
                        work_table[dummy_name] = [set([act]), False, True, None, None, None]
                       
    #Step 5. Creating nodes
    node = 0
    pred_to_nodes = {}
    for act, columns in work_table.items():
        if not columns[2]: # not dummy
            pred = columns[0]
            if frozenset(pred) not in pred_to_nodes:
                pred_to_nodes[frozenset(pred)] = node
                columns[4] = node
                node += 1
            else:
                columns[4] = pred_to_nodes[frozenset(pred)]                

    #Step 6. Associate activities with their end nodes
    # (a) find one non-dummy successor for each activity
    for act, columns in work_table.items():
        for suc, suc_columns in work_table.items():
            if not suc_columns[2]: 
                if act in suc_columns[0]:
                    columns[3] = suc 
                    break 

    # (b) find end node
    for act, columns in work_table.items():
        suc = columns[3]
        if suc:
            end_node = work_table[suc][4]
        else:
            end_node = node
            node += 1
        columns[5] = end_node

    #Step 7. Associate dummy arcs with start nodes
    for act, columns in work_table.items():
        if columns[2]:
            pred = iter(columns[0]).next()
            start_node = work_table[pred][5]            
            columns[4] = start_node

#    print "WC:"
#    for k,v in work_table.items():
#        print k,v

    #Step 8. Generate the graph
    graph = pert.PertMultigraph()
    for act, columns in work_table.items():
        _, _, dummy, _, start, end = columns
        graph.add_arc( (start, end), (act, dummy) )

    graph = graph.to_directed_graph()
    return graph.renumerar()


def test(prelations, graph):
    finished_activities = {}
    successors_nodes = []
    cola = collections.deque()
    
    print "Cola:", cola
    print "Dict finished activiities:",finished_activities
    print "PRELATIONS:", prelations
    print "Graph:", graph
    
    #Find Nodo without predecessors
    for nodo, nodo_successor in graph.predecessors.items():
        if len(nodo_successor) == 0:
            successors_nodes.append(nodo)
    
    if len(successors_nodes) != 1:
        raise Exception ("**ERROR** No es un grafo pert correcto")
    else:
        print "Nodo start:", successors_nodes
    
    cola.appendleft(successors_nodes[0])
    print "Cola:", cola
    
    while len(cola) > 0:
        node = cola.pop()
        print "NODE:", node
        for sig in graph.successors[node]:
            print "SIG:", sig
            activity, dummy = graph.arcs[(node, sig)]
            print "Activity:", activity
            print "prelations:", prelations
            if sig not in finished_activities:
                finished_activities[sig] = [ [activity], 1]
            else:
                finished_activities[sig][0] += [activity]
                finished_activities[sig][1] += 1
            if finished_activities[sig][1] == len(graph.predecessors[sig]):
                cola.append(sig)

    print "Finished_activities:", finished_activities

    print "PRELATIONS ENDS:", prelations
    print "Predecessor"
    for act, suc in graph.successors.items():
        print "NODOstart:", act, "NODOend:",  suc
    print "Successors"
    for act, suc in graph.predecessors.items():
        print "NODOend:", act, "NODOstart:",  suc
        
def main():
    """
    Generates a ppc format file from a library file.
    This new file will be filled with the information of the fields required to perform the
    simulation of the activity duration.

    The program shall receive four arguments:
        infile (.sm file whose data will be read)
        outfile (.ppc file in which the info required for the simulation will be saved)
        -d (type of statistical distribution to be used)
        -k (proportionality constant of the typical deviation)
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')                         
#    parser.add_argument('outfile')
#    parser.add_argument('-d', '--distribution', default='Beta', 
#                        choices=['Beta', 'Normal', 'Uniform', 'Triangular'],
#                        help='Statistical distribution (default: Beta)')
#    parser.add_argument('-k', default=0.2, type=float, 
#                        help='Standard deviation for generated values (default: 0.2)')
    args = parser.parse_args()

    # Open the input file collecting the required information.
    activities, schedules, recurso, asignacion = fileFormats.load_with_some_format(args.infile, [fileFormats.PPCProjectFileFormat(),fileFormats.PSPProjectFileFormat()])
    successors = dict(((act[1], act[2]) for act in activities))
    
    gg1 = cohen_sadeh(graph.successors2precedents(successors))
    #test(successors, gg1)
    

#    gg11 = cohen_sadeh(successors)
#    test(successors, gg11)

#    gg = cohen_sadeh(graph.successors2precedents(successors))
#    print graph.successors2precedents(successors)

#    gg2 = cohen_sadeh(successors)
#    print successors

    window = graph.Test() 
    window.add_image(graph.pert2image(gg1))
#    window.add_image(graph.pert2image(gg11))
    graph.gtk.main()
    print "Successors: ", successors
    print "gg1: ", gg1.pertSuccessors()
    print validation.check_validation(successors, gg1)
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())
