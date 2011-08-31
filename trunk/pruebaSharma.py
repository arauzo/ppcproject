"""
algoritmo que compara la eficiencia del algoritmo de Sharma haciendo
uso o no del tipo de dato grafo
"""

import os
import sys
import graph
import pert
#import pert2
import fileFormats

#REPETICIONES = 1
#REPETICIONES = int(sys.argv[2])


def openProject(filename):
    """
    Abre un proyecto dado un nombre de fichero por linea de comandos
    """
    try:
        actividad  = []
        recurso    = []
        asignacion = []
        schedules  = []
        fileFormat = [
            fileFormats.PPCProjectFileFormat(),
            fileFormats.PPCProjectOLDFileFormat(),
            fileFormats.PSPProjectFileFormat(),
        ]

        

        # Tries to load file with formats that match its extension in format order
        data = None
        extension = filename[filename.rfind('.')+1:]

        for format in fileFormat:
            if extension in format.filenameExtensions:
                try:
                    data = format.load(filename)
                    break
                except fileFormats.InvalidFileFormatException:
                    pass

        if not data:
            print 'Can not understand file'
            sys.exit(1)

        actividad, schedules, recurso, asignacion = data
        return data[0]
    except IOError:
        print 'Error reading file:', filename
        sys.exit(1)

###si hay dos argumentos pasados por lineas de comandos 
if len(sys.argv)==3:
    repeticiones= int(sys.argv[2]) ###repeticiones es igual al segundo parametro
    filename=sys.argv[1]           ###el nombre del fichero es el primer parametro

    data = openProject(filename)
    successors = {}
    ###obtengo los sucesores de cada actividad
    for i in data:
        successors[i[1]]=i[2]
    ###obtengo prelaciones revertiendo sucesores
    prelaciones1 = graph.reversed_prelation_table(successors)
    """
    ejemplos de prelaciones

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
    prelaciones = {
        'A' : [],
        'B' : [],
        'C' : ['A'],
        'D' : ['A','B'],
        'E' : ['C','D'],
        'F' : ['D'],
        'G' : ['E'],
        'H' : ['F','D','C'],
        'I' : ['F'],
        }
    prelaciones = {
        'A' : [],
        'B' : [],
        'C' : [],
        'D' : ['A'],
        'E' : ['B'],
        'F' : ['C'],
        'G' : ['E','F'],
        'H' : ['D'],
        }
    """

#    itime=os.times()
#    for i in range(repeticiones):
#        g = pert2.Pert()
#        g.construct(successors)
#    ftime=os.times()
#    utime = ftime[0] - itime[0]
#    print "Sharma sin tipo de dato Grafo"
#    print "utime %.4f"% (utime)

    itime=os.times()
    for i in range(repeticiones):
        g = pert.Pert()
        g.construct(successors)
    ftime=os.times()
    utime = ftime[0] - itime[0]
    print "Sharma con tipo de dato Grafo"
    print "utime %.4f"% (utime)
    print    

    print "Nodos y arcos de Sharma"
    print "numero de nodos: ",g.number_of_nodes()
    print "numero de arcos: ",g.number_of_arcs()
    print "numero de arcos reales: ",g.numArcsReales()
    print "numero de arcos ficticios: ",g.numArcsFicticios()
    print
    image_text = graph.pert2image(g, format='png')
    fsalida = open('SharmaTDgrafo' + filename + '.png', 'w')
    fsalida.write(image_text)
    fsalida.close()

else:
    print
    print "Numero de parametros introducidos erroneo."
    print
    print "Ejemplo:"
    print
    print "python pruebaAC.py j301_1.sm 1000"
    print


