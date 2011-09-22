import assignment
import graph
import kolmogorov_smirnov
import math
import pert
import zaderenko
import simulation
def load(filename, distribucion, k):
    """
    Load project data (see base class)
    """
    f = open(filename)
    prelaciones = []
    asig = []
    l = f.readline()
    while l:
    # Activities and following activities
        if l[0] == 'j' and l[10] == '#':
            l = f.readline()
            while l[0] != '*':
                prel = (l.split()[0], l.split()[3:])
                prelaciones.append(prel)
                l = f.readline()

        # Activity duration and resource units needed
        if l[0] == '-':
            l = f.readline()
            while l[0] != '*':
                asig.append(l.split())
                l = f.readline()

        l = f.readline()
    
    # Modify data structure
    cont=1
    longitud=len(prelaciones)
    activities = []

    for prelacion in prelaciones:
        if prelacion!=prelaciones[0] and prelacion!=prelaciones[longitud-1]:   
            if prelacion[1]==[str(longitud)]:  #activities with the last activity as next 
                activities.append([cont, prelacion[0], [], '', '', '', '', '','Beta'] )
            else:
                activities.append([cont, prelacion[0], prelacion[1], '', '', '', '', '','Beta'])
                                
            cont += 1  

    
    for n in range(len(asig)-1):   
        if asig[n][2]!='0':
            m=n-1
            activities[m][6]=float(asig[n][2])
            
    
    activity = assignment.actualizarActividadesFichero(k,distribucion,activities)
    f.close()
    return (activity, [])

def save (actividades, filename):

    f = open(filename,"w")
    for line in actividades:
        f.write(str(line))
        f.write('\n')

    f.close()

def test (actividad,it):
    informacionCaminos = []
    # Get all paths removing 'begin' y 'end' from each path
    successors = dict(((act[1], act[2]) for act in actividad))
    g = graph.roy(successors)
    caminos = [c[1:-1]for c in graph.find_all_paths(g, 'Begin', 'End')]

    # Se crea una lista con los caminos, sus duraciones y sus varianzas
    for camino in caminos:   
        media, varianza = mediaYvarianza(camino,actividad) 
        info = [camino, float(media), varianza, math.sqrt(float(varianza))]      
        informacionCaminos.append(info)

    #Se ordena la lista en orden creciente por duracion media de los caminos
    informacionCaminos = kolmogorov_smirnov.ordenaCaminos(informacionCaminos)

    #Se calcula el numero de caminos dominantes (segun Dodin y segun nuestro metodo),
    #Se asignan los valores a alfa y beta para poder realizar la funcion gamma
    m, m1, alfa, beta = kolmogorov_smirnov.calculoValoresGamma(informacionCaminos)
    print m, m1, alfa, beta ,'\n'

    mediaCritico, dTipicaCritico = kolmogorov_smirnov.calculoMcriticoDcriticoNormal(informacionCaminos)
    print mediaCritico, dTipicaCritico ,m,'\n'

    if (m != 1):
        a, b = kolmogorov_smirnov.calculoValoresExtremos (mediaCritico, dTipicaCritico, m)
    #Creamos un vector con las duraciones totales para pasarselo al test
    duracionesTotales = vectorDuraciones(it,actividad)

    valorComparacion = kolmogorov_smirnov.valorComparacion(0.05, len(duracionesTotales)) 
    if (m != 1):
        bondadNormal, bondadGamma, bondadVE = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta, a, b)
        print bondadNormal, bondadGamma , bondadVE, '\n'
    else:
        bondadNormal, bondadGamma, bondadVE = kolmogorov_smirnov.testKS(duracionesTotales, mediaCritico, dTipicaCritico, alfa, beta)
        print bondadNormal, bondadGamma, bondadVE, '\n'

    
    print 'El valor de comparacion es: ', valorComparacion, '\n'  
    print 'La media y la varianza que selecciona es: ', mediaCritico, dTipicaCritico, '\n'
    if (m != 1):
        print 'Los valores de a y b son respectivamente', a, b, '\n'


def mediaYvarianza(camino, actividad):

        d=0
        for a in camino:
            for n in range(len(actividad)):
                if a==actividad[n][1] and actividad[n][6]!='':
                    d+=float(actividad[n][6])
                else:  #controlamos las ficticias
                    d+=0
        #print d

        # Se calcula la desviacion tipica de cada camino. Se suman las desviaciones
        # tipicas de todas las actividades que forman dicho camino.

        t=0
        for a in camino:
            for n in range(len(actividad)):
                if a==actividad[n][1] and actividad[n][7]!='':
                    t+=(float(actividad[n][7])*float(actividad[n][7]))
                else:  #controlamos las ficticias
                    t+=0
        #print t

        return '%5.2f'%(d), '%5.2f'%(t)

def pertFinal(actividad):
        
        successors = dict(((act[1], act[2]) for act in actividad))
        grafo = pert.Pert()
        grafo.construct(successors)
        grafoRenumerado = grafo.renumerar()

        return grafoRenumerado

def simulacion(actividad, n):
    
    simulacion = []
    for i in range(n):
        sim = []
        for m in range(len(actividad)):
            distribucion = actividad[m][8]
            
            if distribucion=='Uniforme':
                if actividad[m][3]!=actividad[m][5]:
                    valor = simulation.generaAleatoriosUniforme(float(actividad[m][3]), 
                                                                float(actividad[m][5]))
                else: 
                    valor=actividad[m][3]


            elif distribucion=='Beta':
                if actividad[m][3] != actividad[m][5] != actividad[m][4]:                            

                    mean, stdev, shape_a, shape_b = simulation.datosBeta(float(actividad[m][3]), 
                                                                         float(actividad[m][4]), 
                                                                         float(actividad[m][5]))
                    valor = simulation.generaAleatoriosBeta(float(actividad[m][3]), 
                                                            float(actividad[m][5]), 
                                                            float(shape_a), float(shape_b))
                else:  
                    valor = actividad[m][3]


            elif distribucion == 'Triangular':
            
                if actividad[m][3] != actividad[m][5] != actividad[m][4]:
                    valor=simulation.generaAleatoriosTriangular(float(actividad[m][3]), 
                                                                float(actividad[m][4]), 
                                                                float(actividad[m][5]))
                else:   
                    valor=actividad[m][3]
                                    
            
            elif distribucion == 'Normal':
            
                if float(actividad[m][7])!=0.00:
                    valor=simulation.generaAleatoriosNormal(float(actividad[m][6]), float(actividad[m][7]))
                else:   
                    valor=self.actividad[m][6]
            
            else: 
                return
                    
            sim.append(float(valor))
            
        simulacion.append(sim)

    return simulacion

def vectorDuraciones(it,actividad):
    
    simulaciones = simulacion(actividad,it)
    grafoRenumerado = pertFinal(actividad)

    nodosN=[]
    for n in range(len(grafoRenumerado.successors)):
        nodosN.append(n+1)

    duraciones = []
    if simulaciones == None:
            return
    else:
        for s in simulaciones: 
            matrizZad = zaderenko.mZad(actividad,grafoRenumerado.arcs, nodosN, 0, s)
            tearly = zaderenko.early(nodosN, matrizZad)  
            tlast = zaderenko.last(nodosN, tearly, matrizZad)      
            tam = len(tearly)
            duracionProyecto = tearly[tam-1]
            duraciones.append(duracionProyecto)

    return duraciones


# --- Start running as a program
if __name__ == '__main__':
    act, dur = load('e605.sm','Beta',0.2)
    cont = 0
    test(act,1000)
    save(act,'e101T.txt')
    

