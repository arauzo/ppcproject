#!/usr/bin/env python

# PERT graph generation
#-----------------------------------------------------------------------
# PPC-PROJECT
#   Multiplatform software tool for education and research in
#   project management
#
# Copyright 2007-8 Universidad de Cordoba
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

import sys
import graph

class Pert(graph.DirectedGraph):
    """
    PERT class to store pert graph data
      arc labels store: (ActivityLabel, DummyActivity)

    DummyActivity: True if dummy, False if real
    """
    def __init__(self, pert=None):
        super(Pert, self).__init__()
        self.construct = self.sharma1998ext
        if pert != None:
            self.successors, self.arcs = pert
            self.predecesors = graph.reversedGraph(self.successors)

    def __repr__(self):
        return 'Pert( (' + str(self.successors) + ',' + str(self.arcs) + ') )'

    def __str__(self):
        rstr = str(self.successors) + '\n'
        for link, act in self.arcs.iteritems():
            rstr += str(link) + ' ' + str(act) + '\n'
        return rstr

    def numArcsReales(self):
        """
        Metodo que devuelve el numero de arcos reales que conforman el grafo
        """
        cont=0
        for (i,j) in self.arcs:
            if self.arcs[(i,j)][1] == False:
                cont = cont+1
        return cont

    def numArcsFicticios(self):
        """
        Metodo que devuelve el numero de arcos ficticios que conforman el grafo
        """
        cont=0
        for (i,j) in self.arcs:
            if self.arcs[(i,j)][1]==True:
                cont = cont+1
        return cont

    def nextNodeNumber(self):
        """
        New node number max(graph)+1 O(n)
          O(1): len(directed graph)+1 must be an available node number
          (i.e. graph nodes must be numbered starting in 0 or 1 at most)
          Valid if nodes are not deleted (or reasigned when deleted
          O(n))
        """
        if self.successors:
            return max(self.successors)+1
        else:
            return 0

    def addActivity(self, activityName, origin=None, destination=None, dummy=False):
        """
        Adds activity with new nodes or the specified ones
        """
        if origin == None:
            origin = self.nextNodeNumber()
            self.addNode(origin)
        if destination == None:
            destination = self.nextNodeNumber()
            self.addNode(destination)
            
        self.addArc( (origin, destination), (activityName, dummy) )
        return (origin, destination)

    def activityArc(self, activityName):
        """
        Given an activity name returns the arc which represents it on graph
        """
        for arc, act in self.arcs.iteritems():
            if act[0] == activityName:
                return arc
        return None


    def inActivities(self, node):
        """
        Return the name of activities directly preceding node
        """
        inAct = []
        for inNode in self.pre(node):
            act, dummy = self.arcs[ (inNode, node) ]
            if not dummy:
                inAct.append(act)

        return inAct

    def inActivitiesR(self, node):
        """
        Return the name of activities preceding node (directly or throgh
        dummies)
        """
        inAct = []
        for inNode in self.pre(node):
            act, dummy = self.arcs[ (inNode, node) ]
            if dummy:
                inAct += self.inActivitiesR(inNode)
            else:
                inAct.append(act)

        return inAct

    def outActivities(self, node):
        """
        Return the name of activities directly following node
        """
        outAct = []
        for outNode in self.successors[node]:
            act, dummy = self.arcs[ (node, outNode) ]
            if not dummy:
                outAct.append(act)

        return outAct

    def outActivitiesR(self, node):
        """
        Return the name of activities following node (directly or throgh
        dummies)
        """
        outAct = []
        for outNode in self.successors[node]:
            act, dummy = self.arcs[ (node, outNode) ]
            if dummy:
                outAct += self.outActivitiesR(outNode)
            else:
                outAct.append(act)

        return outAct


    def pertSuccessors(self):
        """
        Extracts all implicit prelations (not redundant)
        """
        successors = {}
        for node, connections in self.successors.items():
            inputs  = self.inActivities(node)
            outputs = self.outActivitiesR(node)
            for i in inputs:
                if i in successors:
                    successors[i] += outputs
                else:
                    successors[i] = outputs
        return successors

    def sharma1998ext(self, successors):
        """
        Generates a AOA graph (PERT) from successors table
        Algorithm sharma1998 extended
        returns: PERT graph data structure
        """
        if self.successors or self.arcs:
            raise Exception('PERT structure must be empty')

        #XXX Habria que renombrar pre y suc por in y out en DirectedGraph
        precedents = graph.reversedGraph(successors)  

        # Close the graph (not in sharma1998)
        origin = self.nextNodeNumber()
        self.addNode(origin)
        dest = self.nextNodeNumber()
        self.addNode(dest)
        begin_act     = graph.beginingActivities(successors)
        end_act       = graph.endingActivities(successors)
        begin_end_act = begin_act.intersection(end_act)

        #  -Creates a common node for starting activities
        for act in begin_act - begin_end_act:
            self.addActivity(act, origin)

        #  -Creates a common node for ending activities
        for act in end_act - begin_end_act:
            self.addActivity(act, origin=None, destination=dest)

        #  -Deals with begin-end activities
        if begin_end_act:
            act = begin_end_act.pop()
            self.addActivity(act, origin, dest)
            for act in begin_end_act:
                o, d = self.addActivity(act, origin)
                self.addActivity("seDummy", d, dest, dummy=True)

        # Sharma1998 algorithm
        for act in successors:
            #print "Processing", act, self
            #window.images.append( graph.pert2image(self) )
            if not self.activityArc(act):
                self.addActivity(act)
                #window.images.append( graph.pert2image(self) )
            a_origin, a_dest = self.activityArc(act)
            #print '(', a_origin, a_dest, ')'
            for pre in precedents[act]:
                #print self.successors
                #print pre, pre in self.inActivitiesR(graph.reversedGraph(self.successors), a_origin)
                if pre not in self.inActivitiesR(a_origin):
                    if not self.activityArc(pre):
                        self.addActivity(pre)
                        #window.images.append( graph.pert2image(self) )
                    self.makePrelation(pre, act)
                    a_origin, a_dest = self.activityArc(act)


    def equivalentRemovingDummy(self, dummy):
        """
        Idea of Lemma1 of Sharma1998 modified

        dummy given as (origin, destination)
        """
        nodeO, nodeD = dummy

        # Stop being a graph?
        inNodesO  = self.pre(nodeO)
        inNodesD = self.pre(nodeD)
        for n in inNodesO:
            if n in inNodesD:
                return False # Two activities would begin and end in the same nodes
        outNodesO  = self.successors[nodeO]
        outNodesD = self.successors[nodeD]
        for n in outNodesO:
            if n in outNodesD:
                return False # Two activities would begin and end in the same nodes

        # Implies new prelations?
        inO  = set( self.inActivitiesR(nodeO) )
        inD  = set( self.inActivitiesR(nodeD) )
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
        self.successors[nodeO].remove(nodeD)
        self.predecessors[nodeD].remove(nodeO)

        inD = self.predecessors.pop(nodeD)
        outD = self.successors.pop(nodeD)

        for node in inD:
            self.successors[node].remove(nodeD)
            self.successors[node].append(nodeO)
        self.successors[nodeO] += outD

        for node in outD:
            self.predecessors[node].remove(nodeD)
            self.predecessors[node].append(nodeO)
        self.predecessors[nodeO] += inD
            
        # Activities table
        self.arcs.pop( (nodeO, nodeD) )
        for node in inD:
            act = self.arcs.pop( (node, nodeD) )
            self.arcs[ (node, nodeO) ] = act
        for node in outD:
            act = self.arcs.pop( (nodeD, node) )
            self.arcs[ (nodeO, node) ] = act


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
        self.addNode(newO)
        newD = self.nextNodeNumber()
        self.addNode(newD)

        # Moved activities
        pre_act = self.removeArc(pre)
        fol_act = self.removeArc(fol)
        self.addArc( (preO, newO), pre_act )
        self.addArc( (newD, folD), fol_act )         

        # New dummies
        dummy1 = (folO, newD)
        dummy2 = (newO, preD)
        dummy3 = (newO, newD)
        self.addArc( dummy1, ('dummy', True) )
        self.addArc( dummy3, ('dummy', True) )
        self.addArc( dummy2, ('dummy', True) ) 

        #window.images.append( graph.pert2image(self) )

        # Remove dummy activities if possible
        if self.equivalentRemovingDummy(dummy2):
            #print dummy2, ':equivalent'
            self.removeDummy(dummy2)
            #window.images.append( graph.pert2image(self) )

        if self.equivalentRemovingDummy(dummy1):
            #print dummy1, ':equivalent'
            self.removeDummy(dummy1)
            #window.images.append( graph.pert2image(self) )
            dummy3 = (newO, folO)   # Changed by removing dummy1

        if self.equivalentRemovingDummy(dummy3):
            #print dummy3, ':equivalent'
            self.removeDummy(dummy3)
            #window.images.append( graph.pert2image(self) )

    def demoucron(self):
        """
         Divide un grafo PERT en niveles usando el algoritmo de Demoucron
         Return: lista de listas de nodos representando los niveles de inicio a fin
        """
        nodos = self.successors.keys()

        # v inicial, se obtiene un diccionario con la suma de '1' de cada nodo
        v = {}       
        for n in nodos:
            v[n] = 0
            for m in nodos:
                if (n, m) in self.arcs:
                    v[n] += 1

        num = 0
        niveles = []
        # Mientras haya un nodo no marcado
        while [e for e in v if v[e] != 'x']:
            # Se establecen los nodos del nivel
            niveles.append([])
            for i in v:
                if v[i] == 0:
                    v[i] = 'x'
                    niveles[num].append(i)

            # Actualiza v quitando el nivel procesado
            for m in v:
                if v[m] != 'x':
                    for a in niveles[num]:
                        if (m, a) in self.arcs:
                            v[m] -= 1
            num += 1

        niveles.reverse()
        return niveles
         
           
    def renumerar(self):
        """
         Renumera un grafo Pert para que sus nodos vayan desde 1 a N, donde N
         es el numero total de nodos. Cumple que un nodo anterior a otro siempre
         tenga un numero menor.
         Valor de retorno: nuevoGrafo (grafo renumerardo)
        """
        niveles = self.demoucron()
        # Se crea un diccionario con la equivalencia entre los nodos originales y los nuevos
        s = 1
        nuevosNodos = {}
        for m in range(len(niveles)):
            if len(niveles[m]) == 1:
                nuevosNodos[niveles[m][0]] = s
                s += 1
            else:
                for a in niveles[m]:
                    nuevosNodos[a] = s            
                    s += 1

        # Se crea un nuevo grafo
        nuevoGrafo = Pert()
        
        # New graph
#        for n in self.successors:
#            #print n, 'n'
#            for m in nuevosNodos:            
#                #print  m, 'm'
#                if n == m:
#                    if self.successors[n] != []:
#                        for i in range(len(self.successors[n])):
#                            for a in nuevosNodos:
#                                if self.successors[n][i] == a:
#                                    if i == 0:

#                                        nuevoGrafo.successors[nuevosNodos[m]] = [nuevosNodos[a]]
#                                    else:                                   
#                                        nuevoGrafo.successors[nuevosNodos[m]].append(nuevosNodos[a])
#                    else:
#                        nuevoGrafo.addNode(nuevosNodos[m]) 

        # New activities'
        for n in self.arcs:
            for m in nuevosNodos:            
                if n[0] == m:
                    for a in nuevosNodos:
                        if n[1] == a:
                            nuevoGrafo.addArc( (nuevosNodos[m], nuevosNodos[a]), self.arcs[n] )

                elif n[1] == m:
                    for a in nuevosNodos:
                        if n[0] == a:
                            nuevoGrafo.addArc( (nuevosNodos[a], nuevosNodos[m]), self.arcs[n] )

        return nuevoGrafo



#
# --- GTK para probar imagen del grafo
#
import pygtk
pygtk.require('2.0')
import gtk


def main(window):
    """
    Test code
    """
    import traceback
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
    
    


##   print graph.reversedGraph(pert2[0])
##   for n in range(1,6):
##      print inActivitiesR(pert2, graph.reversedGraph(pert2[0]), n)
##   print "OUT"
##   for n in range(1,6):
##      print outActivitiesR(pert2, n)

##   window.images.append( graph.pert2image(pert4) )
##   print equivalentRemovingDummy(pert4, (3,4) )
##   removeDummy(pert4, (3,4) )

##   pertP = pert5
##   window.images.append( graph.pert2image(pertP) )
##   makePrelation( pertP, (1,5), (3,4) )
##   addActivity( pertP, 'nueva' )
##   makePrelation( pertP, (1,2), (7,8) )
##   makePrelation( pertP, (9,8), (6,4) )
       
#    window.images.append( graph.pert2image(pert.Pert(pert4)) )

#    window.images.append( graph2image(successors2) )
#    window.images.append( graph2image(successors3) )
    try:
        pertP = Pert()
        pertP.construct(successors2)
        window.images.append( graph.pert2image(pertP) )
        print pertP
    except Exception:
        traceback.print_exception(*sys.exc_info())

##   s = pertSuccessors(pertP)
##   window.images.append( graph2image( roy(s) ) )
    gtk.main()
    

# If the program is run directly    
if __name__ == "__main__":
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

    window = graph.Test()
    main(window)
