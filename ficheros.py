import assignment
import graph
import kolmogorov_smirnov
import math
import pert
import zaderenko
import simulation
import fileFormats
import ppcproject

#miObjeto = ppcproject.PPCproject()

def load (filename, distribucion, k):

    format = fileFormats.PSPProjectFileFormat()
    activities, none, none1, none2 = format.load(filename)
    activity = assignment.actualizarActividadesFichero(k,distribucion,activities)
    return activity

def save (actividades, filename):

    f = open(filename,"w")
    for line in actividades:
        f.write(str(line))
        f.write('\n')

    f.close()
   

def test (it,distribucion, activity):
    

    informacionCaminos = []
    # Get all paths removing 'begin' y 'end' from each path
    successors = dict(((act[1], act[2]) for act in activity))
    g = graph.roy(successors)
    caminos = [c[1:-1]for c in graph.find_all_paths(g, 'Begin', 'End')]

    # Se crea una lista con los caminos, sus duraciones y sus varianzas
    #miObjeto2 = ppcproject.PPCproject()
    for camino in caminos:   
        media, varianza = miObjeto.mediaYvarianza(camino,activity) 
        info = [camino, float(media), varianza, math.sqrt(float(varianza))]      
        informacionCaminos.append(info)

    #Se ordena la lista en orden creciente por duracion media de los caminos
    informacionCaminos = kolmogorov_smirnov.ordenaCaminos(informacionCaminos)

    #Se calcula el numero de caminos dominantes (segun Dodin y segun nuestro metodo),
    #Se asignan los valores a alfa y beta para poder realizar la funcion gamma
    m, m1, alfa, beta, mediaestimada, sigma = kolmogorov_smirnov.calculoValoresGamma(informacionCaminos)
    print m, m1, alfa, beta , mediaestimada, sigma, '\n'

    mediaCritico, dTipicaCritico = kolmogorov_smirnov.calculoMcriticoDcriticoNormal(informacionCaminos)
    print mediaCritico, dTipicaCritico ,m,'\n'

    if (m != 1):
        a, b = kolmogorov_smirnov.calculoValoresExtremos (mediaCritico, dTipicaCritico, m)
    #Creamos un vector con las duraciones totales para pasarselo al test
    duracionesTotales = vectorDuraciones(it,activity)

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


def vectorDuraciones(it,actividad):
    
    simulaciones = simulation.simulacion(it, actividad)
    #miObjeto = ppcproject.PPCproject()
    grafoRenumerado = miObjeto.pertFinal(actividad)

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
    act = load('e101.sm','Beta',0.2)
    cont = 0
    test(1000,'Beta', act)
    save(act,'e101T.txt')
    

