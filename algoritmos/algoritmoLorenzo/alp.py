import math, os, sys
def matriz(prelaciones):
    
    m=[]
    premat={}
    cont=0
    for i in prelaciones.iteritems():
        premat[cont]=i[0]
        cont=cont+1
        mf=[]
        actividad=i[0]
        for j in prelaciones.iteritems():
            if actividad in j[1]:
                mf.append(1)
            else:
                mf.append(0)
        m.append(mf)



        
    aa=[
    [0,0,1,0,1,0,0,0,0,0,1,0,0,0,0],
    [0,0,1,0,1,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    [0,0,0,0,0,1,0,0,0,0,0,0,0,1,0],
    [0,0,0,1,0,0,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]]
    bb=[
    [0,1,1,1,0,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0],
    [0,0,0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0]]
    cc=[
    [0,0,1,1,0,1,0,0,0,0,0,1],
    [0,0,1,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,1,1,0],
    [0,0,0,0,0,0,0,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0]]
    dd=[
    [0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
    ee=[
    [0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
    ff=[
    [0,0,1,1,0,0,0,0,0],
    [0,0,1,1,1,0,0,0,0],
    [0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,0,1,1,1],
    [0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0]]
    gg=[
    [0,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,1,0],
    [0,0,0,0,1,0,0,0,1,0],
    [0,0,0,0,0,1,0,0,0,1],
    [0,0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0]]

    ###m=ee
    return m,premat

def previo(matriz):
    m=matriz
    a=len(m)    ###tamano de la matriz 
    ###t almacenara la traspuesta de la matriz
    t=[]        
    for i in range(a):
        ini=[]
        for j in range(a):
            ini.append(m[j][i])
        t.append(ini)

    ###af almacenara las actividades finales
    af=[]
    for i in range(a):
        if 1 not in m[i]:    ###si no hay unos en la fila de la matriz
            af.append(i)

    ###ai almacenara las actividades iniciales
    ai=[]
    for i in range(a):
        if 1 not in t[i]:    ###si no hay unos en la columna de la matriz(uso la traspuesta)
            ai.append(i)


    amiD={}        ###amiD sera un diccionario cuyas claves seran las actividades que tengan 
                ###mismo inicio y su significado las actividades que son mismo inicio que la clave
    inc=[]        ###lista auxiliar para no meter actividades dobles
    ami=[]        ###lista que contendra listas de actividades mismo inicio
    for i in range(a):
        ci=[]    ###actividades que tienen columnas iguales(para cada iteracion vuelve a [])
        if i not in inc:
            for j in range(a):
                if j>i and t[i]==t[j] and 1 in t[i]:
                    ci.append(j)
                    inc.append(j)
            if len(ci)>0:
                ci.append(i)
                ami.append(ci)
        ###para formar el diccionario
        for j in ci:
            amiD[j]=[]
            for k in ci:
                if j!=k:
                    amiD[j].append(k)

    amfD={}        ###amfD sera un diccionario cuyas claves seran las actividades que tengan 
                ###mismo fin y su significado las actividades que son mismo fin que la clave
    inc=[]        ###lista auxiliar para no meter actividades dobles
    amf=[]        ###lista que contendra listas de actividades mismo fin
    for i in range(a):
        fi=[]    ###actividades que tienen filas iguales(para cada iteracion vuelve a []) 
        if i not in inc:
            for j in range(a): 
                if j>i and m[i]==m[j]:
                    fi.append(j)
                    inc.append(j)
            if len(fi)>0:
                fi.append(i)
                amf.append(fi)
        ###para formar el diccionario
        for j in fi:
            amfD[j]=[]
            for k in fi:
                if j!=k:
                    amfD[j].append(k)
    
    return m,t,af,ai,ami,amiD,amf,amfD


###import algoritmoLorenzo
###d=algoritmoLorenzo.algoritmoLorenzo()


