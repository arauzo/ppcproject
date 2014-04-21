def check_validation(successors, pert): #Compare in's dict an graph's dict
    """
    Compare input dict with dict generated from graph for validate
    that conection between dicts are correct
    """
    successors_generated = pert.pertSuccessors() #Successors generated from graph
    for activity, successors in successors.items():
        if not activity in successors_generated: #In's dict and graph's dict have differents activities
            print "ERROR: ", activity, successors
            return False
        else: #In's dict and graph's dict are different
            if set(successors) != set(successors_generated[activity]):
                print "ERROR1: ", activity, successors, "generated:", successors_generated[activity]
                return False
    return True
