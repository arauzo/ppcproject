#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Graph functions
-----------------------------------------------------------------------
 PPC-PROJECT
   Multiplatform software tool for education and research in
   project management

 Copyright 2007-8 Universidad de Córdoba
 This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published
   by the Free Software Foundation, either version 3 of the License,
   or (at your option) any later version.
 This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import math, os, sys
import copy
import subprocess

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

successors3 = {'a':['c','e'],
              '1,2,33/-3#':['d/,2,!@9)'],
              'c':['d/,2,!@9)'],
              'd/,2,!@9)':[],
              'e':['d/,2,!@9)'],
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

# Ejemplos introducidos por J.Fdez Ex.
prelaciones = {
    'A' : [],
    'B' : [],
    'C' : ['A','B'],
    'D' : ['A'],
    'E' : ['B'],
    'F' : ['A','B'],
    'G' : ['C'],
    'H' : ['D','E'],
    'I' : ['D','E','F'],
    'J' : ['D','E','F'],
    'K' : ['D','F','L'],
    'L' : ['A'],
    }
prelaciones1 = {
    '3': [], 
    '2': [], 
    '5': ['3'], 
    '4': [], 
    '7': ['4'], 
    '6': ['5'], 
    '9': ['3'], 
    '8': ['7'], 
    '11': ['7'], 
    '10': ['2'], 
    '13': ['4', '6'], 
    '12': ['10'], 
    '15': ['3'], 
    '14': ['9'], 
    '17': ['5'], 
    '16': ['6'], 
    '19': ['7'], 
    '18': ['6'], 
    '20': ['16'], 
    '21': ['11', '15', '17'], 
    '22': ['10'], 
    '23': ['18'], 
    '24': ['12'],
    '25': ['13', '14', '19'], 
    '26': ['11', '17', '16'], 
    '27': ['26', '22', '8'], 
    '28': ['9'], 
    '29': ['24', '22', '17'],
    '30': ['25', '27', '28'],
    '31': ['20', '21', '23'],
    }
prelaciones2 = {
    'B': [], 
    'A': [], 
    'D': ['B'], 
    'C': [], 
    'F': ['C'], 
    'E': ['D'], 
    'H': ['B'], 
    'G': ['F'], 
    'J': ['F'], 
    'I': ['A'], 
    'L': ['C', 'E'], 
    'K': ['I'], 
    'N': ['B'], 
    'M': ['H'], 
    'P': ['D'], 
    'O': ['E'], 
    'R': ['F'], 
    'Q': ['E'], 
    'S': ['O'], 
    'T': ['J', 'N', 'P'], 
    'U': ['I'], 
    'V': ['Q'], 
    'W': ['K'],
    'X': ['L', 'M', 'R'], 
    'Y': ['J', 'P', 'O'], 
    'Z': ['Y', 'U', 'G'], 
    'AB': ['H'], 
    'AC': ['W', 'U', 'P'],
    'AD': ['X', 'Z', 'AB'],
    'AE': ['S', 'T', 'V']
    }
prelaciones3={'24': ['21', '17'], '25': ['12'], '26': ['22', '23'], '27': ['25', '22', '14'], '20': ['2'], '21': ['7', '13'], '22': ['3'], '23': ['20', '13', '18'], '28': ['24', '25', '15'], '29': ['28', '16'], '3': [], '2': [], '5': ['2'], '4': [], '7': ['2'], '6': ['5'], '9': ['5'], '8': ['7'], '11': ['7'], '10': ['5'], '13': ['9'], '12': ['11'], '15': ['14'], '14': ['9'], '17': ['12'], '16': ['9'], '19': ['10', '18'], '18': ['4'], '31': ['27', '23', '19'], '30': ['26', '6', '8']}

prelaciones4={'24': ['2'], '25': ['9'], '26': ['6'], '27': ['7'], '20': ['15'], '21': ['18'], '22': ['6'], '23': ['7'], '28': ['20'], '29': ['11'], '4': [], '8': ['3'], '59': ['58', '39'], '58': ['44'], '55': ['35'], '54': ['26', '47'], '57': ['21'], '56': ['14'], '51': ['32'], '50': ['48', '42'], '53': ['33'], '52': ['33', '10'], '88': ['21', '83', '86'], '89': ['88', '82', '87'], '82': ['80', '38', '31'], '83': ['69', '13', '76'], '80': ['56', '75'], '81': ['53', '72'], '86': ['67', '41', '77'], '87': ['50', '85', '79'], '84': ['54', '78'], '85': ['59', '30', '65'], '3': [], '7': ['3'], '39': ['26'], '38': ['16'], '33': ['20'], '32': ['21'], '31': ['24'], '30': ['5'], '37': ['26'], '36': ['15'], '35': ['15'], '34': ['23'], '60': ['56'], '61': ['52', '37', '9'], '62': ['55'], '63': ['22', '28', '40'], '64': ['62'], '65': ['17'], '66': ['18'], '67': ['24'], '68': ['49', '45'], '69': ['56'], '2': [], '6': ['4'], '91': ['81', '84', '5'], '90': ['46', '73', '72'], '11': ['2'], '10': ['5'], '13': ['10'], '12': ['11'], '15': ['3'], '14': ['12'], '17': ['9'], '16': ['12'], '19': ['4'], '18': ['12'], '48': ['36'], '49': ['27'], '46': ['37'], '47': ['24', '18'], '44': ['29'], '45': ['11'], '42': ['8'], '43': ['36'], '40': ['36'], '41': ['28'], '5': ['4'], '9': ['6'], '77': ['28', '43'], '76': ['58', '41'], '75': ['64'], '74': ['60', '61'], '73': ['34', '69', '41'], '72': ['51', '60', '70'], '71': ['32', '19'], '70': ['25', '23', '63'], '79': ['57', '66', '74'], '78': ['33', '68', '71']}




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

def beginingActivities(successors, check_as_begin=None):
    """
    Returns a set with the name of activities that are not preceded by
    any other
    """
    if check_as_begin:
        begining = check_as_begin
    else:
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
    for node in pert.successors:
        txt += '"'+str(node)+'"' + ';'
    txt += '\n'

    for act, sig in pert.successors.iteritems():
        for s in sig:
            txt += '"'+str(act)+'"' + '->' + '"'+str(s)+'"'
            txt += ' [label="' + pert.arcs[(act,s)][0] + '"'
            if pert.arcs[(act,s)][1]:
                txt += ',style=dashed'
            txt += '];\n'
    txt += '}\n'
    return txt

def pert2image(pert, format='svg'):
    """
    Graph drawed to a image data string in the format specified as a
    format string supported by dot.
    """
    process = subprocess.Popen(['dot', '-T', format], bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    dotIn, dotOut = (process.stdin, process.stdout)
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
    process = subprocess.Popen(['dot', '-T', format], bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    dotIn, dotOut = (process.stdin, process.stdout)
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

def get_activities_start_time(activities, durations, prelations, minimum = True, previous_times = {}, root_activity = None):
    open_list = []
    inv_prelations = {}
    closed_list = []
    start_time = {}
    for activity in activities:
        inv_prelations[activity] = []
    for activity in activities:
        for children in prelations[activity]:
            inv_prelations[children].append(activity)
    if root_activity == None:
        for activity in activities:
            if inv_prelations[activity] == []:
                open_list.append(activity)
    else:
        descendants = [root_activity]
        open_descendants = copy.deepcopy(prelations[root_activity])
        while open_descendants != []:
            activity = open_descendants.pop()
            descendants.append(activity)
            for children in prelations[activity]:
                if children not in descendants and children not in open_descendants:
                    open_descendants.append(children)
        for activity in activities:
            if activity not in descendants:
                closed_list.append(activity)
                try:
                    start_time[activity] = previous_times[activity]
                except:
                    start_time[activity] = 0
        open_list.append(root_activity)
    while open_list != []:
        chosen = open_list.pop()
        closed_list.append(chosen)
        time = [0]
        for activity in inv_prelations[chosen]:
            # print 'XXX start_time[a], duractions[a]', start_time[activity], durations[activity]
            # El float() de la siguiente linea es porque en algun momento se guarda como cadena
            # Investigar y corregir.
            time.append(start_time[activity] + float(durations[activity]) )
        if previous_times != {} and not minimum:
            try:
                time.append(previous_times[chosen])
            except:
                pass
        start_time[chosen] = max(time)
        for activity in prelations[chosen]:
            pending = False
            for parent in inv_prelations[activity]:
                if parent not in closed_list:
                    pending = True
            if not pending:
                open_list.append(activity)
    return(start_time)

#
# --- GTK para probar imagen del grafo
#
import pygtk
pygtk.require('2.0')
import gtk
import cairo
from SVGViewer import SVGViewer

class Test(object):
    def __init__(self):
        self.images = []
        self.imageIndex = 0

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(800, 600)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", gtk.main_quit)

        self.svg_viewer = SVGViewer()
        self.svg_viewer.show()
        self.screen = gtk.ScrolledWindow()
        self.screen.add_with_viewport(self.svg_viewer)

        self.pos_label = gtk.Label(" -- / -- ")
        self.b_prev = gtk.Button("< Previous")
        self.b_prev.connect("clicked", self.pinta, True)
        self.button = gtk.Button("Next >")
        self.button.connect("clicked", self.pinta, None)

        self.hBox = gtk.HBox(homogeneous=False, spacing=0)
        self.hBox.pack_start(self.pos_label, expand=False, fill=False, padding=4)
        self.hBox.pack_start(self.b_prev,    expand=False, fill=False, padding=4)
        self.hBox.pack_start(self.button,    expand=False, fill=False, padding=4)

        self.vBox = gtk.VBox(homogeneous=False, spacing=0)
        self.vBox.pack_start(self.screen, expand=True,  fill=True,  padding=0)
        self.vBox.pack_start(self.hBox,   expand=False, fill=False, padding=4)
        self.window.add(self.vBox)

#        self.screen.show()
#        self.button.show()
#        self.vBox.show()
        self.window.show_all()

    def delete_event(self, widget, event, data=None):
        return False

    def pinta(self, widget, data=None):
        if data:
            self.imageIndex = (self.imageIndex - 1) % len(self.images)
        else:
            self.imageIndex = (self.imageIndex + 1) % len(self.images)
        self.svg_viewer.update_svg( self.images[self.imageIndex] )
        self.pos_label.set_text( str(self.imageIndex+1) + ' / ' + str(len(self.images)) )


def main():
    """
    Test code
    """
    import pert
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
               (3,4) : ('du1-45-45/8/9,4', True),
       }
       )
       
    window.images.append( pert2image(pert.Pert(pert4)) )

    window.images.append( graph2image(successors2) )
    window.images.append( graph2image(successors3) )
    pertP = pert.Pert()
    pertP.pert(successors2)
    #print pertP

    window.images.append( pert2image(pertP) )

##   s = pertSuccessors(pertP)
##   window.images.append( graph2image( roy(s) ) )

    gtk.main()
    

# If the program is run directly    
if __name__ == "__main__":
    main()

