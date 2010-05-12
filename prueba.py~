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
import YCE

def dibujarGrafo():
    prelaciones = {
        'A' : [],
        'B' : [],
        'C' : [],
        'D' : [],
        'E' : [],
        'F' : ['A'],
        'G' : ['A'],
        'H' : ['B'],
        'I' : ['E'],
        'J' : ['C','D','I'],
        'K' : ['H'],
        'L' : ['F','H'],
        'M' : ['G','H'],
        'N' : ['G','K'],
        'O' : ['J','L','M','N'],
    }
    print prelaciones

    prelaciones = {}
    prelaciones['A']=[]
#    prelaciones['A'].append('None')
    prelaciones['B']=[]
#    prelaciones['B'].append('None')
    prelaciones['C']=[]
#    prelaciones['C'].append('None')
    prelaciones['D']=[]
#    prelaciones['D'].append('None')
    prelaciones['E']=[]
#    prelaciones['E'].append('None')
    prelaciones['F']=[]
    prelaciones['F'].append('A')
    prelaciones['G']=[]
    prelaciones['G'].append('A')
    prelaciones['H']=[]
    prelaciones['H'].append('B')
    prelaciones['I']=[]
    prelaciones['I'].append('E')
    prelaciones['J']=[]
    prelaciones['J'].append('C')
    prelaciones['J'].append('D')
    prelaciones['J'].append('I')
    prelaciones['K']=[]
    prelaciones['K'].append('H')
    prelaciones['L']=[]
    prelaciones['L'].append('F')
    prelaciones['L'].append('H')
    prelaciones['M']=[]
    prelaciones['M'].append('G')
    prelaciones['M'].append('H')
    prelaciones['N']=[]
    prelaciones['N'].append('G')
    prelaciones['N'].append('K')
    prelaciones['O']=[]
    prelaciones['O'].append('J')
    prelaciones['O'].append('L')
    prelaciones['O'].append('M')
    prelaciones['O'].append('N')
    print prelaciones

    prelaciones1 = {}
    prelaciones1['A']=[]
    prelaciones1['A'].append('None')
    prelaciones1['B']=[]
    prelaciones1['B'].append('A')
    prelaciones1['C']=[]
    prelaciones1['C'].append('A')
    prelaciones1['D']=[]
    prelaciones1['D'].append('A')
    prelaciones1['E']=[]
    prelaciones1['E'].append('B')
    prelaciones1['F']=[]
    prelaciones1['F'].append('B')
    prelaciones1['F'].append('C')
    prelaciones1['G']=[]
    prelaciones1['G'].append('C')
    prelaciones1['H']=[]
    prelaciones1['H'].append('D')
    prelaciones1['I']=[]
    prelaciones1['I'].append('H')
    prelaciones1['J']=[]
    prelaciones1['J'].append('F')
    prelaciones1['J'].append('G')
    prelaciones1['J'].append('H')
    prelaciones1['K']=[]
    prelaciones1['K'].append('E')
    prelaciones1['K'].append('J')
    prelaciones1['K'].append('I')
    
    
    g=YCE.yuvalCohen(prelaciones)
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
    prelaciones = {}
    prelaciones['A']=[]
    prelaciones['A'].append('None')
    prelaciones['B']=[]
    prelaciones['B'].append('None')
    prelaciones['C']=[]
    prelaciones['C'].append('None')
    prelaciones['D']=[]
    prelaciones['D'].append('None')
    prelaciones['E']=[]
    prelaciones['E'].append('None')
    prelaciones['F']=[]
    prelaciones['F'].append('A')
    prelaciones['G']=[]
    prelaciones['G'].append('A')
    prelaciones['H']=[]
    prelaciones['H'].append('B')
    prelaciones['I']=[]
    prelaciones['I'].append('E')
    prelaciones['J']=[]
    prelaciones['J'].append('C')
    prelaciones['J'].append('D')
    prelaciones['J'].append('I')
    prelaciones['K']=[]
    prelaciones['K'].append('H')
    prelaciones['L']=[]
    prelaciones['L'].append('F')
    prelaciones['L'].append('H')
    prelaciones['M']=[]
    prelaciones['M'].append('G')
    prelaciones['M'].append('H')
    prelaciones['N']=[]
    prelaciones['N'].append('G')
    prelaciones['N'].append('K')
    prelaciones['O']=[]
    prelaciones['O'].append('J')
    prelaciones['O'].append('L')
    prelaciones['O'].append('M')
    prelaciones['O'].append('N')

    prelaciones1 = {}
    prelaciones1['A']=[]
    prelaciones1['A'].append('None')
    prelaciones1['B']=[]
    prelaciones1['B'].append('A')
    prelaciones1['C']=[]
    prelaciones1['C'].append('A')
    prelaciones1['D']=[]
    prelaciones1['D'].append('A')
    prelaciones1['E']=[]
    prelaciones1['E'].append('B')
    prelaciones1['F']=[]
    prelaciones1['F'].append('B')
    prelaciones1['F'].append('C')
    prelaciones1['G']=[]
    prelaciones1['G'].append('C')
    prelaciones1['H']=[]
    prelaciones1['H'].append('D')
    prelaciones1['I']=[]
    prelaciones1['I'].append('H')
    prelaciones1['J']=[]
    prelaciones1['J'].append('F')
    prelaciones1['J'].append('G')
    prelaciones1['J'].append('H')
    prelaciones1['K']=[]
    prelaciones1['K'].append('E')
    prelaciones1['K'].append('J')
    prelaciones1['K'].append('I')
    p=YCE.yuvalCohen(prelaciones)
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

