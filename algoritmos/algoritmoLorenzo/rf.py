import math, os, sys
import copy
def rf(d,cont,a,af,b):
    ###pone todos los finales de todas las actividades finales en el 
    ###el mismo nodo
    nf=af[0]
    for j in af:    
        if d[nf][1]!=d[j][1]:
                d[j][1]=d[nf][1]

    d1=copy.deepcopy(d)

    ###quitas actividades ficticias duplicadas
    retocadas=[]
    for i in d1.iteritems():
        for j in d1.iteritems():
            if i[0]!=j[0] and i[0]>=b and j[0]>=b and i[0] not in retocadas:
                if d1[i[0]]==d1[j[0]]:
                    retocadas.append(j[0])
                    del d[j[0]]    
    ###anade actividades ficticias y redirecciona actividades con
    ###mismo nodo inicio y mismo nodo final    
    retocadas=[]
    for i in d1.iteritems():
        for j in d1.iteritems():
            if i[0]!=j[0] and i[0]<b and j[0]<b and d1[i[0]]==d1[j[0]] and i[0] not in retocadas:
                i[0],j[0]
                cont=cont+1
                d[a]=[d[i[0]][0],cont]
                d[j[0]]=[cont,d[i[0]][1]]
                a=a+1
                retocadas.append(j[0])
    return d
            
            
        
