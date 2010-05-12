import math, os, sys
import copy
import algoritmoLorenzoPrevio
import algoritmoLorenzoFinal
import claseGrafo
def al(prelaciones):
    
    matriz,premat=algoritmoLorenzoPrevio.matriz(prelaciones)
    m,t,af,ai,ami,amiD,amf,amfD=algoritmoLorenzoPrevio.previo(matriz)

    a=len(m)                        ###tamano de la matriz
    b=len(m)                        ###tamano de la matriz
    analizadas=[]                    ###lista que contiene las actividades que ya han sido analizadas                            ###actividad a analizar

    d={}                    
    for i in range(a):
        d[i]=[0,0]        


    ###cont indicara a un nodo, ejem. cont=3-->nodo 3
    ###incializao el diccionario para que contenga las actividades
    ###iniciales
    cont=1                    
    for i in ai:            
        cont=cont+1
        d[i]=[1,cont]
        analizadas.append(i)    

    d1=copy.deepcopy(d)                ###copia del diccionario para poder modificarlo en el for    
    X=0
    while len(analizadas)<b:
        posiciones=[]                ###lista que contiene las posiciones de las actividades siguientes a la actividad X
        ###si actividad X tiene nodo inicio y nodo fin
        if d1[X][0]>0 and d1[X][1]>0:    
            cont1=-1    ###contador auxiliar
            ### meto las actividades siguientes a X en la lista de posiciones
            for j in m[X]:
                cont1=cont1+1
                if j==1:
                    posiciones.append(cont1)
            ###voy analizando cada actividad siguiente a X
            for k in posiciones:
                ###si actividad 'k' no esta en la lista analizadas
                if k not in analizadas:
                    ###si actividad 'k' tiene un solo precedente(solo un 1 en su columna) 
                    if t[k].count(1)==1:
                        ###si actividad 'k' no es clave del diccionario amfD(no es actividad mismo fin)    
                        ###incremento en 1 contador
                        ###asigno actividad, actividad 'k' tiene como nodo inicio 
                        ###el nodo fin de actividad X y como nodo fin cont            
                        if k not in amfD:
                            cont=cont+1                
                            d1[k]=[d1[X][1],cont]    
                        ###si actividad 'k' es clave del diccionario amfD(es actividad mismo fin)                
                        else:
                            ###si nodo final de actividad 'k' es igual a 0
                            ###incremento en 1 contador
                            ###asigno actividad, actividad 'k' tiene como nodo inicio 
                            ###el nodo fin de actividad X y como nodo fin cont
                            if d1[k][1]==0:
                                cont=cont+1                
                                d1[k]=[d1[X][1],cont]    
                            ###si nodo final de actividad 'k' es distinto a 0
                            ###asigno como nodo inicio de actividad 'k' el nodo final de
                            ###actividad X
                            else:
                                d1[k][0]=d1[X][1]    ###4
                            ###recorro todas las actividades con mismo fin que actividad 'k'
                            ###y les asigno el mismo nodo fin que a actividad 'k' si su nodo
                            ###es igual 0
                            for l in amfD[k]:
                                if d1[l][1] == 0:
                                    d1[l][1]=cont
                        analizadas.append(k)    ###inserto actividad 'k' en analizadas
                    ###si actividad 'k' tiene mas de un precedente(mas de un 1 en su columna) 
                    elif t[k].count(1)>1:
                        mi=0            ###mi=0, no es actividad mismo inicio
                                        ###mi=1, es actividad mismo inicio
                        base=[]            ###base=actividades siguientes mismo inicio
                                        ###si no se da el caso base=actividad analizada 'k'
                        ###compruebo si en la lista de listas ami esta la actividad 'k'
                        ###si es asi pongo mi=1 y la lista de actividades mismo inicio que
                        ###que contiene a la actividad 'k' como base        
                        for l in ami:
                            if k in l and k not in analizadas:
                                mi=1
                                base=l
                        ###si mi=0, inserto la actividad que estamos analizando, 'k' 
                        if mi==0:
                            base.append(k)
                        pospre=[]    ###posicion de las actividades predecesores a una
                                    ###de la actividades de la base (como son mismo inicio 
                                    ###solo hace falta una)
                        ###recorro la columna de una de las actividades que conforme base
                        ###y donde haya un 1 es que es predecesora y por tanto inserto en pospre 
                        ###la posicion de dicha actividad predecesora, cont1 me indica la posicion
                        ###de dicha actividad predecesora.                 
                        cont1=-1
                        for n in t[base[0]]:
                            cont1=cont1+1
                            if n==1:
                                pospre.append(cont1)
                        ###si algunas de las actividades predecesoras no esta analizada entonces
                        ###paso a siguiente actividad en la lista posiciones                        
                        hacer=1
                        for n in pospre:
                            if n not in analizadas:
                                hacer=0
                        ###si hacer=1 entonces inserto en analizadas las actividades que conformen
                        ###la base
                        if hacer==1:
                            if mi==1:
                                for p in base:
                                    analizadas.append(p)
                            if mi==0:
                                analizadas.append(k)
                            verdadera=-1        ###verdadera=-1,las actividades siguientes a las prede
                                                ###cesoras de la base no son igual a base
                                                ###verdadera>-1,el valor de verdadera indica la primera
                                                ###actividad predecesora a base cuyas actividades siguientes
                                                ###son igual a base
                            cont1=-1            ###indica la posicion de una actividad en la matriz
                            verdaderaL=[]        ###lista de actividades predecesoras que cumplen que sus actividades
                                                ###siguientes son igual a la base
                            ###recorro las actividades que componen las predecesoras a la base,
                            ###inserto en sigprec dichas actividades,
                            ###ordeno sigprec y base,
                            ###si son iguales,verdadera=actividad predecesora cuyas actividades siguientes son 
                            ###igual a base e inserto en verdaderaL dicha actividad
                            for o in pospre:
                                cont1=-1
                                sigprec=[]        ###para cada actividad en pospre vuelvo a inicializar a []
                                for p in m[o]:
                                    cont1=cont1+1
                                    if p==1:
                                        sigprec.append(cont1)
                                sigprec.sort()
                                base.sort()
                                if sigprec==base:
                                    verdadera=o
                                    verdaderaL.append(o)
                            ###si hay alguna actividad predecesora cuyas actividades siguientes son igual
                            ###a base                
                            if verdadera>-1:
                                amfA=[]            ###lista de las actividades mismo final analizadas
                                                ###para no repetir asignaciones de actividades
                                ###recorro pospre en busca de una actividad predecesora a base que cumpla
                                ###los siguientes requisitos: tenga mas de una actividad siguiente, que sea
                                ###distinta a la actividad cuyas siguientes son inguales a base y que no este
                                ###en amfA(para trazar actividades ficticias)
                                for p in pospre:
                                    if m[p].count(1) > 1:
                                        if verdadera != p and p not in amfA:
                                            ###introduzco actividad imaginaria desde el nodo final de la 
                                            ###actividad buscada hasta el nodo final de la actividad que 
                                            ###denominamos verdadera
                                            d1[a]=[d1[p][1],d1[verdadera][1]]
                                            a=a+1
                                            ###si la actividad buscada es actividad mismo fin introduzco todas
                                            ###las actividades que tienen mismo fin para no asignar actividades 
                                            ###ficticias de mas
                                            if p in amfD:
                                                for u in amfD[p]:
                                                    amfA.append(u)
                                ###recorro las actividades que conforman base para trazar las actividades verdaderas
                                for p in base:
                                    ###si actividad 'p' no es actividad mismo final asigno actividad 'p' con nodo 
                                    ###inicio el final del nodo de la actividad 'verdadera' y nodo final cont+1
                                    if p not in amfD:
                                        cont=cont+1
                                        d1[p]=[d1[verdadera][1],cont]
                                    ###si actividad 'p' es actividad mismo final
                                    else:
                                        ###si nodo final de actividad 'p' no esta asignado asigno actividad 'p' con
                                        ###nodo inicio el nodo final de la actividad verdadera y nodo final cont+1
                                        if d1[p][1]==0:
                                            cont=cont+1
                                            d1[p]=[d1[verdadera][1],cont]
                                        ###si nodo final de actividad 'p' esta asignado
                                        ###y nodo final de la actividad verdadera no esta asignado
                                        ###asigno a nodo inicial de actividad 'p' el nodo final de la actividad verdadera
                                        else:
                                            if d1[verdadera][1] == 0:
                                                ###recorro actividades que podrian ser verdaderas y tengan asignadas
                                                ###nodo final
                                                for l in verdaderaL:
                                                    if l != verdadera and d1[l][1]>0:
                                                        verdadera=l
                                            d1[p][0]=d1[verdadera][1]
                                        ###recorro todas las actividades con mismo fin que actividad 'p'
                                        ###y les asigno el mismo nodo fin que a actividad 'p' si su nodo final
                                        ###es igual 0
                                        for l in amfD[p]:
                                            if d1[l][1] == 0:
                                                d1[l][1]=cont
                            ###si no hay alguna actividad predecesora cuyas actividades siguientes son igual
                            ###a base            
                            else:
                                camino=0     ###si camino=1,actuo sin poner ficticias porque al ser nodos
                                            ###con mismo final no hace falta
                                ###recorro actividades mismo final(listas de listas de actividades mismo final),
                                ###ordeno las listas que van saliendo y si son iguales a pospre, es decir, las 
                                ###las actividades precedentes son actividades mismo final por lo que no hay que
                                ###introducir actividades ficticias, camino=1                
                                for l in amf:
                                    l.sort()
                                    if pospre==l:
                                        camino=1
                                ###si camino=0, actividades precedentes no son actividades mismo final, entonces
                                ###introduzco un nodo nuevo y asigno actividades ficticias desde los nodos precedentes
                                ###hacia el nodo nuevo, asignando las actividades siguientes desde el nodo final del 
                                ###nodo nuevo hasta cont
                                if camino==0:
                                    cont=cont+1
                                    ff=cont
                                    for p in pospre:
                                        d1[a]=[d1[p][1],cont]
                                        a=a+1
                                    for p in base:
                                        cont=cont+1
                                        d1[p]=[ff,cont]
                                        ###recorro todas las actividades con mismo fin que actividad 'p'
                                        ###y les asigno el mismo nodo fin que a actividad 'p' si su nodo final
                                        ###es igual 0
                                        if p in amfD:
                                            for l in amfD[p]:
                                                d1[l][1]=cont
                                ###si camino=1, actividades precedentes son actividades mismo final, entonces
                                ###no hacen falta ni nodo nuevo y actividades ficticias asi que asigno las 
                                ###actividades que conforman la base desde el nodo final de la actividad 'X',
                                ###posicion de la actividad que estoy analizando, y nodo final cont
                                else:
                                    for p in base:
                                        cont=cont+1
                                        d1[p]=[d1[X][1],cont]
                                        ###recorro todas las actividades con mismo fin que actividad 'p'
                                        ###y les asigno el mismo nodo fin que a actividad 'p' si su nodo 
                                        ###final es igual 0
                                        if p in amfD:
                                            for l in amfD[p]:
                                                d1[l][1]=cont
        X=X+1    
        if X==b:
            X=0
    
    d2=copy.deepcopy(d1)
    d2=algoritmoLorenzoFinal.rf(d1,cont,a,af,b)
    
    ###rellenar grafo

    grafo=claseGrafo.Grafo()

    for i in d2.iteritems():
        tupla=i[1][0],i[1][1]        
        if i[0]<b:
            tupla1=premat[i[0]],'False'
            grafo.addArc(tupla,tupla1)
        else:
            tupla1='FICTICIA','True'
            grafo.addArc(tupla,tupla1)

    return grafo

