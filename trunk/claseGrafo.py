class Grafo:

    def __init__(self):
        self.successors = {}
        self.predecessors = {}
        self.arcs = {}
        
    def suc(self,nodo):
        successors = self.successors[nodo]
        return successors

    def pre(self,nodo):
        predecessors=self.predecessors[nodo]
        return predecessors
        
    def addNode(self,nodo):
        self.successors[nodo] = []
        self.predecessors[nodo] = []
        
    def addArc(self,arc,label):
        a,c=arc
        if a not in self.successors:
            self.addNode(a)
        if c not in self.successors:
            self.addNode(c)
        self.successors[a].append(c)
        self.predecessors[c].append(a)
        self.arcs[(a,c)]= [label] # Una lista de etiquetas??? Es un error o tiene algun motivo?
        
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
