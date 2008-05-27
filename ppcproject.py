#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Main program
#-----------------------------------------------------------------------
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

import os, math, sys
import random
import pickle

import pygtk
pygtk.require('2.0')
import gobject
import gtk
import gtk.glade

from copy import deepcopy

import GTKgantt
import loadingSheet

import scipy.stats
from matplotlib import rcParams
rcParams['font.family'] = 'monospace'
from pylab import *
from matplotlib.axes import Subplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
import simulation

# Internationalization
import gettext
APP='PPC-Project' #Program name
DIR='po' #Directory containing translations, usually /usr/share/locale
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
gtk.glade.bindtextdomain(APP, DIR)
gtk.glade.textdomain(APP)

# Own application modules
import pert
import graph
import interface
import fileFormats
from zaderenko import mZad, early, last
from simAnnealing import simulated_annealing
from simAnnealing import resources_availability
from simAnnealing import resources_per_activities
from simAnnealing import calculate_loading_sheet


class PPCproject(object):
    """ Controler of global events in application """

    def __init__(self):
        # Data globaly used in application
        self.actividad  = []
        self.recurso    = []
        self.asignacion = []
        self.optimumSchedule = []
        self.schedules = []
        self.schedule_tab_labels = []
        self.bufer=gtk.TextBuffer()
        # Keeps the name of the open file 
        # (None = no open file, 'Unnamed' = Project without name yet)
        self.openFilename = None #xxx gettext.gettext('Unnamed -PPC-Project')
        self.modified=0
        self.ganttActLoaded = False
        self.interface = interface.Interface(self)
        self._widgets = self.interface._widgets
        self._widgets.signal_autoconnect(self)
        self.vBoxProb = self._widgets.get_widget('vbProb')
        self.grafica = gtk.Image()
        self.box=gtk.VBox()
        self.hBoxSim = self._widgets.get_widget('hbSim')
        self.boxS=gtk.VBox()
        self.vPrincipal=self._widgets.get_widget('wndPrincipal')
        self.vIntroduccion=self._widgets.get_widget('wndIntroduccion')
        self.vZaderenko = self._widgets.get_widget('wndZaderenko')
        self.vActividades=self._widgets.get_widget('wndActividades')
        self.vHolguras=self._widgets.get_widget('wndHolguras')
        self.vProbabilidades=self._widgets.get_widget('wndProbabilidades')
        self.vSimulacion=self._widgets.get_widget('wndSimulacion')
        self.wndSimAnnealing=self._widgets.get_widget('wndSimAnnealing')
        self.vRecursos=self._widgets.get_widget('wndRecursos')
        self.vAsignarRec=self._widgets.get_widget('wndAsignarRec')
        self.vCaminos=self._widgets.get_widget('wndCaminos')
        self.vRoy=self._widgets.get_widget('wndGrafoRoy')
        self.vPert=self._widgets.get_widget('wndGrafoPert')
        self.dAyuda=self._widgets.get_widget('dAyuda')
        self.bHerramientas=self._widgets.get_widget('bHerramientas1')

        self.rbLeveling = self.interface.rbLeveling
        self.btResetSA = self.interface.btResetSA
        self.btSaveSA = self.interface.btSaveSA
        self.entryResultSA = self.interface.entryResultSA
        self.entryAlpha = self.interface.entryAlpha
        self.entryIterations = self.interface.entryIterations
        self.entryMaxTempSA = self.interface.entryMaxTempSA
        self.cbIterationSA = self.interface.cbIterationSA
        self.sbSlackSA = self.interface.sbSlackSA
        self.sbPhi = self.interface.sbPhi
        self.sbNu = self.interface.sbNu
        self.sbMinTempSA = self.interface.sbMinTempSA
        self.sbMaxIterationSA = self.interface.sbMaxIterationSA
        self.sbNoImproveIterSA = self.interface.sbNoImproveIterSA
        self.sbExecuteTimesSA = self.interface.sbExecuteTimesSA

        self.ntbSchedule = self.interface.ntbSchedule

        self.zadViewList = self._widgets.get_widget('vistaZad')
        self.vistaLista = self._widgets.get_widget('vistaListaDatos')
        self.modelo = self.interface.modelo
        self.gantt = self.interface.gantt
        self.ganttSA = self.interface.ganttSA
        self.loadingSheet = self.interface.loadingSheet
        self.loadingTable = self.interface.loadingTable
        self.modeloR = self.interface.modeloR
        self.modeloAR = self.interface.modeloAR
        self.modeloComboS = self.interface.modeloComboS
        self.modeloComboARA = self.interface.modeloComboARA
        self.modeloComboARR = self.interface.modeloComboARR
        self.modeloA = self.interface.modeloA
        self.modeloZ = self.interface.modeloZ
        self.vistaListaZ = self.interface.vistaListaZ
        self.modeloH = self.interface.modeloH
        self.modeloC = self.interface.modeloC
        self.modeloF = self.interface.modeloF
        self.vistaFrecuencias = self.interface.vistaFrecuencias
        self.checkColum=[None]*11
        for n in range(11):
            self.checkColum[n] = self.interface.checkColum[n]
        self._widgets.get_widget('mnSalirPantComp').hide()
        self.enableProjectControls(False)
        self.row_height_signal = self.vistaLista.connect("expose-event", self.cbtreeview)
        self.vistaLista.connect('drag-end', self.reorder_gantt)
        self.modelo.connect('rows-reordered', self.reorder_gantt)
        self.vistaLista.connect('button-press-event', self.treeview_menu_invoked, self.vistaLista)
        self.vistaLista.connect('button-press-event', self.treeview_menu_invoked, self.vistaLista)
        self.vistaLista.connect('button-press-event', self.treeview_menu_invoked, self.vistaLista)
        self._widgets.get_widget('vistaListaRec').connect('button-press-event', self.treeview_menu_invoked, self._widgets.get_widget('vistaListaRec'))
        self._widgets.get_widget('vistaListaAR').connect('button-press-event', self.treeview_menu_invoked, self._widgets.get_widget('vistaListaAR'))

        # File format loaders and savers
        #  (the order is used to try when loading unknown type files)
        self.fileFormats = [
            fileFormats.PPCProjectFileFormat(),
            fileFormats.PPCProjectOLDFileFormat(),
            fileFormats.PSPProjectFileFormat(),
        ]

    def cbtreeview (self, container, widget):
        """
          xxx lacks comment
        """
        self.gantt.set_header_height(self.vistaLista.convert_tree_to_widget_coords(0,1)[1])
        if len (self.modelo) > 0 and self.modelo[0][1] != "":
            self.gantt.set_row_height(self.vistaLista.get_background_area(0,self.vistaLista.columna[0]).height)
            self.vistaLista.disconnect(self.row_height_signal)
        return False

    def enableProjectControls(self, value):
        """
          xxx lacks comment
        """
        self._widgets.get_widget('mnGuardar').set_sensitive(value)
        self._widgets.get_widget('mnGuardarComo').set_sensitive(value)
        self._widgets.get_widget('mnCerrar').set_sensitive(value)
        self._widgets.get_widget('mnAccion').set_sensitive(value)
        self._widgets.get_widget('mnResources').set_sensitive(value)
        self._widgets.get_widget('tbGuardar').set_sensitive(value)
        self._widgets.get_widget('tbCerrar').set_sensitive(value)
        if (not value):
            self._widgets.get_widget('stbStatus').pop(0)
            self._widgets.get_widget('stbStatus').push(0, gettext.gettext("No project file opened"))

    def set_modified(self, value):
        """
          xxx lacks comment
        """
        self._widgets.get_widget('mnGuardar').set_sensitive(value)
        self._widgets.get_widget('mnGuardarComo').set_sensitive(value)
        self._widgets.get_widget('tbGuardar').set_sensitive(value)
        self._widgets.get_widget('stbStatus').pop(0)
        if value:
            self._widgets.get_widget('stbStatus').push(0, gettext.gettext("Project modified"))
        else:
            self._widgets.get_widget('stbStatus').push(0, gettext.gettext("Project without changes"))
   
    def columna_press(self, columna, menu): 
        """
         Muestra los items del menu en la última columna del treeview de 
                  introducción de datos al presionar sobre dicha columna
  
         Parámetros: columna (columna presionada)
                     menu (gtk.Menu)
  
         Valor de retorno: -
        """
        menu.show_all()
        menu.popup(None, None, None, 1, 0)
        for n in range(11):
            self.checkColum[n].connect('activate', self.activarItem, n)
   
   
    def activarItem(self, item, n):
        """
         Activación o desactivación de las columnas según el item 
                  seleccionado en el menu
  
         Parámetros: item (item seleccionado)
                     n (posición en el menu del item seleccionado)
  
         Valor de retorno: -
        """
        if item==self.checkColum[n]:
            if self.checkColum[n].get_active():
                self.vistaLista.columna[n+1].set_visible(True)
            else:
                self.vistaLista.columna[n+1].set_visible(False)
    
    
    
### FUNCIONES DE INTRODUCCIÓN, CARGA Y ACTUALIZACIÓN DATOS

    def introduccionDatos(self):
        """
         Creación de un nuevo proyecto, eliminación de la lista actual y
                  adicción de una fila vacía a la lista
  
         Parámetros: -
         Valor de retorno: -
        """
        self.openFilename = 'Unnamed' 
        self.updateWindowTitle()
        # Se limpian las listas y la interfaz para la introducción de nuevos datos
        self.modelo.clear()   
        self.modeloComboS.clear()
        self.modeloComboARR.clear()
        self.modeloComboARA.clear()
        self.actividad=[]
        self.modeloR.clear()
        self.recurso=[]
        self.modeloAR.clear()
        self.asignacion=[]
        cont=1
        self.modelo.append([cont, '', '', '', '', '', '', '', gettext.gettext('Beta'), ""])  # Se inserta una fila vacia        self.modeloR.append()
        self.modeloAR.append()
        #Minimum schedule
        start_times = graph.get_activities_start_time([], [], [], True)
        self.add_schedule(gettext.gettext("Min"), start_times)
        self.set_schedule(start_times)
        self.enableProjectControls(True)
        self.set_modified(True)
        self.modified = 1
        self.ntbSchedule.show()
  
    def col_edited_cb( self, renderer, path, new_text, modelo, n):
        """
         Edicción de filas y adicción de una fila vacía  
                  cuando escribimos sobre la última insertada
  
         Parámetros: renderer (celda)
                     path (fila)
                     new_text (nuevo texto introducido)
                     modelo (interfaz)
                     n (columna)
  
         Valor de retorno: -
        """
        self.modified=1   # Controlamos que el proyecto ha cambiado
        self.set_modified(True)
        cont=int(path)+1
        #print "cambio '%s' por '%s'" % (modelo[path][n], new_text) 
          
        actividades=self.actividades2Lista()
        # Controlamos la introduccion de las siguientes
        if modelo==self.modelo:  # Interfaz de actividades
            # añadimos las etiquetas de las actividades al selector de las siguientes
            if n==1:  # Columna de las actividades
                if new_text=='':
                    modelo[path][1] = new_text
                else:
                    if modelo[path][1]!='':  # Si modificamos una actividad
                        if new_text not in actividades:  # Si no está introducida                     
                            #print modelo[path][1], new_text, 'valores a intercambiar'
                            modelo=self.modificarSig(modelo, modelo[path][1], new_text)
                            self.gantt.rename_activity(modelo[path][1],new_text)
                            self.gantt.update()
                            for row in self.asignacion:
                                if row[0] == modelo[path][1]:
                                    row[0] = new_text
                            for row in self.modeloAR:
                                if row[0] == modelo[path][1]:
                                    row[0] = new_text
                            modelo[path][1] = new_text
                            it=self.modeloComboS.get_iter(path)
                            self.modeloComboS.set_value(it, 0, new_text)
                            it=self.modeloComboARA.get_iter(path)
                            self.modeloComboARA.set_value(it, 0, new_text)
                        #else:
                            #print 'actividad repetida'
                            #self.dialogoError('Actividad repetida')
                                
                    else:  # Se inserta normalmente
                        modelo[path][1] = new_text
                        self.modeloComboS.append([modelo[path][1]])
                        self.modeloComboARA.append([modelo[path][1]])
                        self.gantt.add_activity(new_text)
                        self.gantt.update()
      
      
            elif n==2:  # Columna de las siguientes
                modelo=self.comprobarSig(modelo, path, new_text)
    
            elif n > 7:
                modelo[path][n-1] = new_text
            else:
                modelo[path][n] = new_text
                
        elif modelo == self.modeloR and n == 0:
            if new_text!='':
                if modelo[path][1]!='':  # Si modificamos un recurso
                    try:
                        it=self.modeloComboARR.get_iter(path)
                        self.modeloComboARR.set_value(it, 0, new_text)
                    except:
                        self.modeloComboARR.append([new_text])
                else:  # Se inserta normalmente
                    self.modeloComboARR.append([new_text])
            modelo[path][0] = new_text
        else:  # Otras interfaces 
            modelo[path][n] = new_text
                    
        iterador=modelo.get_iter(path)
        proximo=modelo.iter_next(iterador)
        if proximo==None:  #si estamos en la última fila, insertamos otra vací­a
            cont+=1
            # Actividades
            if modelo==self.modelo:                
                if len(modelo)!=len(self.actividad): #siempre debe existir un elemento más en modelo que en actividades     
                    modelo.append([cont, '', '', '', '', '', '', '', gettext.gettext('Beta'),""])     
                    fila=['', '', [], '', '', '', '', '', gettext.gettext('Beta'),0]
                    self.actividad.append(fila) 
                else:
                    modelo.append([cont, '', '', '', '', '', '', '', gettext.gettext('Beta'),""])
                    #print self.actividad 
                     
            # Recursos
            elif modelo==self.modeloR:  
                modelo.append()  
                filaR=['', '', '', '']
                self.recurso.append(filaR)
                   
            # Recursos necesarios por actividad
            else:
                modelo.append()
                filaAR=['', '', '']
                self.asignacion.append(filaAR)
                   
        # Actualizamos las listas con los nuevos datos introducidos
        self.actualizacion(modelo, path, n)
        return

    def reorder_gantt(self, dummy1 = 0, dummy2 = 0, dummy3 = 0, dummy4 = 0 ):
        act_list = []
        for activity in self.modelo:
            if activity[1] != "":
                act_list.append(activity[1])
        self.gantt.reorder(act_list)
        self.gantt.update()
  
    def actualizacion(self, modelo, path, n):
        """
         Actualización de las tres listas con los nuevos datos introducidos 
                  (lista de actividades, de recursos y de asignacion)
  
         Parámetros: modelo (interfaz)
                     path (fila)
                     n (columna)
         
         Valor de retorno: -
        """
        # Actividades
        if modelo==self.modelo:
            gantt_modified = False
            if self.modelo[path][n]=='':
                if n==2:
                    self.actividad[int(path)][2]=[]
                    self.gantt.set_activity_prelations(self.actividad[int(path)][1], [])
                    gantt_modified = True
                else:
                    self.actividad[int(path)][n]=self.modelo[path][n]
            else: # Si hay datos introducidos
                # Si se introduce la duración optimista, pesimista o mas probable
                if n in range(3, 6):   
                    self.actividad[int(path)][n]=float(self.modelo[path][n])
                    if self.modelo[path][3]!='' and self.modelo[path][4]!='' and self.modelo[path][5]!='':
                        a=float(self.modelo[path][3]) #d.optimista
                        b=float(self.modelo[path][5]) #d.pesimista
                        m=float(self.modelo[path][4]) #d.más probable
                     
                        # Se comprueba que las duraciones sean correctas
                        ok=self.comprobarDuraciones(a, b, m)   
   
                        if ok:  #se actualizan la media y la desviación tí­pica
                            self.actualizarMediaDTipica(path, self.modelo, self.actividad, a, b, m)
                            
                        else:  #se emite un mensaje de error
                            dialogo=gtk.Dialog(gettext.gettext("Error!!"), None, gtk.MESSAGE_ERROR, (gtk.STOCK_OK, gtk.RESPONSE_OK))
                            label=gtk.Label(gettext.gettext('Wrong durations introduced.'))
                            dialogo.vbox.pack_start(label,True,True,10)
                            label.show()
                            respuesta=dialogo.run()
                            dialogo.destroy()
 
                            self.modelo[path][6]=self.actividad[int(path)][6]=''
                        self.gantt.set_activity_duration(self.modelo[path][1], float(self.modelo[path][6]))
                        gantt_modified = True
                              
                # Si se introduce la media, se elimina el resto de duraciones        
                elif n==6:   
                    self.actividad[int(path)][n]=float(self.modelo[path][n])
                    for i in range(3, 6):
                        self.modelo[path][i]=''
                        self.actividad[int(path)][i]=''
                    self.gantt.set_activity_duration(self.modelo[path][1], float(self.modelo[path][6]))
                    gantt_modified = True
  
                # Si se modifica el tipo de distribución, se actualizan la media y la desviación tí­pica
                elif n==8:  
                    self.actividad[int(path)][8]=self.modelo[path][8]
                    if self.modelo[path][3]!='' or self.modelo[path][4]!='' or self.modelo[path][5]!='':
                        a=float(self.modelo[path][3]) #d.optimista
                        b=float(self.modelo[path][5]) #d.pesimista
                        m=float(self.modelo[path][4]) #d.más probable
                        self.actualizarMediaDTipica(path, self.modelo, self.actividad, a, b, m)
                        self.gantt.set_activity_duration(self.modelo[path][1], float(self.modelo[path][6]))
                        gantt_modified = True                 
   
                # Se controla el valor introducido en las siguientes 
                elif n==2:  
                    if self.modelo[path][2]==self.actividad[int(path)][1]:
                        self.modelo[path][2]==''
                        self.actividad[int(path)][2]=[]
                    else: 
                        self.actividad[int(path)][2] = self.actString2actList(self.modelo[path][2])
                        self.gantt.set_activity_prelations(self.actividad[int(path)][1], self.actString2actList(self.modelo[path][2]))
                        gantt_modified = True
                elif n==9:
                    self.schedules[self.ntbSchedule.get_current_page()][1][modelo[path][1]] = float(self.modelo[path][9])
                    gantt_modified = True
                # Si no es ningún caso de los anteriores, se actualiza normalmente
                else:
                    self.actividad[int(path)][n]=self.modelo[path][n]
 
        # Recursos 
        elif modelo == self.modeloR:
            if n == 0:
                for index in range(len(self.asignacion)):
                    if self.asignacion[index][1] == self.recurso[int(path)][0]:
                        self.asignacion[index][1] = self.modeloR[path][n]
                        self.modeloAR[index][1] = self.modeloR[path][n]
            self.recurso[int(path)][n] = self.modeloR[path][n]
            # Si el recurso es Renovable    
            if self.modeloR[path][1] == gettext.gettext('Renewable'):
                if n == 2:
                    self.dialogoRec(gettext.gettext('Renewable'))
                self.recurso[int(path)][2] = self.modeloR[path][2] = ''
            # Si el recurso es No Renovable    
            elif self.modeloR[path][1] == gettext.gettext('Non renewable'):
                if n == 3:
                    self.dialogoRec(gettext.gettext('Non renewable'))
                self.recurso[int(path)][3] = self.modeloR[path][3] = ''
            # Si el recurso es Ilimitado
            elif self.modeloR[path][1] == gettext.gettext('Unlimited'):
                if n == 2 or n == 3:
                    self.dialogoRec(gettext.gettext('Unlimited'))
                self.recurso[int(path)][3] = self.modeloR[path][3] = self.recurso[int(path)][2] = self.modeloR[path][2] = ''

        # Recursos necesarios por actividad
        else:
            self.asignacion[int(path)][n] = self.modeloAR[path][n]
   
            #print self.asignacion
        if gantt_modified == True:
            act_list = []
            dur_dic = {}
            pre_dic = {}
            for i in range(len(self.actividad)):
                act_list.append(self.actividad[i][1])
                dur_dic[self.actividad[i][1]] = float(self.actividad[i][6] if self.actividad[i][6] != "" else 0)
                pre_dic[self.actividad[i][1]] = self.actividad[i][2]
            if n == 9:
                self.schedules[self.ntbSchedule.get_current_page()][1] = graph.get_activities_start_time(act_list, dur_dic, pre_dic, self.ntbSchedule.get_current_page() == 0, self.schedules[self.ntbSchedule.get_current_page()][1], modelo[path][1])
            elif n == 2:
                self.schedules[0][1] = graph.get_activities_start_time(act_list, dur_dic, pre_dic, True, self.schedules[0][1])
            else:
                self.schedules[0][1] = graph.get_activities_start_time(act_list, dur_dic, pre_dic, True, self.schedules[0][1], modelo[path][1])
                for index in range(1, len(self.schedules)):
                    self.schedules[index][1] = graph.get_activities_start_time(act_list, dur_dic, pre_dic, False, self.schedules[index][1], modelo[path][1])
            self.set_schedule(self.schedules[self.ntbSchedule.get_current_page()][1])
   
   
    def actualizarMediaDTipica(self, path, modelo, actividad, a, b, m):
        """
         Actualización de la media y la desviación típica 
  
         Parámetros: path (fila)
                     modelo (interfaz)
                     actividad (lista de actividades)
                       a (duración optimista)
                 b (duración pesimista)
                 m (duración más probable)
  
         Valor de retorno: -
        """
        # Si la distribución es Normal, se dejan las celdas vacías para la introducción manual de los datos
        if modelo[path][9]==gettext.gettext('Normal'):  
            modelo[path][6]=actividad[int(path)][6]=''
            modelo[path][7]=actividad[int(path)][7]=''

        # Si la distribución no es Normal, se recalculan los valores
        else:  
            media, dTipica=self.calcularMediaYDTipica(modelo[path][9], a, b, m)
            m='%4.3f'%(media)
            actividad[int(path)][6]=modelo[path][6]=m
            dT='%4.3f'%(dTipica)
            actividad[int(path)][7]=modelo[path][7]=dT 

    def comprobarSig(self, modelo, path, new_text):
        """
         Control de la introducción de las siguientes  

         Parámetros: modelo (interfaz)
                     path (fila)
                     new_tex (nuevo texto introducido)

         Valor de retorno: modelo (interfaz)
        """
        # Se introducen en una lista las etiquetas de las actividades
        actividades=self.actividades2Lista()

    # Se pasa a una lista las actividades que tengo como siguientes antes de la modificación
        anterior=self.actString2actList(modelo[path][2]) 
        #print anterior, 'anterior' 

        # Se pasa el nuevo texto a una lista
        modificacion=self.actString2actList(new_text)
        #print modificacion, 'modificacion'
        if modificacion==[""]:  # Si no se introduce texto (estamos borrando todas las siguientes)
            modelo[path][2] = ''

        else:  # Se introduce texto
            if len(modificacion)==1:  # Si se introduce un sólo dato (es seleccionado del selector, introducido manualmente ó se intentan borran todos las siguientes menos esa)
                if modificacion[0] in actividades:  # Si esa etiqueta existe como actividad
                    if modificacion[0]!=modelo[path][1]: # Si no coincide con su etiqueta 
                        if modificacion[0] not in anterior: # Si no se encuentra ya introducida como siguiente, la añadimos 
                            self.insertamosSiguiente(modelo, path, modificacion[0])
  
                        else: # Si se encontraba anteriormente, lo más probable es que se intenten borrar todas las siguientes excepto esa
                            modelo[path][2] = modificacion[0]
                            self.actividad[int(path)][2]=modelo[path][2]
             
            else:  # Al intentar introducir más de un elemento, estoy añadiendo manualmente o intentando borrar
                c=0  # Controla condiciones erróneas
                d=0  #    "         "           "
                for n in modificacion:  # Analizamos cada siguiente de la lista de modificacion
                    if n not in actividades:  # Si esa etiqueta existe como actividad 
                        c+=1
                    else:
                        if n==modelo[path][1]:  # Si coincide con su etiqueta 
                            c+=1
                        else:
                            if n in anterior:  # Si se encuentra ya introducida como siguiente
                                d+=1
                 
                if c==0: # Si no se da ninguno de los dos primeros casos
                    cadena=self.lista2Cadena2(modificacion) # Pasamos la lista a cadena para mostrarla en la interfaz
                    if d!=0:  # Si se da el último caso, se sobreescribe
                        modelo[path][2] = cadena
                        self.actividad[int(path)][2]=modelo[path][2]
                    else: # Si todo es correcto, se añade normalmente
                        self.insertamosSiguiente(modelo, path, cadena)    
       
        return modelo


    def modificarSig(self, modelo, original, nuevo):
        """
        Al modificar la etiqueta de alguna actividad, se modifica  
                 también cuando ésta sea siguiente de alguna otra actividad

        Parámetros: modelo (interfaz) 
                    original (etiqueta original)
                    nuevo (etiqueta nueva)

        Valor de retorno: modelo (interfaz modificada)
        """
        for a in range(len(self.actividad)):
            if original in self.actividad[a][2]: # Si original está como siguiente de alguna actividad
                #print '1'
                if len(self.actividad[a][2])==1: # Si original es la única siguiente, se modifica por nuevo
                    #print '2'
                    modelo[a][2]=nuevo
                    self.actividad[a][2]=self.actString2actList(nuevo)
 
                else: # Si original no es la única siguiente
                    for m in range(len(self.actividad[a][2])):
                        if original==self.actividad[a][2][m]: # La siguiente que coincida con original, se modifica por nuevo
                            #print '3'
                            self.actividad[a][2][m]=nuevo
                            modelo[a][2]=self.lista2Cadena2(self.actividad[a][2])
  
        return modelo
   

    def add_schedule(self, name , sch_dic):
        if name == None:
            name = "P" + str(len(self.schedules))
        self.schedules.append([name, sch_dic])
        label = gtk.Label(name)
        self.schedule_tab_labels.append(label)
        fixed = gtk.Fixed()
        self.ntbSchedule.append_page(fixed, label)
        fixed.show()
        label.show()
        self.set_modified(True)
        self.modified = 1

    def set_schedule(self, schedule):
        for row in self.modelo:
            if row[1] != "":
                row[9] = schedule[row[1]]
        for row in self.actividad:
            row[9] = schedule[row[1]]
            self.gantt.set_activity_start_time(row[1], row[9])
        self.gantt.update()
  
    def actualizarColSig(self, datos):
        """
         Actualización de la columna de las siguientes en   
                  la interfaz para los proyectos con extensión '.prj'

         Parámetros: datos (lista que almacena los datos de 
                            las actividades)

         Valor de retorno: -
        """
        for m in range(len(self.modelo)):
            if datos[m][2]==[]:
                self.modelo[m][2]=''
            else:
                s=''
                for n in datos[m][2]:
                    if s!='':
                        s+=', '
                        s+=n
                    else:
                        s+=n 
                    self.modelo[m][2]=s


    def actualizarColR(self, columnaRec):
        """
         Actualización de la columna de recursos en la lista de    
                  actividades y en la interfaz

         Parámetros: columnaRec (lista que almacena una lista por
                           cada actividad con la relacion 
                           actividad-recurso-unidad necesaria)

         Valor de retorno: -
        """
        # Se actualiza la lista de actividades
        for n in range(len(self.actividad)):
            self.actividad[n][8]=columnaRec[n]

        # Se actualiza la interfaz
        for m in range(len(columnaRec)):
            cadena=self.lista2Cadena(columnaRec, m)
            self.modelo[m][8]=cadena
        self.sumarUnidadesRec(self.asignacion)



#                    PSPLIB                        

     
    def actualizarColSigPSPLIB(self, prelacion):
        """
Actualización de la columna de las siguientes en   
        la interfaz para los proyectos de la librería PSPLIB

Parámetros: prelacion (lista que almacena las actividades 
                              y sus siguientes)

Valor de retorno: -
        """   
        longitud=len(prelacion)
        for m in range(len(self.modelo)):
            if prelacion[m]!=prelacion[0] and prelacion[m]!=prelacion[longitud-1]:
                s=''
                if prelacion[m][1]==[str(longitud)]: 
                        #print 'entra'
                    self.modelo[m][2]=''
                else: 
                    s=self.lista2Cadena2(prelacion[m][1])
                    self.modelo[m-1][2]=s


# FUNCIONES DE COMPROBACIÓN #
     
    def comprobarDuraciones(self, a, b, m):
        """
Comprobación de que los tiempos optimista, pesimista y
         más probable son correctoso

Parámetros: a (d.optimista)
            b (d.pesimista)
            m (d.mas probable)

Valor de retorno: 0 (valores incorrectos)
                  1 (valores correctos)
        """
        if ( (a<b and m<=b and m>=a) or (a==b and b==m)):
            return 1 
        else:
            return 0


    def actividadesRepetidas(self, actividad):
        """
 Comprueba si se han introducido actividades repetidas 

 Parámetros: actividad (lista de actividades)

 Valor de retorno: error (0 si no hay error
                          1 si hay error) 
                   repetidas (lista de actividades repetidas)
        """
        error=0
        actividades=[]
        repetidas=[]
        # Si nos encontramos alguna repetida, la metemos en una lista
        for n in range(len(actividad)):
            if actividad[n][1] not in actividades:
                actividades.append(actividad[n][1])
            else:
                repetidas.append(actividad[n][1])
                error=1

        return error, repetidas


    def comprobarActExisten(self, actividad):
        """
Comprobación de que las actividades 
          introducidas en la ventana 'recursos necesarios por 
          actividad' existen

Parámetros: actividad (lista de actividades)

Valor de retorno: error (0 si no hay error
                         1 si hay error) 
        """
        error=0
        actividades=[]
        for n in range(len(actividad)):
            actividades.append(actividad[n][1])

        # Si alguna actividad no existe, se añade a una lista
        actividadesErroneas=[]
        for fila in self.asignacion:
            if fila[0] not in actividades:
                error=1
                actividadesErroneas.append(fila[0])

        # Se imprime un mensaje de error con las actividades erróneas
        if actividadesErroneas!=[]:
            self.errorRecNecAct(actividadesErroneas, gettext.gettext('Activity'))  
  
        return error


    def comprobarRecExisten(self, recurso):
        """
Comprobación de que los recursos
         introducidos en la ventana 'recursos necesarios por 
         actividad' existen

Parámetros: recurso (lista de recursos)

Valor de retorno: error (0 si no hay error
                         1 si hay error) 
        """
        error=0
        recursos=[]
        for n in range(len(recurso)):
            recursos.append(recurso[n][0])

        # Si alguna actividad no existe, se añade a una lista
        recursosErroneos=[]
        for fila in self.asignacion:
            if fila[1] not in recursos:
                error=1
                recursosErroneos.append(fila[1])

        # Se imprime un mensaje de error con las actividades erróneas
        if recursosErroneos!=[]:
            self.errorRecNecAct(recursosErroneos, gettext.gettext('Resource'))

        return error

        
# OTRAS FUNCIONES #
 
    def sumarUnidadesRec(self, asignacion):
        """
Suma de las unidades de recurso disponibles
         por proyecto usadas por las actividades

Parámetros: asignacion (lista que almacena actividad,
                        recurso y unidades necesarias por actividad)

Valor de retorno: unidadesRec (lista que contiene el recurso y la suma de 
                              las unidades de dicho recurso disponibles 
                              por proyecto usadas por las actividades)
        """
        unidadesRec=[]
        for n in range(len(self.recurso)): 
            if self.recurso[n][1]==gettext.gettext('Non renewable') or self.recurso[n][1]==gettext.gettext('Double constrained'):
                cont=0
                recurso=self.recurso[n][0]
                for m in range(len(asignacion)):
                    if asignacion[m][1]==recurso:
                        cont+=int(asignacion[m][2])
                        conjunto=[recurso, cont]
                unidadesRec.append(conjunto)
        #print unidadesRec
        return unidadesRec

    
    def mostrarRec(self, asignacion, num): 
        """
 Almacenamiento en una lista de listas (filas) las relaciones entre    
          actividades, recursos y unidades de recurso 
          necesarias por actividad

 Parámetros: asignacion (lista que almacena actividad,
                         recurso y unid. necesarias por act.)
             num (0: fichero con extensión '.sm'
                  1: fichero con extensión '.prj')

 Valor de retorno: mostrarR (lista que almacena una lista por
                  cada actividad con la relacion 
                  actividad-recurso-unidad necesaria)
        """
        mostrarR=[]
        i=asignacion.index(asignacion[0])
        # Si el archivo tiene extensión '.sm' (PSPLIB)
        if num==0:  
            i+=2  
            for m in range(i, len(self.actividad)+i):
                mostrarR.append(self.colR(m, asignacion, 0))

        # Si el archivo tiene extensión '.prj'
        else:   
            for m in range(i, len(self.actividad)+i):
                mostrarR.append(self.colR(m, asignacion, 1))

        return mostrarR

     
    def colR(self, m, asignacion, num):
        """
         Extracción en una lista las relaciones entre    
                  actividades, recursos y unidades de recurso 
                  necesarias por actividad

         Parámetros: m (fila)
                     asignacion (lista que almacena actividad,
                                 recurso y unidades necesarias por actividad)
                     num (0: fichero con extensión '.sm'
                          1: fichero con extensión '.prj')

         Valor de retorno: mostrar (lista que almacena una lista por
                           cada actividad con la relacion 
                           actividad-recurso-unidad necesaria)
        """
        mostrar=[]
        for n in range(len(asignacion)): 
            # Si el archivo tiene extensión '.sm' (PSPLIB)   
            if num==0:     
                if int(asignacion[n][0])==m:
                    f='%s(%5.2f)'%(asignacion[n][1], float(asignacion[n][2]))
                    mostrar.append(f)

            # Si el archivo tiene extensión '.prj'
            else:        
                if asignacion[n][0]==self.actividad[m][1]:
                    f='%s(%5.2f)'%(asignacion[n][1], float(asignacion[n][2]))
                    mostrar.append(f)
        m+=1

        return mostrar


    def insertamosSiguiente(self, modelo, path, texto):
        """
        Se inserta una o varias actividades siguientes  

        Parámetros: modelo (interfaz)
                    path (fila)
                    texto (nuevo texto a introducir)

        Valor de retorno: -
        """
        if self.actividad[int(path)][2]!=[]:  # Si hay alguna siguiente colocada
            modelo[path][2] = modelo[path][2] + ', ' + texto
            self.actividad[int(path)][2]=modelo[path][2] 
        else:
            modelo[path][2] = texto
            self.actividad[int(path)][2]=modelo[path][2]


    def lista2Cadena(self, listaCadenas, m):
        """
        xxx Puede eliminarse??
         Pasa una lista de listas a formato cadena

         Parámetros: listaCadenas (lista de listas)
             m (posición)

         Valor de retorno: cadena (cadena resultado)
        """
        return ', '.join(listaCadenas[m])

    def lista2Cadena2(self, lista):
        """
        xxx Puede eliminarse??
         Pasa una lista a formato cadena

         Parámetros: lista (lista)

         Valor de retorno: cadena (cadena resultado)
        """
        return ', '.join(lista)           
   
    def actString2actList(self, s):
        """
        xxx Puede eliminarse??
         Splits activities separated in a string by ','
         Returns: list of activity names
        """
        return [a.strip() for a in s.split(',')]


    def actividades2Lista(self):
        """
         Introduce en una lista todas las etiquetas de las actividades  
         Valor de retorno: listaAct (lista de actividades)
        """
        return [n[1] for n in self.actividad]

     
    def calcularMediaYDTipica(self, distribucion, a, b, m):
        """
         Cálculo de la media y la desviación típica a partir de la distribución, 
                  del tiempo optimista, pesimista y más probable 

         Parámetros: distribucion (tipo de distribución)
                     a (d.optimista)
                     b (d.pesimista)
                     m (d.más probable)

         Valor de retorno: media (media calculada)
                           dTipica (desviación típica calculada)
        """
        # Si el tipo de distribución es Beta
        if distribucion==gettext.gettext('Beta'):
            #print 'beta'
            media=(a+b+4.0*m)/6.0
            dTipica=(b-a)/6.0

        # Si el tipo de distribución es Triangular
        elif distribucion==gettext.gettext('Triangular'):
            #print 'triangular'
            media=(a+b+m)/3.0
            dTipica=(a**2.0+b**2.0+m**2.0-a*b-a*m-b*m)/18.0

        # Si el tipo de distribución es Uniforme
        else: 
            #print 'uniforme'
            media=(a+b)/2.0
            dTipica=((b-a)**2.0)/12.0

        # NOTA: La media y la desviación típica de la distribución Normal
        #       no se calculan, se deben introducir manualmente

        return media, dTipica


    def mostrarTextView(self, widget, valor):
        """
         Muestra datos en el Text View correspondiente 

         Parámetros: widget (lugar donde mostrar el dato)
                     valor (dato a mostrar)

         Valor de retorno: -
        """
        bufer=gtk.TextBuffer()
        widget.set_buffer(bufer)
        iterator=bufer.get_iter_at_line(0)
        bufer.set_text(valor) 
                    

    def updateWindowTitle(self):
        """
        Updates window title (should be called when open file changes)
        """
        if self.openFilename:
            basename = os.path.basename(self.openFilename)
            path = self.openFilename[:-(len(basename)+1)]
            if path=='': 
                self.vPrincipal.set_title(basename + ' - PPC-Project')
            else:
                self.vPrincipal.set_title(basename + ' (' + path + ')' + ' - PPC-Project')
        else:
            self.vPrincipal.set_title('PPC-Project')
               
### FUNCIONES VENTANAS DE ACCIÓN

# GRAFO PERT                     
    def pertFinal(self):
        """
         Creación del grafo Pert numerado en orden
         Valor de retorno: grafoRenumerado (grafo final)
        """
        successors = self.tablaSucesoras(self.actividad)
        grafo = pert.Pert()
        grafo.pert(successors)
        grafoRenumerado = grafo.renumerar()
        return grafoRenumerado

    def tablaSucesoras(self, actividades):
        """
         Obtiene un diccionario que contiene las actividades 
                  y sus sucesoras  

         Parámetros: actividades (lista de actividades)

         Valor de retorno: successors(diccionario con las actividades y sus sucesoras)
        """
        successors={}
        for n in range(len(actividades)):
            successors[actividades[n][1]]=actividades[n][2]
        return successors
                 

    
#          ZADERENKO                     
    def ventanaZaderenko(self):
        """
         Acción usuario para calcular todos los datos relacionados con Zaderenko 
         Valor de retorno: -
        """
        informacionCaminos=[]

        # Se crea el grafo Pert y se renumera
        grafoRenumerado=self.pertFinal()

        # Nuevos nodos
        nodosN=[]
        for n in range(len(grafoRenumerado.graph)):
            nodosN.append(n+1)
 
        # Se calcula la matriz de Zaderenko
        matrizZad=mZad(self.actividad,grafoRenumerado.activities, nodosN, 1, []) 

        # Se calculan los tiempos early y last
        tearly=early(nodosN, matrizZad)      
        tlast=last(nodosN, tearly, matrizZad)  

        # duración del proyecto
        tam=len(tearly)
        duracionProyecto=tearly[tam-1]
        #print duracionProyecto, 'duracion proyecto'            

        # Se buscan las actividades que son crí­ticas, que serán aquellas cuya holgura total sea 0
        holguras=self.holguras(grafoRenumerado.activities, tearly, tlast, []) 
        #print holguras, 'holguras'
        actCriticas=self.actCriticas(holguras, grafoRenumerado.activities)
        #print 'actividades criticas: ', actCriticas
       
        # Se crea un grafo sólo con las actividades crí­ticas y se extraen los caminos del grafo (todos serán crí­ticos)
        caminosCriticos=self.grafoCriticas(actCriticas) 
        #print caminosCriticos, 'caminos criticos'

        # Se extraen todos los caminos (crí­ticos o no) del grafo original
        successors = self.tablaSucesoras(self.actividad)
        g=graph.roy(successors)
        # Se eliminan 'begin' y 'end' de todos los caminos
        caminos=[c[1:-1]for c in graph.findAllPaths(g, 'Begin', 'End')]
        #print 'caminos', caminos

        # Se marca con 1 los caminos crí­ticos en todos los caminos del grafo, el resto se marca con 0
        criticos=self.caminosCriticos(caminos, caminosCriticos)  
        #print criticos, 'vector criticos'

        # Se crea una lista con los caminos, sus duraciones y sus desviaciones tí­picas
        for camino in caminos:   
            media, dTipica=self.mediaYdTipica(camino) 
            info=[camino, media, dTipica]      
            informacionCaminos.append(info)
        #print 'caminos, duraciones y dt: ', informacionCaminos

        # Se muestran Zaderenko y los caminos en la interfaz
        #self.zaderenko(tearly, tlast, nodosN, matrizZad)

        #Creating Zaderenko Matrix model
        previous_model = self.zadViewList.get_model()
        if previous_model != None:
            previous_model.clear()
        columns_type = [str] * (len(nodosN) + 3)
        zad_model = gtk.ListStore(*columns_type)
        self.zadViewList.set_model(zad_model)
        for column in self.zadViewList.get_columns():
            self.zadViewList.remove_column(column)
        for node in range(len(nodosN)):
            row = []
            row.append(str(tearly[node]))
            row.append(str(nodosN[node]))
            for nodes in range(len(nodosN)):
                row.append(str(matrizZad[node][nodes]))
            row.append(str(tlast[node]))
            zad_model.append(row)
        #Early Column
        column = gtk.TreeViewColumn(gettext.gettext("Early"))
        self.zadViewList.append_column(column)
        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, 'text', 0)
        column.set_min_width(50)
        #Activities Column
        column = gtk.TreeViewColumn(gettext.gettext("Node"))
        self.zadViewList.append_column(column)
        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, 'text', 1)
        column.set_min_width(50)
        for node in range(len(nodosN)):
            column = gtk.TreeViewColumn(str(nodosN[node]))
            self.zadViewList.append_column(column)
            cell = gtk.CellRendererText()
            column.pack_start(cell, False)
            column.add_attribute(cell, 'text', 2 + node)
            column.set_min_width(50)
        #Last Column
        column = gtk.TreeViewColumn(gettext.gettext("Last"))
        self.zadViewList.append_column(column)
        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, 'text', len(nodosN) + 2)
        column.set_min_width(50)
        self.mostrarCaminosZad(self.modeloZ, criticos, informacionCaminos)
        self.vZaderenko.hide()
        self.vZaderenko.show()


    def mostrarCaminosZad(self, modelo, criticos, informacionCaminos):
        """
 Muestra los caminos del grafo en la interfaz (ventana Zaderenko)

 Parámetros: modelo (lista donde se muestran los caminos)
             criticos (lista caminos criticos)
             informacionCaminos (lista caminos del grafo, sus duraciones
                          y sus desviaciones tí­picas)

 Valor de retorno: -
        """
        #Se cambia el formato de los caminos para mostrarlos en la interfaz
        camino=[]
        for n in range(len(informacionCaminos)):
            s=''
            for c in informacionCaminos[n][0]:
                if s!='':
                    s+=' -> '
                    s+=str(c)
                else:
                    s+=str(c)
            camino.append(s)
 
        # Se muestra la información de los caminos en la interfaz 
        modelo.clear()
        for n in range(len(camino)):
            # El camino es crí­tico
            if criticos[n]==1: 
                modelo.append([informacionCaminos[n][1], informacionCaminos[n][2], camino[n], True])

            # El camino no es crí­tico                      
            else:
                modelo.append([informacionCaminos[n][1], informacionCaminos[n][2], camino[n],  False])

        #Se pintan de amarillo los caminos crí­ticos para distinguirlos de los no crí­ticos
        for m in range(3):  
                #self.vistaListaZ.renderer[m].set_property('cell-background', 'lightGoldenRodYellow')                    
            self.vistaListaZ.renderer[m].set_property('cell-background', 'LightCoral')
            self.vistaListaZ.columna[m].set_attributes(self.vistaListaZ.renderer[m], text=m, cell_background_set=3)
        
           
   
    def actCriticas(self, holguras, actividadesGrafo):  
        """
         Cálculo de las actividades criticas 

         Parámetros: holguras (lista con las hoguras de cada actividad)
                     actividadesGrafo (etiqueta actividades, nodo inicio y fí­n)

         Valor de retorno: criticas (lista de actividades criticas)
        LAS ACTIVIDADES CRITICAS SON AQUELLAS CUYA HOLG. TOTAL ES 0
        """
        actividades=actividadesGrafo.values()         
        nuevas=[]
        for n in range(len(actividadesGrafo)):
            nuevas.append(round(float(holguras[n][1])))
        #print nuevas
        criticas=[]
        for n in range(len(actividadesGrafo)):
            #if holguras[n][1]=='%5.2f'%(0):
            if nuevas[n] == 0.0:
            #print actividades[n]
                a=actividades[n]
                criticas.append(a)
        return criticas

  
    def grafoCriticas(self, actCriticas):
        """
         Creación de un grafo sólo con actividades crí­ticas y extracción de
                  los caminos de dicho grafo, que serán todos crí­ticos 

         Parámetros: actCriticas (lista de actividades crí­ticas)

         Valor de retorno: caminosCriticos (lista de caminos crí­ticos)
        """
        # Se crea un grafo con las activididades crí­ticas y se extraen los caminos de dicho grafo, que serán crí­ticos
        sucesorasCriticas=self.tablaSucesorasCriticas(actCriticas)
        gCritico=graph.roy(sucesorasCriticas)
        #print gCritico
        caminosCriticos=[]
        caminos=graph.findAllPaths(gCritico, 'Begin', 'End')

        # Se eliminan 'begin' y 'end' de todos los caminos
        caminosCriticos=[c[1:-1]for c in caminos]

        return caminosCriticos


    def tablaSucesorasCriticas(self, criticas):
        """
         Obtiene un diccionario que contiene las actividades 
                  crí­ticas y sus sucesoras  

         Parámetros: criticas (lista de actividades crí­ticas)

         Valor de retorno: sucesorasCriticas(diccionario que almacena 
                           las actividades críticas y sus sucesoras)
        """
        cr=[]
        for n in criticas:
            cr.append(n[0])
        #print cr, 'cr'

        sucesorasCriticas={}
        for n in cr:
            for m in range(len(self.actividad)):
                if n==self.actividad[m][1]:
                    for a in self.actividad[m][2]:
                        if a in cr:
                            if n not in sucesorasCriticas:
                                sucesorasCriticas[n]=[a]
                            else:
                                sucesorasCriticas[n].append(a)

            if n not in sucesorasCriticas:  
                sucesorasCriticas[n]=[]

        return sucesorasCriticas


    def caminosCriticos(self, caminos, caminosCriticos):
        """
         Búsqueda de los caminos criticos en todos los caminos
                  del grafo. Se marca con un 1 los crí­ticos y con un 0
                  los no crí­ticos

         Parámetros: caminos (lista todos los caminos)
                     caminosCriticos (lista caminos criticos)

         Valor de retorno: criticos (lista con los caminos marcados)
        """
        # Se buscan los caminos criticos entre todos los caminos y se marca en la lista con un 1
        # Esta lista de 0 y 1 nos servirá para saber cuáles son los criticos a la hora de mostrarlos

        # Inicializamos la lista a 0
        criticos=[]
        for n in range(len(caminos)):
            c=0
            criticos.append(c)

        # Marcamos con 1 los que sean crí­ticos
        for i in range(len(caminos)):
            for j in range(len(caminosCriticos)):
                if caminos[i]==caminosCriticos[j]:
                    #print i, j, 'critico: ', caminosCriticos[j]
                    criticos[i]=1

        return criticos


    def mediaYdTipica(self, camino):
        """
         Cálculo de la duración media y la desviación tí­pica
                  de un camino del grafo

         Parámetros: camino (camino del grafo)

         Valor de retorno: d (duración media)
                           t (desviación tí­pica)
        """
        # Se calcula la duración de cada camino. Se suman las duraciones de
        # todas las actividades que forman dicho camino.

        d=0
        for a in camino:
            for n in range(len(self.actividad)):
                if a==self.actividad[n][1] and self.actividad[n][6]!='':
                    d+=float(self.actividad[n][6])
                else:  #controlamos las ficticias
                    d+=0
        #print d

        # Se calcula la desviación típica de cada camino. Se suman las desviaciones
        # tí­picas de todas las actividades que forman dicho camino.

        t=0
        for a in camino:
            for n in range(len(self.actividad)):
                if a==self.actividad[n][1] and self.actividad[n][7]!='':
                    t+=float(self.actividad[n][7])
                else:  #controlamos las ficticias
                    t+=0
        #print t

        return '%5.2f'%(d), '%5.2f'%(t)
    

#              ACTIVIDADES                 

    def mostrarActividades(self, modelo, actividadesGrafo, grafo):
        """
         Acción usuario para mostrar la etiqueta de cada actividad con su
                  nodo inicio y fin en la interfaz

         Parámetros: modelo (interfaz)
                     actividadesGrafo (etiqueta actividades, nodo inicio y fí­n)
                     grafo (grafo Pert)

         Valor de retorno: -
        """
        self.vActividades.show()         

        # Se muestran las actividades y sus nodos inicio y fin
        modelo.clear()
        for g in actividadesGrafo:
            modelo.append([actividadesGrafo[g][0], g[0], g[1]])

        # Se calculan los datos resumen a mostrar:

        # Nº de actividades totales
        actividades=len(actividadesGrafo)
        widget=self._widgets.get_widget('tvActividades')
        widget.set_text(str(actividades))
        widget.set_sensitive(False)

        # Nº de ficticias
        ficticias=len(actividadesGrafo)-len(self.actividad) 
        widget1=self._widgets.get_widget('tvFicticias')
        widget1.set_text(str(ficticias))
        widget1.set_sensitive(False)

        # Nº de nodos
        nNodos=len(grafo)
        widget2=self._widgets.get_widget('tvNodos')
        widget2.set_text(str(nNodos))
        widget2.set_sensitive(False)



#               HOLGURAS                      

    def ventanaHolguras(self):
        """
         Acción usuario para mostrar los tres tipos de
                  holguras: total, libre e independiente

         Parámetros: -

         Valor de retorno: -
        """
        # Se crea el grafo Pert y se renumera
        grafoRenumerado=self.pertFinal()
    
        # Nuevos nodos
        nodosN=[]
        for n in range(len(grafoRenumerado.graph)):
            nodosN.append(n+1)
 
        # Se calcula la matriz de Zaderenko
        matrizZad = mZad(self.actividad, grafoRenumerado.activities, nodosN, 1, []) 

        # Se calculan los tiempos early y last
        tearly=early(nodosN, matrizZad) 
        tlast=last(nodosN, tearly, matrizZad)

        # Se calculan los tres tipos de holgura y se muestran en la interfaz
        holguras=self.holguras(grafoRenumerado.activities, tearly, tlast, []) 
        self.mostrarHolguras(self.modeloH, holguras) 



    def holguras(self, grafo, early, last, duraciones):  
        """
         Cálculo de los tres tipos de holguras

         Parámetros: grafo (grafo Pert)
                     early (lista con los tiempos early)
                     last (lista con los tiempos last)
                 duraciones (duraciones simuladas)

         Valor de retorno: holguras (lista que contiene cada actividad y sus tres
                                      tipos de holguras)
        """
        holguras=[]
        #print grafo
        for g in grafo:
            inicio=g[0]-1
            fin=g[1]-1

            actividades=[]
            for n in range(len(self.actividad)):
                actividades.append(self.actividad[n][1])
            #print actividades, 'actividades'

            #print grafo[inicio+1, fin+1] 
            if grafo[inicio+1, fin+1][0] in actividades and self.actividad[n][6]!='':
                for n in range(len(self.actividad)):
                    if grafo[inicio+1, fin+1][0]==self.actividad[n][1]:
                        if duraciones==[]: # Es llamada desde cualquier sitio excepto desde simulación
                            t=last[fin] - early[inicio] - float(self.actividad[n][6])
                            l=early[fin] - early[inicio] - float(self.actividad[n][6])
                            i=early[fin] - last[inicio] - float(self.actividad[n][6])
                        else:   # Es llamada desde simulación
                            t=last[fin] - early[inicio] - float('%5.2f'%(duraciones[n]))
                            l=early[fin] - early[inicio] - float('%5.2f'%(duraciones[n]))
                            i=early[fin] - last[inicio] - float('%5.2f'%(duraciones[n]))
 
            else:  # Si son actividades ficticias (duración 0)
                        #print 'ficticias'
                t=last[fin] - early[inicio]   
                l=early[fin] - early[inicio] 
                i=early[fin] - last[inicio] 
         
       
            holgura=[grafo[inicio+1, fin+1][0], '%5.2f'%(t), '%5.2f'%(l), '%5.2f'%(i)] 
            holguras.append(holgura)
 
        return holguras
      

    def mostrarHolguras(self, modelo, holguras):
        """
         Muestra las hoguras en la interfaz

         Parámetros: modelo (lista de actividades)
                     hoguras (lista con los tres tipos de holguras de cada actividad)

         Valor de retorno: -
        """
        self.vHolguras.hide()  
        self.vHolguras.show()  

        modelo.clear()
        for n in range(len(holguras)):  
            modelo.append([holguras[n][0], holguras[n][1], holguras[n][2], holguras[n][3]])


#           CAMINOS DEL GRAFO                  #

    def calcularCaminos(self):
        """
         Acción usuario para calcular y mostrar todos los 
                  caminos de un grafo 

         Parámetros: -

         Valor de retorno: -
        """
        # Se comprueba que exista algún grafo
        if self.actividad==[]:
            self.dialogoError(gettext.gettext('A graph is needed to calculate its paths'))
 
        else:
            successors = self.tablaSucesoras(self.actividad)
            roy = graph.roy(successors)
            #print roy, 'grafo'
 
            # Se eliminan 'begin' y 'end' de todos los caminos
            caminosSinBeginEnd=[c[1:-1]for c in graph.findAllPaths(roy, 'Begin', 'End')]
            # Se preparan los caminos para mostrarlos en el interfaz
            numeroCaminos=len(caminosSinBeginEnd) 
            camino=gettext.gettext('Number of paths: ') + (str(numeroCaminos)) + '\n' 
            for n in range(len(caminosSinBeginEnd)):
                cadena=self.lista2Cadena(caminosSinBeginEnd, n)
                camino+=cadena
                camino+='\n'
           
            # Se muestran los caminos en la interfaz
            self.vCaminos.show()
            widget=self._widgets.get_widget('tvCaminos')
            self.mostrarTextView(widget, camino)
#              SIMULACIÓN                      

    def simulacion(self, n):
        """
         Simulación de duraciones de cada actividad según  
                  su tipo de distribución

         Parámetros: n (número de iteraciones)

         Valor de retorno: simulacion (lista con 'n' simulaciones del proyecto)
        """
        simulacion=[]
        for i in range(n):
            #print i+1, 'nº iteracion'
            sim=[]
            for m in range(len(self.actividad)):
                distribucion=self.actividad[m][9]
                #print distribucion, 'dist'
                # Si la actividad tiene una distribución 'uniforme'
                if distribucion==gettext.gettext('Uniform'):
                    if self.actividad[m][3]!='' and self.actividad[m][5]!='':
                        if self.actividad[m][3]!=self.actividad[m][5]:
                            valor=simulation.generaAleatoriosUniforme(float(self.actividad[m][3]), float(self.actividad[m][5]))
                        else: # Si d.optimista=d.pesimista
                            valor=self.actividad[m][3]
                    else:
                        self.dialogoError(gettext.gettext('Optimistic, pessimistic and most probable durations of this activity must be introduced')) 
                        return
  
                # Si la actividad tiene una distribución 'beta'
                elif distribucion==gettext.gettext('Beta'):
                    if self.actividad[m][3]!='' and self.actividad[m][4]!='' and self.actividad[m][5]!='':
                        if self.actividad[m][3]!=self.actividad[m][5]!=self.actividad[m][4]:
                            mean, stdev, shape_a, shape_b=simulation.datosBeta(float(self.actividad[m][3]), float(self.actividad[m][4]), float(self.actividad[m][5]))
                        #print "Mean=", mean, "Stdev=", stdev
                        #print "shape_a=", shape_a, "shape_b=", shape_b
                            valor=simulation.generaAleatoriosBeta(float(self.actividad[m][3]), float(self.actividad[m][5]), float(shape_a), float(shape_b))
                        else:  # Si d.optimista=d.pesimista=d.mas probable
                            valor=self.actividad[m][3]
                    else:
                        self.dialogoError(gettext.gettext('Optimistic, pessimistic and most probable durations of this activity must be introduced')) 
                        return
 
                # Si la actividad tiene una distribución 'triangular'
                elif distribucion==gettext.gettext('Triangular'):
                    if self.actividad[m][3]!='' and self.actividad[m][4]!='' and self.actividad[m][5]!='':
                        if self.actividad[m][3]!=self.actividad[m][5]!=self.actividad[m][4]:
                            valor=simulation.generaAleatoriosTriangular(float(self.actividad[m][3]), float(self.actividad[m][4]), float(self.actividad[m][5]))
                        else:   # Si d.optimista=d.pesimista=d.mas probable
                            valor=self.actividad[m][3]
                    else:
                        self.dialogoError(gettext.gettext('Optimistic, pessimistic and most probable durations of this activity must be introduced')) 
                        return
                # Si la actividad tiene una distribución 'normal'
                else:
                    if self.actividad[m][6]!='' and self.actividad[m][7]!='':
                        if float(self.actividad[m][7])!=0.00:
                            valor=simulation.generaAleatoriosNormal(float(self.actividad[m][6]), float(self.actividad[m][7]))
                        else:   # Si d.tipica=0
                            valor=self.actividad[m][6]
                    else:
                        self.dialogoError(gettext.gettext('The average duration and the typical deviation of this activity must be introduced')) 
                        return
                sim.append(float(valor))
                #print sim, 'sim'
            simulacion.append(sim)

        return simulacion


    def indiceCriticidad(self, grafo, duraciones, early, last, itTotales):
        """
           Extrae los caminos crí­ticos, calcula su í­ndice de
                    criticidad y muestra el resultado en la interfaz
  
           Parámetros: grafo (grafo Pert)
                   duraciones (duraciones simuladas)
                       early (lista con los tiempos early)
                       last (lista con los tiempos last)
                   itTotales (iteraciones totales)
  
           Valor de retorno: - 
        """
        #Se extraen los caminos crí­ticos
        holguras=self.holguras(grafo.activities, early, last, duraciones)  # Holguras de cada actividad
        actCriticas=self.actCriticas(holguras, grafo.activities)  # Se extraen las act. crí­ticas
        criticos=self.grafoCriticas(actCriticas) # Se crea un grafo crí­tico y se extraen los caminos
  
        # Se extraen todos los caminos (crí­ticos o no) del grafo original
        successors = self.tablaSucesoras(self.actividad)
        g=graph.roy(successors)
        caminos = [c[1:-1]for c in graph.findAllPaths(g, 'Begin', 'End')]
     
        # Se crea una lista con los caminos críticos de la simulación que son caminos del grafo original
        caminosCriticos=[]
        for c in criticos:
            if c in caminos:
                caminosCriticos.append(c)
        #print caminosCriticos, 'caminos criticos'
  
        # Se pasan todos los caminos a formato cadena
        nuevosCaminos=[]
        for c in caminosCriticos:
            s=''
            for m in c:
                if s!='':
                    s+=' -> '
                    s+=str(m)
                else:
                    s+=str(m)
            nuevo=[s]
            nuevosCaminos.append(nuevo)
            #print nuevosCaminos, 'formato'
   
        # Se establece la criticidad de cada camino
        for c in nuevosCaminos:
            if c[0] not in self.criticidad:
                self.criticidad[c[0]]=1
            else:
                self.criticidad[c[0]]+=1
        #print self.criticidad

        # Se muestran los caminos y el í­ndice de criticidad en la interfaz
        self.modeloC.clear()
        for c in self.criticidad:
            n=self.criticidad[c]
            self.modeloC.append([n, str('%3.2f'%((float(n)/itTotales)*100))+'%', c])
   
   
    def limpiarVentanaSim(self):
        """
         Limpia los datos de la ventana de simulación 

         Parámetros: -

         Valor de retorno: -
        """
        # Se limpian los datos
        iteracion=self._widgets.get_widget('iteracion')
        iteracion.set_text('')
        totales=self._widgets.get_widget('iteracionesTotales')   
        totales.set_text('')
        media=self._widgets.get_widget('mediaSim')
        media.set_text('')
        dTipica=self._widgets.get_widget('dTipicaSim')
        dTipica.set_text('')
        frecuencias=self._widgets.get_widget('vistaFrecuencias')
        self.modeloF.clear()
        self.modeloC.clear()
        if len(self.boxS)>0:
            self.hBoxSim.remove(self.boxS)
 
 
#            PROBABILIDADES                    


    def extraerMediaYDTipica(self):
        """
         Se extraen los valores de la media y la desviación típica del camino que va a ser objeto del
                  cálculo de probabilidades, es decir, el camino seleccionado

         Parámetros: -

         Valor de retorno: media (duración media)
                           dTipica (desviación tí­pica)
        """
        vistaListaZ = self._widgets.get_widget('vistaListaZad')
        sel = vistaListaZ.get_selection()
        modo= sel.get_mode()
        modelo, it = sel.get_selected()
        media=modelo.get_value(it, 0)
        dTipica=modelo.get_value(it, 1)

        return media, dTipica



    def calcularProb(self, dato1, dato2, media, dTipica):
        """
         Cálculo de probabilidades       

         Parámetros: dato1 (dato primer Entry)
                     dato2 (dato segundo Entry)
                     media (duración media)
                     dTipica (desviación tí­pica)

         Valor de retorno: p (probabilidad calculada)
        """
        # Se hacen los cálculos
        if dato1=='': # Si no se introduce el dato1
            x=(float(dato2)-float(media))/float(dTipica)
            p=float(scipy.stats.distributions.norm.cdf(x))


        elif dato2=='': # Si no se introduce el dato2
            x=(float(dato1)-float(media))/float(dTipica)
            p=float(scipy.stats.distributions.norm.cdf(x))


        else: # Si se introducen los dos datos
            if float(dato1)>float(dato2):
                self.dialogoError(gettext.gettext('The first number must be bigger than the second one.'))
            else:
                x1=(float(dato1)-float(media))/float(dTipica)
                p1=float(scipy.stats.distributions.norm.cdf(x1))
                x2=(float(dato2)-float(media))/float(dTipica)
                p2=float(scipy.stats.distributions.norm.cdf(x2))
                p=p2-p1
    

        #print p
        return p
  


    def calcularProbSim(self, dato1, dato2, intervalos, itTotales):
        """
          Cálculo de probabilidades para la simulación      
  
          Parámetros: dato1 (dato primer Entry)
                      dato2 (dato segundo Entry)
                      intervalos (lista de intervalos)
                      itTotales (iteraciones totales)
  
          Valor de retorno: x (probabilidad calculada)
        """
        x=0
        if dato1=='':
            for n in range(len(intervalos)):
                #print intervalos[n][0], intervalos[n][1], dato2
                if float(intervalos[n][0])<float(dato2):
                    if float(intervalos[n][0])<float(dato2)<float(intervalos[n][1]):
                    #print 'entre'
                        s=self.Fa[n]/float(itTotales)
                        #print s, 's'
                        x+=s
                else:
                    s=self.Fa[n]/float(itTotales)
                    #print s, 's'
                    x+=s
            #print x, 'suma'
 
        elif dato2=='':
            for n in range(len(intervalos)):
                #print intervalos[n][0], intervalos[n][1], dato1
                if float(intervalos[n][1])>float(dato1):
                    if float(intervalos[n][0])<float(dato1)<float(intervalos[n][1]):
                        s=self.Fa[n]/float(itTotales)
                        #print s, 's'
                        x+=s
                else:
                    s=self.Fa[n]/float(itTotales)
                    #print s, 's'
                    x+=s
            #print x, 'suma'
 
        else:
            if float(dato1)>float(dato2):
                self.dialogoError(gettext.gettext('The first number must be bigger than the second one.'))
            else:
                for n in range(len(intervalos)):
                    #print intervalos[n][0], dato2, intervalos[n][1], dato1
                    if float(intervalos[n][1])>float(dato1) and float(intervalos[n][0])<float(dato2):
                #print 'entra'
                        s=self.Fa[n]/float(itTotales)
                        #print s, 's'
                        x += s
                        #print x, 'suma'
        return x           
  
  
    def escribirProb(self, dato):
        """
         Escribe en el TextView las probabilidades calculadas        

         Parámetros: dato (probabilidad a escribir)

         Valor de retorno: -
        """
        prob=self._widgets.get_widget('tvProbabilidades')
        prob.set_buffer(self.bufer)
        it1=self.bufer.get_start_iter()
        it2=self.bufer.get_end_iter()
        textoBufer=self.bufer.get_text(it1, it2)
        #print textoBufer, 'bufer'
        completo=textoBufer+'\n'+dato
        #print completo
        self.bufer.set_text(completo) 



    def limpiarVentanaProb(self, c):
        """
         Limpia los datos de la ventana de probabilidades 

         Parámetros: c (0: llamada desde la ventana Zaderenko
               1: llamada desde la ventana Simulación)

         Valor de retorno: -
        """
        # Se limpia el bufer
        probabilidades=self._widgets.get_widget('tvProbabilidades')
        probabilidades.set_buffer(self.bufer)
        it1=self.bufer.get_start_iter()
        it2=self.bufer.get_end_iter()
        self.bufer.delete(it1, it2)

        # Se limpian los datos
        valor1=self._widgets.get_widget('valor1Prob')
        valor1.set_text('')
        valor2=self._widgets.get_widget('valor2Prob')
        valor2.set_text('')
        valor3=self._widgets.get_widget('valor3Prob')
        valor3.set_text('')
        resultado1=self._widgets.get_widget('resultado1Prob')   
        resultado1.set_text('')
        resultado2=self._widgets.get_widget('resultado2Prob')   
        resultado2.set_text('')
         
        # Se elimina el grafico
        if c==0 and len(self.vBoxProb)>1:
            self.vBoxProb.remove(self.grafica)
            self.grafica=gtk.Image()
        elif len(self.box)>0:
            self.vBoxProb.remove(self.box)
            self.box=gtk.VBox()
 


    def openProject(self, filename):
        """
        Open a project file given by filename
        """
        # xxx Código que sustituirá la antigua carga de ficheros cuando esté todo terminado
        try:
            # Tries to load file with formats that match its extension in format order
            data = None
            extension = filename[filename.rfind('.')+1:]

            for format in self.fileFormats:
                if extension in format.filenameExtensions:
                    try:
                        data = format.load(filename)
                        break
                    except:# xxxException:
                        pass

            # if not data:
            # xxx Should we try here to load files in any format independently of their 
            # extension. It would the same previous code without the 'if extension'
            if data:
                self.actividad, schedules, self.recurso, self.asignacion = data
                for res in self.recurso:
                    self.modeloComboARR.append([res[0]])
                    res[1] = gettext.gettext(res[1])
                    
                act_list = []
                dur_dic = {}
                pre_dic = {}

                for act in self.actividad:
                    act_list.append(act[1])
                    dur_dic[act[1]] = act[6]
                    pre_dic[act[1]] = act[2]
                    self.gantt.add_activity(act[1],act[2],act[6])
                min_sched = graph.get_activities_start_time(act_list,dur_dic,pre_dic)
                schedules = [[gettext.gettext('Min'), min_sched]] + schedules
                
                cont = 1
                for act in self.actividad:
                    act.append(0)
                    act[0] = cont
                    cont += 1

                for sched in schedules:
                    self.add_schedule(*sched)
                self.set_schedule(self.schedules[0][1]) 
                self.ntbSchedule.show()             
                for row in self.recurso:
                    self.modeloR.append(row)
                for row in self.asignacion:
                    self.modeloAR.append(row)

                for act in self.actividad:
                    self.modelo.append(act[0:2] + [', '.join(act[2])] + act[3:6] + [str(act[6])] + act[7:9] + [str(act[9])])
                    self.modeloComboS.append([act[1]])            
                    self.modeloComboARA.append([act[1]])
    
                # xxx Update model data
                # Update interface 
                self.openFilename=filename
                self.updateWindowTitle()
                self.enableProjectControls(True)
                self.set_modified(False)
                self.modified = 0
                self.modelo.append([cont, '', '', '', '', '', '', '', gettext.gettext('Beta'), ""])  # Se inserta una fila vacia
                cont += 1                self.modeloR.append()
                self.modeloAR.append()
            else:
                self.dialogoError(gettext.gettext('Error reading file:') + filename 
                      + ' ' + gettext.gettext('Unknown format')) 

        except IOError:
            self.dialogoError(gettext.gettext('Error reading file:') + filename) 


    def saveProject(self, nombre):
        """
        Saves a project in ppcproject format '.prj'
        """
        # xxx Código que sustituirá la antigua carga de ficheros cuando esté todo terminado
        
        # xxx Here extension should be checked to choose the save format
        # by now we suppose it is .prj
        if nombre[-4:] != '.ppc':
            nombre = nombre + '.ppc'

        format = fileFormats.PPCProjectFileFormat()

        resources = deepcopy(self.recurso)
        for res in resources:
            if res[1] == gettext.gettext('Renewable'): 
                res[1] = 'Renewable'
            elif res[1] == gettext.gettext('Non renewable'):
                res[1] = 'Non renewable'
            elif res[1] == gettext.gettext('Double constrained'):
                res[1] = 'Double constrained'
            else:
                res[1] = 'Unlimited'
        
        activities = []
        for act in self.actividad:
            activities.append(act[0:-1])

        # xxx Here data should be prepared to be stored
        try:
            format.save((activities, self.schedules[1:], resources, self.asignacion), nombre)
            # Update interface 
            self.openFilename=nombre
            self.updateWindowTitle()
            self.set_modified(False)
            self.modified = 0
        except IOError :
            self.dialogoError(gettext.gettext('Error saving the file'))    



 
# --- FUNCIONES DIALOGOS GUARDAR Y ADVERTENCIA/ERRORES #            
  
    def on_btnSaveRoy_clicked(self, button):
        self.save_graph_image(self.grafoRoy.get_pixbuf())

    def on_btnSavePert_clicked(self, button):
        self.save_graph_image(self.grafoPert.get_pixbuf())

    def save_graph_image(self, pixbuf):
        dialogoGuardar = gtk.FileChooserDialog(gettext.gettext("Save Image"),
                                               None,
                                               gtk.FILE_CHOOSER_ACTION_SAVE,
                                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                               gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialogoGuardar.set_default_response(gtk.RESPONSE_OK)
        resultado = dialogoGuardar.run()

        if resultado == gtk.RESPONSE_OK:
            filename = dialogoGuardar.get_filename()
            pixbuf.save(filename if filename[-4:] == ".png" else filename + ".png","png")
        dialogoGuardar.destroy()


# --- DIÁLOGOS DE ADVERTENCIA Y ERRORES       

    def closeProject(self):
        """
        Close the project checking if it has been modified.
        If it has been modified, show a dialog: Save-Discard-Cancel

        Return: True if closed
                False if canceled
        """
        if self.modified==0:   # El proyecto actual ha sido guardado
            close = True
        else:                 # El proyecto actual aún no se ha guardado
            dialogo = gtk.Dialog(gettext.gettext("Attention!!"),
                                 None,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gettext.gettext('Discard'), gtk.RESPONSE_CLOSE,
                                  gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_OK )
                                 )
            label = gtk.Label(gettext.gettext('Project has been modified. Do you want to save the changes?'))
            dialogo.vbox.pack_start(label,True,True,10)
            label.show()
            respuesta=dialogo.run()
           
            if respuesta==gtk.RESPONSE_OK:
                self.guardar()
                close = True
            elif respuesta==gtk.RESPONSE_CLOSE:
                close = True
            else:
                close = False

            dialogo.destroy()

        if close:
            # Se limpian todas las listas de datos
            self.openFilename = None
            self.modelo.clear()
            self.actividad=[]
            self.modeloR.clear()
            self.recurso=[]
            self.modeloAR.clear()
            self.asignacion=[]
            self.updateWindowTitle()
            self.modified = 0
            self.gantt.clear()
            self.gantt.update()
            self.modeloComboS.clear()
            self.modeloComboARA.clear()
            self.modeloComboARR.clear()
            while self.ntbSchedule.get_current_page() != -1:
                self.clicked_tab = len(self.schedule_tab_labels) - 1
                self.delete_tab(None)
            self.schedules = []
            self.enableProjectControls(False)
            self.modified = 0
            self.ntbSchedule.hide()

        return close
  
  
    def dialogoRec(self, tipo):
        """
 Muestra un mensaje de advertencia si no se han
          introducido bien las unidades de recurso

 Parámetros: tipo (tipo de recurso)

 Valor de retorno: -
        """
        dialogo=gtk.Dialog(gettext.gettext("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        # Si el recurso es Renovable, las unidades deben ser 'por periodo'
        if tipo==gettext.gettext('Renewable'):
            label=gtk.Label(gettext.gettext('Renember that the resource is "Renewable"'))
        # Si el recurso es No Renovable, las unidades deben ser 'por proyecto'
        else:
            label=gtk.Label(gettext.gettext('Renember that the resource is "Non renewable"'))
        dialogo.vbox.pack_start(label,True,True,10)
        label.show()
        respuesta=dialogo.run()

        dialogo.destroy()   


     
    def dialogoError(self, cadena):
        """
 Muestra un mensaje de error en la apertura del fichero

 Parámetros: -

 Valor de retorno: -
        """
        dialogo=gtk.Dialog(gettext.gettext("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        label=gtk.Label(cadena)
        dialogo.vbox.pack_start(label,True,True,10)
        label.show()
        respuesta=dialogo.run()

        dialogo.destroy()   



    def errorActividadesRepetidas(self, repetidas):
        """
 Muestra un mensaje de error si en la introducción
          de datos hay alguna actividad repetida

 Parámetros: repetidas (lista con las actividades repetidas)

 Valor de retorno: -
        """
        dialogo=gtk.Dialog(gettext.gettext("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        for actividad in repetidas:
            label=gtk.Label(gettext.gettext('The activity ')+' "'+actividad+'"'+gettext.gettext(' is repeated\n'))
            dialogo.vbox.pack_start(label,True,True,5)
            label.show()
        respuesta=dialogo.run()

        dialogo.destroy() 


    def errorRecNecAct(self, datosErroneos, cadena):
        """
 Muestra un mensaje de error si en la ventana
          'recursos necesarios por actividad' hay alguna
          actividad o algun recurso inexistente

 Parámetros: datosErroneos (lista con los datos erróneos)
             cadena (cadena de texto)

 Valor de retorno: -
        """
        dialogo=gtk.Dialog(gettext.gettext("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        for dato in datosErroneos:
            label=gtk.Label(cadena+' "'+dato+'"'+ gettext.gettext(' does not exist\n'))
            dialogo.vbox.pack_start(label,True,True,5)
            label.show()
        respuesta=dialogo.run()

        dialogo.destroy() 

    def treeview_menu_invoked(self, widget, event, treeview):
        """
          xxx lacks comment
        """
        if event.button == 3 and treeview.get_selection().count_selected_rows() != 0 and treeview.get_model()[treeview.get_selection().get_selected_rows()[1][0]][1] != "":
            self._widgets.get_widget("ctxTreeviewMenu").popup(None, None, None, event.button, event.time)
            self.treemenu_invoker = treeview

    def delete_tree_row(self, widget):
        """
          xxx lacks comment
        """
        path = self.treemenu_invoker.get_selection().get_selected_rows()[1][0]
        model = self.treemenu_invoker.get_model()
        if self.treemenu_invoker == self.vistaLista:
            for index in range(len(self.actividad)-1,-1, -1):
                if self.actividad[index][1] == model[path][1]:
                    del self.actividad[index]
            for index in range(len(self.asignacion)-1,-1, -1):
                if self.asignacion[index][1] == model[path][1]:
                    del self.asignacion[index]
                if self._widgets.get_widget('vistaListaAR').get_model()[index][1] == model[path][0]:
                    self._widgets.get_widget('vistaListaAR').get_model().remove(self._widgets.get_widget('vistaListaAR').get_model().get_iter(index))
            #xxx TODO: Update gantt diagram and Schedules.
        elif self.treemenu_invoker == self._widgets.get_widget('vistaListaRec'):
            for index in range(len(self.recurso)-1,-1, -1):
                if self.recurso[index][0] == model[path][0]:
                    del self.recurso[index]
            for index in range(len(self.asignacion)-1,-1, -1):
                if self.asignacion[index][1] == model[path][0]:
                    del self.asignacion[index]
                if self._widgets.get_widget('vistaListaAR').get_model()[index][1] == model[path][0]:
                    self._widgets.get_widget('vistaListaAR').get_model().remove(self._widgets.get_widget('vistaListaAR').get_model().get_iter(index))
        else:
            for index in range(len(self.asignacion)-1,-1, -1):
                if self.asignacion[index][0] == model[path][0] and self.asignacion[index][1] == model[path][1]:
                    del self.asignacion[index]
        model.remove(model.get_iter(path))
        self.modified=1   # Controlamos que el proyecto ha cambiado
        self.set_modified(True)
  
# MANEJADORES #
# --- Menu actions

# File menu actions
    def on_New_activate(self, item):
        """ User ask for new file (from menu or toolbar) """
        self.introduccionDatos()
  
    def on_Open_activate(self, item):
        """ User ask for open file (from menu or toolbar)
        """
        
        # Dialog asking for file to open
        dialogoFicheros = gtk.FileChooserDialog(gettext.gettext("Open File"),
                                                None,
                                                gtk.FILE_CHOOSER_ACTION_OPEN,
                                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK)
                                                )
        # Creates a filter for all supported file formats
        ffilter = gtk.FileFilter()
        pats = []
        for f in self.fileFormats:
            for pat in f.filenamePatterns():
                pats.append(pat)
                ffilter.add_pattern(pat)
        ffilter.set_name(''.join([gettext.gettext('All project files') + ' (', ', '.join(pats), ')']))
        dialogoFicheros.add_filter(ffilter)                 

        # Creates a filter for each supported file format
        for f in self.fileFormats:
            ffilter = gtk.FileFilter()
            for pat in f.filenamePatterns():
                ffilter.add_pattern(pat)
            ffilter.set_name(f.description())
            dialogoFicheros.add_filter(ffilter)                 

        # Creates the filter allowing to see all files            
        ffilter = gtk.FileFilter()
        ffilter.add_pattern('*')
        ffilter.set_name(gettext.gettext('All files'))
        dialogoFicheros.add_filter(ffilter)                 

        dialogoFicheros.set_default_response(gtk.RESPONSE_OK)
        resultado = dialogoFicheros.run()
        if resultado == gtk.RESPONSE_OK:
            # Close open project if any
            closed = self.closeProject()
            if closed:
                self.openProject(dialogoFicheros.get_filename())
        dialogoFicheros.destroy()
        
    def  on_Save_activate(self, item):
        # Se comprueba que no haya actividades repetidas (xxx esto debe ir aqui?)
        errorActRepetidas, actividadesRepetidas=self.actividadesRepetidas(self.actividad)
        if errorActRepetidas==0:
            if self.openFilename==gettext.gettext('Unnamed'):
                on_SaveAs_activate(item)
            else:
                self.saveProject(self.openFilename)
        else:
            self.errorActividadesRepetidas(actividadesRepetidas) 

    def on_SaveAs_activate(self, menu_item):
        # Se comprueba que no haya actividades repetidas (xxx esto debe ir aqui?)
        errorActRepetidas, actividadesRepetidas = self.actividadesRepetidas(self.actividad)
        if errorActRepetidas == 0:
            dialogoGuardar = gtk.FileChooserDialog(gettext.gettext("Save as"),
                                                   None,
                                                   gtk.FILE_CHOOSER_ACTION_SAVE,
                                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_SAVE, gtk.RESPONSE_OK))
            dialogoGuardar.set_default_response(gtk.RESPONSE_OK)
            resultado = dialogoGuardar.run()
      
            if resultado == gtk.RESPONSE_OK:
                self.openFilename = dialogoGuardar.get_filename()
                self.saveProject(self.openFilename)
            dialogoGuardar.destroy() 
        else:
            self.errorActividadesRepetidas(actividadesRepetidas) 
       

    def on_Close_activate(self, menu_item):
        self.closeProject()
   
    def on_Exit_activate(self, *args):
        closed = self.closeProject()
        if closed:
            #XXX Salir propiamente??
            gtk.main_quit()

# View menu actions

    def on_bHerramientas_activate(self, checkMenuItem):
        """
        Acción usuario para activar o desactivar la barra
        de herramientas, inicialmente inactiva
        """
        checkMenuItem==self.bHerramientas
        if checkMenuItem.get_active():
            self.bHerramientas.show()
        else:
            self.bHerramientas.hide()
   
    def on_mnPantallaComp_activate(self, menu_item):
        self.vPrincipal.fullscreen()
        self._widgets.get_widget('mnSalirPantComp').show()
        self._widgets.get_widget('mnPantallaComp').hide()
  
    def on_mnSalirPantComp_activate(self, menu_item):
        self.vPrincipal.unfullscreen()
        self._widgets.get_widget('mnSalirPantComp').hide()
        self._widgets.get_widget('mnPantallaComp').show()
  
# Action menu actions                 

    def on_mnCrearRecursos_activate(self, menu_item):
        self.vRecursos.show()

    def on_mnGrafoRoy_activate(self, menu_item):
        # Se calcula el grafo ROY a través de la tabla de sucesoras
        successors = self.tablaSucesoras(self.actividad)
        roy = graph.roy(successors)
        self.grafoRoy=self._widgets.get_widget('imagenGrafoRoy')

        # Se dibuja el grafo ROY y se carga la imagen en la ventana
        pixbufloader = gtk.gdk.PixbufLoader()
        pixbufloader.write( graph.graph2image(roy) )
        pixbufloader.close()
        self.grafoRoy.set_from_pixbuf( pixbufloader.get_pixbuf() )
        
        # Se muestra la ventana
        self.vRoy.show()
        

    def on_mnGrafoPert_activate(self, menu_item):
        # Se crea el grafo Pert y se renumera
        grafoRenumerado=self.pertFinal()
  
        # Se dibuja el grafo Pert y se carga la imagen en la ventana
        self.grafoPert = self._widgets.get_widget('imagenGrafoPert')
        pixbufloader = gtk.gdk.PixbufLoader()
        pixbufloader.write( graph.pert2image(grafoRenumerado) )
        pixbufloader.close()
        self.grafoPert.set_from_pixbuf( pixbufloader.get_pixbuf() )
        
        # Se muestra la ventana
        self.vPert.show()
  
    def on_mnActividades_activate(self, menu_item):
        """ User ask for activities in PERT graph """
        # Se crea el grafo Pert y se renumera
        grafoRenumerado=self.pertFinal()
  
        # Se muestran las actividades y su nodo inicio y fí­n  
        self.mostrarActividades(self.modeloA, grafoRenumerado.activities, grafoRenumerado.graph)
       
    def on_mnZaderenko_activate(self, menu_item):
        s=0
        for a in self.actividad:
            if a[6]=='':
                s+=1
        if s>0:
            self.dialogoError(gettext.gettext('There are uncomplete activities'))
        else:
            self.ventanaZaderenko()
   
    def on_mnHolguras_activate(self, menu_item):
        """ User ask for slacks """
        s=0
        for a in self.actividad:
            if a[6]=='':
                s+=1
                
        if s>0:
            self.dialogoError(gettext.gettext('There are uncomplete activities'))
        else:
            self.ventanaHolguras()
   
    def on_mnSimulacion_activate(self, menu_item):
        """Acción usuario para acceder a la ventana que muestra
        los resultados de la simulación de duraciones (tabla
        de frecuencias, gráfica, ...)
        """
        s=0
        m=0
        for a in self.actividad:
            if a[9]==gettext.gettext('Uniform') or a[9]==gettext.gettext('Beta') or a[9]==gettext.gettext('Triangular'):
                if a[3]=='' or a[4]=='' or a[5]=='':
                    s+=1
            else:
                if a[6]=='' or a[7]=='':
                    m=+1

        if s>0 and m==0:
            self.dialogoError(gettext.gettext('You must introduce the durations: ')+'\n'+'\t'+gettext.gettext('- Optimistic')+'\n'+'\t'+gettext.gettext('- Most probable')+'\n'+'\t'+gettext.gettext('- Pessimistic'))
        elif s==0 and m>0:
            self.dialogoError(gettext.gettext('You must introduce the durations: ')+'\n'+'\t'+gettext.gettext('- Average')+'\n'+'\t'+gettext.gettext('- Typical Dev.'))
        elif s>0 and m>0:
            self.dialogoError(gettext.gettext('You must introduce the durations: ')+'\n'+'\t'+gettext.gettext('- Optimistic')+'\n'+'\t'+gettext.gettext('- Most probable')+'\n'+'\t'+gettext.gettext('- Pessimistic')+'\n'+'\t'+gettext.gettext('- Average')+'\n'+'\t'+gettext.gettext('- Typical Dev.'))
        else:
            self._widgets.get_widget('btProbSim').set_sensitive(False)
            self._widgets.get_widget('btGuardarSim').set_sensitive(False)
            for column in self.vistaFrecuencias.get_columns()[1:]:
                column.set_title("")
            self.vSimulacion.show()
            self.simTotales=[] # Lista con las simulaciones totales
            self.duraciones=[] # Lista con las duraciones de las simulaciones
            self.criticidad={} # Diccionario con los caminos y su í­ndice de criticidad
            self.intervalos=[] # Lista con los intervalos de las duraciones

    def on_mnCalcularCaminos_activate(self, menu_item):
        """ User ask for paths in project """
        self.calcularCaminos()


      # XXX XXX XXX XXX --- SimAnnealing


    def on_wndSimAnnealing_delete_event(self, window, event):
        """
        User action to close the window

        Parameters: window
                    event
        Returns: True
        """
        self.btResetSA.clicked()
        window.hide()

        return True
        
    def on_btnSaveSA_clicked (self, menu_item):
        """
        Save the schedule calculated

        Parameters: menu_item
        
        Returns: -
        """
        optSchDic = {}
        if self.optimumSchedule == []:
            self.dialogoError(gettext.gettext('There is no schedule.'))
            return False
        else:
            for act,startTime,endTime in self.optimumSchedule:
                optSchDic[act] = startTime
        self.add_schedule(None, optSchDic)
            
    def on_rbAllocation_pressed (self, menu_item):
        """
        Choose allocation

        Parameters: menu_item
        
        Returns: -
        """
        self.sbSlackSA.set_sensitive(False)

    def on_rbLeveling_pressed (self, menu_item):
        """
        Choose leveling

        Parameters: menu_item
        
        Returns: -
        """
        self.sbSlackSA.set_sensitive(True)

    def on_cbIterationSA_toggled (self, menu_item):
        """
        Choose unlimited number of iterations without improve

        Parameters: menu_item
        
        Returns: -
        """
        if self.cbIterationSA.get_active():
            self.sbNoImproveIterSA.set_sensitive(False)
        else:
            self.sbNoImproveIterSA.set_sensitive(True)

    def on_mnSimAnnealing_activate(self, menu_item):
        """
        User action to open the simulated annealing window

        Parameters: menu_item

        Returns: -
        """
        self.wndSimAnnealing.show()


    def on_btnSimAnnealingReset_clicked(self,menu_item):
        """
        User action to restart the values of the simulated annealing window fields

        Parameters: menu_item

        Returns: -
        """
        self.ganttActLoaded = False
        self.ganttSA.clear()
        self.loadingSheet.clear()
        self.loadingTable.clear()
        self.ganttSA.update()        
        self.loadingSheet.update()
        self.loadingTable.update()
        self.entryResultSA.set_text('')
        self.entryMaxTempSA.set_text('')
        self.entryAlpha.set_text('')
        self.cbIterationSA.set_active(False)
        self.sbPhi.set_value(0.1)
        self.sbNu.set_value(0.1)
        self.sbMinTempSA.set_value(0.1)
        self.sbNoImproveIterSA.set_value(100)
        self.sbMaxIterationSA.set_value(100)
        self.sbExecuteTimesSA.set_value(1)
        self.sbSlackSA.set_value(0)


    def on_btnSimAnnealingCalculate_clicked(self, menu_item):
        """
        User action to start the simulated annealing algorithm

        Parameters: menu_item

        Returns: -
        """
        # Add all activities in rest dictionary
        rest={}
        for a in self.actividad:
            if a[6] == '':
                self.dialogoError(gettext.gettext('You must introduce the average duration.'))
                return False
            rest[a[1]] = [float(a[6])]

        if self.rbLeveling.get_active():
            leveling = 1
        else:
            leveling = 0
        
        if leveling == 1 and self.recurso == []:
            self.dialogoError(gettext.gettext('There are not resources introduced.'))
            return False
        # Create main dictionaries
        resources = resources_availability(self.recurso)
        asignation = resources_per_activities(self.asignacion, resources)
        successors = self.tablaSucesoras(self.actividad)
        activities = self.altered_last(rest)
        # Get the simulated annealing algorithm's paremeters
        phi = self.sbPhi.get_value()
        nu = self.sbNu.get_value()
        minTemperature = self.sbMinTempSA.get_value()
        maxIteration = self.sbMaxIterationSA.get_value()
        times = self.sbExecuteTimesSA.get_value()

        if self.cbIterationSA.get_active():
            noImproveIter = -1
        else:
            noImproveIter = self.sbNoImproveIterSA.get_value()

        self.optimumSchedule, optSchEvaluated, optSchDuration, optSchAlpha, optSchTemp, optSchIt = simulated_annealing(asignation,resources,successors,activities,leveling,nu,phi,minTemperature,maxIteration,noImproveIter)
        if self.optimumSchedule != None: # If no error
            # Load gantt diagram
            if not self.ganttActLoaded:
                self.ganttActLoaded = True
                self.ganttSA.clear()
                for a in self.actividad:
                    self.ganttSA.add_activity(a[1],[],float(a[6]),0,0,'Activity: ' + a[1])
            # Execute the algorithm as many times as the user introduced
            for a in range(0,int(times - 1)):
                schedule, schEvaluated, schDuration, schAlpha, schTemp, schIt = simulated_annealing      (asignation,resources,successors,activities,leveling,nu,phi,minTemperature,maxIteration,noImproveIter)
                # Save the best schedule
                if optSchEvaluated > schEvaluated2:
                    self.optimumSchedule = schedule
                    optSchEvaluated = schEvaluated
                    optSchDuration = schDuration
                    optSchAlpha = schAlpha
                    optSchTemp = schTemp
                    optSchIt = schIt
            # Show the value of algorithm's parameters
            self.entryResultSA.set_text(str(optSchDuration))
            self.entryAlpha.set_text(str(optSchAlpha))
            self.entryMaxTempSA.set_text(str(optSchTemp))
            self.entryIterations.set_text(str(optSchIt))
            # Calculate loadingSheet
            resources = resources_availability(self.recurso, True)
            asignation = resources_per_activities(self.asignacion, resources)
            optSchLoadingSheet = calculate_loading_sheet(self.optimumSchedule, resources, asignation, optSchDuration)
            # Add activities to gantt
            for act,startTime,finalTime in self.optimumSchedule:
                self.ganttSA.set_activity_start_time(act, startTime)
                if act in successors.keys():
                    self.ganttSA.set_activity_prelations(act,successors[act])

            self.ganttSA.update()
            # Add loading to loadingSheet
            self.loadingSheet.set_loading(optSchLoadingSheet)
            self.loadingSheet.set_duration(optSchDuration)
            self.loadingSheet.update()
            # Add loading to loadingTable
            self.loadingTable.set_loading(optSchLoadingSheet)
            self.loadingTable.set_duration(optSchDuration)
            self.loadingTable.update()
        else:
            self.dialogoError(gettext.gettext('Initial temperature not high enough.'))
            return False

    def altered_last(self,rest):
        """
        Calculate last time modified

        Parameters: rest (activities in the project)

        Returns: rest (dictionary of the activities and their characteristics (duration, last time))
        """
        # Create graph and number it
        grafoRenumerado = self.pertFinal()
  
        # New nodes
        nodosN = []
        for n in range(len(grafoRenumerado.graph)):
            nodosN.append(n+1)
   
        # Calculate Zaderenko matrix
        matrizZad = mZad(self.actividad,grafoRenumerado.activities, nodosN, 1, []) 

        # Calculate early and last times
        tearly = early(nodosN, matrizZad)      
        tlast = last(nodosN, tearly, matrizZad)

        slack = self.sbSlackSA.get_value()
        # Calculate altered last time
        for a in grafoRenumerado.activities:
            if grafoRenumerado.activities[a][0] != 'dummy':
                rest[grafoRenumerado.activities[a][0]] += [tlast[a[1]-1] + slack - float(rest[grafoRenumerado.activities[a][0]][0])]

        return rest
        

# Help menu actions

    def on_mnAyuda_activate(self, menu_item):
        dialogoAyuda = self.dAyuda
        dialogoAyuda.show()


# --- Window actions

    def on_wndGrafoPert_delete_event(self, window, event):
        window.hide()
        return True

    def on_wndGrafoRoy_delete_event(self, window, event):
        window.hide()
        return True


# ACTIVIDADES window

    def on_btAceptarAct_clicked(self, boton):
        """
         Acción usuario para acceder aceptar los datos
                  que aparecen en la ventana de actividades

         Parámetros: boton (botón clickeado)
        """
        self.vActividades.hide()

    def on_wndActividades_delete_event(self, ventana, evento):
        """
         Acción usuario para acceder cerrar la ventana de actividades

         Parámetros: ventana (ventana actual)
                     evento (evento cerrar)
        """
        ventana.hide()
        return True


# ZADERENKO window

    def on_vistaListaZad_cursor_changed(self, vistaListaZ):
        """
         Al seleccionar uno de los caminos del grafo que se muestran
                  en la ventana de Zaderenko, se activa el botón 
                  'calcular probabilidad' que aparací­a inactivo inicialmente          

         Parámetros: vistaListaZ (widget donde se muestran los caminos)
        """
        vistaListaZ = self._widgets.get_widget('vistaListaZad')
        cursor, columna = vistaListaZ.get_cursor()
        if cursor:
            self._widgets.get_widget('btCalcularProb').set_sensitive(True)
            modelo = vistaListaZ.get_model()
            iterador = modelo.get_iter(cursor)
        else:
            self._widgets.get_widget('btCalcularProb').set_sensitive(False)

    def on_btCalcularProb_clicked(self, boton):
        """
        Acción usuario para acceder a la ventana que muestra
                 el cálculo de probabilidades

        Parámetros: boton (botón clickeado)
        """
        # Extraigo los valores de la media y la desviación típica del camino que va a ser objeto del
        # cálculo de probabilidades
        media, dTipica=self.extraerMediaYDTipica()

        if float(dTipica)==0.00:
            texto=gettext.gettext('Path duration is ') +'%5.2f'%(float(media))+' t.u. with 100% probability'
            self.dialogoError(texto)
        else:
            # Se asigna tí­tulo y gráfica a la ventana de probabilidad
            self.vProbabilidades.set_title(gettext.gettext('Probability related to the path'))
            #imagen=self._widgets.get_widget('graficaProb')
            if len(self.vBoxProb)>1:
                self.vBoxProb.remove(self.grafica)
                self.grafica=gtk.Image()

            self.grafica.set_from_file('graficaNormal.gif')
            self.vBoxProb.add(self.grafica)
            self.vBoxProb.show_all()
        
            # Se muestran la media y desviación típica en la ventana de probabilidades
            widgetMedia=self._widgets.get_widget('mediaProb')
            widgetMedia.set_text(media)
            widgetMedia.set_sensitive(False)
            widgetdTipica=self._widgets.get_widget('dTipicaProb')
            widgetdTipica.set_text(dTipica)
            widgetdTipica.set_sensitive(False)

            # Se insensibilizan las casillas resultado
            resultado1=self._widgets.get_widget('resultado1Prob')
            resultado1.set_sensitive(False)
            resultado2=self._widgets.get_widget('resultado2Prob')
            resultado2.set_sensitive(False)

            self.vProbabilidades.show()
            self.on_btnIntervalReset_clicked(None)
            self.on_btnProbabilityReset_clicked(None)

    def on_btAceptarZad_clicked(self, boton):
        """
           Acción usuario para aceptar la información 
                    que aparece en la ventana de Zaderenko: matriz de
                    Zaderenko, tiempos early y last, caminos del grafo, ...
  
           Parámetros: boton (botón clickeado)
        """
        self._widgets.get_widget('btCalcularProb').set_sensitive(False)
        self.vZaderenko.hide()
  
    def on_btHolgZad_clicked(self, boton):
        """
         Acción usuario para acceder a la ventana que muestra 
                  las holguras de cada actividad

         Parámetros: boton (botón clickeado)
        """
        s=0
        for a in self.actividad:
            if a[6]=='' or a[7]=='':
                s+=1
                
        if s>0:
            self.dialogoError(gettext.gettext('There are uncomplete activities'))
        else:
            self.ventanaHolguras()
    
    def on_wndZaderenko_delete_event(self, ventana, evento):
        """
         Acción usuario para cerrar la ventana de Zaderenko

         Parámetros: ventana (ventana actual)
                     evento (evento cerrar)
        """
        self._widgets.get_widget('btCalcularProb').set_sensitive(False)
        ventana.hide()
        return True


# HOLGURAS window

    def on_btAceptarHolg_clicked(self, boton):
        """
           Acción usuario para aceptar la información 
                    que aparece en la ventana de holguras: los tres
                    tipos de holgura para cada actividad
  
           Parámetros: boton (botón clickeado)
        """
        self.vHolguras.hide()
  
    def on_btZadHolg_clicked(self, boton):
        """
         Acción usuario para acceder a la ventana de Zaderenko

         Parámetros: boton (botón clickeado)
        """
        s=0
        for a in self.actividad:
            if a[6]=='' or a[7]=='':
                s+=1
                
        if s>0:
            self.dialogoError(gettext.gettext('There are uncomplete activities'))
        else:
            self.ventanaZaderenko()


    def on_wndHolguras_delete_event(self, ventana, evento):
        """
         Acción usuario para cerrar la ventana de holguras

         Parámetros: ventana (ventana actual)
                     evento (evento cerrar)
        """
        ventana.hide()
        return True


# PROBABILIDADES window

    def on_btnIntervalReset_clicked(self, button):
        """
        """
        widgetMedia=self._widgets.get_widget('mediaProb')
        media=float(widgetMedia.get_text())
        widgetdTipica=self._widgets.get_widget('dTipicaProb')
        dTipica=float(widgetdTipica.get_text())
        self._widgets.get_widget('valor1Prob').set_value(media - 2 * dTipica)
        self._widgets.get_widget('valor2Prob').set_value(media + 2 * dTipica)
        self.on_interval_changed(None)

    def on_interval_changed(self, widget):
        """
        Acción usuario al activar el valor introducido en 
                 el primer gtk.Entry de la ventana de probabilidades          

        Parámetros: entry (entry activado)
        """

        # Se extraen los valores de las u.d.t. de la interfaz
        valor1=self._widgets.get_widget('valor1Prob')
        dato1=str(valor1.get_value())
        valor2=self._widgets.get_widget('valor2Prob')
        dato2=str(valor2.get_value())
        if valor2.get_value() > valor1.get_value():
            titulo=self.vProbabilidades.get_title()
            if titulo==gettext.gettext('Probability related to the path'):
                # Se extrae la media y la desviación típica de la interfaz
                widgetMedia=self._widgets.get_widget('mediaProb')
                media=widgetMedia.get_text()
                widgetdTipica=self._widgets.get_widget('dTipicaProb')
                dTipica=widgetdTipica.get_text()
                # Se calcula la probabilidad
                x=self.calcularProb(dato1, dato2, media, dTipica)
 
            else:
                    # Extraigo las iteraciones totales
                totales=self._widgets.get_widget('iteracionesTotales')
                itTotales=totales.get_text()

                intervalos=[]
                for n in self.intervalos:
                    d=n.split('[')
                    interv=d[1].split(',')
                    intervalos.append(interv) 
 
                # Se calcula la probabilidad
                x=self.calcularProbSim(dato1, dato2, intervalos, itTotales)
         
            # Se muestra el resultado en la casilla correspondiente
            prob=str('%3.2f'%(x*100))+' %'
            resultado1=self._widgets.get_widget('resultado1Prob')
            resultado1.set_text(prob)
        else:
            prob=""
            resultado1=self._widgets.get_widget('resultado1Prob')
            resultado1.set_text(prob)
        return False

           
    def on_bntIntervalCalculate_clicked(self, button):
        """
        Acción usuario al activar el valor introducido en 
                 el primer gtk.Entry de la ventana de probabilidades          

        Parámetros: entry (entry activado)
        """

        # Se extraen los valores de las u.d.t. de la interfaz
        valor1=self._widgets.get_widget('valor1Prob')
        dato1=str(valor1.get_value())
        valor2=self._widgets.get_widget('valor2Prob')
        dato2=str(valor2.get_value())

        titulo=self.vProbabilidades.get_title()
        if titulo==gettext.gettext('Probability related to the path'):
            # Se extrae la media y la desviación típica de la interfaz
            widgetMedia=self._widgets.get_widget('mediaProb')
            media=widgetMedia.get_text()
            widgetdTipica=self._widgets.get_widget('dTipicaProb')
            dTipica=widgetdTipica.get_text()
         
            # Se calcula la probabilidad
            x=self.calcularProb(dato1, dato2, media, dTipica)

        else:
                # Extraigo las iteraciones totales
            totales=self._widgets.get_widget('iteracionesTotales')
            itTotales=totales.get_text()

            intervalos=[]
            for n in self.intervalos:
                d=n.split('[')
                interv=d[1].split(',')
                intervalos.append(interv) 

            # Se calcula la probabilidad
            x=self.calcularProbSim(dato1, dato2, intervalos, itTotales)
    
        # Se muestra el resultado en la casilla correspondiente
        prob=str('%3.2f'%(x*100))+' %'
        resultado1=self._widgets.get_widget('resultado1Prob')
        resultado1.set_text(prob)

        # Se muestra el resultado completo en el textView
        if dato2=='':
            mostrarDato='P ( '+str(dato1)+gettext.gettext(' < Project ) = ')+str('%3.3f'%(x))+' ('+prob+')'
        elif dato1=='':
            mostrarDato=gettext.gettext('P ( Project < ')+str(dato2)+' ) = '+str('%3.3f'%(x))+' ('+prob+')'
        else:
            mostrarDato='P ( '+str(dato1)+gettext.gettext(' < Project > ')+str(dato2)+' ) = '+str('%3.3f'%(x))+' ('+prob+')'
        self.escribirProb(mostrarDato)

    def on_btnProbabilityReset_clicked(self, button):
        self._widgets.get_widget('valor3Prob').set_value(90)
        self.on_probability_changed(None)

    def on_probability_changed(self, widget):
        """
        Acción usuario al activar el valor introducido en 
                 el tercer gtk.Entry de la ventana de probabilidades          

        Parámetros: entry (entry activado)
        """

        # Se extrae el valor de probabilidad de la interfaz
        valor3=self._widgets.get_widget('valor3Prob')   
        dato3=float(valor3.get_value() / 100)
        #print dato3, 'dato3'

        x=0
        titulo=self.vProbabilidades.get_title()
        if titulo==gettext.gettext('Probability related to the path'):         
            # Se extrae la media y la desviación típica de la interfaz
            widgetMedia=self._widgets.get_widget('mediaProb')
            media=widgetMedia.get_text()
            widgetdTipica=self._widgets.get_widget('dTipicaProb')
            dTipica=widgetdTipica.get_text()

            valorTabla=float(scipy.stats.distributions.norm.ppf(float(dato3)))
            #print valorTabla

            x=(valorTabla*float(dTipica))+float(media)

        else:
            # Extraigo las iteraciones totales
            totales=self._widgets.get_widget('iteracionesTotales')
            itTotales=totales.get_text()

            intervalos=[]
            for n in self.intervalos:
                d=n.split('[')
                interv=d[1].split(',')
                intervalos.append(interv) 

            # Se calcula la probabilidad
            suma=0
            for n in range(len(intervalos)):
                suma+=self.Fa[n]/float(itTotales)
                if suma>float(dato3) or suma==float(dato3):
                    x=intervalos[n][1]
                    break
             
        if x==0:
            return             
        # Se muestra el resultado en la casilla correspondiente
        tiempo='%5.2f'%(float(x))+' u.d.t.'
        resultado2=self._widgets.get_widget('resultado2Prob')
        resultado2.set_text(tiempo)

    def on_btnProbabilityCalculate_clicked(self, button):
        """
        Acción usuario al activar el valor introducido en 
                 el tercer gtk.Entry de la ventana de probabilidades          

        Parámetros: entry (entry activado)
        """

        # Se extrae el valor de probabilidad de la interfaz
        valor3=self._widgets.get_widget('valor3Prob')   
        dato3=float(valor3.get_value() / 100)
        #print dato3, 'dato3'

        x=0
        titulo=self.vProbabilidades.get_title()
        if titulo==gettext.gettext('Probability related to the path'):         
            # Se extrae la media y la desviación típica de la interfaz
            widgetMedia=self._widgets.get_widget('mediaProb')
            media=widgetMedia.get_text()
            widgetdTipica=self._widgets.get_widget('dTipicaProb')
            dTipica=widgetdTipica.get_text()

            valorTabla=float(scipy.stats.distributions.norm.ppf(float(dato3)))
            #print valorTabla

            x=(valorTabla*float(dTipica))+float(media)

        else:
            # Extraigo las iteraciones totales
            totales=self._widgets.get_widget('iteracionesTotales')
            itTotales=totales.get_text()

            intervalos=[]
            for n in self.intervalos:
                d=n.split('[')
                interv=d[1].split(',')
                intervalos.append(interv) 

            # Se calcula la probabilidad
            suma=0
            for n in range(len(intervalos)):
                suma+=self.Fa[n]/float(itTotales)
                if suma>float(dato3) or suma==float(dato3):
                    x=intervalos[n][1]
                    break
             
        if x==0:
            return             
        # Se muestra el resultado en la casilla correspondiente
        tiempo='%5.2f'%(float(x))+' u.d.t.'
        resultado2=self._widgets.get_widget('resultado2Prob')
        resultado2.set_text(tiempo)

        # Se muestra el resultado completo en el textView
        prob='%5.2f'%(float(dato3)*100)
        mostrarDato=gettext.gettext('P ( Project < ')+tiempo+' ) = '+str(prob)+' %'
        
        self.escribirProb(mostrarDato)
               

    def on_btAceptarProb_clicked(self, boton):
        """
           Acción usuario para aceptar la información que
                    muestra la ventana de cálculo de probabilidades
  
           Parámetros: boton (botón clickeado)
        """
        titulo=self.vProbabilidades.get_title()
        if titulo==gettext.gettext('Probability related to the path'):
            self.limpiarVentanaProb(0)
        else:
            self.limpiarVentanaProb(1)

        self.vProbabilidades.hide()
  
    def on_wndProbabilidades_delete_event(self, ventana, evento):
        """
         Acción usuario para cerrar la ventana de cálculo 
                  de probabilidades

         Parámetros: ventana (ventana actual)
                     evento (evento cerrar)
        """
        titulo=self.vProbabilidades.get_title()
        if titulo==gettext.gettext('Probability related to the path'):
            self.limpiarVentanaProb(0)
        else:
            self.limpiarVentanaProb(1)

        ventana.hide()
        return True



# --- Simulation window

    def on_btContinuarIterando_clicked(self, boton):
        """
        -
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        self._widgets.get_widget('btProbSim').set_sensitive(True)
        self._widgets.get_widget('btGuardarSim').set_sensitive(True)
        # Se extrae el número de iteraciones 
        iteracion=self._widgets.get_widget('iteracion')
        it=iteracion.get_value_as_int()
        #print it, 'iteraciones'
  
        # Se almacenan las iteraciones totales en una variable y se muestra en la interfaz
        totales=self._widgets.get_widget('iteracionesTotales')
        interfaz=totales.get_text()
        if interfaz!='':
            itTotales= it +int(interfaz)
        else:
            itTotales= it
        #print itTotales, 'iteraciones totales'
        totales.set_text(str(itTotales))
  
        # Se realiza la simulación
        simulacion=self.simulacion(it)
        self.simTotales.append(simulacion)
        #print len(self.simTotales), 'simulaciones'
        #for s in self.simTotales:
            #print s
   
        # Se crea el grafo Pert y se renumera
        grafoRenumerado=self.pertFinal()
  
        # Nuevos nodos
        nodosN=[]
        for n in range(len(grafoRenumerado.graph)):
            nodosN.append(n+1)
         
        # Zaderenko
        if simulacion==None:
            return
        else:
            for s in simulacion: 
                matrizZad=mZad(self.actividad,grafoRenumerado.activities, nodosN, 0, s)
                tearly=early(nodosN, matrizZad)  
                tlast=last(nodosN, tearly, matrizZad)      
                tam=len(tearly)
                # Se calcula la duración del proyecto para cada simulación
                duracionProyecto=tearly[tam-1]
                #print duracionProyecto, 'duracion proyecto'  
                self.duraciones.append(duracionProyecto) 
                #print self.duraciones,'duraciones simuladas'
                # Se extraen los caminos crí­ticos y se calcula su í­ndice de criticidad
                self.indiceCriticidad(grafoRenumerado, s, tearly, tlast, itTotales)
    
                # Se añaden la media y la desviación típica a la interfaz
                duracionMedia=scipy.stats.mean(self.duraciones)
                media=self._widgets.get_widget('mediaSim')
                media.set_text(str(duracionMedia))
    
                desviacionTipica=scipy.stats.std(self.duraciones)
                dTipica=self._widgets.get_widget('dTipicaSim')
                dTipica.set_text(str(desviacionTipica))
    
        # Se calculan los intervalos
        interv=[]
        N=20 # Número de intervalos
        dMax=float(max(self.duraciones)+0.00001)  # duración máxima
        dMin=float(min(self.duraciones))   # duración mí­nima
        #print dMax, 'max', dMin, 'min'
        if int(it)==int(itTotales):
            for n in range(N):
                valor='['+str('%5.2f'%(simulation.duracion(n, dMax, dMin, N)))+', '+str('%5.2f'%(simulation.duracion((n+1), dMax, dMin, N)))+'['       
                interv.append(valor)
        if self.intervalos==[]:
            self.intervalos=interv
   
        # Se calculan las frecuencias
        self.Fa, Fr=simulation.calcularFrecuencias(self.duraciones, dMax, dMin, itTotales, N)
  
        # Se muestran los intervalos y las frecuencias en forma de tabla en la interfaz
        self.modeloF.clear()
        i = 0
        for column in self.vistaFrecuencias.get_columns()[1:]:
            column.set_title(self.intervalos[i])
            i = i + 1
        self.modeloF.append([gettext.gettext("Absolute freq.")] + map(str,self.Fa))
        self.modeloF.append([gettext.gettext("Relative freq.")] + map(str,Fr))
        #self.mostrarFrecuencias(self.intervalos, self.Fa, Fr)
  
        # Dibuja histograma devolviendo los intervalos (bins) y otros datos
        fig = Figure(figsize=(5,4), dpi=100)
        ax = fig.add_subplot(111)
  
        n, bins, patches = ax.hist(self.duraciones, 100, normed=1)
        canvas = FigureCanvas(fig)  # a gtk.DrawingArea
        if len(self.boxS)>0: # Si ya hay introducido un box, que lo borre y lo vuelva a añadir
            self.hBoxSim.remove(self.boxS)
            self.boxS=gtk.VBox()

        self.hBoxSim.add(self.boxS)
        self.boxS.pack_start(canvas)
        self.boxS.show_all()
  
    def on_btAceptarSim_clicked(self, boton):
        """
        Acción usuario para aceptar la información que
                 muestra la ventana de simulación de duraciones:
                 tabla, gráfica, ....
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        self.limpiarVentanaSim()
        self.vSimulacion.hide()
         
    def on_btProbSim_clicked(self, boton):
        """
        Acción usuario para acceder a la ventana de 
                 cálculo de probabilidades
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        # Se asigna tí­tulo 
        self.vProbabilidades.set_title(gettext.gettext('Probability related to the simulation'))
        
        # Extraigo los valores de la media y la desviación típica
        media=self._widgets.get_widget('mediaSim')
        m=media.get_text()
        dTipica=self._widgets.get_widget('dTipicaSim')
        dt=dTipica.get_text()
  
        # Se muestran la media y desviación típica en la ventana de probabilidades
        widgetMedia=self._widgets.get_widget('mediaProb')
        widgetMedia.set_text(m)
        widgetdTipica=self._widgets.get_widget('dTipicaProb')
        widgetdTipica.set_text(dt)
  
  
        # Se muestra la gráfica
        fig = Figure(figsize=(5,4), dpi=100)
        ax = fig.add_subplot(111)
        n, bins, patches = ax.hist(self.duraciones, 100, normed=1)
        canvas = FigureCanvas(fig)  # a gtk.DrawingArea
        if len(self.box)>0:
            self.vBoxProb.remove(self.box)
            self.box=gtk.VBox()
            
        self.vBoxProb.add(self.box)
        self.box.pack_end(canvas)
        self.box.show_all()
        self.vProbabilidades.show()
        self.on_btnIntervalReset_clicked(None)
        self.on_btnProbabilityReset_clicked(None)
  
    def on_btGuardarSim_clicked(self, boton):
        """
        Acción usuario para salvar la información que
                 muestra la ventana de simulación de duraciones
                 tabla, gráfica, ....
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        # Se extraen los datos de la interfaz
        # Media y desviación tí­pica
        media=self._widgets.get_widget('mediaSim')
        m=media.get_text()
        dTipica=self._widgets.get_widget('dTipicaSim')
        dt=dTipica.get_text()
        # Iteraciones
        totales=self._widgets.get_widget('iteracionesTotales')
        iteraciones=totales.get_text()
  
        # Se pasan los datos de la simulación a formato CSV
        simulacionCsv = simulation.datosSimulacion2csv(self.duraciones, iteraciones, m, dt, self.modeloC)
        
        # Se muestra el diálogo para salvar el archivo
        fileFormats.guardarCsv(simulacionCsv, self)
  
  
    def on_wndSimulacion_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de simulación 
                 de duraciones
  
        Parámetros: ventana (ventana actual)
                    evento (evento cerrar)
  
        Valor de retorno: -
        """
        self.limpiarVentanaSim()
        ventana.hide()
        return True

# --- Resources
  
    def on_btAsignarRec_clicked(self, boton):
        """
        Acción usuario para acceder a la ventana de recursos
                 necesarios por actividad 
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        
        Nota: Antes de introducir los recursos que cada actividad necesita, deben existir tanto recursos como actividades.
        """
        # Se comprueba que se hayan introducido actividades
        if self.actividad == []:
            self.dialogoError(gettext.gettext('No activities introduced'))
 
        # Se comprueba que se hayan introducido recursos
        elif self.recurso == []:
            self.dialogoError(gettext.gettext('No resources introduced'))
           
        # Si todo es correcto, se accede a la ventana con normalidad
        else:
            self.vAsignarRec.show()

        
    def on_wndRecursos_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de recursos
  
        Parámetros: ventana (ventana actual)
                    evento (evento cerrar)
  
        Valor de retorno: -
        """
        ventana.hide()
        return True
   
   
  
# --- Necessary resources per activity

    def on_btAceptarAR_clicked(self, boton):
        """
        Acción usuario para aceptar la información que
                 muestra la ventana de recursos necesarios por
                 actividad: actividad, recurso, unidad necesaria
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        if self.asignacion==[]: 
            self.vAsignarRec.hide()
   
        else:
            # Se comprueba que las actividades y los recursos introducidos existen
            errorAct=self.comprobarActExisten(self.actividad)
            errorRec=self.comprobarRecExisten(self.recurso)
   
            if errorAct==0 and errorRec==0:
                # Se actualiza la columna de recursos en la introducción de las actividades
                mostrarColumnaRec=self.mostrarRec(self.asignacion, 1)
                self.actualizarColR(mostrarColumnaRec)
                self.vAsignarRec.hide()
 
                 
    def on_btCancelarAR_clicked(self, boton):
        """
        Acción usuario para cancelar la información que
                 muestra la ventana de recursos necesarios por
                 actividad: actividad, recurso, unidad necesaria. 
                 Si se cancelan los datos, se borran definitivamente
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        self.modeloAR.clear()
        self.asignacion=[]
        self.vAsignarRec.hide()
   
    def on_wndAsignarRec_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de recursos
                 necesarios por actividad 
  
        Parámetros: ventana (ventana actual)
                    evento (evento cerrar)
  
        Valor de retorno: -
        """
        ventana.hide()
        return True
  
  
# --- Calculate paths

    def on_btAceptarCaminos_clicked(self, boton):
        """
        Acción usuario para aceptar la información que
                 muestra la ventana de calcular caminos
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        self.vCaminos.hide()
  
    def on_btExportarCsv_clicked(self, boton): 
        """
        Acción usuario para exportar los caminos que se
                 muestran en la ventana a formato CSV para 
                 hoja de cálculo
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        # Se buscan todos los caminos 
        successors = self.tablaSucesoras(self.actividad)
        g = graph.roy(successors)
        todosCaminos = graph.findAllPaths(g, 'Begin', 'End')
  
        # Se pasan a formato CSV
        #pathsInCSV = graph.royPaths2csv2(g)
        pathsInCSV = graph.royPaths2csv([self.actividad[i][1] for i in range(len(self.actividad))], todosCaminos)
        
        # Se muestra el diálogo para salvar el archivo
        fileFormats.guardarCsv(pathsInCSV, self) 
  
    def on_wndCaminos_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de calcular
                 caminos
  
        Parámetros: ventana (ventana actual)
                    evento (evento cerrar)
  
        Valor de retorno: -
        """
        ventana.hide()
        return True
  
  
# --- Help ---

    def on_dAyuda_response(self, False, boton):
        """
        Acción usuario para aceptar la información que
                 muestra el diálodo de ayuda
  
        Parámetros: boton (botón clickeado)
  
        Valor de retorno: -
        """
        self.dAyuda.hide()
  
    def on_dAyuda_delete_event(self, dialogo, evento):
        """
        Acción usuario para cerrar el diálogo de ayuda 
  
        Parámetros: ventana (ventana actual)
                    evento (evento cerrar)
  
        Valor de retorno: -
        """
        self.dAyuda.hide()
        return True

    def on_tab_clicked(self, widget, event):
        """
          xxx lacks comment
        """
        if event.button == 3:
            for i in range(self.ntbSchedule.get_n_pages()):
                x, y = self.ntbSchedule.translate_coordinates(self.vPrincipal, int(event.x), int(event.y))
                if self.schedule_tab_labels[i].intersect(gtk.gdk.Rectangle(x, y, 1, 1)):
                    self.clicked_tab = i
                    self._widgets.get_widget("mnTabsDelete").set_sensitive(i != 0)
                    self._widgets.get_widget("ctxTabsMenu").popup(None, None, None, event.button, event.time)
                    break

    def delete_tab(self, widget):
        self.schedule_tab_labels.remove(self.schedule_tab_labels[self.clicked_tab])
        if self.clicked_tab == self.ntbSchedule.get_current_page():
            self.ntbSchedule.set_current_page((self.clicked_tab - 1) % self.ntbSchedule.get_n_pages())
        del self.schedules[self.clicked_tab]
        self.ntbSchedule.remove_page(self.clicked_tab)
        self.set_modified(True)
        self.modified = 1

    def new_tab(self, widget):
        new_sched = deepcopy(self.schedules[0][1])
        self.add_schedule(None, new_sched )

    def on_tab_changed(self, notebook, page, page_num):
        self.set_schedule(self.schedules[page_num][1])


def main(filename=None):
    app = PPCproject()
    if filename:
        app.openProject(filename)
    gtk.main()   


# --- Start running as a program
if __name__ == '__main__':
    if   len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print gettext.gettext('Syntax is:')
        print sys.argv[0], '[project_file]'


