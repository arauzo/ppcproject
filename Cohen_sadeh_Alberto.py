import graph
import copy
import pert

def cohen_sadeh(prelations):
    """
    """
    #Step 1. Construct Immediate Predecessors Table
    #Prepare a table with the immediate predecessors of each activity
#    prelations = graph.successors2precedents(successors) #Pass successors to predecessors
    immediate_predecessors = prelations.values() #Obtain only the predecessors
    print "immediate_predecessors:", immediate_predecessors
    #Step 2. Identify Identical Precedence Constraint of Diferent Activities
    #Duplicate the Immediate Predecessors
    work_column = copy.deepcopy(immediate_predecessors)
    print "work_column:", work_column
    #Find similar precedence constraint and block them
    visited = [] #List of visited activities
    for i in range(len(work_column)):
        if work_column[i] in visited and work_column[i] != ['-']: #If similar precedence
            work_column[i] = ['-'] #Block similar precedence
        visited.append(work_column[i]) #Add activity to list of visited
    print "work_column1:", work_column
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

    #Each of the repetitions not found before,requires a dummy arc(paralel dummy)

    same_predecessor = [] #List of list of activities with same_predecessors
    visited = [] #List of visited activities
    for activity, predecessor in prelations.iteritems():
        if activity not in more_than_once: #Avoid repeated comparison
            for act, pre in prelations.iteritems():
                if activity != act and predecessor == pre: #Same predecessors
                    visited.append(activity)
                    if act not in visited: #Avoid repeated comparison
                        activities_same_predecessor = [] #List for activity and act
                        activities_same_predecessor.append(activity)
                        activities_same_predecessor.append(act)
                        same_predecessor.append(activities_same_predecessor)

    set_predecessors = () #Set of predecessors
    paralel_dummy = [] #List of paralel dummies
    for activity, predecessor in prelations.iteritems():
        set_predecessors = set(predecessor)
        for set_same_predecessor in same_predecessor:
            intermediate_set = set_predecessors.intersection(set(set_same_predecessor)) #Activities with same predecessors and successors
            while len(intermediate_set) > 1: #While more than one activity have some predecessors
                paralel_dummy.append(intermediate_set.pop())

    #If constraint of more_than_once not is a single activity dummy needed
    #Rename the dummies with numbers
    visited = [] #List of visited activities
    dummy_activities = [] #List of dummy activities
    activity_dummy = [] #List of activity and dummy
    for i in range(len(immediate_predecessors)):
        if len(immediate_predecessors[i]) > 1: #If predecessors are not single
            for j in range(len(immediate_predecessors[i])):
                relation = [] #Relation between activity and dummy
                #If activity have more than one constraint or activity is paralel dummy
                if immediate_predecessors[i][j] in more_than_once or immediate_predecessors[i][j] in paralel_dummy:
                    visited.append(immediate_predecessors[i][j])
                    number = visited.count(immediate_predecessors[i][j]) #Count number of dummy ocurrence
                    dummy = immediate_predecessors[i][j] #Dummy = activity 
                    immediate_predecessors[i][j] = immediate_predecessors[i][j] + str(number) #Rename dummy
                    activity = immediate_predecessors[i][j] #Activity = dummy
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
        for j in range(len(immediate_predecessors)):
            if i == j:
                relation.append(immediate_predecessors[j])
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
                    if constraint[i] == predecessor: #Relative position is the count
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
    for activity, dummy in activity_dummy:
        relation = [] #Relation between activity(dummy) and end
        relation.append(activity)
        for act, end in activity_end: #Add ends for activities
            if act == dummy:
                relation.append(end)
                dummy_end.append(relation)
    for i in range(len(starting_node)): #Add ends for dummy_activities
        for dummy, end in dummy_end:
            if starting_node[i][0] == dummy:
                starting_node[i][1] = end

    #Step 8. Update the table with the new activity names
    visited = [] #List of visited activities
#    activity_start_end = [] #List Activity, start, end
    grafo = pert.Pert()
    for activity, start in starting_node:
        relation = [] #Relation between start and end
        relation.append(start)
        for act, end in activity_end:
            if activity == act and activity not in visited:
                visited.append(act)
                relation.append(end)
#                activity_start_end.append(activity)
#                activity_start_end.append(relation)
                if activity in dummy_activities:
                    dummy = activity, True
                else:
                    dummy = activity, False
                grafo.add_arc(relation, dummy)
                
    print "Grafo:", grafo
    return grafo
#    f = open('grafico.png', "w")
#    png_text = graph.pert2image(grafo, file_format='png')
#    f.write(png_text)

# --- Start running as a program
#if __name__ == '__main__':
#    prelations = {
#        'B' : ['E', 'F'],
#        'C' : ['G'],
#        'D' : ['H'],
#        'E' : ['G'],
#        'F' : ['H'],
#        'G' : ['H'],
#        'H' : []
#    }
#    
##        'B' : [],
##        'C' : [],
##        'D' : [],
##        'E' : ['B'],
##        'F' : ['B'],
##        'G' : ['C', 'E']
##    }

#    prelations1 = {
#        'A' : ['B', 'E'],
#        'B' : ['F', 'G'],
#        'C' : ['D', 'E'],
#        'D' : ['F'],
#        'E' : ['J'],
#        'F' : ['I'],
#        'G' : ['H'],
#        'H' : ['I', 'J'],
#        'I' : ['K'],
#        'J' : ['K'],
#        'K' : [],
#    }
#    
##    e101Predecessors = {
##        'A' : [],
##        'B' : ['A'],
##        'C' : ['A'],
##        'D' : ['A'],
##        'E' : ['B'],
##        'F' : ['B'],
##        'G' : ['C', 'E'],
##        'H' : ['D', 'F', 'G']
##    }
##    
#    e101 = {
#        'A' : ['B', 'C', 'D'],
#        'B' : ['E', 'F'],
#        'C' : ['G'],
#        'D' : ['H'],
#        'E' : ['G'],
#        'F' : ['H'],
#        'G' : ['H'],
#        'H' : []
#    }
#    
#    e102 = {
#        'A' : ['B', 'C', 'D'],
#        'B' : ['E'],
#        'C' : ['F', 'G', 'H'],
#        'D' : ['J'],
#        'E' : ['F', 'G', 'H'],
#        'F' : ['I'],
#        'G' : ['J'],
#        'H' : ['K'],
#        'I' : ['J'],
#        'J' : ['K'],
#        'K' : []
#    }
#    no_conexo = {
#        'A' : ['B', 'C', 'D'],
#        'B' : ['E'],
#        'C' : ['F', 'G', 'H'],
#        'D' : ['J'],
#        'E' : ['F', 'G', 'H'],
#        'F' : ['I'],
#        'G' : ['J'],
#        'H' : ['K'],
#        'I' : ['J'],
#        'J' : ['K'],
#        'K' : [],
#        'L' : ['M', 'N'],
#        'M' : [],
#        'N' : []
#    }
#    act_paralelas = {
#        'A' : [],
#        'B' : [],
#        'C' : ['A'],
#        'D' : ['B'],
#        'E' : ['B'],
#        'F' : ['A'],
#        'G' : ['A'],
#        'H' : ['B'],
#        'I' : ['A'],
#    }
#    e103 = {
#        '1' : ['2', '3', '4'],
#        '2' : ['5'],
#        '3' : ['6'],
#        '4' : ['11', '12'],
#        '5' : ['7', '8', '9'],
#        '6' : ['7', '8', '9'],
#        '7' : [10],
#        '8' : ['11', '12'],
#        '9' : ['14'],
#        '10' : ['11', '12'],
#        '11' : ['13'],
#        '12' : ['14'],
#        '13' : ['14'],
#        '14' : []
#    }
    #cohen_sadeh(pert.Pert(), prelations)
#    cohen_sadeh(pert.Pert(), prelations1)
#    cohen_sadeh(pert.Pert(), e101)
#    cohen_sadeh(act_paralelas)

### ejecucion del algoritmo por defecto
window = None

if __name__ == "__main__":

    window = graph.Test() 

    gg = cohen_sadeh(graph.prelaciones4)
    image1 = graph.pert2image(gg)

    window.images.append(image1)
    graph.gtk.main()
