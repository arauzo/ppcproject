#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Graph related classes and functions (module of PPC-PROJECT), includes:

 - A generic class for directed graphs
 - Handling precedent and successor tables
 - Graph pictures generation
 - Graph paths
 - GTK GUI to help test and debugging of graph related code
 
 Data structures used:

     Precedents data structure
      { ActivityLabel : [PreviousActivityLabel,  ... ], ... }

     Successors data structure
      { ActivityLabel : [FollowingActivityLabel, ... ], ... }
     for example:
        successors = {'a':['c','e'],
                      'b':['d'],
                      'c':[],
                      'd':[],
                      'e':['d'],
                      }

 *** Next structures are deprecated in favour of the Graph class
 *** however their description is kept here as they are still used inside ppc-project
               
 * Directed graph data structure
 (the same as successors and precedents but using nodes)
  { NodeNumber : [FollowingNodeNumber, ... ], ... }

 * ROY graph data structure
  A successors table with 'Begin' and 'End' activities closing the
  implicit graph on both sides
  for example:
        roy = {'a': ['c', 'e'],
               'c': ['End'],
               'b': ['d'],
               'e': ['d'],
               'd': ['End'],
               'Begin': ['a', 'b'],
               'End': [],
               }

 Copyright 2007-11 Universidad de Córdoba
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
import subprocess

class DirectedGraph(object):
    """
    Directed graph class using dictionaries (hash tables) to connect nodes and arc labels

    Both lists, incoming and outgoing arcs, are ketp (though redundant) to speedup access

        successors, outgoing connected nodes, example  {'a' : ['b','c']}
        predecessors, incoming connected, example {'b' : ['a']}
        arcs, arcs from graph with linked Data (a Python object), example {('a', 'b') : ('label',3)}

    """
    # XXX Use set instead of list??

    def __init__(self):
        """
        Creates an empty graph
        """                    #XXX Hacer el cambio con @property
                               # http://docs.python.org/2/library/functions.html#property
        self.successors = {}   #XXX next? followers? out?
        self.predecessors = {} #XXX previous? in? (no: reserved word) in_nodes?
        self.arcs = {}
        
    def suc(self, node):
        """
        Returns successors of node
        """
        # Rename to prev (previous)? XXX
        # It is faster to access directly to instance var dict. Remove this method?
        return self.successors[node]

    def pre(self, node):
        """
        Returns predecesors of node
        """
        # XXX idem as suc
        return self.predecessors[node]
        
    def add_node(self, node):
        """
        Add an unconnected node to graph
        """
        self.successors[node] = []
        self.predecessors[node] = []
        
    def add_arc(self, arc, label=None):
        """
        Insert an arc in the graph. If origin, destination nodes are not present in graph they get created.

        arc = (origin node, destination)
        label = label to be linked with arc (maybe None if unlabeled)
        """
        origin, destination = arc
        if origin not in self.successors:
            self.add_node(origin)
        if destination not in self.successors:
            self.add_node(destination)
        if destination not in self.successors[origin]:
            self.successors[origin].append(destination)
        if origin not in self.predecessors[destination]:
            self.predecessors[destination].append(origin)
        self.arcs[(origin, destination)] = label 
        
    def remove_node(self, node):
        """
        Remove a node from the graph and all arcs referencing it
        """
        if node in self.successors:
            del self.successors[node]
        if node in self.predecessors:
            del self.predecessors[node]
        
        for i in self.successors:
            if node in self.successors[i]:
                self.successors[i].remove(node)
        for i in self.predecessors:
            if node in self.predecessors[i]:
                self.predecessors[i].remove(node)

        lista_borrar = []
        for (i, j) in self.arcs:
            if i == node:
                lista_borrar.append((i, j))
            if j == node:
                lista_borrar.append((i, j))
        for i, j in lista_borrar:
            del self.arcs[(i, j)]

    def remove_arc(self, arc):
        """
        Remove an Arc from the graph
         arc = (origin, destination)
        """
        i, j = arc
        self.successors[i].remove(j)
        self.predecessors[j].remove(i)
        return self.arcs.pop(arc)

    def number_of_nodes(self):
        """
        Return the number of nodes in graph
        """
        return len(self.successors)

    def number_of_arcs(self):
        """
        Return the number of arcs in graph
        """
        return len(self.arcs)



#
# Precedent and successor table operations
#

def reversed_prelation_table(graph):
    """
    Returns a new prelation table with all arcs reversed.
    """
    reverted = {}
    for node in graph:
        inputs = []
        for key, out in graph.items():
            if node in out:
                inputs.append(key)
        reverted[node] = inputs
    return reverted

def successors2precedents(successors):
    """
    Given a successors table returns the precedents table
    """
    return reversed_prelation_table(successors)

def precedents2successors(precedents):
    """
    Given a precedents table returns the successors table
    """
    return reversed_prelation_table(precedents)


def roy(successors):
    """
    Generates an AON graph (ROY) from succesors table by adding 'Begin'
    and 'End' activities

    returns: ROY graph data structure
    """
    roy_g = {'End':[]}

    begining = set( successors.keys() )
    for (act, followers) in successors.items():
        begining -= set(followers)
        if followers:
            roy_g[act] = list(followers)
        else:
            roy_g[act] = ['End']
    roy_g['Begin'] = list(begining)
    return roy_g

def begining_activities(successors, check_as_begin=None):
    """
    Returns a set with the name of activities that are not preceded by
    any other
    
    check_as_begin = None or a subset of activities. 
                     If specified, only these activities will be considered (faster)
    """
    if check_as_begin:
        begining = check_as_begin
    else:
        begining = set( successors.keys() )
       
    for act, followers in successors.iteritems():
        begining -= set(followers)

    return begining

def ending_activities(successors):
    """
    Returns a set with the name of activities that do not precede to
    any other
    """
    ending = set()
    for act, followers in successors.iteritems():
        if not followers:
            ending.add(act)

    return ending


#
# Drawing graphs
#
def pert2dot(pert_graph):
    """
    Graph to txt dot format

    returns: string with text of dot language to draw the graph
    """
    txt = """digraph G {
             rankdir=LR;
             """
    for node in pert_graph.successors:
        txt += '"'+str(node)+'"' + ';'
    txt += '\n'

    for act, sig in pert_graph.successors.iteritems():
        for act_sig in sig:
            txt += '"'+str(act)+'"' + '->' + '"'+str(act_sig)+'"'
            txt += ' [label="' + pert_graph.arcs[(act, act_sig)][0] + '"'
            if pert_graph.arcs[(act, act_sig)][1]:
                txt += ',style=dashed'
            txt += '];\n'
    txt += '}\n'
    return txt

def pert2image(pert_graph, file_format='svg'):
    """
    Graph drawed to a image data string in the file_format specified as a
    format string supported by dot.
    """
    process = subprocess.Popen(['dot', '-T', file_format], bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    dot_in, dot_out = (process.stdin, process.stdout)
    dot_in.write( pert2dot(pert_graph) )
    dot_in.close()
    graph_image = dot_out.read()
    dot_out.close()
    return graph_image


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

    for (act, sigs) in graph.iteritems():
        for sig in sigs:
            txt += '"'+str(act)+'"' + '->' + '"'+str(sig)+'"' + ';\n'
    txt += '}\n'
    return txt

def graph2image(graph, file_format='svg'):
    """
    Graph drawed to a image data string in the format specified as a
    format string supported by dot.
    """
    process = subprocess.Popen(['dot', '-T', file_format], bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    dot_in, dot_out = (process.stdin, process.stdout)
    dot_in.write( graph2dot(graph) )
    dot_in.close()
    graph_image = dot_out.read()
    dot_out.close()
    return graph_image


#
# Finding graph paths
#
def find_path(graph, start, end, path=None):
    """
    Search for one path between start and end in a graph

    returns: the path as a the list of nodes including start and end nodes
    """
    if path == None:
        path = []
        
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: 
                return newpath
    return None


def find_all_paths(graph, start, end, path=None):
    """
    Search for all paths between start and end in an acyclic graph

    Preconditions: graph must not have cycles
                   start and end must be nodes in graph
    returns: a list of paths given as list of nodes including start and end nodes
             example: [[1,2,3], [1,4,3], [1,3]]
    """
    if path == None:
        path = []

    path = path + [start]
    if start == end:
        return [path]
    paths = []
    for node in graph[start]:
        # Must be tested outside (precondition)
        #if node in path: 
        #    raise Exception("CYCLIC GRAPH!!")
        new_paths = find_all_paths(graph, node, end, path)
        for new_path in new_paths:
            paths.append(new_path)

    return paths


def roy_paths2csv(ordered_activity_list, paths):
    """
    Prepares the csv text to export a matrix of graph paths given by
    activities in columns and paths in rows, with each cell crossed if
    activity belongs to path
    """
    csv_text = ''

    # Header
    csv_text += 'Paths,'
    for act in ordered_activity_list:
        if act not in ['Begin','End']:
            csv_text += str(act) + ','
    csv_text += '\n'

    # Body
    for path in paths:
        trimmed_path = path[1:-1]
        csv_text += '"' + str(trimmed_path) + '",'
        for act in ordered_activity_list:
            if act not in ['Begin','End']:
                if act in trimmed_path:
                    csv_text += 'x,'
                else:
                    csv_text += ' ,'
        csv_text += '\n'

    return csv_text


#
# --- GTK GUI to test and debug
#
import pygtk
pygtk.require('2.0')
import gtk
from svgviewer import SVGViewer

class Test(object):
    """
    Shows a window with several graph pictures to test
    """

    def __init__(self):
        """
        Create the GTK window
        """
        self.images = []
        self.image_index = 0

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(800, 600)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", gtk.main_quit)

        self.svg_viewer = SVGViewer()
        self.svg_viewer.show()
        screen = gtk.ScrolledWindow()
        screen.add_with_viewport(self.svg_viewer)

        self.pos_label = gtk.Label(" -- / -- ")
        self.b_prev = gtk.Button("< Previous")
        self.b_prev.connect("clicked", self.change_image, True)
        self.button = gtk.Button("Next >")
        self.button.connect("clicked", self.change_image, None)

        h_box = gtk.HBox(homogeneous=False, spacing=0)
        h_box.pack_start(self.pos_label, expand=False, fill=False, padding=4)
        h_box.pack_start(self.b_prev,    expand=False, fill=False, padding=4)
        h_box.pack_start(self.button,    expand=False, fill=False, padding=4)

        v_box = gtk.VBox(homogeneous=False, spacing=0)
        v_box.pack_start(screen, expand=True,  fill=True,  padding=0)
        v_box.pack_start(h_box,   expand=False, fill=False, padding=4)
        self.window.add(v_box)

        self.window.show_all()

    def delete_event(self, widget, event, data=None):
        """ Close window """
        return False

    def add_image(self, image):
        self.images.append(image)
        self.svg_viewer.update_svg( self.images[self.image_index] )

    def change_image(self, widget, data=None):
        """
        Toggles to previous or next image
        """
        if data:
            self.image_index = (self.image_index - 1) % len(self.images)
        else:
            self.image_index = (self.image_index + 1) % len(self.images)
        self.svg_viewer.update_svg( self.images[self.image_index] )
        self.pos_label.set_text( str(self.image_index+1) + ' / ' + str(len(self.images)) )


def main():
    """
    Test code
    """
    window = Test()

##   print reversed_prelation_table(pert2[0])
##   for n in range(1,6):
##      print inActivitiesR(pert2, reversed_prelation_table(pert2[0]), n)
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

    pert4 = ( {1 : [2, 3],
               2 : [4, 5],
               3 : [4],
               4 : [5],
               5 : [],
               },
              {(1, 2) : ('a', False),
               (1, 3) : ('b', False),
               (2, 5) : ('c', False),
               (4, 5) : ('d', False),
               (2, 4) : ('e', False),
               (3, 4) : ('du1-45-45/8/9,4', True),
       }
       )
       
    window.images.append( pert2image(pert.Pert(pert4)) )

    successors2 = {'a':['c', 'e', 'd'],
                  'b':['d'],
                  'c':['f'],
                  'd':['f', 'g'],
                  'e':['g'],
                  'f':['h'],
                  'g':['h'],
                  'h':['i', 'j', 'k'],
                  'i':['l'],
                  'j':['l'],
                  'k':[],
                  'l':[],
                   }

    successors3 = {'a':['c', 'e'],
                  '1,2,33/-3#':['d/,2,!@9)'],
                  'c':['d/,2,!@9)'],
                  'd/,2,!@9)':[],
                  'e':['d/,2,!@9)'],
                  }

    window.images.append( graph2image(successors2) )
    window.images.append( graph2image(successors3) )
    pert_p = pert.Pert()
    pert_p.construct(successors2)
    #print pert_p

    window.images.append( pert2image(pert_p) )

##   s = pertSuccessors(pert_p)
##   window.images.append( graph2image( roy(s) ) )

    gtk.main()
    

# If the program is run directly    
if __name__ == "__main__":
    import pert
    main()

