import random
import copy
from math import exp
from graph import successors2precedents

#-----------------------------------------------------------
# Create a dictionary with the resources availability.
# Works only with Renewable and Doubly restricted resources
#
# Parameters: -
#
# Return value: resources 
#-----------------------------------------------------------

def resourcesAvailability(recursos):

    resources={} 
   
    #Create a dictionary with the resources' name and number available   
    for a in recursos:
        if a[1] == 'Renovable':
            resources[a[0]] = a[3]
        elif a[1] == 'Doblemente restringido':
            resources[a[0]] = a[2]
   
    return resources

#-----------------------------------------------------------
# Create a dictionary with the resources
#          the activities need
#
# Parameters: -
#
# Return value: asignation 
#-----------------------------------------------------------

def resourcesPerActivities(asignacion):
      
    asignation={}
      
    #Create a dictionary with the activities and the resources they need
    for a in asignacion:
        if a[0] in asignation.keys():
            asignation[a[0]] = asignation[a[0]] + [(a[1],a[2])]
        else:
            asignation[a[0]] = [(a[1],a[2])] 
     
    return asignation
      
#-----------------------------------------------------------
# Generate or modify a planning. It depends on currentTime. 
#
#
# Parametros: asignation (dictionary of activities and the resources they need)
#             resources (dictionary of the resources and their availability)
#
# Valor de retorno: result 
#-----------------------------------------------------------
def simulatedAnnealing(asignation,resources,successors,activities,balance,temperature,minTemperature,k,numIteraciones):

    predecessors = successors2precedents(successors)

    for a in predecessors.copy():
        if predecessors[a] == []:
            del predecessors[a]

    # Con estos datos realiza 153,9 reducciones de temperatura
    #temperature = 100000
    #k = 0.9
    #minTemperature = 0.01
    #numIteraciones = 100
   

    # prog1 will store the best planning
    prog1=generate(asignation,resources.copy(),copy.deepcopy(predecessors),activities.copy(),balance)
    prog1Evaluated = evaluate(prog1,balance,asignation,resources)
      
    while temperature > minTemperature and numIteraciones > 0: # XXX numIteraciones sin mejora infinito
      
        prog2=modify(asignation,resources.copy(),copy.deepcopy(predecessors),activities.copy(),prog1,balance)
      
        prog2Evaluated = evaluate(prog2,balance,asignation,resources)

        print 'resultado1: ',prog1Evaluated,' resultado2: ',prog2Evaluated
         
        if prog2Evaluated <= prog1Evaluated:
            prog1 = prog2
            prog1Evaluated = prog2Evaluated
        else:
            numIteraciones -= 1
            r = random.random()
            #print 'r: ',r
            m = exp(-(prog2Evaluated*10000-prog1Evaluated*10000) / temperature)
            #print 'm: ',m
            if r < m:
                print 'Escojo sol peor'
                prog1 = prog2
                prog1Evaluated = prog2Evaluated 
      
        temperature = k * temperature
        #print 'temperatura: ',temperature
   
    if numIteraciones == 0:
        print 'Se corto por numIteraciones'
    else:
        print 'Se corto por temperatura', temperature
      
    print prog1
    print prog1Evaluated
#-----------------------------------------------------------
# Generate a planning. 
#
#
# Parametros: asignation (dictionary of activities and the resources they need)
#             resources (dictionary of the resources and their availability)
#
# Valor de retorno: result 
#-----------------------------------------------------------  
def generate(asignation,resources,predecessors,activities,balance):
   
    currentTime = 0
    possibles = {}
    executing = {}
    result = []
   
    prog=generateOrModify(asignation,resources,predecessors,activities,balance,possibles,executing,result,currentTime)
    return prog

#-----------------------------------------------------------
# Modify a planning. 
#
#
# Parametros: asignation (dictionary of activities and the resources they need)
#             resources (dictionary of the resources and their availability)
#
# Valor de retorno: result 
#-----------------------------------------------------------  
def modify(asignation,resources,predecessors,activities,prog1,balance):
   
    result = []
    executing = {}
    possibles = {}

   
    # The modification will start at this time
    currentTime = random.randint(0, prog1[-2][1])
    #print 'activities: ',activities
    #print 'tiempo actual: ',currentTime
   
    # Update the state of result, executing, resources and activities to the state they would be at currentTime
    for act,startTime,endTime in prog1:
        if startTime < currentTime:
            result += [(act,startTime,endTime)]
            if startTime + activities[act][0] > currentTime:
                executing[act] = startTime + activities[act][0] - currentTime
                if act in asignation.keys() and balance == 0:
                    for resource,amount in asignation[act]:
                        resources[resource] = float(resources[resource]) - float(amount)
            activities.pop(act) # falta pasar de activities a possibles
   
    #print 'resultado mod: ', result
    #print 'ejecutando mod: ', executing
    #print 'actividad mod: ', activities
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
    #print 'predecessors mod: ', predecessors
    #print 'possibles mod: ', possibles
      
    prog=generateOrModify(asignation,resources,predecessors,activities,balance,possibles,executing,result,currentTime)
    return prog

#-----------------------------------------------------------
# Evaluate a planning. 
#
#
# Parametros: asignation (dictionary of activities and the resources they need)
#             resources (dictionary of the resources and their availability)
#
# Valor de retorno: result 
#-----------------------------------------------------------
def evaluate(prog,balance,asignation,resources):

    duration = 0
  
    # Calculate duration
    for act,startTime,endTime in prog:
        if endTime > duration:
            duration = endTime

    print 'duracion: ', duration 
    if balance == 0: # if allocate
        return duration
         
    else: #if balance
        variance = calculateVariance(prog,resources,asignation,duration) 
        return variance
      
      
def calculateVariance(prog,resources,asignation,duration): 

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
      
                    
            
   
#-----------------------------------------------------------
# Generate or modify a planning. It depends on currentTime. 
#
#
# Parametros: asignation (dictionary of activities and the resources they need)
#             resources (dictionary of the resources and their availability)
#             predecessors (list of the relation of the activities)
#             activities (list of activities, their duration and their maximum time to start)
#             balance (flag if it will balance or allocate resources)
#             possibles (dictionary of possibles activities to execute)
#             executing (dictionary of activities executing)
#             result (list with the planning)
#             currentTime (time in which is the algorithm)
# Valor de retorno: result 
#-----------------------------------------------------------   
def generateOrModify(asignation,resources,predecessors,activities,balance,possibles,executing,result,currentTime):
   
   
    lengthResources = len(resources)
    if lengthResources == 0: #XXX prueba limite recursos lista vacia->prog minima
        lengthResources = -1 
   
    resourcesUsedUp = 0 
   
   
    while activities != {} or possibles != {} or executing != {}: # Until all the activities have finished
        #print 'currentTime: ',currentTime
        # Choose activities with no predecessors
        for a in activities.copy():
            if a not in predecessors.keys():
                possibles[a] = activities.pop(a)
      
        #print 'possibles: ', possibles
        #print 'predecessores :', predecessors
      
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

                #print 'possiblesCopy ',possiblesCopy
                # Pop a random item of possiblesCopy
                possiblesKeys = possiblesCopy.keys()
                key = random.choice(possiblesKeys)
                act = possiblesCopy.pop(key)
 
                # If resources are required            
                if key in asignation.keys() and balance == 0:
                    #print 'recursos: ', resources
                    for resource,amount in asignation[key]:
                        #print 'recurso disponible: ',resources[resource],'cantidad: ',amount
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
            
                #print 'executing ', executing
                #print 'result ', result      
      
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
    #print result               
    return result
    

