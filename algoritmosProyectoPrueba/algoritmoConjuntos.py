prelaciones = {
    '3': [], 
    '2': [], 
    '5': ['3'], 
    '4': [], 
    '7': ['4'], 
    '6': ['5'], 
    '9': ['3'], 
    '8': ['7'], 
    '11': ['7'], 
    '10': ['2'], 
    '13': ['4', '6'], 
    '12': ['10'], 
    '15': ['3'], 
    '14': ['9'], 
    '17': ['5'], 
    '16': ['6'], 
    '19': ['7'], 
    '18': ['6'], 
    '20': ['16'], 
    '21': ['11', '15', '17'], 
    '22': ['10'], 
    '23': ['18'], 
    '24': ['12'],
    '25': ['13', '14', '19'], 
    '26': ['11', '17', '16'], 
    '27': ['26', '22', '8'], 
    '28': ['9'], 
    '29': ['24', '22', '17'],
    '30': ['25', '27', '28'],
    '31': ['20', '21', '23'],
}
prelaciones = {
    'B': [], 
    'A': [], 
    'D': ['B'], 
    'C': [], 
    'F': ['C'], 
    'E': ['D'], 
    'H': ['B'], 
    'G': ['F'], 
    'J': ['F'], 
    'I': ['A'], 
    'L': ['C', 'E'], 
    'K': ['I'], 
    'N': ['B'], 
    'M': ['H'], 
    'P': ['D'], 
    'O': ['E'], 
    'R': ['F'], 
    'Q': ['E'], 
    'S': ['O'], 
    'T': ['J', 'N', 'P'], 
    'U': ['I'], 
    'V': ['Q'], 
    'W': ['K'],
    'X': ['L', 'M', 'R'], 
    'Y': ['J', 'P', 'O'], 
    'Z': ['Y', 'U', 'G'], 
    'AB': ['H'], 
    'AC': ['W', 'U', 'P'],
    'AD': ['X', 'Z', 'AB'],
    'AE': ['S', 'T', 'V']
}

prelaciones = {
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


import copy
import sys
import claseGrafo

def algoritmoN(prelaciones):
    ###Dada la tabla de predecesores saco los nodos iniciales que
    ###compondran el grafo (predecesores) y los introduzco en NI

    NI=[]
    for label in prelaciones:
        if prelaciones[label]==[]:
            a=['start']
        else:
            a=prelaciones[label]
        if a not in NI:
            NI.append(a)

    ###Cojo los nodos en los que hay mas de una actividad(b)
    b=[]
    for i in NI:
        if len(i)>1:
            b.append(i)

    ###comparo cada nodo con todos los demas para ver si esta contenido en alguno
    ###alguno de ellos, si esta contenido lo borro de la lista(b)
    for i in b:
        e=set(i)
        for j in b:
            f=set(j)
            if f != e:
                g=f&e
                if g==e: 
                    b.remove(i)
                elif g==f:
                    b.remove(j)

    ###Descompongo(b) y voy introduciendo en una lista(c) y si se repite es que tengo que
    ###anadir ese ndo 
    c=[]
    for i in b:
        for j in i:
            if j not in c:
                c.append(j)
            else:
                d=[j]
                if d not in NI:
                    NI.append(d)

    ###Anado el nodo final
    d=['end']
    NI.append(d)



    ###para anadir las actividades ficiticias en el grafo
    ###cojo los nodos y veo si alguno esta compuesto por otro nodo, si es asi
    ###trazo arco ficticio
    gg=claseGrafo.Grafo()
    for i in NI:
        l=""
        for j in i:
            l=l+j+"-"
        l=l[:-1]
        gg.addNode(l)


    z=[]
    for i in NI:
        y=set(i)
        for j in NI:
            l=""
            l1=""
            w=set(j)
            if i!=j:
                t=y&w
                label='AA','True'
                if t==y:
                    for k in i:
                        l=l+k+"-"
                    for k in j:
                        l1=l1+k+"-"
                    l,l1
                    l=l[:-1]
                    l1=l1[:-1]
                    arco=l,l1
                    arco
                    
                    gg.addArc(arco,label)
                elif t==w:
                    for k in i:
                        l=l+k+"-"
                    for k in j:
                        l1=l1+k+"-"
                    l1,l
                    l=l[:-1]
                    l1=l1[:-1]
                    arco=l1,l
                    arco
                    gg.addArc(arco,label)
    ###Una vez anadidos todos los arcos veo que hay arcos que no deben estar
    ###(D a DEF ya que ya anado arco de D a DE y de DE a DEF). Los borro
    for i in gg.successors:
        a=gg.successors[i]
        for j in a:
            s=set(j)
            for k in a:
                if k!=j:
                    r=set(k)
                    t=s&r
                    if t==s:
                        arco=i,k
                        gg.removeArc(arco)
                    if t==r:
                        arco=i,j
                        gg.removeArc(arco)

    ###para anadir las actividades reales cojo prelaciones y anado arco desde
    ###prec a act. Si act no esta definida como nodo busco el nodo de menor tamano
    ###que la contenga y act pasa a ser dicho nodo.

    l=""
    for i in prelaciones:            
        infinity= sys.maxint -1        ###valor infinito para compara tamano en caso de que haga falta
        ll=[]
        ll.append(i)
        l=i
        l1=""
        if prelaciones[i] == []:
            l1='start'
        else:
            for j in prelaciones[i]:     ###como prec siempre va a ser nodo los desmiembro para ponerlo en una cadena
                l1=l1+j+"-"
            l1=l1[:-1]
        if ll in NI:                 ###si act es un nodo
            arco=l1,l                 ###arco es prec-->act
        else:                         ###si act no es nodo
            for j in gg.successors:
                if l in j:             ###busco nodo de menor tamano que contega a act
                    tam=len(j)
                    if tam<infinity:
                        infinity=tam
                        l=j
                        arco=l1,l
        label=i,'False'
        if arco not in gg.arcs:
            gg.addArc(arco,label)         ###trazo arco desde prec hasta act

    ### anado en una lista los nodos que no tienen sucesores porque es el nodo final
    ### o lo que es lo mismo los que no aparecen como actividades predecesoras de ninguna

    k=[]
    for i in prelaciones:
        enc=0
        for j in prelaciones:
            if i in prelaciones[j]:
                enc=1
        if enc==0:
            k.append(i)

    ###Para cada nodo que no tiene sucesores busco cual es su actividad precedente y trazo arco
    ###hacia el nodo final. si de un mismo nodo salen dos actividades hacia otro mismo nodo anado nodo 
    ###puente y actividad ficticia hasta dicho nodo

    for i in k:
        cad=""
        for j in prelaciones[i]:
            cad=cad+j+"-"
        cad=cad[:-1]
        arco=cad,'end'
        hecho=0
        for j in gg.arcs:
            if arco==j:
                arco1=cad,i
                arco2=i,'end'
                hecho=1
        if hecho==0:
            label=i,'False'
            gg.addArc(arco,label)
        else:
            label='AA','True'
            gg.addArc(arco1,label)
            label=i,'False'
            gg.addArc(arco2,label)
    return gg

