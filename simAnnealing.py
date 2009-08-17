#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Calculate optimum schedule
#-----------------------------------------------------------------------
# PPC-PROJECT
#   Multiplatform software tool for education and research in 
#   project management
#
# Copyright 2007-9 Universidad de Córdoba
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

# Internationalization
import gettext
APP='PPC-Project' #Program name
DIR='po' #Directory containing translations, usually /usr/share/locale
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)


def resources_availability(availableResources, flag = False):
    """
    Create a dictionary with the renewable and the
            doubly constrained resources

    Parameters: availableResources (list of resources in the project)
                flag (True : consider only renewable and double constrained resources;
                      False: consider also unlimited resources)

    Returned value: resources
    """
    resources={} 
   
    #Create a dictionary with the resources' name and number available   
    for a in availableResources:
        if a[1] == gettext.gettext('Renewable'):
            resources[a[0]] = a[3]
        elif a[1] == gettext.gettext('Double constrained'):
            resources[a[0]] = a[2]
        elif flag and a[1] == gettext.gettext('Unlimited'):
            resources[a[0]] = None
            
    return resources


def resources_per_activities(initialAsignation, resources):
    """
    Create a dictionary with the resources
          the activities need

    Parameters: initialAsignation (list of the activities and the resources they need) 
                resources

    Returned value: asignation
    """
      
    asignation={}
    #Create a dictionary with the activities and the resources they need
    for act,resource,amount in initialAsignation:
        if resource in resources.keys():
            if act in asignation.keys():
                asignation[act] = asignation[act] + [(resource,amount)]
            else:
                asignation[act] = [(resource,amount)]
     
    return asignation
      
def simulated_annealing(asignation,resources,successors,activities,leveling,nu,phi,minTemperature,maxIteration,numIterations):
    """
    Try to find the best schedule of the project by
        the technique of simulated annealing

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                successors (the prelations of the activities)
                activities (dictionary with the name of activities and their characteristics)
                leveling (if 0 it will allocate else it will level)
                nu (parameter to configure simulated annealing algorithm)
                phi (parameter to configure simulated annealing algorithm)
                minTemperature (parameter to configure simulated annealing algorithm)
                maxIteration (parameter to configure simulated annealing algorithm)
                numIterations (parameter to configure simulated annealing algorithm)

    Returned value: sch (the best schedule found)
                    schEvaluated (loading sheet of schedule)
                    duration (duration of schedule)
                    alpha (parameter to configure simulated annealing algorithm)
                    tempAux (parameter to configure simulated annealing algorithm)
                    it (number of iterations done)
    """
    predecessors = successors2precedents(successors)

    for a in predecessors.copy():
        if predecessors[a] == []:
            del predecessors[a]

    # sch1 will store the best plannings
    schAux = sch1 = generate(asignation,resources.copy(),copy.deepcopy(predecessors),activities.copy(),leveling)
    sch1Evaluated, loadSheet1, duration1 = evaluate(sch1,leveling,asignation,resources)
    schAuxEvaluated = sch1Evaluated
    durationAux = duration1
    loadSheetAux = loadSheet1
    
    if duration1 == 0:
        return (sch1, sch1Evaluated, duration1, None, None, None)
    if sch1Evaluated == 0:
        return (sch1, sch1Evaluated, duration1, None, None, 0)
        
    tempAux = temperature = (nu / -log(phi)) * sch1Evaluated
    alpha = (minTemperature / temperature) ** (1 / maxIteration)
    if alpha >= 1:
        return (None,None,None,None,None,None)
    it=0
    numIterationsAux = numIterations
    
    while temperature > minTemperature and numIterations != 0:
        it += 1
        sch2 = modify(asignation,resources.copy(),copy.deepcopy(predecessors),activities.copy(),sch1,leveling)
        sch2Evaluated, loadSheet2, duration2 = evaluate(sch2,leveling,asignation,resources)
        if sch2Evaluated <= sch1Evaluated:
            loadSheet1 = loadSheet2
            duration1 = duration2
            sch1 = sch2
            sch1Evaluated = sch2Evaluated
            # Set numIterations to initial value
            numIterations = numIterationsAux 
        else:
            numIterations -= 1 
            r = random.random()
            m = exp(-(sch2Evaluated-sch1Evaluated) / temperature)
            if r < m:
                if schAuxEvaluated > sch1Evaluated:
                    loadSheetAux = loadSheet1
                    durationAux = duration1
                    schAux = sch1 
                    schAuxEvaluated = sch1Evaluated              
                sch1 = sch2
                sch1Evaluated = sch2Evaluated
                loadSheet1 = loadSheet2
                duration1 = duration2   
                    
        temperature = alpha * temperature

    if sch1Evaluated <= schAuxEvaluated:
        return (sch1, sch1Evaluated, duration1, alpha, tempAux, it)
    else:
        return (schAux, schAuxEvaluated, durationAux, alpha, tempAux, it)


def generate(asignation,resources,predecessors,activities,leveling):
    """
    Generate a schedule

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                predecessors (dictionary with activities and their predecessors)
                activities (dictionary with the name of activities and their characteristics)
                leveling (if 0 it will allocate else it will level)

    Returned value: sch (planing generated)
    """
       
    currentTime = 0
    executing = {}
    result = []
   
    sch = generate_or_modify(asignation,resources,predecessors,activities,leveling,executing,result,currentTime)
    return sch


def modify(asignation,resources,predecessors,activities,sch1,leveling):
    """
    Modify a planning

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                predecessors (dictionary with activities and their predecessors)
                activities (dictionary with the name of activities and their characteristics)
                sch1 (planning to modify)
                leveling (if 0 it will allocate else it will level)

    Returned value: sch (planning modified)
    """
       
    result = []
    executing = {}
   
    # The modification will start at this time
    currentTime = random.randint(0, int(sch1[-1][1]))
   
    # Update the state of result, executing, resources and activities to the state they would be at currentTime
    for act,startTime,endTime in sch1:
        if startTime < currentTime:
            result += [(act,startTime,endTime)]
            if startTime + activities[act][0] > currentTime:
                executing[act] = startTime + activities[act][0] - currentTime
                if act in asignation.keys() and leveling == 0:
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
      
    sch = generate_or_modify(asignation,resources,predecessors,activities,leveling,executing,result,currentTime)
    return sch


def evaluate(sch,leveling,asignation,resources):
    """
    Evaluate a planning

    Parameters: sch (planning to evaluate)
                leveling (if 0 it will consider resoucers)
                asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                

    Returned value: duration or variance
                    loadSheet
                    duration
    """
    
    duration = 0
    
    # Calculate duration
    for act,startTime,endTime in sch:
        if endTime > duration:
            duration = endTime
    
    if duration == 0:
        return (None, None, 0)
        
    loadSheet = calculate_loading_sheet(sch, resources, asignation, duration)
    if leveling == 0: # if allocate
        return (duration, loadSheet, duration)  
    else: #if leveling
        variance = calculate_variance(resources,asignation,duration,loadSheet) 
        return (variance, loadSheet, duration)

def calculate_loading_sheet (sch, resources, asignation, duration):
    """
    Calculate the loading sheet of sch

    Parameters: sch (schedule)
                resources 
                asignation
                duration
               
    Returned value: loadSheet
    """
        
    startTime = []
    endTime = []
    loadSheet = {}
        
    for act in sch:
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
            for act,start,end in sch:
                if time >= start and time < end and act in asignation.keys():
                    for r, a in asignation[act]:
                        if r == resource:
                            amount += float(a)
                            break
            if resource in loadSheet.keys() and loadSheet[resource][-1][1] != amount:
                loadSheet[resource] += [(time,amount)]
            elif resource not in loadSheet.keys():
                loadSheet[resource] = [(time,amount)]
            
            if startTimeCopy != []:    
                time = min(min(startTimeCopy),min(endTimeCopy))
            else:
                time = min(endTimeCopy)
                
    return loadSheet
    
      
def calculate_variance(resources,asignation,duration, loadSheet): 
    """
    Calculate the variance of the planning it receives

    Parameters: resources (returned by resourcesAvailability)
                asignation (returned by resourcesPerActivity)
                duration (duration of the planning)
                loadSheet (loadSheet of the planning)
                
    Returned value: variance (the average of all resources' variance)
    """
    average = {}
    variance = {}
    finalVariance = 0

    for resource in resources:
        average[resource] = 0
        pre = 0
        value = 0
        for time,data in loadSheet[resource]:
            average[resource] += (time - pre) * value
            pre = time
            value = data
        average[resource] = (average[resource] + (duration - pre) * value) / duration
        
        variance[resource] = 0
        pre = 0
        value = 0
        for time,data in loadSheet[resource]:
            variance[resource] += (time - pre) * (value - average[resource])**2
            pre = time
            value = data
        variance[resource] = (variance[resource] + (duration - pre) * (value - average[resource])**2) / (duration - 1)
        finalVariance += variance[resource] 

    return finalVariance / len(resources)
         

def generate_or_modify(asignation,resources,predecessors,activities,leveling,executing,result,currentTime):
    """
    Generate or modify a planning.
    It depends on currentTime

    Parameters: asignation (returned by resourcesPerActivity)
                resources (returned by resourcesAvailability)
                predecessors (dictionary with activities and their predecessors)
                activities (dictionary with the name of activities and their characteristics)
                leveling (if 0 it will allocate else it will level)
                possibles (dictionary of the activities which can execute at currentTime)
                executing (dictionary of the activities which are executing at currentTime)
                result (planning of the project up to currentTime)
                currentTime (time when the algorithm starts to generate a new planning) 

    Returned value: result (planning calculated)
    """
    possibles = {}
    
    lengthResources = len(resources)
    if lengthResources == 0: 
        lengthResources = -1 
   
    resourcesUsedUp = 0 
   
    while activities != {} or possibles != {}: # Until all the activities have finished
        # Choose activities with no predecessors
        for a in activities.copy():
            if a not in predecessors.keys():
                possibles[a] = activities.pop(a)
      
        if possibles != {}:           
            # If it level, pop the activities with maximum time to start = currentTime 
            if leveling == 1:
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

            possiblesCopy = possibles.copy()
            # Execute activities until a number of activities have executed, no more possibles activities or no more resources 
            while numActivities != 0 and lengthResources != resourcesUsedUp:
            
                noExecute = 0

                # Pop a random item of possiblesCopy
                possiblesKeys = possiblesCopy.keys()
                key = random.choice(possiblesKeys)
                act = possiblesCopy.pop(key)
                # If resources are required            
                if key in asignation.keys() and leveling == 0:
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
        if leveling == 0:
            currentTime += time
        else:
            if time <= 1:
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
                if a in asignation.keys() and leveling == 0:
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
    

