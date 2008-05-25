#!/usr/bin/python
# -*- coding: utf-8 -*-
# Load, Save, Import and Export files
#  Classes here should deal with data storing and recovering. They should
#  not have anything to do with graphical or text user interface (filenames,
#  and options should be received by parameter).
# -----------------------------------------------------------------------
# PPC-PROJECT
#   Multiplatform software tool for education and research in
#   project management
#
# Copyright 2007-8 Universidad de Córdoba
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

import gtk
import gettext

class ProjectFileFormat(object):
    """
    Base class for general project file format loader and saver
    """
    def __init__(self):
        """
        Initializes self.filenameExtensions as a list of strings with 
        the filename extensions (excluding '.') supported by this format
        """
        self.filenameExtensions = []  # Example: ['sm', 'prj']
        raise Exception('Virtual class can not be instantiated')

    def filenamePatterns(self):
        """
        Returns a list of the wildcard pattern that matches files on this format.

        Implementing this function on subclasses is: not appropiate.
        """
        return ['*.'+e for e in self.filenameExtensions]

    def description(self):
        """
        Returns a string with the name or description of this format to show on 
        dialogs

        Implementing this function on subclasses is: recommended.
        Example string: 'PPC-Project files (*.prj, *.prj2)'
        """
        return ''.join(['(', ', '.join(self.filenamePatterns()), ')'])
        
    def canLoad(self):
        """
        Returns if this project format allows to save all data

        Implementing this function on subclasses is: not appropiate.
        """
        #xxx should be corrected to work on all subclass hierarchy

        return 'load' in self.__class__.__dict__

    def load(self, filename):
        """
        Returns project data: (activities, schedules, resources, resourceAsignaments)
           xxx Describe here complete data structure of each.

        Implementing this function on subclasses is: optional.
        """
        raise Exception('Virtual method not implemented (base class reached)')

    def canSave(self):
        """
        Returns if this project format allows to save all data

        Implementing this function on subclasses is: not appropiate.
        """
        #xxx should be corrected to work on all subclass hierarchy

        return 'save' in self.__class__.__dict__
        
    def save(self, projectData, filename):
        """
        project data: exactly the same structure as load method: 
          (activities, schedules, resources, resourceAsignaments)
          See load method for details.
        filename: path and filename to save (should include extension)
        Returns: None

        Implementing this function on subclasses is: optional.
        """
        raise Exception('Virtual method not implemented (base class reached)')


class PSPProjectFileFormat(ProjectFileFormat):
    """
    Allows loading PSPlib files
    """
    def __init__(self):
        self.filenameExtensions = ['sm']
        
    def load(self, filename):
        """
        Load project data (see base class)
        """
        f = open(filename)
        prelaciones = []
        asig = []
        rec = []
        l = f.readline()
        while l:
        # Lectura de las actividades y sus siguientes
            if l[0] == 'j' and l[10] == '#':
                l = f.readline()
                while l[0] != '*':
                    prel = (l.split()[0], l.split()[3:])
                    prelaciones.append(prel)
                    l = f.readline()

            # Lectura de la duración de las actividades y de las unidades de recursos 
            # necesarias por actividad
            if l[0] == '-':
                l = f.readline()
                while l[0] != '*':
                    asig.append(l.split())
                    l = f.readline()

            # Lectura del nombre, tipo y unidad de los recursos
            if l[0:22] == 'RESOURCEAVAILABILITIES':
                l = f.readline()
                while l[0] != '*':
                    rec.append(l.split())
                    l = f.readline()

            l = f.readline()

        return (prelaciones, [], rec, asig)


class PPCProjectOLDFileFormat(ProjectFileFormat):
    """
    Permite cargar los fichero .prj generados con la versión anterior

    (está a drede en español ya que esta clase debe ser eliminada cuando 
    se consolide el formato nuevo (convirtamos los ficheros útiles))
    """
    def __init__(self):
        self.filenameExtensions = ['prj']

    def load(self, filename):
        """
        Load project data (see base class)
        """
        pass # xxx


class PPCProjectFileFormat(ProjectFileFormat):
    """
    New project file format (xxx to define)
    """
    def __init__(self):
        self.filenameExtensions = ['prj']

    def load(self, filename):
        """
        Load project data (see base class)
        """
        pass # xxx 





def guardarCsv(texto, principal):
    """
     Salva texto en formato CSV

     Parámetros: texto (texto a guardar)

     Valor de retorno: -
    """
    dialogoGuardar = gtk.FileChooserDialog(gettext.gettext('Save'), None,
                                           gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL,
                                           gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE,
                                           gtk.RESPONSE_OK))
    dialogoGuardar.set_default_response(gtk.RESPONSE_OK)
    resultado = dialogoGuardar.run()
    if resultado == gtk.RESPONSE_OK:
        try:
            nombre = dialogoGuardar.get_filename()
            if nombre[-4:] == '.csv':
                fescritura = open(nombre, 'w')
            else:
                fescritura = open(nombre + '.csv', 'w')
            fescritura.write(texto)
        except IOError:

            principal.dialogoError(gettext.gettext('Error saving the file'))
        fescritura.close()
    # elif resultado == gtk.RESPONSE_CANCEL:
        # print "No hay elementos seleccionados"

    dialogoGuardar.destroy()


def leerPSPLIB(f):
    """
    xxx To be removed
     Lectura de un proyecto de la librería de proyectos PSPLIB   

     Parámetros: f (fichero) 

     Valor de retorno: prelaciones (lista que almacena las actividades 
                                    y sus siguientes)
                       rec (lista que almacena el nombre y las unidades
                           de recurso)
                       asig (lista que almacena las duraciones y las 
                             unid. de recurso necesarias por cada actividad)
    """

    prelaciones = []
    asig = []
    rec = []
    l = f.readline()
    while l:
    # Lectura de las actividades y sus siguientes
        if l[0] == 'j' and l[10] == '#':
            l = f.readline()
            while l[0] != '*':
                prel = (l.split()[0], l.split()[3:])
                prelaciones.append(prel)
                l = f.readline()

        # Lectura de la duración de las actividades y de las unidades de recursos 
        # necesarias por actividad
        if l[0] == '-':
            l = f.readline()
            while l[0] != '*':
                asig.append(l.split())
                l = f.readline()

        # Lectura del nombre, tipo y unidad de los recursos
        if l[0:22] == 'RESOURCEAVAILABILITIES':
            l = f.readline()
            while l[0] != '*':
                rec.append(l.split())
                l = f.readline()

        l = f.readline()

    return (prelaciones, rec, asig)


def leerTxt(f):
    """
     Lectura de un fichero con extensión '.txt'

     Parámetros: f (fichero)

     Valor de retorno: tabla (datos leidos)
    """

    tabla = []
    l = f.readline()
    while l:
        linea = l.split('\t')
        linea[1] = linea[1].split(',')
        tabla.append(linea)
        l = f.readline()

    l = f.readline()

    return tabla

# --- Start running as a program
if __name__ == '__main__':
    o = PSPProjectFileFormat()
    print o.canSave()
    

