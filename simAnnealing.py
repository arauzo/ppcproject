import random
import copy
from math import exp
from graph import successors2precedents


def resourcesAvailability(availableResources):
    """
    Create a dictionary with the renewable and the
            doubly restricted resources

    Parameters: availableResources (list of resources in the project)

    Returned value: resources
    """

    resources={} 
   
    #Create a dictionary with the resources' name and number available   
    for a in availableResources:
        if a[1] == 'Renovable':
            resources[a[0]] = a[3]
        elif a[1] == 'Doblemente restringido':
            resources[a[0]] = a[2]
   
    return resources


def resourcesPerActivities(initialAsignation):
    """
    Create a dictionary with the resources
          the activities need

    Parameters: initialAsignation (list of the activities and the resources they need) 

    Returned value: asignation
    """
      
    asignation={}
    
    #Create a dictionary with the activities and the resources they need
    for a in initialAsignation:
        if a[0] in asignation.keys():
            asignation[a[0]] = asignation[a[0]] + [(a[1],a[2])]
        else:
            asignation[a[0]] = [(a[1],a[2])] 
     
    return asignation
      
def simulatedAnnealing(asignation,resources,successors,activities,balance,temperature,minTemperature,k,numIterations):
    """
    Try to find the best planning of the project by
        the technique of simulated annealing

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                successors (the prelations of the activities)
                activities (dictionary with the name of activities and their characteristics)
                balance (if 0 it will allocate else it will balance)
                temperature (parameter to configure simulated annealing algorithm)
                minTemperature ((parameter to configure simulated annealing algorithm)
                k ((parameter to configure simulated annealing algorithm)
                numIterations ((parameter to configure simulated annealing algorithm)

    Returned value: (prog1,prog1Evaluated) or (progAux,progAuxEvaluated) (the best planning and the duration/variance of the project)
    """
    
    predecessors = successors2precedents(successors)

    for a in predecessors.copy():
        if predecessors[a] == []:
            del predecessors[a]

    # prog1 will store the best planning
    progAux = prog1 = generate(asignation,resources.copy(),copy.deepcopy(predecessors),activities.copy(),balance)
    progAuxEvaluated = prog1Evaluated = evaluate(prog1,balance,asignation,resources)
      
    while temperature > minTemperature and numIterations != 0: # XXX grafica?
      
        prog2 = modify(asignation,resources.copy(),copy.deepcopy(predecessors),activities.copy(),prog1,balance)
        prog2Evaluated = evaluate(prog2,balance,asignation,resources)
         
        if prog2Evaluated <= prog1Evaluated:
            prog1 = prog2
            prog1Evaluated = prog2Evaluated
        else:
            numIterations -= 1
            r = random.random()
            m = exp(-(prog2Evaluated*10000-prog1Evaluated*10000) / temperature)
            if r < m:
                progAux = prog1 # XXX Lorenzo dijo de quedarnos con la mejor solucion de todas aunque se fuese por un camino peor
                progAuxEvaluated = prog1Evaluated
                prog1 = prog2
                prog1Evaluated = prog2Evaluated       
        temperature = k * temperature

    if prog1Evaluated <= progAuxEvaluated:
        return (prog1,prog1Evaluated)
    else:
        return (progAux,progAuxEvaluated)


def generate(asignation,resources,predecessors,activities,balance):
    """
    Generate a planning

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                predecessors (dictionary with activities and their predecessors)
                activities (dictionary with the name of activities and their characteristics)
                balance (if 0 it will allocate else it will balance)

    Returned value: prog (planing generated)
    """
       
    currentTime = 0
    possibles = {}
    executing = {}
    result = []
   
    prog=generateOrModify(asignation,resources,predecessors,activities,balance,possibles,executing,result,currentTime)
    return prog


def modify(asignation,resources,predecessors,activities,prog1,balance):
    """
    Modify a planning

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                predecessors (dictionary with activities and their predecessors)
                activities (dictionary with the name of activities and their characteristics)
                prog1 (planning to modify)
                balance (if 0 it will allocate else it will balance)

    Returned value: prog (planning modified)
    """
       
    result = []
    executing = {}
    possibles = {}

   
    # The modification will start at this time
    currentTime = random.randint(0, prog1[-2][1])
   
    # Update the state of result, executing, resources and activities to the state they would be at currentTime
    for act,startTime,endTime in prog1:
        if startTime < currentTime:
            result += [(act,startTime,endTime)]
            if startTime + activities[act][0] > currentTime:
                executing[act] = startTime + activities[act][0] - currentTime
                if act in asignation.keys() and balance == 0:
                    for resource,amount in asignation[act]:
                        resources[resource] = float(resources[resource]) - float(amount)
            activities.pop(act) 

    # Update the state of predecessors to the state it would be at currentTime
    for act,startTime,endTime in result:
        if act not in executing:
            for a in predecessors.copy():
                if act in predecessors[a]: 
                    predecessors[a].remove(act)
                    if predecessors[a] == []:
                        del predecessors[a]   

    # Update the state of possibles
    for a in activities.copy():
        if a not in predecessors.keys(): 
            possibles[a] = activities.pop(a)   
      
    prog = generateOrModify(asignation,resources,predecessors,activities,balance,possibles,executing,result,currentTime)
    return prog


def evaluate(prog,balance,asignation,resources):
    """
    Evaluate a planning

    Parameters: prog (planning to evaluate)
                balance (if 0 it will consider resoucers)
                asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                

    Returned value: duration or variance (duration or variance of the planning evaluated)
    """
    
    duration = 0
  
    # Calculate duration
    for act,startTime,endTime in prog:
        if endTime > duration:
            duration = endTime
 
    if balance == 0: # if allocate
        return duration   
    else: #if balance
        variance = calculateVariance(prog,resources,asignation,duration) 
        return variance
      
      
def calculateVariance(prog,resources,asignation,duration): 
    """
    Calculate the variance of the planning it receives

    Parameters: prog (planning to evaluate)
                resources (returned by resourcesAvailability)
                asignation (returned by resourcesPerActivity)
                duration (duration of the planning)
                
                

    Returned value: variance (the average of all resources' variance)
    """
    
    # Calculate the loading sheet for each resource for prog1
    loadingSheet = {}
    average = {}
    variance = {}
    finalVariance = 0

    for resource in resources:
        average[resource] = 0
        for time in range(0,int(duration)):
            amount = 0
            for act in prog:
                if act[1]<=time and time<act[2] and act[0] in asignation.keys():
                    for r,c in asignation[act[0]]:
                        if r == resource:
                            amount += float(c)
                            break
            if resource in loadingSheet.keys():
                loadingSheet[resource] += [(time,amount)]
            else:
                loadingSheet[resource] = [(time,amount)]  
            average[resource] += amount
        average[resource] = average[resource] / duration
      
    for resource in resources:
        variance[resource] = 0
        for time,amount in loadingSheet:
            variance[resource] += (float(amount) - average[resource])**2
        variance[resource] = variance[resource] / (duration-1)
        finalVariance += variance[resource]
      
    return finalVariance / len(resources)
         

def generateOrModify(asignation,resources,predecessors,activities,balance,possibles,executing,result,currentTime):
    """
    Generate or modify a planning.
    It depends on currentTime

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                predecessors (dictionary with activities and their predecessors)
                activities (dictionary with the name of activities and their characteristics)
                balance (if 0 it will allocate else it will balance)
                possibles (dictionary of the activities which can execute at currentTime)
                executing (dictionary of the activities which are executing at currentTime)
                result (planning of the project up to currentTime)
                currentTime (time when the algorithm starts to generate a new planning) 

    Returned value: result (planning calculated)
    """
    
    lengthResources = len(resources)
    if lengthResources == 0: 
        lengthResources = -1 
   
    resourcesUsedUp = 0 
   
    while activities != {} or possibles != {} or executing != {}: # Until all the activities have finished
        # Choose activities with no predecessors
        for a in activities.copy():
            if a not in predecessors.keys():
                possibles[a] = activities.pop(a)
      
        if possibles != {}:

            # If it balance, pop the activities with maximum time to start = currentTime 
            if balance == 1:
                for act in possibles.copy():
                    if possibles[act][1] == currentTime:
                        executing[act] = possibles[act][0]
                        result += [(act, currentTime, currentTime + possibles[act][0])]
                        del possibles[act]
                # Calculate a number of activities to execute       
                # A minimum of one activity has to be executing
                if executing == {}:
                    numActivities = random.randint(1,len(possibles))
                else:
                    numActivities = random.randint(0,len(possibles))
            else:
                numActivities = -1
       
            possiblesCopy = possibles.copy()
         
            # Execute activities until a number of activities have executed, no more possibles activities or no more resources 
            while numActivities != 0 and possiblesCopy != {} and lengthResources != resourcesUsedUp:
            
                noExecute = 0

                # Pop a random item of possiblesCopy
                possiblesKeys = possiblesCopy.keys()
                key = random.choice(possiblesKeys)
                act = possiblesCopy.pop(key)
 
                # If resources are required            
                if key in asignation.keys() and balance == 0:
                    for resource,amount in asignation[key]:
                        # if resource required > resource available
                        if float(amount) > float(resources[resource]):
                            noExecute = 1
                            break                     
                    if noExecute == 0:
                        for resource,amount in asignation[key]:
                            resources[resource] = float(resources[resource]) - float(amount)
                            if resources[resource] == 0:
                                resourcesUsedUp += 1          
                        executing[key] = act[0] # Add activity in executing
                        result += [(key, currentTime, currentTime + act[0])] # Update result
                        del possibles[key] # Remove the activity from possibles dictionary             
                else: # The activity doesn't consumed any resource
                    executing[key] = act[0]
                    result += [(key, currentTime, currentTime + act[0])]
                    del possibles[key] #remove the activity from possibles dictionary
                    numActivities -= 1      
      
        currentTime += 1

        # Update the remaining time of all activities executing
        for a in executing.copy():
            executing[a] = float(executing[a]) - 1
            if executing[a] == 0:
                del executing[a]
                # Once one activity finish, update the resources' availability
                if a in asignation.keys() and balance == 0:
                    for resource,amount in asignation[a]:
                        if float(resources[resource]) == 0:
                            resourcesUsedUp -= 1
                        resources[resource] = float(resources[resource]) + float(amount)
            
                # If a was predecessor of any activity, update and remove the relation of predecessor
                for act in predecessors.copy():
                    if a in predecessors[act]:
                        predecessors[act].remove(a)
                        if predecessors[act]==[]:
                            del predecessors[act]
              
    return result
    

