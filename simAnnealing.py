#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Gantt diagram drawing GTK widget
#-----------------------------------------------------------------------
# PPC-PROJECT
#   Multiplatform software tool for education and research in 
#   project management
#
# Copyright 2007-8 Universidad de Córdoba
# This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published
#   by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random
import copy
from math import exp,log
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
      
def simulatedAnnealing(asignation,resources,successors,activities,balance,mu,phi,minTemperature,maxIteration,numIterations):
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
                alpha ((parameter to configure simulated annealing algorithm)
                numIterations ((parameter to configure simulated annealing algorithm)

    Returned value: (prog1,prog1Evaluated) or (progAux,progAuxEvaluated) (the best planning and the duration/variance of the project)
    """
    
    predecessors = successors2precedents(successors)

    for a in predecessors.copy():
        if predecessors[a] == []:
            del predecessors[a]

    # prog1 will store the best planning
    progAux = prog1 = generate(asignation,resources.copy(),copy.deepcopy(predecessors),activities.copy(),balance)
    prog1Evaluated, loadingSheet1, duration1 = evaluate(prog1,balance,asignation,resources)
    progAuxEvaluated = prog1Evaluated
    durationAux = duration1
    loadingSheetAux = loadingSheet1
    
    tempAux = temperature = (mu/-log(phi)) * prog1Evaluated
    alpha = (minTemperature / temperature) ** (1/maxIteration)
    
    #it=0 #XXX mostrar numero de iteraciones realizado?
    numIterationsAux = numIterations
    
    while temperature >= minTemperature and numIterations != 0:
        
        prog2 = modify(asignation,resources.copy(),copy.deepcopy(predecessors),activities.copy(),prog1,balance)
        prog2Evaluated, loadingSheet2, duration2 = evaluate(prog2,balance,asignation,resources)
        if prog2Evaluated <= prog1Evaluated:
            loadingSheet1 = loadingSheet2
            duration1 = duration2
            prog1 = prog2
            prog1Evaluated = prog2Evaluated
            numIterations = numIterationsAux # Set numIterations to initial value
        else:
            numIterations -= 1 
            r = random.random()
            m = exp(-(prog2Evaluated-prog1Evaluated) / temperature)
            if r < m:
                loadingSheetAux = loadingSheet1
                durationAux = duration1
                progAux = prog1 
                progAuxEvaluated = prog1Evaluated
                prog1 = prog2
                prog1Evaluated = prog2Evaluated   
                    
        temperature = alpha * temperature
        #it += 1 #XXX iteraciones?
    #print it
    if prog1Evaluated <= progAuxEvaluated:
        return (prog1, prog1Evaluated, loadingSheet1, duration1, predecessors, alpha, tempAux)
    else:
        return (progAux, progAuxEvaluated, loadingSheetAux, durationAux, predecessors, alpha, tempAux)


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
    currentTime = random.randint(0, int(prog1[-1][1]))
   
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
    
    loadingSheet = calculateLoadingSheet(prog, resources, asignation, duration)
    if balance == 0: # if allocate
        return (duration, loadingSheet, duration)  
    else: #if balance
        variance = calculateVariance(resources,asignation,duration,loadingSheet) 
        return (variance, loadingSheet, duration)

def calculateLoadingSheet (prog, resources, asignation, duration):
    """
    Calculate the loading sheet of prog

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                predecessors (dictionary with activities and their predecessors)
                activities (dictionary with the name of activities and their characteristics)
                balance (if 0 it will allocate else it will balance)

    Returned value: prog (planing generated)
    """
        
    startTime = []
    endTime = []
    loadingSheet = {}

    for act in prog:
        startTime.append(act[1])
        endTime.append(act[2])
    
    for resource in resources:
        startTimeCopy = copy.copy(startTime)
        endTimeCopy = copy.copy(endTime)
        time = min(min(startTimeCopy),min(endTimeCopy))      
        while time != duration:
            # remove activities with start time = current time
            for a in copy.copy(startTimeCopy):
                if a == time:
                    startTimeCopy.remove(a)
            # remove activities with end time = current time
            for a in copy.copy(endTimeCopy):
                if a == time:
                    endTimeCopy.remove(a)
            amount = 0        
            for act,start,end in prog:
                if time >= start and time < end and act in asignation.keys():
                    for r, a in asignation[act]:
                        if r == resource:
                            amount += float(a)
                            break
            if resource in loadingSheet.keys() and loadingSheet[resource][-1][1] != amount:
                loadingSheet[resource] += [(time,amount)]
            elif resource not in loadingSheet.keys():
                loadingSheet[resource] = [(time,amount)]
            
            if startTimeCopy != []:    
                time = min(min(startTimeCopy),min(endTimeCopy))
            else:
                time = min(endTimeCopy)
                
    return loadingSheet
    
      
def calculateVariance(resources,asignation,duration, loadingSheet): 
    """
    Calculate the variance of the planning it receives

    Parameters: prog (planning to evaluate)
                resources (returned by resourcesAvailability)
                asignation (returned by resourcesPerActivity)
                duration (duration of the planning)
                loadingSheet (loadingSheet of the planning)
                
    Returned value: variance (the average of all resources' variance)
    """
    
    average = {}
    variance = {}
    finalVariance = 0

    for resource in resources:
        average[resource] = 0
        pre = 0
        value = 0
        for time,data in loadingSheet[resource]:
            average[resource] += (time - pre) * value
            pre = time
            value = data
        average[resource] = (average[resource] + (duration - pre) * value) / duration
        
        variance[resource] = 0
        pre = 0
        value = 0
        for time,data in loadingSheet[resource]:
            variance[resource] += (time - pre) * (value - average[resource])**2
            pre = time
            value = data
        variance[resource] = (variance[resource] + (duration - pre) * (value - average[resource])**2) / (duration - 1)
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
        
        
        time = min(executing.values())
            
        if balance == 0:
            currentTime += time
        else:
            if time < (int(currentTime) + 1):
                currentTime += time 
            else:
                time = 1
                currentTime = int(currentTime) + time

        # Update the remaining time of all activities executing
        for a in executing.copy():
            executing[a] = float(executing[a]) - time
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
    

