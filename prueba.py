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
import algoritmoSharma
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

        activities, schedules, recurso, asignacion = data
        return activities
    except IOError:
        print 'Error reading file:', filename
        sys.exit(1)

def check_activities(activities):
    """
    Activities table is checked for consistency printing results on stdout
    """
    # Get successors
    successors = {}
    for i in activities:
        successors[i[1]] = i[2]

    # Check conexos
    print "Check Conexos: ", conexos.check_conexos(successors)
    # Check cycles
    print "Check Cycles: ", Kahn1962.check_cycles(successors)
    print ""

##def test_algorithm(activities, algorithm, repeat=1):
##    """
##    Test one algorithm using activities table.
##    """
##    # Get successors
##    successors = {}
##    for i in activities:
##        successors[i[1]] = i[2]

##    # obtengo prelaciones revertiendo sucesores
##    prelaciones = graph.reversed_prelation_table(successors)

##    # Run algorithm
##    itime = os.times()
##    for i in range(repeat):
##        pert_graph = algorithm(prelaciones)
##    ftime = os.times()
##    utime = ftime[0] - itime[0]
##    execution_time = utime
##    
##    # Print test results
##    print "utime %.4f"% (utime)
##    print "numero de nodos: ", pert_graph.number_of_nodes()
##    print "numero de arcos: ", pert_graph.number_of_arcs()
##    print "numero de arcos reales: ", pert_graph.numArcsReales()
##    print "numero de arcos ficticios: ", pert_graph.numArcsFicticios()
##    print "Validation: ", validation.check_validation(successors, pert_graph)
##    print ""
##    return pert_graph


###si hay dos argumentos pasados por lineas de comandos 
if len(sys.argv) == 3:
    filename = sys.argv[1]           ###el nombre del fichero es el primer parametro
    repeat = int(sys.argv[2])  ###repeticiones es igual al segundo parametro
    
    # File input
    print "\nFilename: ",filename 
    data = openProject(filename)
    check_activities(data)
    # List of name and file of each algorithm to test ##Poner como tupla##
    algorithms = [  
#                    ('Cohen-Sadeh', Cohen_sadeh_Alberto.cohen_sadeh), 
                    ('Algoritmo Sharma', algoritmoSharma.sharma1998ext),
#                    ('Algoritmo Conjuntos', algoritmoConjuntos.algoritmoN),
                 ]

    f_csv = open("resultados.csv", "a")

    for name, alg in algorithms:
        print name
    #Sacar aqui test algorithm
    #   Test one algorithm using data(activities table).
        # Get successors
        successors = {}
        repeat = 1;
        for i in data:
            successors[i[1]] = i[2]

        # obtengo prelaciones revertiendo sucesores
        prelaciones = graph.reversed_prelation_table(successors)

        # Run algorithm
        itime = os.times()
        for i in range(repeat):
            pert_graph = alg(prelaciones)
        ftime = os.times()
        utime = ftime[0] - itime[0]
        
        # Print test results
    #    precision_utime = "utime %.4f"% (utime)
        print "numero de nodos: ", pert_graph.number_of_nodes()
        print "numero de arcos: ", pert_graph.number_of_arcs()
        print "numero de arcos reales: ", pert_graph.numArcsReales()
        print "numero de arcos ficticios: ", pert_graph.numArcsFicticios()
        print "Validation: ", validation.check_validation(successors, pert_graph)
        print ""

    #        result_graph = test_algorithm(data, alg, repeat)

        result_line = '"' + filename + '",' + '"' + name + '",' + str(len(data)) + ',' + \
            str(pert_graph.number_of_nodes()) + ',' + str(pert_graph.number_of_arcs()) + ',' + \
            str(pert_graph.numArcsReales()) + ',' + str(pert_graph.numArcsFicticios()) + ',' + "%.4f"%(utime)
            # Draw graph and save in a file (*.svg)
    #        image_text = graph.pert2image(result_graph) 
    #        fsalida = open(os.path.split(filename)[1] + '_' + name + '.svg', 'w')
    #        fsalida.write(image_text)
    #        fsalida.close()

        f_csv.write(result_line + "\n")
    f_csv.close()


else:
    print
    print "Numero de parametros introducidos erroneo."
    print
    print "Ejemplo:"
    print
    print "python pruebaAC.py j301_1.sm 1000"
    print
