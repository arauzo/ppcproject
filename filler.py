#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# PPC-PROJECT
#   Multiplatform software tool for education and research in
#   project management
#
# Copyright 2007-9 Universidad de Córdoba
# This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published
#   by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
import assignment
import fileFormats

def load (filename):
    """
    Function in charge of uploading ppcproject-compatible files; that is to say .ppc files & .sm files

    filename (names of the files to be uploaded)

    return: data (file info)
    """

    formatos = [fileFormats.PPCProjectFileFormat(),fileFormats.PSPProjectFileFormat()]
    #print filename
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
        self.dialogoError(_('Error saving the file'))  

def main():
    """
    The following program of simulation batch generates a ppc format file from a library file.
    This new file will be filled with the information of the fields required to perform the
    simulation of the activity duration.

    The program shall receive four arguments for each console:
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
                        help='Value of constant to generate missing values (default: 0.2)')
   
    args = parser.parse_args()

    # We open the input file collecting the required information.
    act, schedules, recurso, asignacion = load(args.infile)

    # We attatch the required values to each activity according to the distribution and the proportionality constant of the typical deviation
    if (args.k < 0):
        raise Exception ('ERROR: The parameter value k must be greater  than 0')
    else:
        activity = assignment.actualizarActividadesFichero(args.k,args.distribution,act)

        # We save the project with ppcproject format with the values already assigned.
        saveProject(args.outfile, activity, schedules, recurso, asignacion)

    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

