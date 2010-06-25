import copy
import sys
import claseGrafo

def algoritmoN(prelaciones):
    ###Dada la tabla de predecesores saco los nodos iniciales que
    ###compondran el grafo (predecesores) y los introduzco en NI

    NI=[]
    for label in prelaciones:
        if prelaciones[label]==[]:
            a=['-']
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
                NI.append(d)

    ###Anado el nodo final
    d=['1']
    NI.append(d)
    

    ###para anadir las actividades ficiticias en el grafo
    ###cojo los nodos y veo si alguno esta compuesto por otro nodo, si es asi
    ###trazo arco ficticio
    gg=claseGrafo.Grafo()
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
                        l=l+k[0]
                    for k in j:
                        l1=l1+k[0]
                    arco=l,l1
                    arco
                    
                    gg.addArc(arco,label)
                elif t==w:
                    for k in i:
                        l=l+k[0]
                    for k in j:
                        l1=l1+k[0]
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
            l1='0'
        else:
            for j in prelaciones[i]:     ###como prec siempre va a ser nodo los desmiembro para ponerlo en una cadena
                l1=l1+j
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
            cad=cad+j
        arco=cad,'1'
        hecho=0
        for j in gg.arcs:
            if arco==j:
                arco1=cad,i
                arco2=i,'1'
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


   