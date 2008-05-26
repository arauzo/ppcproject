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
import pickle

class InvalidFilFormatException(Exception):
    """
    Raised when a file does not contain data in the expected format
    """
    pass

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
        Return: project data=(activities, schedules, resources, resourceAsignaments)
           xxx Describe here complete data structure of each part.

        Raises: InvalidFileFormatException if data in file does not follow the format
        Implementing this function on subclasses is: optional.
        """
        raise Exception('Virtual method not implemented (base class reached)')

    def canSave(self):
        """
        Return: if this project format allows to save all data

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
        
        # Modify data structure
        cont=1
        longitud=len(prelaciones)
        activities = []

        for prelacion in prelaciones:
            if prelacion!=prelaciones[0] and prelacion!=prelaciones[longitud-1]:   
                if prelacion[1]==[str(longitud)]:  #activities with the last activity as next 
                    activities.append([cont, prelacion[0], [], '', '', '', '', '', gettext.gettext('Beta')] )
                else:
                    activities.append([cont, prelacion[0], prelacion[1], '', '', '', '', '', gettext.gettext('Beta')])
                                    
                cont += 1  

        # Update activities duration
        for n in range(len(asig)-1):   
            if asig[n][2]!='0':
                m=n-1
                activities[m][6]=float(asig[n][2])

        # Se actualizan los recursos
        i=1
        m=0
        resources = []
        for n in range(len(rec[1])):
            # Si el recurso es Renovable
            if rec[0][m]=='R' or rec[0][m][0]=='R':
                if rec[0][m]=='R':
                    row=[rec[0][m]+rec[0][i], 'Renewable', '', rec[1][n]] 
                    m+=2
                else:
                    row=[rec[0][m], 'Renewable', '', rec[1][n]] 
                    m+=1      
            # Si el recurso es No Renovable
            elif rec[0][m]=='N' or rec[0][m][0]=='N':
                if rec[0][m]=='N':
                    row=[rec[0][m]+rec[0][i], 'Non renewable', rec[1][n], '']
                    m+=2
                else:
                    row=[rec[0][m], 'Non renewable', rec[1][n], ''] 
                    m+=1
            # Si el recurso es Doblemente restringido
            elif rec[0][m]=='D' or rec[0][m][0]=='D':
                if rec[0][m]=='D':
                    row=[rec[0][m]+rec[0][i], 'Double restricted', rec[1][n], rec[1][n]]
                    m+=2
                else:
                    row=[rec[0][m], 'Double restricted', rec[1][n], rec[1][n]] 
                    m+=1
                
            resources.append(row)
            i += 2
            
            # NOTA: no tenemos en cuenta si el recurso es Ilimitado porque éste tipo de recurso no existe en 
            #       en la librería de proyectos PSPLIB   

        # Se actualizan los recursos necesarios por actividad
        asignation = []
        for n in range(len(asig)):                     
            for m in range(3, 3+len(rec[1])):  #len(self.rec[1]): número de recursos 
                if asig[n][m] != '0':          #los recursos no usados no se muestran
                    i = m-3
                    row = [asig[n][0], resources[i][0], asig[n][m]] 
                    asignation.append(row)
        
        return (activities, [], resources, asignation)


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
        f = open(filename, 'rb')
        try:
            table = pickle.load(f)
        except (UnpicklingError, AttributeError, EOFError, ImportError, IndexError, ValueError):
            raise InvalidFileFormatException('Unpickle failed')

        # xxx Check activities, schedules, resources, resourceAsignaments have the right data structure
        # if len(activities) != 6 and ... :
        #     raise InvalidFileFormatException('Incorrect data on file')

        f.close()
        # Se actualiza la interfaz de las actividades
        activities = []
        assignations = []
        resources = []
        for row in table[0]:      
            prepared_row = row[0:6] + [float(row[6])] + [row[7]] + row[9:]
            activities.append(prepared_row)
        for res in table[1]:
            if res[1] == 'Renovable': 
                res[1] = 'Renewable'
            elif res[1] == 'No renovable':
                res[1] = 'Non renewable'
            elif res[1] == 'Doblemente restringido':
                res[1] = 'Double restricted'
            else:
                res[1] = 'Unlimited'
            resources.append(res)
        assignations = table[2]
        return (activities, [], resources, assignations)


class PPCProjectFileFormat(ProjectFileFormat):
    """
    New project file format (xxx to define)
    """
    def __init__(self):
        self.filenameExtensions = ['ppc']

    def load(self, filename):
        """
        Load project data (see base class)
        """
        f = open(filename, 'rb')
        try:
            data = pickle.load(f)
            activities, schedules, resources, resourceAsignaments = data
        except (UnpicklingError, AttributeError, EOFError, ImportError, IndexError, ValueError):
            raise InvalidFileFormatException('Unpickle failed')

        # xxx Check activities, schedules, resources, resourceAsignaments have the right data structure
        # if len(activities) != 6 and ... :
        #     raise InvalidFileFormatException('Incorrect data on file')

        f.close()
        return data

    def save(self, projectData, filename):
        """
        Saves project data (see base class)
        """
        f = open(filename, 'wb')
        pickle.dump(projectData, f, protocol=1)
        f.close()


class TxtProjectFileFormat(ProjectFileFormat):
    """
    New project file format (xxx to define)
    """
    def __init__(self):
        self.filenameExtensions = ['txt']

    def load(self, filename):
        """
        Lectura de un fichero con extensión '.txt' ¿qué formato era este y para que??
        xxx Funcion incorrecta hay que adaptarla para que devuelva lo que debe (load)
        """
        f = open(filename)
        tabla = []
        l = f.readline()
        while l:
            linea = l.split('\t')
            linea[1] = linea[1].split(',')
            tabla.append(linea)
            l = f.readline()

        l = f.readline()

        return tabla




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
     xxx To be removed (code copied to class PSPlibFileFormat)
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
         xxx To be removed (code copied to class TxtProjectFileFormat)
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
    

