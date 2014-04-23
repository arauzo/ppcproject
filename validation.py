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

    return True
