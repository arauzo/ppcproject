import pert
import graph

def sharma1998ext(precedents):
    """
    Generates a AOA graph (PERT) from successors table
    Algorithm sharma1998 extended
    returns: pert.Pert() graph data structure
    """
    pert_graph = pert.Pert()
    successors = graph.reversed_prelation_table(precedents)  

    # Close the graph (not in sharma1998)
    origin = pert_graph.nextNodeNumber()
    pert_graph.add_node(origin)
    dest = pert_graph.nextNodeNumber()
    pert_graph.add_node(dest)
    begin_act     = graph.begining_activities(successors)
    end_act       = graph.ending_activities(successors)
    begin_end_act = begin_act.intersection(end_act)

    #  -Creates a common node for starting activities
    for act in begin_act - begin_end_act:
        pert_graph.addActivity(act, origin)

    #  -Creates a common node for ending activities
    for act in end_act - begin_end_act:
        pert_graph.addActivity(act, origin=None, destination=dest)

    #  -Deals with begin-end activities
    if begin_end_act:
        act = begin_end_act.pop()
        pert_graph.addActivity(act, origin, dest)
        for act in begin_end_act:
            o, d = pert_graph.addActivity(act, origin)
            pert_graph.addActivity("seDummy", d, dest, dummy=True)

    # Sharma1998 algorithm
    for act in successors:
        #print "Processing", act, pert_graph
        #window.images.append( graph.pert2image(pert_graph) )
        if not pert_graph.activityArc(act):
            pert_graph.addActivity(act)
            #window.images.append( graph.pert2image(pert_graph) )
        a_origin, a_dest = pert_graph.activityArc(act)
        #print '(', a_origin, a_dest, ')'
        for pre in precedents[act]:
            #print pert_graph.successors
            #print pre, pre in pert_graph.inActivitiesR(graph.reversed_prelation_table(pert_graph.successors), a_origin)
            if pre not in pert_graph.inActivitiesR(a_origin):
                if not pert_graph.activityArc(pre):
                    pert_graph.addActivity(pre)
                    #window.images.append( graph.pert2image(pert_graph) )
                pert_graph.makePrelation(pre, act)
                a_origin, a_dest = pert_graph.activityArc(act)
                
    return pert_graph

