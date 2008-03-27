#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Graph functions
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
from pert import *

# Prototype of new class Graph
class Grafo:

    def __init__(self):
        """ Creates an empty graph
        Efficiency: O(1)
        """
        self.successors = {}
        self.predecessors = {}
        self.arcs = {}
        
    def suc(self,nodo):
        """
        """
        successors = self.successors[nodo]
        return successors

    def pre(self,nodo):
        """
        """
        predecessors=self.predecessors[nodo]
        return predecessors
        
    def addNode(self,nodo):
        self.successors[nodo] = []
        self.predecessors[nodo] = []
        
    def addArc(self,arc,label):
        a,c=arc
        self.successors[a].append(c)
        self.predecessors[c].append(a)
        self.arcs[(a,c)]= [label]
        
    def removeNode(self,nodo):
        if nodo in self.successors:
            del self.successors[nodo]
        if nodo in self.predecessors:
            del self.predecessors[nodo]
        
        for i in self.successors:
            if nodo in self.successors[i]:
                self.successors[i].remove(nodo)
        for i in self.predecessors:
            if nodo in self.predecessors[i]:
                self.predecessors[i].remove(nodo)
        listaBorrar=[]
        for (i,j) in self.arcs:
            if i==nodo:
                listaBorrar.append((i,j))
            if j==nodo:
                listaBorrar.append((i,j))
        for i,j in listaBorrar:
            del self.arcs[(i,j)]

    def removeArc(self, arco):
        i,j=arco
        self.successors[i].remove(j)
        self.predecessors[j].remove(i)
        del self.arcs[arco]

    def numNodes(self):
        return len(self.successors)

    def numArcs(self):
        return len(self.arcs)



# ----------------
# Data structures:
# ----------------

# Precedents data structure
#  { ActivityLabel : [PreviousActivityLabel,  ... ], ... }
# for example:
precedents =  {'a':[],
               'b':[],
               'c':['a'],
               'd':['b','e'],
               'e':['a'],
               }

# Successors data structure
#  { ActivityLabel : [FollowingActivityLabel, ... ], ... }
# for example:
successors = {'a':['c','e'],
              'b':['d'],
              'c':[],
              'd':[],
              'e':['d'],
              }

successors2 = {'a':['c','e','d'],
              'b':['d'],
              'c':['f'],
              'd':['f','g'],
              'e':['g'],
              'f':['h'],
              'g':['h'],
              'h':['i','j','k'],
              'i':['l'],
              'j':['l'],
              'k':[],
              'l':[],
               }

# Directed graph data structure
# (the same as successors and precedents but using nodes)
#  { NodeNumber : [FollowingNodeNumber, ... ], ... }
#
# XXX think about using sets instead of lists
# for example:
graph = {1 : [2,3],
         2 : [4],
         3 : [4],
         4 : [],
         }

graph2 = {1 : [2,3],
          2 : [5,6,7],
          3 : [4,6,8],
          4 : [5],
          5 : [9],
          6 : [10],
          7 : [9],
          8 : [10],
          9 : [],
          10: [],
          }

# ROY graph data structure
#  A successors table with 'Begin' and 'End' activities closing the
#  graph on both sides
# for example:
roy = {'a': ['c', 'e'],
       'c': ['End'],
       'b': ['d'],
       'e': ['d'],
       'd': ['End'],
       'Begin': ['a', 'b'],
       'End': [],
       }



def reversedGraph(graph):
   """
   Returns a new directed graph data structure with all arcs
   reversed. Can be used as a table of inputs to nodes instead of
   outputs (following nodes).
   """
   reverted = {}
   for node in graph:
      inputs = []
      for n,out in graph.items():
         if node in out:
            inputs.append(n)
      reverted[node] = inputs
   return reverted    

def successors2precedents(successors):
   """
   Given a successors table returns the precedents table
   """
   return reversedGraph(successors)    

def precedents2successors(precedents):
   """
   Given a precedents table returns the successors table
   """
   return reversedGraph(precedents)


def roy(successors):
   """
   Generates an AON graph (ROY) from succesors table by adding 'Begin'
   and 'End' activities

   returns: ROY graph data structure
   """

   g = {'End':[]}

   begining = set( successors.keys() )
   for (act, next) in successors.items():
      begining -= set(next)
      if next:
         g[act] = list(next)
      else:
         g[act] = ['End']
   g['Begin'] = list(begining)
   return g

def beginingActivities(successors):
   """
   Returns a set with the name of activities that are not preceded by
   any other
   """
   begining = set( successors.keys() )
   for act,next in successors.iteritems():
      begining -= set(next)

   return begining

def endingActivities(successors):
   """
   Returns a set with the name of activities that do not precede to
   any other
   """
   ending = set()
   for act,next in successors.iteritems():
      if not next:
         ending.add(act)

   return ending


#
# Drawing graphs
#
def pert2dot(pert):
   """
   Graph to txt dot format

   returns: string with text of dot language to draw the graph
   """
   txt = """digraph G {
            rankdir=LR;
            """
   for node in pert.graph:
      txt += str(node) + ';'
   txt += '\n'
   
   for act,sig in pert.graph.iteritems():
      for s in sig:
         txt += str(act) + '->' + str(s)
         txt += ' [label="' + pert.activities[(act,s)][0] + '"'
         if pert.activities[(act,s)][1]:
            txt += ',style=dashed'
         txt += '];\n'
   txt += '}\n'
   return txt

def pert2image(pert, format='svg'):
   """
   Graph drawed to a image data string in the format specified as a
   format string supported by dot.
   """
   dotIn, dotOut = os.popen2('dot -T' + format)
   dotIn.write( pert2dot(pert) )
   dotIn.close()
   graphImage = dotOut.read()
   dotOut.close()
   return graphImage


def graph2dot(graph):
   """
   Graph to txt dot format

   returns: string with text of dot language to draw the graph
   """
   txt = """digraph G {
            rankdir=LR;
            """
   for act in graph:
         txt += '"'+str(act)+'"' + ';'
   txt += '\n'
   
   for (act,sig) in graph.iteritems():
      for s in sig:
         txt += '"'+str(act)+'"' + '->' + '"'+str(s)+'"' + ';\n'
   txt += '}\n'
   return txt

def graph2image(graph, format='svg'):
   """
   Graph drawed to a image data string in the format specified as a
   format string supported by dot.
   """
   dotIn, dotOut = os.popen2('dot -T' + format)
   dotIn.write( graph2dot(graph) )
   dotIn.close()
   graphImage = dotOut.read()
   dotOut.close()
   return graphImage


#
# Finding graph paths
#
def findPath(graph, start, end, path=[]):
   """
   Search for one path between start and end in a graph

   returns: the path as a the list of nodes including start and end nodes
   """
   path = path + [start]
   if start == end:
      return path
   if not graph.has_key(start):
      return None
   for node in graph[start]:
      if node not in path:
         newpath = findPath(graph, node, end, path)
         if newpath: return newpath
   return None


def findAllPaths(graph, start, end, path=[]):
   """
   Search for all paths between start and end in an acyclic graph

   Preconditions: graph must not have cycles (XXX not fully considered yet)
                  start and end must be nodes in graph
   returns: a list of paths given as list of nodes including start and end nodes
            example: [[1,2,3], [1,4,3], [1,3]]
   """
   path = path + [start]
   if start == end:  
      return [path]
   paths = []
   for node in graph[start]:
      if node in path:
         raise Exception("CYCLIC GRAPH!!") # XXX remove when tested outside
      newPaths = findAllPaths(graph, node, end, path)
      for newPath in newPaths:
         paths.append(newPath)
              
   return paths


def royPaths2csv(orderedActivityList, paths):
   """
   Prepares the csv text to export a matrix of graph paths given by
   activities in columns and paths in rows, with each cell crossed if
   activity belongs to path
   """
   s = ''
   
   # Header
   s += 'Paths,'
   for a in orderedActivityList:
      if a not in ['Begin','End']:
         s += str(a) + ','
   s += '\n'
         
   # Body
   for path in paths:
      p = path[1:-1]
      s += '"' + str(p) + '",'
      for a in orderedActivityList:
         if a not in ['Begin','End']:
            if a in p:
               s += 'x,'
            else:
               s += ' ,'
      s += '\n'
               
   return s


def royPaths2csv2(royGraph):
   """
   Prepares the csv text to export a matrix of graph paths given by
   activities in columns and paths in rows, with each cell crossed if
   activity belongs to path
   """
   s = ''
   
   # Header
   s += 'Paths,'
   for a in sorted(royGraph):
      if a not in ['Begin','End']:
         s += str(a) + ','
   s += '\n'
         
   # Body
   paths = findAllPaths(royGraph, 'Begin', 'End')
   for path in paths:
      p = path[1:-1]
      s += '"' + str(p) + '",'
      for a in sorted(royGraph):
         if a not in ['Begin','End']:
            if a in p:
               s += 'x,'
            else:
               s += ' ,'
      s += '\n'
               
   return s



#
# --- GTK para probar imagen del grafo
#
import pygtk
pygtk.require('2.0')
import gtk

class Test:

   def delete_event(self, widget, event, data=None):
      return False

   def destroy(self, widget, data=None):
      gtk.main_quit()

   def pinta(self, widget, data=None):
      pixbufloader = gtk.gdk.PixbufLoader()
      pixbufloader.write( self.images[self.imageIndex] )
      pixbufloader.close()
      self.grafoGTK.set_from_pixbuf( pixbufloader.get_pixbuf() )
      self.imageIndex = (self.imageIndex + 1) % len(self.images)

   def __init__(self):
       self.images = []
       self.imageIndex = 0

       self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
       self.window.connect("delete_event", self.delete_event)
       self.window.connect("destroy", self.destroy)

       self.grafoGTK = gtk.Image()

       self.button = gtk.Button("Pintar grafo")
       self.button.connect("clicked", self.pinta, None)
    
       self.vBox = gtk.VBox(homogeneous=False, spacing=0)
       self.vBox.pack_start(self.grafoGTK, expand=True, fill=True, padding=0)
       self.vBox.pack_start(self.button,   expand=False, fill=False, padding=4)
       self.window.add(self.vBox)
        
       self.grafoGTK.show()
       self.button.show()
       self.vBox.show()
       self.window.show()

   def main(self):
       gtk.main()

# Pruebas:
window = None

if __name__ == "__main__":
   window = Test()

##   print reversedGraph(pert2[0])
##   for n in range(1,6):
##      print inActivitiesR(pert2, reversedGraph(pert2[0]), n)
##   print "OUT"
##   for n in range(1,6):
##      print outActivitiesR(pert2, n)

##   window.images.append( pert2image(pert4) )
##   print equivalentRemovingDummy(pert4, (3,4) )
##   removeDummy(pert4, (3,4) )

##   pertP = pert5
##   window.images.append( pert2image(pertP) )
##   makePrelation( pertP, (1,5), (3,4) )
##   addActivity( pertP, 'nueva' )
##   makePrelation( pertP, (1,2), (7,8) )
##   makePrelation( pertP, (9,8), (6,4) )

   window.images.append( graph2image(successors2) )
   pertP = Pert()
   pertP.pert(successors2)
   #print pertP

   window.images.append( pert2image(pertP) )

##   s = pertSuccessors(pertP)
##   window.images.append( graph2image( roy(s) ) )

   window.main()
