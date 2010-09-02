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

from pert import *

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
            time.append(start_time[activity] + durations[activity])
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
import rsvg
import cairo


class SVGViewer(gtk.DrawingArea):
    """
    Create a GTK+ widget to draw an SVG using rsvg and Cairo
    
    XXX Implement pan operation
    XXX Zoom centering to pointer
    XXX Do not allow zoom out over actual size of widget
    XXX Implement scrollable ??
    """
    def __init__(self, svg_text=None):
        super(SVGViewer, self).__init__()
        self.svg = None
        self.update_svg(svg_text)
        self.connect("expose_event", self.expose_event)
        self.connect("scroll-event", self.mousewheel_scrolled)
        self.add_events(gtk.gdk.SCROLL_MASK)

    def update_svg(self, svg_text):
        self.svg_text = svg_text
        self.zoom_factor = 1.0
        if svg_text != None:
            self.svg = rsvg.Handle(data=svg_text)
            self.update_transformation()
            
    def update_transformation(self):
        rect = self.get_allocation()
        width = rect.width
        height = rect.height
        
        pw, ph, graph_width, graph_height = self.svg.get_dimension_data()
        scale_factor = min(width/graph_width, height/graph_height) # keep proportions
        #scale_factor *= self.zoom_factor # esto era para cuando no se ampliaba el espacio
        self.matrix = cairo.Matrix()
        self.matrix.scale(scale_factor, scale_factor)
        
        self.set_size_request(int(graph_width*self.zoom_factor), int(graph_height*self.zoom_factor))

    def expose_event(self, widget, event):
        """Handle the expose-event by drawing"""
        context = widget.window.cairo_create()
         
        # Restrict Cairo to the exposed area; avoid extra work
        # (set a clip region for the expose event)
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()
         
        self.draw(context)
        return False

    def draw(self, cr):
        rect = self.get_allocation()
        width = rect.width
        height = rect.height

#        # Fill the background with default foreground color (just to see if we are not drawing some area)
#        cr.set_source_color(self.style.fg[self.state]) #rgb(0.5, 0.5, 0.5) #grey
#        cr.rectangle(0, 0, width, height)
#        cr.fill()

#        cr.set_source_color(self.style.fg[self.state])
#        cr.rectangle(BORDER_WIDTH, BORDER_WIDTH,
#                    width - 2*BORDER_WIDTH, height - 2*BORDER_WIDTH)
#        cr.set_line_width(5.0)
#        cr.set_line_join(cairo.LINE_JOIN_ROUND)
#        cr.stroke()

        if self.svg != None:
            self.update_transformation()
            cr.transform(self.matrix)
            self.svg.render_cairo(cr)

        return True

    def redraw_canvas(self):
        """Force updating the canvas"""
        if self.window:
            alloc = self.get_allocation()
            rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
            self.window.invalidate_rect(rect, True)
            self.window.process_updates(True)

    def mousewheel_scrolled(self, widget, event):
        if event.type == gtk.gdk.SCROLL:
            # Ctrl-mousewheel (faster zoom)
            if event.state & gtk.gdk.CONTROL_MASK:
                if event.direction == gtk.gdk.SCROLL_UP:
                        self.zoom_factor *= 2.0
                elif event.direction == gtk.gdk.SCROLL_DOWN:
                        self.zoom_factor *= 0.5
            # Mousewheel scroll alone (zoom)
            else:
                if event.direction == gtk.gdk.SCROLL_UP:
                        self.zoom_factor *= 1.25
                elif event.direction == gtk.gdk.SCROLL_DOWN:
                        self.zoom_factor *= 0.8
            zoom_point = event.x, event.y
            self.redraw_canvas()
            return True


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

        self.button = gtk.Button("Pintar grafo")
        self.button.connect("clicked", self.pinta, None)

        self.vBox = gtk.VBox(homogeneous=False, spacing=0)
        self.vBox.pack_start(self.screen,   expand=True,  fill=True,  padding=0)
        self.vBox.pack_start(self.button,   expand=False, fill=False, padding=4)
        self.window.add(self.vBox)

        self.screen.show()
        self.button.show()
        self.vBox.show()
        self.window.show()

    def delete_event(self, widget, event, data=None):
        return False

    def pinta(self, widget, data=None):
        self.svg_viewer.update_svg( self.images[self.imageIndex] )
        self.imageIndex = (self.imageIndex + 1) % len(self.images)


def main():
    """
    Test code
    """
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
    window.images.append( graph2image(successors3) )
    pertP = Pert()
    pertP.pert(successors2)
    #print pertP

    window.images.append( pert2image(pertP) )

##   s = pertSuccessors(pertP)
##   window.images.append( graph2image( roy(s) ) )

    gtk.main()
    

# If the program is run directly    
if __name__ == "__main__":
    main()

