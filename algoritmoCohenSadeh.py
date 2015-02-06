"""
Algorithm to draw Graph PERT based on algorithm from Yuval Cohen and Arick Sadeh
"""
import collections
import namedlist

import graph
import pert
import fileFormats
import validation

def __print_work_table(table):
    """
    For debugging purposes, pretty prints CohenSadeh working table
    """
    print "%-5s %-30s %5s %5s %5s %5s %5s" % ('Act', 'Pred', 'Block', 'Dummy', 'Succ', 'start', 'end')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %5s %5s %5s %5s %5s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])


def cohen_sadeh(prelations):
    """
    Build graph PERT using Cohen-Sadeh algorithm
    Note: the original algorithm does not consider parallel activities (creates a multigraph)

    prelations = {'activity': ['predecesor1', 'predecesor2'...}

    return graph pert.Pert()
    """
    # Adaptation to avoid multiple end nodes
    successors = graph.reversed_prelation_table(prelations)
    end_act = graph.ending_activities(successors)

    #Step 1. Construct work table with Immediate Predecessors
    Columns = namedlist.namedlist('Columns', ['pre', 'blocked', 'dummy', 'suc', 'start_node', 'end_node'])
                            # [0 Predecesors,   1 Blocked, 2 Dummy, 3 Successors, 4 Start node, 5 End node]
                            #   Blocked = (False or Activity with same precedents)
    work_table = {}
    for act, predecessors in prelations.items():
        work_table[act] = Columns(set(predecessors), False, False, None, None, None)

#    print "\n--- Step 1 ---"
#    __print_work_table(work_table)

    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    visited_pred = {}
    for act, columns in work_table.items():
        pred = frozenset(columns.pre)
        if pred not in visited_pred:
            visited_pred[pred] = act
        else:
            columns.blocked = visited_pred[pred]

#    print "\n--- Step 2 ---"
#    __print_work_table(work_table)


    #Step 3. Identify Necessary Dummy Arcs
    dups = set()
    visited_act = set()
    for columns in work_table.values():
        if not columns.blocked:
            for act in columns.pre:
                if act in visited_act:
                    dups.add(act)
                visited_act.add(act)

#    print "\n--- Step 3.1 ---"
#    print dups


    #Step 3.2, 3.3 and 4. Create rows and information for Dummy Arcs
    dummy_counter = collections.Counter()
    for _, columns in work_table.items():
        # Avoid blocked
        if not columns.blocked:
            predecessors = columns.pre
            if len(predecessors) > 1:
                for pre in list(predecessors):
                    if pre in dups:
                        predecessors.remove(pre)
                        dummy_name = pre + '-d' + str(dummy_counter[pre])
                        dummy_counter[pre] += 1
                        predecessors.add(dummy_name)
                        work_table[dummy_name] = Columns(set([pre]), False, True, None, None, None)

#    print "\n--- Step 4 ---"
#    __print_work_table(work_table)


    #Step 5. Creating nodes
    node = 0 # instead of 0, can start at 100 to avoid confusion with activities named with numbers when debugging
    for act, columns in work_table.items():
        if not columns.dummy and not columns.blocked:
            columns.start_node = node
            node += 1

#    print "\n--- Step 5a ---"
#    __print_work_table(work_table)

    for act, columns in work_table.items():
        if not columns.dummy and columns.blocked:
            columns.start_node = work_table[columns.blocked].start_node

#    print "\n--- Step 5b ---"
#    __print_work_table(work_table)


    #Step 6. Associate activities with their end nodes
    # (a) find one non-dummy successor for each activity
    for act, columns in work_table.items():
        for suc, suc_columns in work_table.items():
            if not suc_columns.dummy and not suc_columns.blocked:
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

#    print "\n--- Step 6b ---"
#    __print_work_table(work_table)


    #Step 7. Associate dummy arcs with start nodes
    for act, columns in work_table.items():
        if columns.dummy:
            pred = iter(columns.pre).next()
            start_node = work_table[pred].end_node
            columns.start_node = start_node

#    print "\n--- Step 7 ---"
#    __print_work_table(work_table)


    #Step 8. Generate the graph
    pm_graph = pert.PertMultigraph()
    for act, columns in work_table.items():
        _, _, dummy, _, start, end = columns
        pm_graph.add_arc((start, end), (act, dummy))

    p_graph = pm_graph.to_directed_graph()
    return p_graph#.renumerar()



def main():
    """
    Test Cohen-Sadeh algorithm

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

    gg1 = cohen_sadeh(graph.successors2precedents(successors))
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
