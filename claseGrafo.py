"""
Directed graph data type using dictionaries (hash tables) to connect nodes and arc labels
"""

class Grafo(object):

    def __init__(self):
        """
        Se mantienen las listas de sucesores y predecesores aunque son redundantes 
        para acelerar el acceso
        /successors/ contiene los sucesores de un nodo dado
        /predecessors/ contiene los predecesores de un nodo dado
        /arcs/ contiene todos los arcos del grafo asi como si es real o ficticia 
        y el nombre del arco
        """
        self.successors = {}   #XXX previous?
        self.predecessors = {} #XXX next? followers?
        self.arcs = {}
        
    def suc(self, node):
        """
        Returns successors of node
        """
        # Rename to prev (previous)? XXX
        # It is faster to access directly to instance var dict. Remove this method? XXX
        return self.successors[node]

    def pre(self, node):
        """
        Returns predecesors of node
        """
        # XXX idem as suc
        return self.predecessors[node]
        
    def addNode(self, node):
        """
        Add an unconnected node to graph
        """
        self.successors[node] = []
        self.predecessors[node] = []
        
    def addArc(self, arc, label=None):
        """
        Insert an arc in the graph. If origin, destination nodes are not present in graph they get created.

        arc = (origin node, destination)
        label = label to be linked with arc (maybe None if unlabeled)
        """
        origin, destination = arc
        if origin not in self.successors:
            self.addNode(origin)
        if destination not in self.successors:
            self.addNode(destination)
        if destination not in self.successors[origin]:
            self.successors[origin].append(destination)
        if origin not in self.predecessors[destination]:
            self.predecessors[destination].append(origin)
        self.arcs[(origin, destination)] = label 
        
    def removeNode(self,node):
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

        listaBorrar=[]
        for (i,j) in self.arcs:
            if i==nodo:
                listaBorrar.append((i,j))
            if j==nodo:
                listaBorrar.append((i,j))
        for i,j in listaBorrar:
            del self.arcs[(i,j)]

    def removeArc(self, arc):
        """
        Metodo que borra un arco del grafo
        arc = (actividad origen, actividad destino)
        del grafo
        """

        i,j = arc
        self.successors[i].remove(j)
        self.predecessors[j].remove(i)
        return self.arcs.pop(arc)

    def numNodes(self):
        """
        Return the number of nodes in graph
        """
        return len(self.successors)

    def numArcs(self):
        """
        Return the number of arcs in graph
        """
        return len(self.arcs)

    def numArcsReales(self):
        """
        Metodo que devuelve el numero de arcos reales que conforman el grafo
        """
        # XXX Fuera de tipo dato grafo es concreto de grafos PERT
        cont=0
        for (i,j) in self.arcs:
            if self.arcs[(i,j)][1]==False:
                cont = cont+1
        return cont

    def numArcsFicticios(self):
        """
        Metodo que devuelve el numero de arcos ficticios que conforman el grafo
        """
        # XXX Fuera de tipo dato grafo es concreto de grafos PERT
        cont=0
        for (i,j) in self.arcs:
            if self.arcs[(i,j)][1]==True:
                cont = cont+1
        return cont

