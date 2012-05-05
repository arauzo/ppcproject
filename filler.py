#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Program to include random probabilistic estimates for each activity in a PSPlib project. In this way, outfile can be used in simulation.
"""
import assignment
import fileFormats

def load(filename):
    """
    Load ppcproject-compatible files (.ppc files & .sm files)

    filename (name of the file to load)

    return: data (file info)
    """
    formatos = [fileFormats.PPCProjectFileFormat(),fileFormats.PSPProjectFileFormat()]
    try:
        # Tries to load file with formats that match its extension in format order
        data = None
        extension = filename[filename.rfind('.')+1:]

        for format in formatos:
            if extension in format.filenameExtensions:
                try:
                    data = format.load(filename)
                    break
                except fileFormats.InvalidFileFormatException:
                    pass

        # If load by extension failed, try to load files in any format independently of their extension
        if not data:
            for format in formatos:
                try:
                    data = format.load(filename)
                    break
                except fileFormats.InvalidFileFormatException:
                    pass
        
        #Data successfully loaded
        if data:
            return data
        else:
            raise Exception('ERROR: Formato del archivo origen no reconocido')

    except IOError:
        print 'ERROR: leyendo el archivo origen', '\n'
        

def saveProject(nombre, activities, schedules, resources, asignacion):
    """
    Saves a project in ppcproject format '.ppc'
    """
    if nombre[-4:] != '.ppc':
        nombre = nombre + '.ppc'

    format = fileFormats.PPCProjectFileFormat()
    try:
        format.save((activities, schedules, resources, asignacion), nombre)
    except IOError :
        self.dialogoError(_('Error saving the file'))  

def main():
    """
    Generates a ppc format file from a library file.
    This new file will be filled with the information of the fields required to perform the
    simulation of the activity duration.

    The program shall receive four arguments:
        infile (.sm file whose data will be read)
        outfile (.ppc file in which the info required for the simulation will be saved)
        -d (type of statistical distribution to be used)
        -k (proportionality constant of the typical deviation)
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')                         
    parser.add_argument('outfile')
    parser.add_argument('-d', '--distribution', default='Beta', 
                        choices=['Beta', 'Normal', 'Uniform', 'Triangular'],
                        help='Statistical distribution (default: Beta)')
    parser.add_argument('-k', default=0.2, type=float, 
                        help='Standard deviation for generated values (default: 0.2)')
    args = parser.parse_args()

    # Open the input file collecting the required information.
    act, schedules, recurso, asignacion = load(args.infile)

    if (args.k < 0):
        raise Exception ('ERROR: The parameter value k must be >= 0')
    else:
        activity = assignment.actualizarActividadesFichero(args.k,args.distribution,act)
        saveProject(args.outfile, activity, schedules, recurso, asignacion)

    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

