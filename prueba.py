"""
Program to check graph generation algorithms with the project file passed as parameter

The tests are:
    - If graph does not have cycles (Kahn1962)
    - If graph have not related nodes (Conexos)
    - If graph draw, have the nodes, arcs, and dummy required (validation_graph)

Apart from test results, show: run time, number of arcs, number of dummy arcs, numbers of real arcs and number of nodes

algorithms: list to include all algorithm to check.
"""

import os
import os.path
import sys

import algoritmoConjuntos
import algoritmoSalas
import algoritmoCohenSadeh
import Cohen_sadeh_Alberto
import graph
import fileFormats
import pert
import Kahn1962
import validation
import conexos

#REPETICIONES = 1
#REPETICIONES = int(sys.argv[2])
def openProject(filename):
    """
    abre un proyecto ante un nombre pasado como paramentro por linea de comandos
    """
    try:
        actividad  = []
        recurso    = []
        asignacion = []
        schedules  = []
        fileFormat = [
            fileFormats.PPCProjectFileFormat(),
#            fileFormats.PPCProjectOLDFileFormat(),
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
if len(sys.argv) == 3:
    repeticiones = int(sys.argv[2]) ###repeticiones es igual al segundo parametro
    filename = sys.argv[1]           ###el nombre del fichero es el primer parametro

    data = openProject(filename)
    successors = {}
    ###obtengo los sucesores de cada actividad
    for i in data:
        successors[i[1]] = i[2]
    ###Name of file
    print "\nFilename: ",filename 
    ###Check conexos
    print "Succesors:", successors
    print "Conexos: ", conexos.check_conexos(successors)
    ###Check cycles
    print "Kahn: ", Kahn1962.check_cycles(successors)
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
    # List of name and file of each algorithm to test 
    algorithms = [  ('Cohen-Sadeh', Cohen_sadeh_Alberto.cohen_sadeh), 
                    ('Algoritmo Conjuntos', algoritmoConjuntos.algoritmoN),
                    ('Algoritmo Salas', algoritmoSalas.salas)
                 ]
                    
    for name, alg in algorithms:
        itime = os.times()
        for i in range(repeticiones):
            pert_graph = alg(prelaciones1)
        ftime = os.times()
        utime = ftime[0] - itime[0]
        print name
        print "utime %.4f"% (utime)
        print "numero de nodos: ", pert_graph.number_of_nodes()
        print "numero de arcos: ", pert_graph.number_of_arcs()
        print "numero de arcos reales: ", pert_graph.numArcsReales()
        print "numero de arcos ficticios: ", pert_graph.numArcsFicticios()
#        print "Prelaciones1: ", prelaciones1
        gg1 = alg(prelaciones1)
#        print "gg1: ", gg1.pertSuccessors()
#        print "Successors: ", successors
        print "Validation: ", validation.check_validation(successors, gg1)
#        image_text = graph.pert2image(g) # Draw graph and save in a file (*.svg)
#        fsalida = open(name + ' ' + os.path.split(filename)[1] + '.svg', 'w')
#        fsalida.write(image_text) # Draw in directory images
#        fsalida.close()

else:
    print
    print "Numero de parametros introducidos erroneo."
    print
    print "Ejemplo:"
    print
    print "python pruebaAC.py j301_1.sm 1000"
    print
