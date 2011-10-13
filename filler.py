#!/usr/bin/env python
"""
Template for main programs and modules with test code

This template must be used for all programs written in Python and for almost all 
modules (as modules should have test code). 

The comments, specially those marked with XXX, are supposed to be deleted or replaced with your own comments.

It is inspired in the comments from Guido's article[1]. I have not included Usage exception as OptionParser
has the method .error to return when something is wrong on arguments (note that getopt is deprecated).

[1] http://www.artima.com/weblogs/viewpost.jsp?thread=4829
"""
# Imports from Python standard library

# Imports from other external libraries

# Imports from our libraries
import assignment
import fileFormats

def load (filename):

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
            actividad, schedules, recurso, asignacion = data
            return actividad, schedules, recurso, asignacion
        else:
            raise Exception('ERROR: Formato del archivo origen no reconocido')

    except IOError:
        print 'ERROR: Formato del archivo origen no reconocido', '\n'
        

def saveProject( nombre, activities, schedules, resources, asignacion):
    """
    Saves a project in ppcproject format '.ppc'
    """
    
    # Here extension should be checked to choose the save format
    # by now we suppose it is .ppc
    if nombre[-4:] != '.ppc':
        nombre = nombre + '.ppc'

    format = fileFormats.PPCProjectFileFormat()
   
    try:
        format.save((activities, schedules, resources, asignacion), nombre)
        
    except IOError :
        self.dialogoError(gettext.gettext('Error saving the file'))  

def main():
    """
    XXX Main program or test code
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs=1,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('outfile', nargs=1,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('-d', '--distribution', default='Beta', 
                        choices=['Beta', 'Normal', 'Uniform', 'Triangular'],
                        help='Statistical distribution (default: Beta)')
    parser.add_argument('-k', default=0.2, type=float, 
                        help='Value of constant to generate missing values (default: 0.2)')
   
    args = parser.parse_args()

    act, schedules, recurso, asignacion = load(args.infile)
    activity = assignment.actualizarActividadesFichero(args.k,args.distribution,act)
    saveProject(args.outfile, activity, schedules, recurso, asignacion)  
    print 'We have readed from ', args.infile
    print 'We have saved in ', args.outfile
    print 'The distribution used have been', args.distribution
    print 'Constant value for k have been', args.k

    # XXX Use return 1 or any non 0 code to finish with error state
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

