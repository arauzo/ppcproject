def check_validation(successors, pert):
    """
    Compare a successors table (usually the input used to generate a graph) with the successors table
    generated from a PERT graph to validate that graph conections are correct
    """
    successors_generated = pert.pertSuccessors() #Successors generated from graph

    # Check if input successors and PERT graph have the same activities
    for activity in successors:
        if not activity in successors_generated:
            print "WRONG GRAPH: activity '%s' is not in graph" % (activity, )
            return False

    for activity in successors_generated:
        if not activity in successors:
            print "WRONG GRAPH: extra activity '%s' included not from input successors" % (activity, )
            return False

    # Check if input successors and PERT graph implicit successors match
    for activity, successors in successors.items():
        if set(successors) != set(successors_generated[activity]):
            print "WRONG GRAPH:\n    IN: '%s' -> %s\n GRAPH: '%s' -> %s" % (activity, sorted(successors), activity, sorted(successors_generated[activity]))
            return False

    # Check that there is exactly one start node and one end node
    # XXX TODO
    #Find Nodo without predecessors
#    for nodo, nodo_successor in graph.predecessors.items():
#        if len(nodo_successor) == 0:
#            successors_nodes.append(nodo)
#
#    if len(successors_nodes) != 1:
#        raise Exception ("**ERROR** No es un grafo pert correcto")
#    else:
#        print "Nodo start:", successors_nodes


    print "OK --> Pass"
    return True
