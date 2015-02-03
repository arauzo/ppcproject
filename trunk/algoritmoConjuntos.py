"""
Algoritmo basado en conjuntos para construir el grafo PERT
"""
import sys
import pert
import graph

def algoritmoN(prelations):
    """
    Built PERT graph with prelations
    Dadas las prelations construye el grafo PERT
    
    prelations = {'Activity': ['prelation1','prelation2'], ...}
    prelations = {'Act': ['Predecesora1','Predecesora2'], ... }
    
    Return pert.Pert
    Devuelve: un pert.Pert()
    """

    #Get nodes of graph from predecesors and add in Nodes
    # Dada la tabla de predecesores saco los nodos iniciales que
    # compondran el grafo (predecesores) y los introduzco en Nodes
    Nodes = [] #List of nodes
    for label in prelations:
        if prelations[label]==[]: 
            node = ['start']
        else:
            node = prelations[label]
        if node not in Nodes:
            Nodes.append(node)

    #Nodes with more than one activity
    # Cojo los nodos en los que hay mas de una actividad(b)
    more_than_one = [] #List of nodes with more than one activity
    for n in Nodes:
        if len(n)>1: #If node have more than one activity
            more_than_one.append(n) #add to more_than_one

    #Check every node with others, if it is included, it is delete from more_than_one
    # comparo cada nodo con todos los demas para ver si esta contenido en alguno
    # alguno de ellos, si esta contenido lo borro de la lista(b)
    for activities1 in more_than_one:
        set_1 = set(activities1)
        for activities2 in more_than_one:
            set_2 = set(activities2)
            if set_2 != set_1:
                set_intersection = set_2&set_1
                if set_intersection == set_1: 
                    more_than_one.remove(activities1)
                elif set_intersection == set_2:
                    more_than_one.remove(activities2)

    #Check if more_then_one have two equal activities, if check true, add node
    # Descompongo(b) y voy introduciendo en una lista(c) y si se repite es que tengo que
    # anadir ese ndo 
    node_list = []
    for activities in more_than_one:
        for activity in activities:
            if activity not in node_list:
                node_list.append(activity)
            else:
                aux_activity = [activity]
                if aux_activity not in Nodes:
                    Nodes.append(aux_activity)

    #Add end node
    # Anado el nodo final
    end_node = ['end']
    Nodes.append(end_node)

    #Add dummy Activities if node are included in other
    # para anadir las actividades ficiticias en el grafo
    # cojo los nodos y veo si alguno esta compuesto por otro nodo, si es asi
    # trazo arc ficticio
    gg = pert.Pert()
    for node in Nodes:
        label = ""
        for label1 in node: #l string join NO HACE STRING JOIN, NO SE SI SE PUEDE CAMBIAR POR STRING JOIN
            label = label + label1 + "-"
        label = label[:-1]
#        print "TEST", node 
#        print label
#        print '-'.join(node) # XXX Si hace lo mismo ?no?
        gg.add_node(label)
#    print "gg:", gg

    for node in Nodes:
        node_set = set(node)
        for node1 in Nodes:
            label = ""
            label1 = ""
            node_set1 = set(node1)
#            print "node:", node, "node1:", node1
            if node != node1: #NO TIENE SENTIDO hacemos que sean distintos
                t = node_set&node_set1 #guardamos su interseccion (si son distintos nunca tendran interseccion)
                aux_label = 'AA',True
                if t == node_set: #Comparamos la interseccion(vacia) con un conjunto de nodos
#                    print "OK"
                    built_labels(node, node1, label, label1)
#                    for k in node:
#                        l = l + k + "-"
#                    for k in j:
#                        l1 = l1 + k + "-"
#                    l,l1
#                    l = l[:-1]
#                    l1 = l1[:-1]
                    arc = label, label1
#                    arc
                    gg.add_arc(arc,aux_label)
                elif t == node_set1:
#                    print "OKOK"
                    built_labels(node, node1, label, label1)
#                    for k in node:
#                        l = l + k + "-"
#                    for k in j:
#                        l1 = l1 + k + "-"
#                    l = l[:-1]
#                    l1 = l1[:-1]
                    arc = label1, label
#                    arc
                    gg.add_arc(arc, aux_label)
                    
#    print "gg::", gg
    #Delete arcs in others that they are unnecessary
    #(D a DEF) because have arcs (D a DE) and (DE a DEF)
    # Una vez anadidos todos los arcs veo que hay arcs que no deben estar
    # (D a DEF ya que ya anado arc de D a DE y de DE a DEF). Los borro
#    for suc1 in gg.successors:
#        print "suc1:", suc1
    for successor in gg.successors:
        suc = gg.successors[successor] #suc esta siempre vacio
        for s in suc:
            set_s = set(s)
            for s1 in suc:
                if s1 != s:
                    set_s1 = set(s1)
                    set_intersection = set_s&set_s1
                    if set_intersection == set_s:
                        arc = successor, s1
                        gg.remove_arc(arc)
                    if set_intersection == set_s1:
                        arc = successor, s
                        gg.remove_arc(arc)
#    print "gg:::", gg

    #For add real activities pass through prelations and add arcs from prec a act
    # para anadir las actividades reales cojo prelations y anado arc desde
    # prec a act. Si act no esta definida como nodo busco el nodo de menor tamano
    # que la contenga y act pasa a ser dicho nodo.

    label = ""
    for predecessor in prelations:
        infinity = sys.maxint -1 #infinite value for compare size if required valor infinito para compara tamano en caso de que haga falta
        list_predecessor = []
        list_predecessor.append(predecessor)
        label = predecessor
        label1=""
        if prelations[predecessor] == []:
            label1 = 'start'
        else:
            for j in prelations[predecessor]: #prec always node divide to put on string como prec siempre va a ser nodo los desmiembro para ponerlo en una cadena
                label1 = label1 + j + "-"
            label1 = label1[:-1]
        if list_predecessor in Nodes: #if sct is node si act es un nodo
            arc = label1,label #arc is prec-->act arc es prec-->act
        else: # si act no es nodo
#            for j in gg.successors:
#                if label in j:#search smaller in act busco nodo de menor tamano que contega a act
#                    tam = len(j)
#                    if tam < infinite:
#                        infinite = tam
#                        
#                        arc = label1,j
            aux_list=""
            aux_list1=""
            list_labels=[]
            for j in gg.successors:
                if label in j:
                    aux_list1=j+"-"
                    list_labels=[]
                    for k in aux_list1:
                        if k !="-":
                            aux_list=aux_list+k
                        else:
                            list_labels.append(aux_list)
                            aux_list=""
                    if list_predecessor[0] in list_labels:
                        arc=label1,j

#        print "gg.arcs:", gg.arcs
#        print "arc:", arc
        label = predecessor,False
        if arc not in gg.arcs:
            gg.add_arc(arc,label) #join arc from prec to act trazo arc desde prec hasta act
#    print "gg::::", gg
    #Add to end_list nodes that haven't successors
    #anado en una lista los nodos que no tienen sucesores porque es el nodo final
    #o lo que es lo mismo los que no aparecen como actividades predecesoras de ninguna

    end_list = []
    for pre in prelations:
        find = 0
        for pre1 in prelations:
            if pre in prelations[pre1]:
                find = 1
        if find == 0:
            end_list.append(pre)
#    print "gg:::::", gg
    #For each node that haven'y successors search his predeccessor activity and add an arc to final node
    #If two activities have same start and end if necessary to add dummy activity and intermediate node
    #Para cada nodo que no tiene sucesores busco cual es su actividad precedente y trazo arc
    #hacia el nodo final. si de un mismo nodo salen dos actividades hacia otro mismo nodo anado nodo 
    #puente y actividad ficticia hasta dicho nodo

    for node in end_list:
        aux_label = ""
        for pre in prelations[node]:
            aux_label = aux_label + pre + "-"
        aux_label = aux_label[:-1]
        if aux_label!="":
            arc = aux_label,'end'
        else:
            arc = 'start','end'
        ok = 0
        for aux_arc in gg.arcs:
            if arc == aux_arc:
                arc1 = aux_label, node
                arc2 = node, 'end'
                ok = 1
        if ok == 0:
            label = node, False
            gg.add_arc(arc,label)
        else:
            label = 'AA', True
            gg.add_arc(arc1,label)
            label = node, False
            gg.add_arc(arc2,label)
#    print "gg::::::", gg
    return gg


def built_labels(node, node1, label, label1):
    for n in node:
        label = label + n + "-"
    for n1 in node1:
        label1 = label1 + n1 + "-"
#    l,l1
    label = label[:-1]
    label1 = label1[:-1]

# Test algorithm
if __name__ == "__main__":
    import prueba

    filename = sys.argv[1]
    data = prueba.openProject(filename)
    prueba.check_activities(data)

    result_graph = prueba.test_algorithm(data, algoritmoN)

    # Draw graph on screen
    window = None
    window = graph.Test() 
    image1 = graph.pert2image(result_graph)
    window.images.append(image1)
    graph.gtk.main()
    

