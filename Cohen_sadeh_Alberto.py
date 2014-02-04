"""
Algorithm to draw Graph PERT based on Algorithm Yuval Cohen and Arick Sadeh
"""
import graph
import copy
import pert
import fileFormats
import collections
import validation

def cohen_sadeh(prelations):
    """
    Build graph PERT with prelations
    
    prelations = {'activity': ['prelations1', 'prelations2'...}
    
    return graph pert.Pert()
    """
    #Step 1. Construct Immediate Predecessors Table
    #Prepare a table with the immediate predecessors of each activity
    immediate_pred = prelations.values() #Obtain only the predecessors

    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    #Duplicate the Immediate Predecessors
    work_column = copy.deepcopy(immediate_pred)

    #Find similar precedence constraint and block them
    visited = [] #List of visited activities
    for i in range(len(work_column)):
        #If similar precedence
        if work_column[i] in visited and work_column[i] != ['-']: 
            work_column[i] = ['-'] #Block similar precedence
        visited.append(work_column[i]) #Add activity to list of visited

    #Step 3. Identify Necessary Dummy Arcs
    #Scan work_column and list digit that appear more than once in that column
    visited = [] #List of visited activities
    more_than_once = [] #List of activities that appear more than once
    for predecessors in work_column:
        for activity in predecessors:
            if activity != '-': #If activity no blocked
                if activity in visited: #If activity visited
                    more_than_once.append(activity) #Add activity duplicate
                visited.append(activity) #Add activity to list of visited

    #Repetitions not found before,requires a dummy arc(paralel dummy)
    same_predecessor = [] #List of list of activities with same_predecessors
    visited = [] #List of visited activities
    for activity, predecessor in prelations.iteritems():
        if activity not in more_than_once: #No repeated comparison
            for act, pre in prelations.iteritems():
                if activity != act and predecessor == pre: #Same predecessors
                    visited.append(activity)
                    if act not in visited: #No repeated comparison
                        #List for activity and act
                        activities_same_predecessor = [] 
                        activities_same_predecessor.append(activity)
                        activities_same_predecessor.append(act)
                        same_predecessor.append(activities_same_predecessor)

    set_pred = () #Set of predecessors
    paralel_dummy = [] #List of paralel dummies
    for activity, predecessor in prelations.iteritems():
        set_pred = set(predecessor)
        for set_same_pred in same_predecessor:
            #Activities with same predecessors and successors
            intermediate_set = set_pred.intersection(set(set_same_pred))
            #While more than one activity have some predecessors
            while len(intermediate_set) > 1: 
                paralel_dummy.append(intermediate_set.pop())

    #If constraint of more_than_once not is a single activity dummy needed
    #Rename the dummies with numbers
    visited = [] #List of visited activities
    dummy_activities = [] #List of dummy activities
    activity_dummy = [] #List of activity and dummy
    for i in range(len(immediate_pred)):
        #If predecessors are not single
        if len(immediate_pred[i]) > 1:
            for j in range(len(immediate_pred[i])):
                relation = [] #Relation between activity and dummy
                #If activity have more than one constraint 
                #Or activity is paralel dummy
                if immediate_pred[i][j] in more_than_once or immediate_pred[i][j] in paralel_dummy:
                    visited.append(immediate_pred[i][j])
                    #Count number of dummy ocurrence
                    number = visited.count(immediate_pred[i][j]) 
                    dummy = immediate_pred[i][j] #Dummy = activity 
                    #Rename dummy
                    immediate_pred[i][j] = immediate_pred[i][j] + str(number)
                    activity = immediate_pred[i][j] #Activity = dummy
                    dummy_activities.append(activity)
                    relation.append(activity)
                    relation.append(dummy)
                    activity_dummy.append(relation)

    #Create a table with activities and their immediate predecessors
    activity_predecessor = [] #List of activity and predecessor
    activities = prelations.keys() #List of activities
    for i in range(len(activities)):
        relation = [] #Relation between activity(int) and predecessor
        relation.append(activities[i])
        for j in range(len(immediate_pred)):
            if i == j:
                relation.append(immediate_pred[j])
                activity_predecessor.append(relation)

    #Step 4. Add Rows and Information for Dummy Arcs
    for activity in activity_dummy:
        activity_predecessor.append(activity)

    #Step 5. Number the AOA nodes
    starting_node = [] #List of starting nodes
    constraint = [] #List of constraint
    count = 0 #Count for number activities
    for activity, predecessor in activity_predecessor:
        relation = [] #relation between activity and count
        relation.append(activity)
        if activity in dummy_activities: #If activity is dummy
            relation.append('ignore_dummy')
            starting_node.append(relation)
        else: #Activity not dummy
            if len(constraint) == 0: #If no constraints
                relation.append(count)
                constraint.append(predecessor)
                starting_node.append(relation)
            elif predecessor in constraint: #Constraint repeated
                for i in range(len(constraint)): #Search constraint
                    #Relative position is the count
                    if constraint[i] == predecessor:
                        relation.append(i)
                starting_node.append(relation)
            else: #At lest one constraint, constraints not repeated
                count += 1
                relation.append(count)
                constraint.append(predecessor)
                starting_node.append(relation)

    #Step 6. Associate Activities with their End Nodes
    #Finding non-dummy sucessors for the successor column
    activity_sucessor = [] #List of activity and sucessor
    visited = [] #List of visited activities
    for activity, predecessor in activity_predecessor:
        if activity not in dummy_activities: #If activity is not dummy
            for pre in predecessor:
                relation = [] #Relation between predecessor and activity
                visited.append(pre)
                relation.append(pre) #Put predecessor like activity
                relation.append(activity) #Put activity like successor
                activity_sucessor.append(relation)
    for activity, predecessor in activity_predecessor:
        relation = [] #Relation between activity and empty list
        if activity not in visited: #If activity has no predecessor
            relation.append(activity)
            relation.append([])
            activity_sucessor.append(relation)

    #Finding the AOA end node column
    max_count = 0
    activity_end = [] #List of activity and end node
    for activity, predecessor in activity_predecessor:
        if activity not in dummy_activities: #If activity is not dummy
            for pre in predecessor:
                for act, count in starting_node:
                    if pre == act:
                        relation = [] #Relation between act and end_node
                        if act not in activity_end:
                            relation.append(act)
                            for act, count in starting_node:
                                if activity == act:
                                    if count > max_count: #Calculate max_count
                                        max_count = count
                                    relation.append(count)
                                    activity_end.append(relation)
    predecessors = [] #List of predecessors
    followed_dummies = [] #List of followed dummies
    end_nodes = [] #Lis of end_nodes
    for act, pre in activity_predecessor: #Get predecessors
        predecessors.append(pre)
    for act_suc, sucessor in activity_sucessor:
        if len(sucessor) < 1: #If number of sucessors < 1
            if act_suc in predecessors:
                followed_dummies.append(act_suc)
            else: #Activities without sucessors
                end_nodes.append(act_suc)
    for activity in followed_dummies: #Activity follow only by dummies 
        relation = [] #Relation between act and end_node
        max_count += 1
        relation.append(activity)
        relation.append(max_count)
        activity_end.append(relation)
    for act_end in end_nodes: #Activities without sucessors
        relation = [] #Relation between act and end_node
        final_node = max_count + 1 #Only final nodes
        relation.append(act_end)
        relation.append(final_node)
        activity_end.append(relation)
        
    #Step 7. Associate Dummy Arcs with Their Start nodes
    dummy_end = [] #List of dummy and end
    print "activity_dummy: ", activity_dummy
    print "activity_end: ", activity_end
    for activity, dummy in activity_dummy:
        relation = [] #Relation between activity(dummy) and end
        relation.append(activity)
        for act, end in activity_end: #Add ends for activities
            if act == dummy:
                print "relation: ", relation
                print "end: ", end
                if end not in relation:
                    print "end not in relation"
                    relation.append(end)
                    dummy_end.append(relation)
#                else:
#                    print "end in relation"
#                    dummy_end.append(relation)
                print "dummy end", dummy_end
    print "relation: ", relation
    print "dummy_end: ", dummy_end
    print "starting_node: ", starting_node
    for i in range(len(starting_node)): #Add ends for dummy_activities
        for dummy1, end in dummy_end:
            if starting_node[i][0] == dummy1:
                starting_node[i][1] = end

    #Step 8. Update the table with the new activity names
    visited = [] #List of visited activities
    graph = pert.Pert() #Graph to draw
    for activity, start in starting_node:
        relation = [] #Relation between start and end
        relation.append(start)
        for act, end in activity_end:
            if activity == act and activity not in visited:
                visited.append(act)
                relation.append(end)
                if activity in dummy_activities:
                    dummy = activity, True
                else:
                    dummy = activity, False
                graph.add_arc(relation, dummy)
    return graph #graph.renumerar()

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
