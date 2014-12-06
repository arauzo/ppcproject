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
    start_nodes = [node for node, preds in pert.predecessors.items() if len(preds) < 1]
    if len(start_nodes) > 1:
        print "WRONG GRAPH: more than one start node (%s)" % (str(end_nodes), )
        return False

    end_nodes = [node for node, sucs in pert.successors.items() if len(sucs) < 1]
    if len(end_nodes) > 1:
        print "WRONG GRAPH: more than one end node (%s)" % (str(end_nodes), )
        return False

    print "OK --> Pass"
    return True

