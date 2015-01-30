"""
Program to check graph generation algorithms with the project file passed as parameter

The tests are:
    - If graph does not have cycles (Kahn1962)
    - If graph have not related nodes (Conexos)
    - If graph draw, have the nodes, arcs, and dummy required (validation_graph)

Apart from test results, show: run time, number of arcs, number of dummy arcs, numbers of real arcs and number of nodes

algorithms: list to include all algorithm to check.

(C) 2014-2015 Antonio Arauzo-Azofra, Alberto Perez Caballero, Universidad de Cordoba
"""

import os
import os.path
import sys
import traceback

import graph
import fileFormats
import pert
import Kahn1962
import validation
import conexos
import algoritmoCohenSadeh
import algoritmoSharma
import algoritmoConjuntos
import algoritmoGentoMunicio
import algoritmoSalas

def openProject(filename):
    """
    Open filename as a project and return activities data

    if error or format not recognized returns None
    """
    fileFormat = [
        fileFormats.PPCProjectFileFormat(),
        fileFormats.PSPProjectFileFormat(),
    ]
    activities = None
    extension = filename[filename.rfind('.')+1:]
    # Tries to load file with formats that match its extension in format order
    try:
        for format in fileFormat:
            if extension in format.filenameExtensions:
                try:
                    activities, _, _, _ = format.load(filename)
                    break
                except fileFormats.InvalidFileFormatException:
                    pass

        return activities

    except IOError:
        return None

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
    # XXX Miss checking for non-redundancy

def main():
    """
    Test AOA (PERT) network generation algorithms with some given project files
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser(description='Test AOA graph generation algorithms with given files')
    parser.add_argument('infiles', nargs='*',
                        help='Project files to test')
    parser.add_argument('--table-file', '-t', default='resultados.csv',
                        help='Name of file to append test results in CSV format (default: resultados.csv)')
    parser.add_argument('-r', '--repeat', default=1, type=int,
                        help='Number of repetitions (default: 1)')
    parser.add_argument('--SVG', action='store_true',
                        help='Draw the graph in a SVG file')
    parser.add_argument('--show', action='store_true',
                        help='Draw the graph in a window')
    parser.add_argument('--no-stop', action='store_true',
                        help='Do not stop when an algorithm fails')

    parser.add_argument('-c', '--CohenSadeh', action='store_true',
                        help='Test Cohen Sadeh algorithm')
    parser.add_argument('-s', '--Sharma', action='store_true',
                        help='Test Sharma algorithm')
    parser.add_argument('-l', '--Salas', action='store_true',
                        help='Test Lorenzo Salas algorithm')
    parser.add_argument('-g', '--GentoMunicio', action='store_true',
                        help='Test Gento Municio algorithm')
    parser.add_argument('-o', '--Optimal', action='store_true',
                        help='Test set based optimal algorithm')

    args = parser.parse_args()

    if not args.infiles:
        print 'No input files. Use --help to see syntax.'
        return 0
        
    if args.repeat < 1:
        print 'Number of repetitions must be > 0'
        return 1

    try:
        f_csv = open(args.table_file, "a")
    except IOError:
        print 'Can not open table file (%s) to append results in CSV format' % (args.table_file, )
        return 1        

    # List of name and function of each algorithm to test
    algorithms = []  
    if args.CohenSadeh:
        algorithms.append( ('CohenSadeh', algoritmoCohenSadeh.cohen_sadeh) )
    if args.Sharma: 
        algorithms.append( ('Sharma', algoritmoSharma.sharma1998ext) )
    if args.Optimal:
        algorithms.append( ('Conjuntos', algoritmoConjuntos.algoritmoN) )
    if args.GentoMunicio:
        algorithms.append( ('GentoMunicio', algoritmoGentoMunicio.gento_municio) )
    if args.Salas:
        algorithms.append( ('Salas', algoritmoSalas.salas) )
    if len(algorithms) < 1:
        print 'No algorithm selected. Just testing input files...'

    # Perform tests on each file 
    for filename in args.infiles:
        print "\nFilename: ", filename 
        data = openProject(filename)
        if not data:
            print 'Can not read or understand file'
        else:
            # XXX Aqui habria que cortar si falla el checkeo del fichero
            check_activities(data)

            # Test each algorithm
            for name, alg in algorithms:
                print name

                # Get successors from activities table
                successors = {}
                for i in data:
                    successors[i[1]] = i[2]
                    
                # Count prelations
                list_of_predecessors = successors.values()
                num_of_predecessors = 0
                for predecessors in list_of_predecessors:
                    num_of_predecessors += len(predecessors)
                    
                # Get predecessors from successors
                prelaciones = graph.reversed_prelation_table(successors)

                # Run algorithm
                pert_graph = None
                itime = os.times()
                for i in range(args.repeat):
                    try:
                        pert_graph = alg(prelaciones)
                    except Exception:
                        print traceback.format_exc()
                        print " --- Algorithm failed! --- "
                        if not args.no_stop:
                            return 1
                        break

                if pert_graph:
                    ftime = os.times()
                    utime = ftime[0] - itime[0]
                    
                    # Print test results
                    print "utime %.4f"% (utime)
                    print "utime: ", utime
                    print "numero de nodos: ", pert_graph.number_of_nodes()
                    print "numero de arcos: ", pert_graph.number_of_arcs()
                    print "numero de arcos reales: ", pert_graph.numArcsReales()
                    print "numero de arcos ficticios: ", pert_graph.numArcsFicticios()
                    print "numero de predecesors/sucesores: ", num_of_predecessors
                    print "Validation: "
                    if not validation.check_validation(successors, pert_graph) and not args.no_stop:
                        return 1
                    print ""

                    # XXX ??Falta incluir aqui el numero de actividades?? Alberto -> Comprobar str(len(data)) num_actividades
                    result_line = '"' + filename + '",' + '"' + name + '",' + str(len(data)) + ',' + str(num_of_predecessors) + ',' + \
                        str(pert_graph.number_of_nodes()) + ',' + str(pert_graph.number_of_arcs()) + ',' + \
                        str(pert_graph.numArcsReales()) + ',' + str(pert_graph.numArcsFicticios()) + ',' + "%.4f"%(utime)
                    f_csv.write(result_line + "\n")
                        

                    # Draw graph and save in a file (*.svg)
                    if args.SVG:
                        image_text = graph.pert2image(pert_graph) 
                        fsalida = open(os.path.split(filename)[1] + '_' + name + '.svg', 'w')
                        fsalida.write(image_text)
                        fsalida.close()

                    # Interactively show graph on a window
                    if args.show:
                        window = graph.Test()
                        window.add_image(graph.pert2image(pert_graph))
                        graph.gtk.main()


    f_csv.close()
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

