class Grafo(object):

    def __init__(self):
        # Se mantienen las listas de sucesores y predecesores aunque son redundantes para acelerar el acceso
        self.successors = {}
        self.predecessors = {}
        self.arcs = {}
        
    def suc(self, node):
        return self.successors[node]

    def pre(self, node):
        return self.predecessors[node]
        
    def addNode(self, node):
        self.successors[node] = []
        self.predecessors[node] = []
        
    def addArc(self, arc, label=None):
        """
        Insertar arco en el grafo si los nodos no existen los crea
        
        arc = (origen, destino)
        label = etiqueta asociada al arco
        """
        a, c = arc
        if a not in self.successors:
            self.addNode(a)
        if c not in self.successors:
            self.addNode(c)
        if c not in self.successors[a]:
            self.successors[a].append(c)
        if a not in self.predecessors[c]:
            self.predecessors[c].append(a)
        self.arcs[(a,c)] = label 
        
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

    def removeArc(self, arc):
        i,j = arc
        self.successors[i].remove(j)
        self.predecessors[j].remove(i)
        del self.arcs[arc]

    def numNodes(self):
        return len(self.successors)

    def numArcs(self):
        return len(self.arcs)

    def numArcsReales(self):
        cont=0
        for (i,j) in self.arcs:
            if self.arcs[(i,j)][1]==False:
                cont = cont+1
        return cont

    def numArcsFicticios(self):
        cont=0
        for (i,j) in self.arcs:
            if self.arcs[(i,j)][1]==True:
                cont = cont+1
        return cont
        
