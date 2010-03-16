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
#from pert import *
import al

def dibujarGrafo():
	prelaciones1 = {
        'A' : [],
        'B' : [],
        'C' : ['A','B'],
        'D' : ['K'],
        'E' : ['A','B'],
        'F' : ['E','J'],
        'G' : ['C'],
        'H' : ['D'],
        'I' : ['D'],
        'J' : ['K'],
        'K' : ['A'],
        'L' : ['G','M','N'],
		'M' : ['F','I'],
		'N' : ['E','J','O'],
		'O' : ['C'],
    }

	prelaciones3 = {
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
	prelaciones2 = {
		'A' : [],
		'B' : ['A'],
		'C' : ['A'],
		'D' : ['A'],
		'E' : ['B'],
		'F' : ['B','C'],
		'G' : ['C'],
		'H' : ['D'],
		'I' : ['H'],
		'J' : ['F','G','H'],
		'K' : ['E','J','I'],
	}
	
	prelaciones4 = {
		'A' : [],
		'B' : [],
		'C' : ['A','B'],
		'D' : ['A'],
		'E' : ['A'],
		'F' : ['D'],
		'G' : ['D'],
		'H' : ['G'],
		'I' : ['F'],
		'J' : ['E'],
		'K' : ['C'],
		'L' : ['H','I','J'],
		'M' : ['K'],
		'N' : ['M'],
		'P' : ['L'],
		'Q' : ['N','P'],
		'R' : ['Q'],
	}

	prelaciones5 = {
		'A' : [],
		'B' : [],
		'C' : ['A'],
		'D' : ['B'],
		'E' : ['B'],
		'F' : ['C'],
		'G' : ['A','B'],
		'H' : ['D'],
		'I' : ['C'],
		'J' : ['I'],
		'K' : ['F','G'],
		'L' : ['E'],
		'M' : ['F','G','H'],
		'N' : ['K'],
		'O' : ['K','M'],
		'P' : ['J','N','O'],
	}

	prelaciones6 = {
		'A' : [],
		'B' : [],
		'C' : ['A','B'],
		'D' : ['A','B'],
		'E' : ['B'],
		'F' : ['C','D'],
		'G' : ['C','D','E'],
		'H' : ['E','F'],
		'I' : ['E'],
	}

	prelaciones7 = {
		'A' : [],
		'B' : ['A'],
		'C' : ['A'],
		'D' : ['A'],
		'F' : ['B','D'],
		'E' : ['B','C'],
		'G' : ['E','F','I'],
		'H' : ['E','I'],
		'I' : ['B','C'],
		'J' : ['D'],
	}


	g=al.al(prelaciones7)
	return g

def graph2dot(graph):

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
    dotIn, dotOut = os.popen2('dot -T' + format)
    dotIn.write( graph2dot(graph) )
    dotIn.close()
    graphImage = dotOut.read()
    dotOut.close()
    return graphImage

def dibujarPert():
	prelaciones1 = {
        'A' : [],
        'B' : [],
        'C' : ['A','B'],
        'D' : ['K'],
        'E' : ['A','B'],
        'F' : ['E','J'],
        'G' : ['C'],
        'H' : ['D'],
        'I' : ['D'],
        'J' : ['K'],
        'K' : ['A'],
        'L' : ['G','M','N'],
		'M' : ['F','I'],
		'N' : ['E','J','O'],
		'O' : ['C'],
    }

	prelaciones3 = {
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

	prelaciones4 = {
		'A' : [],
		'B' : [],
		'C' : ['A','B'],
		'D' : ['A'],
		'E' : ['A'],
		'F' : ['D'],
		'G' : ['D'],
		'H' : ['G'],
		'I' : ['F'],
		'J' : ['E'],
		'K' : ['C'],
		'L' : ['H','I','J'],
		'M' : ['K'],
		'N' : ['M'],
		'P' : ['L'],
		'Q' : ['N','P'],
		'R' : ['Q'],
	}
	
	prelaciones2 = {
		'A' : [],
		'B' : ['A'],
		'C' : ['A'],
		'D' : ['A'],
		'E' : ['B'],
		'F' : ['B','C'],
		'G' : ['C'],
		'H' : ['D'],
		'I' : ['H'],
		'J' : ['F','G','H'],
		'K' : ['E','J','I'],
	}
	
	prelaciones5 = {
		'A' : [],
		'B' : [],
		'C' : ['A'],
		'D' : ['B'],
		'E' : ['B'],
		'F' : ['C'],
		'G' : ['A','B'],
		'H' : ['D'],
		'I' : ['C'],
		'J' : ['I'],
		'K' : ['F','G'],
		'L' : ['E'],
		'M' : ['F','G','H'],
		'N' : ['K'],
		'O' : ['K','M'],
		'P' : ['J','N','O'],
	}
	
	prelaciones6 = {
		'A' : [],
		'B' : [],
		'C' : ['A','B'],
		'D' : ['A','B'],
		'E' : ['B'],
		'F' : ['C','D'],
		'G' : ['C','D','E'],
		'H' : ['E','F'],
		'I' : ['E'],
	}

	prelaciones7 = {
		'A' : [],
		'B' : ['A'],
		'C' : ['A'],
		'D' : ['A'],
		'F' : ['B','D'],
		'E' : ['B','C'],
		'G' : ['E','F','I'],
		'H' : ['E','I'],
		'I' : ['B','C'],
		'J' : ['D'],
	}

	p=al.al(prelaciones7)
	return p

def pert2image(pert, format='svg'): 
   """
   Graph drawed to a image data string in the format specified as a
   format string supported by dot.
   """
   dotIn, dotOut = os.popen2('dot -T' + format)
   dotIn.write( pert2dot(p) )
   dotIn.close()
   graphImage = dotOut.read()
   dotOut.close()
   return graphImage

def pert2dot(pert):
   """
   Graph to txt dot format

   returns: string with text of dot language to draw the graph
   """
   txt = """digraph G {
            rankdir=LR;
            """
   for node in pert.successors:
      txt += str(node) + ';'
   txt += '\n'
   
   for act,sig in pert.successors.iteritems():
      for s in sig:
         txt += str(act) + '->' + str(s)
         txt += ' [label="' + pert.arcs[(act,s)][0][0] + '"'
         if pert.arcs[(act,s)][0][1]=='True':
            txt += ',style=dashed'
         txt += '];\n'
   txt += '}\n'
   return txt

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
    g=dibujarGrafo()
    image=graph2image(g.successors)
    window.images.append(image)

    p=dibujarPert()
    image1=pert2image(p)
    window.images.append(image1)

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

    window.main()

