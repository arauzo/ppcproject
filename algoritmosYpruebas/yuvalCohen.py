import copy
import claseGrafo
import graph1

def yuvalCohen(prelaciones):
    ###dadas las relaciones averiguo la lista de actividades predecesoras
    ###para cada actividad e imprimo la tabla
    LIPA=[] 
    for label in prelaciones:
        relation=[]
        activity=[]
        prececent=[]
        activity.append(label)
        precedent=prelaciones[label]
        relation.append(activity)
        relation.append(precedent)
        LIPA.append(relation)
    """PASO1(LIPA)
    for i in LIPA:
        i"""

    ###unica combinacion de actividades inmediatas predecesoras e
    ###imprimo la tabla
    UCIP=copy.deepcopy(LIPA)
    for i in UCIP:
        a=i[1]
        if a!=['-']:
            for j in UCIP:
                if a == j[1] and i!=j:
                    j[1]=['-']    
    """PASO2(UCIP)"
    for i in UCIP:
        i"""

    ###Numero de nodo de comienzo de cada actividad(starting Node)
    ###e imprimo la tabla                
    SN=copy.deepcopy(LIPA)
    cont=0
    l=[]
    for i in LIPA:
        if i[1] not in l:
            for j in SN:
                if i[1]==j[1]:
                    l.append(j[1])
                    j[1]=[cont]
            cont=cont+1

    """PASO2(SN)"
    for i in SN:
        i"""

    ###Dummy activities. Averiguo las actvidades que son ficticias e
    ###imprimo la tabla
    DA=copy.deepcopy(UCIP) 
    
    #Mete en una lista todas las activity precedentes menos los -
    a=[]
    for i in UCIP:
        for j in i[1]:
            if j!='-':
                a.append(j)
    #Mete en una lista los que salen mas de 1 vez
    b=[]
    for i in a:
        if a.count(i)>1:
            if i not in b:
                b.append(i)
    #Mete en una lista las precedentes en las que aparecen las de la lista anterior
    c=[]
    for i in UCIP:
        for j in b:
            if j in i[1] and len(i[1])>1 and i[1] not in c:
                c.append(i[1])    
    #nombra las actividades dummy(paso3) y rellena las nuevas filas(paso4)
    l1=[]
    l2=[]
    l=[]
    e=[]
    cont=1
    for i in c:
        d=[]
        for j in i:
            if j in b:
                cont=cont+1
                l1=[]
                l2=[]
                l2.append(j)
                j='ficticia '+j*cont
                l1.append(j)
                d.append(j)
                relation=[]
                relation.append(l1)
                relation.append(l2)
                l.append(relation)
            else:
                d.append(j)
        e.append(d) 
    #Rellena DA
    for i in DA:
        if i[1] in c:
             t=c.index(i[1])
             i[1]=e[t]

    """PASO3(DA)"
    for i in DA:
        i"""

    ###modifico LIPA para anadir las nuevas filas con las imaginarias y las
    ###precedentes ya modificadas e imprimo la tabla
    LIPA1=copy.deepcopy(LIPA)
    for i in LIPA1:
        if i[1] in c:
            t=c.index(i[1])
            i[1]=e[t]
    for i in l:
        LIPA1.append(i)
    """PASO4(LIPA1)"
    for i in LIPA1:
        i"""

    
    ###Asociar actividades con sus nodos finales

    #Starting Node ya lo tengo   SN

    #Succeeding Activities
    SA=[]
    for i in LIPA1:
        l1=[]
        l2=[]
        relation=[]
        cont=0
        l1=i[0]
        for j in LIPA1:
            if i[0][0] in j[1]:
                l2.append(j[0][0])
                cont=cont+1
        if cont==0:
            l2.append('End')
        relation.append(l1)
        relation.append(l2)
        SA.append(relation)
    #Successors Star Node
    SSN=copy.deepcopy(SA)
    #Veo cual es el ultimo comienzo de nodo
    b=-1
    for i in SN:
        a=i[1][0]
        if a>b:
            b=a

    #Ahora coloco los star node de los sucesores poniendo cuando solo hay
    #ficticias a partir del ultimo nodo y me falta por poner cuando sean
    #'End' el ultimo nodo
    for i in SSN:
        cont=0
        for j in i[1]:
            if len(j)==1:
                a=j
                cont=cont+1
        if cont==0:
            b=b+1
            i[1]=[b]
        else:
            for j in SN:
                if j[0][0]==a:
                    i[1]=j[1]

    """PASO5(SA)"
    for i in SA:
        i
    "PASO5(SSN)"
    for i in SSN:
        i"""

    
    ###Asocia actividades ficticias con sus nodos iniciales
    #todas las actividades sucesoras
    a=[]
    for i in SA:
        for j in i[1]:
                a.append(j)

    #sucesoras que se repiten
    b=[]
    for i in a:
        if a.count(i)>1:
            if i not in b:
                b.append(i)

    #las actividades predecesoras de los sucesores que se repiten
    c={}
    for i in b:
        d=[]
        for j in SA:
            if i in j[1]:
                d.append(j[0][0])
        c[i]=d
         
    ##### new ficticias
    ND=[]
    for i in b:
        f=[]
        g=[]
        t=c[i]
        for j in SN:
            if j[0][0] in t:
                f.append(j[1][0])
                f.append(j[0][0])
        cont1=-1
        g=[]
        for j in f:
            cont1=cont1+1
            if f.count(j)>1:
                k=cont1+1
                g.append(f[k])
        if g != []:        
            ND.append(g)

    ####en ND tengo una lista de listas de las cuales tengo que elegir las imaginarias

    rf=[]
    for i in ND:
        ne=len(i)
        cont1=0
        for j in i:
            
            cont1=cont1+1
            if ne > cont1:
                    cont=cont+1
                    r=[]
                    l1=[]
                    l2=[]
                    im='ficticia '+j*cont
                    l2.append(j)
                    l1.append(im)
                    r.append(l1)
                    r.append(l2)
                    rf.append(r)
            ###rf tiene la nueva fila para lIPA1
    LIPA2=copy.deepcopy(LIPA1)
    #con esto obtengo la actividad real y la imaginaria y cambio las actividades
    #precedentes la real por la imaginaria
    for i in rf:
        real=i[1][0]
        imaginario=i[0][0]
        for j in LIPA2:
            if real in j[1]:
                j[1].remove(real)
                j[1].append(imaginario)

    
    for i in rf:
        LIPA2.append(i)

    #ya supuestamente tengo todas las ficticias y todo actualizado en LIPA2

    """PASO6(LIPA2)"
    for i in LIPA2:
        i"""

    ####startin node final
    SNF=copy.deepcopy(LIPA2) #como hacer para que copie pero no modifique
    
    cont=0
    l=[]
    for i in LIPA2:
        if i[1] not in l:
            for j in SNF:
                if i[1]==j[1]:
                    l.append(j[1])
                    j[1]=[cont]
            cont=cont+1
    ###Para saber cual es el SNF mas grande
    maximo=0
    for i in SNF:
        a=i[1][0]
        if a > maximo:
            maximo=a
        
    ###succeding star node
    SA1=[]
    for i in LIPA2:
        l1=[]
        l2=[]
        relation=[]
        cont=0
        l1=i[0]
        for j in LIPA2:
            if i[0][0] in j[1]:
                l2.append(j[0][0])
                cont=cont+1
        if cont==0:
            l2.append(maximo+1)
        relation.append(l1)
        relation.append(l2)
        SA1.append(relation)

    SSNF=copy.deepcopy(SA1)
    for i in SSNF:
        for j in SNF:
            if j[0][0] in i[1]:
                i[1]=j[1]

    ###return LIPA,UCIP,SN,DA, LIPA1, SA, SSN, ND, LIPA2, SNF, SSNF

    ###creo que ya solo falta nombrar las actividades con los nodos iniciales y
    ###finales y la lista de predecesoras

    ###rellenar grafo

    grafo=claseGrafo.Grafo()

    ###la(lista de arcos) contendra la actividad, y su nodo de comienzo y el de final
    la=copy.deepcopy(SNF)
    cont=0
    for i in SSNF:
        la[cont].append(i[1])
        cont=cont+1

    for i in la:
        tup=i[1][0],i[2][0]
        cad=i[0][0]
        tamanyo=len(i[0][0])
        if cad[:8]=='ficticia':
            label=cad,True
        else:
            label=cad,False
        grafo.addArc(tup,label)

    return grafo


window = None

if __name__ == "__main__":

    window = graph1.Test() 

    gg=yuvalCohen(graph1.prelaciones4)
    image1=graph1.pert2image(gg)

    window.images.append(image1)
    graph1.gtk.main()
