#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PERT graph generation
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

import math, os, sys
from graph import *

class Pert:
   """
   PERT class to store graph data, contains:
     self.graph = directed graph data structure
     self.activities = activity labels

   directed graph data structure: see graph.py.

   activity labels:
    { (OriginNode, DestinationNode) : (ActivityLabel, DummyActivity), ... }

   DummyActivity: True if dummy, False if real
  
   Create example PERT graphs with Pert(pertN):
   """
   pert2= ( {1 : [2,4],
             2 : [3],
             3 : [4,6],
             4 : [5],
             5 : [],
             6 : [5]
             },
            {(1,2) : ('b',   False),
             (1,4) : ('a',   False),
             (2,3) : ('d',   False),
             (3,4) : ('du1', True),
             (3,6) : ('e',   False),
             (4,5) : ('c',   False),
             (6,5) : ('f',   False),
             }
           )

   pert3= ( {1 : [2,4],
             2 : [3],
             3 : [4,5],
             4 : [5],
             5 : [],
             },
            {(1,2) : ('b',   False),
             (1,4) : ('a',   False),
             (2,3) : ('d',   False),
             (3,4) : ('du1', True),
             (3,5) : ('e',   False),
             (4,5) : ('c',   False),
             }
           )

   pert4 = ( {1 : [2,3],
              2 : [4,5],
              3 : [4],
              4 : [5],
              5 : [],
              },
             {(1,2) : ('a', False),
              (1,3) : ('b', False),
              (2,5) : ('c', False),
              (4,5) : ('d', False),
              (2,4) : ('e', False),
              (3,4) : ('du1', True),
      }
      )

   pert5 = ( {1 : [2,5],
              2 : [3],
              3 : [4],
              4 : [],
              5 : []
              },
             {(1,2) : ('a', False),
              (2,3) : ('b', False),
              (3,4) : ('c', False),
              (1,5) : ('d', False),
              }
             )

   pert6 = ( {1 : [2],
              2 : [3],
              3 : [4],
              4 : [],
              5 : [6],
              6 : []
              },
             {(1,2) : ('a', False),
              (2,3) : ('b', False),
              (3,4) : ('c', False),
              (5,6) : ('d', False),
              }
             )

   def __init__(self, pert=None):
      if pert == None:
         self.graph = {}
         self.activities = {}
      else:
         self.graph, self.activities = pert

   def __repr__(self):
      return 'Pert( (' + str(self.graph) + ',' + str(self.activities) + ') )'

   def __str__(self):
      s = str(self.graph) + '\n'
      for link, act in self.activities.iteritems():
         s += str(link) + ' ' + str(act) + '\n'
      return s

   def nextNodeNumber(self):
      """
      New node number max(graph)+1 O(n)
        O(1): len(directed graph)+1 must be an available node number
        (i.e. graph nodes must be numbered starting in 0 or 1 at most)
        Valid if nodes are not deleted (or reasigned when deleted
        O(n))
      """ 
      if self.graph:
         return max(self.graph)+1
      else:
         return 0

   def addActivity(self, activityName, origin=None, destination=None, dummy=False):
      """
      Adds activity with new nodes or the specified ones
      """
      if origin == None:
         origin = self.nextNodeNumber()
         self.graph[origin] = []

      if destination == None:
         destination = self.nextNodeNumber()
         self.graph[destination] = []

      self.graph[origin].append(destination)
      self.activities[(origin,destination)] = (activityName, dummy)
      return (origin,destination)

   def addNode(self, node):
      self.graph[node] = []

   def activityArc(self, activityName):
      """
      Given an activity name returns the arc which represents it on graph
      """
      for arc,act in self.activities.iteritems():
         if act[0] == activityName:
            return arc
      return None


   def inActivities(self, reversedGraph, node):
      """
      Return the name of activities directly preceding node
      """
      inAct = []
      for inNode in reversedGraph[node]:
         act, dummy = self.activities[ (inNode, node) ]
         if not dummy:
            inAct.append(act)
      
      return inAct

   def inActivitiesR(self, reversedGraph, node):
      """
      Return the name of activities preceding node (directly or throgh
      dummies)
      """
      inAct = []
      for inNode in reversedGraph[node]:
         act, dummy = self.activities[ (inNode, node) ]
         if dummy:
            inAct += self.inActivitiesR(reversedGraph, inNode)
         else:
            inAct.append(act)
      
      return inAct

   def outActivities(self, node):
      """
      Return the name of activities directly following node
      """
      outAct = []
      for outNode in self.graph[node]:
         act, dummy = self.activities[ (node, outNode) ]
         if not dummy:
            outAct.append(act)
      
      return outAct

   def outActivitiesR(self, node):
      """
      Return the name of activities following node (directly or throgh
      dummies)
      """
      outAct = []
      for outNode in self.graph[node]:
         act, dummy = self.activities[ (node, outNode) ]
         if dummy:
            outAct += self.outActivitiesR(outNode)
         else:
            outAct.append(act)
      
      return outAct


   def pertSuccessors(self):
      """
      Extracts all implicit prelations (not redundant)
      """
      revGraph = reversedGraph(self.graph)
      successors = {}
      for node,connections in self.graph.items():
         inputs  = self.inActivities(revGraph, node)
         outputs = self.outActivitiesR(node)
         for i in inputs:
            if i in successors:
               successors[i] += outputs
            else:
               successors[i] = outputs
      return successors



   def pert(self, successors):
      """
      Generates a AOA graph (PERT) from successors table
      Algorithm sharma1998 extended
      returns: PERT graph data structure
      """
      if self.graph or self.activities:
         raise Exception('PERT structure must be empty')

      precedents = reversedGraph(successors)

      # Close the graph (not in sharma1998)
      origin = self.nextNodeNumber()
      self.graph[origin] = []
      dest = self.nextNodeNumber()
      self.graph[dest] = []
      beginAct    = beginingActivities(successors)
      endAct      = endingActivities(successors)
      beginEndAct = beginAct.intersection(endAct) 

      #  -Creates a common node for starting activities
      for act in beginAct - beginEndAct:
         self.addActivity(act, origin)

      #  -Creates a common node for ending activities
      for act in endAct - beginEndAct:
         self.addActivity(act, origin=None, destination=dest)

      #  -Deals with begin-end activities
      if beginEndAct:
         act = beginEndAct.pop()
         self.addActivity(act, origin, dest)
         for act in beginEndAct:
            o,d = self.addActivity(act, origin)
            self.addActivity("seDummy", d, dest, dummy=True)
      
      # Sharma1998 algorithm
      for act in successors:
         #print "Processing", act
         if not self.activityArc(act):
            self.addActivity(act)
            #window.images.append( pert2image(self) )
         aOrigin, aDest = self.activityArc(act)
         #print '(', aOrigin, aDest, ')'
         for pre in precedents[act]:
            #print self.graph
            #print pre, pre in self.inActivitiesR(reversedGraph(self.graph), aOrigin)
            if pre not in self.inActivitiesR(reversedGraph(self.graph), aOrigin):
               if not self.activityArc(pre):
                  self.addActivity(pre)
                  #window.images.append( pert2image(self) )
               self.makePrelation(pre, act)
               aOrigin, aDest = self.activityArc(act)


     


   def equivalentRemovingDummy(self, dummy):
      """
      Idea of Lemma1 of Sharma1998 modified

      dummy given as (origin, destination)
      """
      revGraph = reversedGraph(self.graph)
      nodeO, nodeD = dummy

      # Stop being a graph?
      inNodesO  = revGraph[nodeO]
      inNodesD = revGraph[nodeD]
      for n in inNodesO:
         if n in inNodesD:
            return False # Two activities would begin and end in the same nodes
      outNodesO  = self.graph[nodeO]
      outNodesD = self.graph[nodeD]
      for n in outNodesO:
         if n in outNodesD:
            return False # Two activities would begin and end in the same nodes

      # Implies new prelations?
      inO  = set( self.inActivitiesR(revGraph, nodeO) )
      inD  = set( self.inActivitiesR(revGraph, nodeD) )
      outO = set( self.outActivitiesR(nodeO) )
      outD = set( self.outActivitiesR(nodeD) )
      return inD.issubset(inO) or outO.issubset(outD)

   def removeDummy(self, dummy):
      """
      Removes a dummy activity as in sharma1998 (removes destination node
      of dummy moving their dependencies to origin)
      """
      nodeO, nodeD = dummy

      # Removes the dummy activity link from graph
      self.graph[nodeO].remove(nodeD)
      revGraph = reversedGraph(self.graph)

      inD = revGraph[nodeD]
      outD = self.graph[nodeD]
      self.graph.pop(nodeD)

      for node in inD:
         self.graph[node].remove(nodeD)
         self.graph[node].append(nodeO)
      self.graph[nodeO] += outD

      # Activities table
      self.activities.pop( (nodeO, nodeD) )
      for node in inD:
         act = self.activities.pop( (node,nodeD) )
         self.activities[ (node,nodeO) ] = act
      for node in outD:
         act = self.activities.pop( (nodeD,node) )
         self.activities[ (nodeO,node) ] = act


   def makePrelation(self, preName, folName):
      """
      Links two activities as described in Sharma1998 (simplified to
      change less arcs)
      """
      pre = self.activityArc(preName)
      fol = self.activityArc(folName)
      preO, preD = pre 
      folO, folD = fol

      # New nodes
      newO = self.nextNodeNumber()
      self.graph[newO] = []
      newD = self.nextNodeNumber()
      self.graph[newD] = []

      # Change links of existing nodes to new nodes
      self.graph[folO].remove(folD)
      self.graph[folO].append(newD)
      self.graph[preO].remove(preD)
      self.graph[preO].append(newO)
      # New links
      self.graph[newO].append(newD)
      self.graph[newO].append(preD)
      self.graph[newD].append(folD)

      # Activities table
      # New dummy activities
      dummy1 = (folO, newD)
      dummy2 = (newO, preD)
      dummy3 = (newO, newD)
      self.activities[ dummy1 ] = ('dummy', True)
      self.activities[ dummy2 ] = ('dummy', True)
      self.activities[ dummy3 ] = ('dummy', True)
      # New link of activities with new nodes
      act = self.activities.pop(pre)
      self.activities[ (preO, newO) ] = act
      act = self.activities.pop(fol)
      self.activities[ (newD, folD) ] = act

      #window.images.append( pert2image(self) )

      # Remove dummy activities if possible
      if self.equivalentRemovingDummy(dummy2):
         #print dummy2, ':equivalent'
         self.removeDummy(dummy2)
         #window.images.append( pert2image(self) )

      if self.equivalentRemovingDummy(dummy1):
         #print dummy1, ':equivalent'
         self.removeDummy(dummy1)
         #window.images.append( pert2image(self) )
         dummy3 = (newO, folO)

      if self.equivalentRemovingDummy(dummy3):
         #print dummy3, ':equivalent'
         self.removeDummy(dummy3)
         #window.images.append( pert2image(self) )



