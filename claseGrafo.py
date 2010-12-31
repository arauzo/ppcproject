"""
Clase que almacenara toda la informacion concerniente a cualquier 
grafo implementado en la aplicacion
"""

class Grafo(object):

    def __init__(self):
        """
        Inicializador que contiene las variables de instancia de la clase Grafo
        Se mantienen las listas de sucesores y predecesores aunque son redundantes 
        para acelerar el acceso
        /successors/ contiene los sucesores de un nodo dado
        /predecessors/ contiene los predecesores de un nodo dado
        /arcs/ contiene todos los arcos del grafo asi como si es real o ficticia 
        y el nombre del arco
        """
        self.successors = {}
        self.predecessors = {}
        self.arcs = {}
        
    def suc(self, activity):
        """
        Metodo que devuelve las actividades sucesoras(lista) a una actividad dada
        activity = "Actividad"
        """

        return self.successors[activity]

    def pre(self, activity):
        """
        Metodo que devuelve las actividades predecesoras(lista) a una actividad dada
        activity = "Actividad"
        """

        return self.predecessors[activity]
        
    def addNode(self, activity):
        """
        Metodo que anade una actividad
        activity = "Actividad" 
        en las variables de instancia successors y predecessor
        """

        self.successors[activity] = []
        self.predecessors[activity] = []
        
    def addArc(self, arc, label=None):
        """
        Insertar arco en el grafo si los nodos no existen los crea
        arc = (actividad origen, actividad destino)
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
        
    def removeNode(self,activity):
        """
        Bora una Actividad
        activity="A"
        tiene que borrarlo en todas las variables de instancia de la clase
        """

        if activity in self.successors:
            del self.successors[activity]
        if activity in self.predecessors:
            del self.predecessors[activity]
        
        for i in self.successors:
            if activity in self.successors[i]:
                self.successors[i].remove(activity)
        for i in self.predecessors:
            if activity in self.predecessors[i]:
                self.predecessors[i].remove(activity)

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
        Metodo que devuelve el numero de nodos que conforman el grafo
        """

        return len(self.successors)

    def numArcs(self):
        """
        Metodo que devuelve el numero de arcos que conforman el grafo
        """

        return len(self.arcs)

    def numArcsReales(self):
        """
        Metodo que devuelve el numero de arcos reales que conforman el grafo
        """

        cont=0
        for (i,j) in self.arcs:
            if self.arcs[(i,j)][1]==False:
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
        
