#!/usr/bin/env python
# -*- coding: utf-8 -*-

#PPC-PROJECT. HERRAMIENTA MULTIPLATAFORMA PARA LA
#DOCENCIA E INVESTIGACIÓN EN GESTIÓN DE PROYECTOS
#Copyright (C) 2007 UNIVESIDAD DE CÓRDOBA
#Author: CRISTINA URBANO ROLDÁN

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
pygtk.require('2.0')
import gobject
import gtk
import gtk.glade

#Internationalization
import gettext

import pert, graph

import pickle
import os, math, sys
from os.path import basename
import random
import scipy.stats
from matplotlib import rcParams
rcParams['text.fontname'] = 'cmr10'
from pylab import *
from matplotlib.axes import Subplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas

#Internationalization
APP='PPC-Project' #Program name
DIR='po' #Directory containing translations, usually /usr/share/locale
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
gtk.glade.bindtextdomain(APP, DIR)
gtk.glade.textdomain(APP)

# Se crea la clase Proyecto, que englobará toda la aplicación

class Proyecto:
   def __init__(self):
      self._widgets = gtk.glade.XML('proyecto.glade')
      self._widgets.signal_autoconnect(self)

      self.bufer=gtk.TextBuffer()
      self.directorio= gettext.gettext('Unnamed -PPC-Project')
      self.control=0
      self.vBoxProb=self._widgets.get_widget('vbProb')
      self.grafica=gtk.Image()
      self.box=gtk.VBox()
      self.hBoxSim=self._widgets.get_widget('hbSim')
      self.boxS=gtk.VBox()
        
      # Estructuras de datos básicas de la aplicación
      self.actividad=[]
      self.recurso=[]
      self.asignacion=[]
      self.tabla=[]

         
#####################################################################################################################

      self.vPrincipal=self._widgets.get_widget('wndPrincipal')
      self.vIntroduccion=self._widgets.get_widget('wndIntroduccion')
      self.vZaderenko = self._widgets.get_widget('wndZaderenko')
      self.vActividades=self._widgets.get_widget('wndActividades')
      self.vHolguras=self._widgets.get_widget('wndHolguras')
      self.vProbabilidades=self._widgets.get_widget('wndProbabilidades')
      self.vSimulacion=self._widgets.get_widget('wndSimulacion')
      self.vRecursos=self._widgets.get_widget('wndRecursos')
      self.vAsignarRec=self._widgets.get_widget('wndAsignarRec')
      self.vCaminos=self._widgets.get_widget('wndCaminos')
      self.vRoy=self._widgets.get_widget('wndGrafoRoy')
      self.vPert=self._widgets.get_widget('wndGrafoPert')
      self.dAyuda=self._widgets.get_widget('dAyuda')
      self.bHerramientas=self._widgets.get_widget('bHerramientas')
      
        

##############################  CREAMOS TODOS LOS TREEVIEWS DE LA APLICACIÓN  #######################################  
     
#-----------------------------------------------------------
# Función: Creación de todos los TreeViews que se utilizarán
#          en la aplicación
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------
 
   def crearTreeViews(self):

   # TREEVIEW para la INTRODUCCIÓN DE DATOS
      self.vistaLista=self._widgets.get_widget('vistaListaDatos')
      self.vistaLista.show() 
      self.selec=self.vistaLista.get_selection()
      self.selec.set_mode(gtk.SELECTION_MULTIPLE)
      mode=self.selec.get_mode()   
      self.menu=gtk.Menu()
      self.modelo = gtk.ListStore(int, str, str, str, str, str, str, str, str, str)
      self.vistaLista.set_model(self.modelo)
      self.orden=gtk.TreeModelSort(self.modelo)
      self.orden.set_sort_column_id(0,gtk.SORT_ASCENDING)
      self.vistaLista.columna=[None]*11
      self.vistaLista.columna[0] = gtk.TreeViewColumn(gettext.gettext('ID'))
      self.vistaLista.columna[1] = gtk.TreeViewColumn(gettext.gettext('Activities'))
      self.vistaLista.columna[2] = gtk.TreeViewColumn(gettext.gettext('Following Act.'))
      self.vistaLista.columna[3] = gtk.TreeViewColumn(gettext.gettext('Optimistic Dur.'))
      self.vistaLista.columna[4] = gtk.TreeViewColumn(gettext.gettext('Most Probable Dur.'))
      self.vistaLista.columna[5] = gtk.TreeViewColumn(gettext.gettext('Pessimistic Dur.'))
      self.vistaLista.columna[6] = gtk.TreeViewColumn(gettext.gettext('Average Dur.'))
      self.vistaLista.columna[7] = gtk.TreeViewColumn(gettext.gettext('Typical Dev.'))
      self.vistaLista.columna[8] = gtk.TreeViewColumn(gettext.gettext('Resources'))
      self.vistaLista.columna[9] = gtk.TreeViewColumn(gettext.gettext('Distribution'))
      self.vistaLista.renderer=[None]*10 
         
      self.columnaNoEditableColor(0)
      self.columnaEditable(self.vistaLista, self.modelo, 1)
      self.modeloComboS=self.columnaCombo(self.vistaLista, self.modelo, 2)
      self.columnaEditable(self.vistaLista, self.modelo, 3)
      self.columnaEditable(self.vistaLista, self.modelo, 4)
      self.columnaEditable(self.vistaLista, self.modelo, 5)
      self.columnaEditable(self.vistaLista, self.modelo, 6)
      self.columnaEditable(self.vistaLista, self.modelo, 7)
      self.columnaNoEditableColor(8)
      self.modeloComboD=self.columnaCombo(self.vistaLista, self.modelo, 9)  
      
      # Se añaden los tipos de distribución
      self.modeloComboD.append([gettext.gettext('Normal')])
      self.modeloComboD.append([gettext.gettext('Triangular')])
      self.modeloComboD.append([gettext.gettext('Beta')])
      self.modeloComboD.append([gettext.gettext('Uniform')])

      # Se ocultan algunas columnas 
      self.vistaLista.columna[3].set_visible(False) 
      self.vistaLista.columna[4].set_visible(False)
      self.vistaLista.columna[5].set_visible(False)  
      self.vistaLista.columna[8].set_visible(False) 
      self.vistaLista.columna[9].set_visible(False) 

      # Columna menu
      self.menu=gtk.Menu()
      self.imagen=gtk.Image()
      self.imagen.set_from_file('icono076.gif')
      self.imagen.show()
      self.vistaLista.columna[10] = gtk.TreeViewColumn()
      self.vistaLista.columna[10].set_widget(self.imagen)
      self.vistaLista.render = gtk.CellRendererText()
      self.vistaLista.render.set_property('cell-background', 'lightGoldenRodYellow')
      self.vistaLista.append_column(self.vistaLista.columna[10])
      self.vistaLista.columna[10].pack_start(self.vistaLista.render, True)
      self.vistaLista.columna[10].set_attributes(self.vistaLista.render)
      self.vistaLista.columna[10].set_clickable(True)
      self.vistaLista.columna[10].connect('clicked', self.columna_press, self.menu) 
      self.vistaLista.columna[10].set_expand(False)
      self.checkColum=[None]*9
      self.checkColum[0] = gtk.CheckMenuItem(gettext.gettext('Activities'), True)
      self.checkColum[1] = gtk.CheckMenuItem(gettext.gettext('Following Act.'), True)
      self.checkColum[2] = gtk.CheckMenuItem(gettext.gettext('Optimistic Dur.'), True)
      self.checkColum[3] = gtk.CheckMenuItem(gettext.gettext('Most Probable Dur.'), True)
      self.checkColum[4] = gtk.CheckMenuItem(gettext.gettext('Pessimistic Dur.'), True)
      self.checkColum[5] = gtk.CheckMenuItem(gettext.gettext('Average Dur.'), True)
      self.checkColum[6] = gtk.CheckMenuItem(gettext.gettext('Typical Dev.'), True)
      self.checkColum[7] = gtk.CheckMenuItem(gettext.gettext('Resources'), True)
      self.checkColum[8] = gtk.CheckMenuItem(gettext.gettext('Distribution'), True)
      for n in range(9):
         self.menu.add(self.checkColum[n])
         self.checkColum[n].set_active(True)

      # Las columnas inactivas aparecen desactivadas en el menú
      self.checkColum[2].set_active(False)
      self.checkColum[3].set_active(False)
      self.checkColum[4].set_active(False)
      self.checkColum[7].set_active(False)
      self.checkColum[8].set_active(False)

      # TREEVIEW para los caminos (ventana de ZADERENKO)
      self.vistaListaZ = self._widgets.get_widget('vistaListaZad')
      self.modeloZ = gtk.ListStore(str, str, str, bool)
      self.vistaListaZ.set_model(self.modeloZ)
      self.ordenZ=gtk.TreeModelSort(self.modeloZ)
      self.ordenZ.set_sort_column_id(0,gtk.SORT_ASCENDING)
      self.vistaListaZ.columna=[None]*3
      self.vistaListaZ.columna[0] = gtk.TreeViewColumn(gettext.gettext('Duration'))
      self.vistaListaZ.columna[1] = gtk.TreeViewColumn(gettext.gettext('Typical Dev.'))
      self.vistaListaZ.columna[2] = gtk.TreeViewColumn(gettext.gettext('Path'))
      self.vistaListaZ.renderer=[None]*3
        
      self.columnaNoEditable(self.vistaListaZ, 0)
      self.columnaNoEditable(self.vistaListaZ, 1)
      self.columnaNoEditable(self.vistaListaZ, 2)

      for n in range(2):
         self.vistaListaZ.columna[n].set_expand(False)

                 
     # TREEVIEW para las ACTIVIDADES y NODOS
      self.vistaListaA = self._widgets.get_widget('vistaListaAct')
      self.modeloA = gtk.ListStore(str, str, str)
      self.vistaListaA.set_model(self.modeloA)
      self.ordenA=gtk.TreeModelSort(self.modeloA)
      self.ordenA.set_sort_column_id(0,gtk.SORT_ASCENDING)
      self.vistaListaA.columna=[None]*3
      self.vistaListaA.columna[0] = gtk.TreeViewColumn(gettext.gettext('Activity'))
      self.vistaListaA.columna[1] = gtk.TreeViewColumn(gettext.gettext('First Node'))
      self.vistaListaA.columna[2] = gtk.TreeViewColumn(gettext.gettext('Last Node'))
      self.vistaListaA.renderer=[None]*3

      self.columnaNoEditable(self.vistaListaA, 0)
      self.columnaNoEditable(self.vistaListaA, 1)
      self.columnaNoEditable(self.vistaListaA, 2)


     # TREEVIEW para las HOLGURAS
      self.vistaListaH = self._widgets.get_widget('vistaListaHolg')
      self.modeloH = gtk.ListStore(str, str, str, str)
      self.vistaListaH.set_model(self.modeloH)
      self.ordenH=gtk.TreeModelSort(self.modeloH)
      self.ordenH.set_sort_column_id(0,gtk.SORT_ASCENDING)
      self.vistaListaH.columna=[None]*4
      self.vistaListaH.columna[0] = gtk.TreeViewColumn(gettext.gettext('Activities'))
      self.vistaListaH.columna[1] = gtk.TreeViewColumn(gettext.gettext('Total Sl.'))
      self.vistaListaH.columna[2] = gtk.TreeViewColumn(gettext.gettext('Free Sl.'))
      self.vistaListaH.columna[3] = gtk.TreeViewColumn(gettext.gettext('Independent Sl.'))
      self.vistaListaH.renderer=[None]*4

      self.columnaNoEditable(self.vistaListaH, 0)
      self.columnaNoEditable(self.vistaListaH, 1)
      self.columnaNoEditable(self.vistaListaH, 2)
      self.columnaNoEditable(self.vistaListaH, 3)


      # TREEVIEW para los RECURSOS
      self.vistaListaR = self._widgets.get_widget('vistaListaRec')
      self.modeloR = gtk.ListStore(str, str, str, str)
      self.vistaListaR.set_model(self.modeloR)
      self.ordenR=gtk.TreeModelSort(self.modeloR)
      self.ordenR.set_sort_column_id(0,gtk.SORT_ASCENDING)
      self.vistaListaR.columna=[None]*4
      self.vistaListaR.columna[0] = gtk.TreeViewColumn(gettext.gettext('Name'))
      self.vistaListaR.columna[1] = gtk.TreeViewColumn(gettext.gettext('Kind'))
      self.vistaListaR.columna[2] = gtk.TreeViewColumn(gettext.gettext('Project Dur. Unit'))
      self.vistaListaR.columna[3] = gtk.TreeViewColumn(gettext.gettext('Period Dur. Unit'))
      self.vistaListaR.renderer=[None]*4
     
      self.columnaEditable(self.vistaListaR, self.modeloR, 0)
      self.modeloComboR=self.columnaCombo(self.vistaListaR, self.modeloR, 1)
      self.columnaEditable(self.vistaListaR, self.modeloR, 2)
      self.columnaEditable(self.vistaListaR, self.modeloR, 3)

      # Se añaden los tipos de recursos
      self.modeloComboR.append([gettext.gettext('Renewable')])
      self.modeloComboR.append([gettext.gettext('Non renewable')])
      self.modeloComboR.append([gettext.gettext('Double restricted')])
      self.modeloComboR.append([gettext.gettext('Unlimited')])
  
      # TREEVIEW para los RECURSOS NECESARIOS POR ACTIVIDAD
      self.vistaListaAR = self._widgets.get_widget('vistaListaAR')
      self.modeloAR = gtk.ListStore(str, str, str)
      self.vistaListaAR.set_model(self.modeloAR)
      self.ordenAR=gtk.TreeModelSort(self.modeloAR)
      self.ordenAR.set_sort_column_id(0,gtk.SORT_ASCENDING)
      self.vistaListaAR.columna=[None]*3
      self.vistaListaAR.columna[0] = gtk.TreeViewColumn(gettext.gettext('Activity'))
      self.vistaListaAR.columna[1] = gtk.TreeViewColumn(gettext.gettext('Resource'))
      self.vistaListaAR.columna[2] = gtk.TreeViewColumn(gettext.gettext('Needed Units'))
      self.vistaListaAR.renderer=[None]*3

      self.columnaEditable(self.vistaListaAR, self.modeloAR, 0)
      self.columnaEditable(self.vistaListaAR, self.modeloAR, 1)
      self.columnaEditable(self.vistaListaAR, self.modeloAR, 2)


      # TREEVIEW para los caminos (ventana de SIMULACIÓN)
      self.vLCriticidad = self._widgets.get_widget('vistaListaCriticidad')
      self.modeloC = gtk.ListStore(str, str, str)
      self.vLCriticidad.set_model(self.modeloC)
      self.ordenC=gtk.TreeModelSort(self.modeloC)
      self.ordenC.set_sort_column_id(0,gtk.SORT_ASCENDING)
      self.vLCriticidad.columna=[None]*3
      self.vLCriticidad.columna[0] = gtk.TreeViewColumn(gettext.gettext('N'))
      self.vLCriticidad.columna[1] = gtk.TreeViewColumn(gettext.gettext('I.Criticidad'))
      self.vLCriticidad.columna[2] = gtk.TreeViewColumn(gettext.gettext('Paths'))
      self.vLCriticidad.renderer=[None]*3
      
      self.columnaNoEditable(self.vLCriticidad, 0)
      self.columnaNoEditable(self.vLCriticidad, 1)
      self.columnaNoEditable(self.vLCriticidad, 2)

      for n in range(2):
         self.vLCriticidad.columna[n].set_expand(False)
       


#####################################################################################################################
                                 # FUNCIONES RELACIONADAS CON LOS TREEVIEW #
#####################################################################################################################

#-----------------------------------------------------------
# Función: Creación de las columnas no editables y con 
#          color de celda
#
# Parámetros: n (columna)
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def columnaNoEditableColor(self, n):  
      self.vistaLista.renderer[n] = gtk.CellRendererText()
      self.vistaLista.renderer[n].set_property('editable', False)
      self.vistaLista.renderer[n].set_property('cell-background', 'lightGoldenRodYellow')
      self.vistaLista.append_column(self.vistaLista.columna[n])
      self.vistaLista.columna[n].set_sort_column_id(n)
      self.vistaLista.columna[n].pack_start(self.vistaLista.renderer[n], True)
      self.vistaLista.columna[n].set_attributes(self.vistaLista.renderer[n], text=n)
      self.vistaLista.columna[n].set_spacing(8)
      self.vistaLista.columna[n].set_expand(True)
      self.vistaLista.columna[0].set_expand(False)
      self.vistaLista.columna[n].set_resizable(True)
      

#*********************************************************************
#-----------------------------------------------------------
# Función: Creación de las columnas no editables y 
#          sin color de celda 
#
# Parámetros: vista (widget que muestra el treeview)
#             n (columna)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def columnaNoEditable(self, vista, n):
      vista.renderer[n] = gtk.CellRendererText()
      vista.append_column(vista.columna[n])
      vista.columna[n].set_sort_column_id(n)
      vista.columna[n].pack_start(vista.renderer[n], True)
      vista.columna[n].set_attributes(vista.renderer[n], text=n)
      vista.columna[n].set_spacing(8)
      vista.columna[n].set_expand(True)
      vista.columna[n].set_reorderable(True)

#********************************************************************
#-----------------------------------------------------------
# Función: Creación de las columnas editables y con color
#          de celda
#
# Parámetros: vista (widget que muestra el treeview)
#             modelo (lista) 
#             n (columna)
#
# Valor de retorno: -
#-----------------------------------------------------------                           
     
   def columnaEditable(self, vista, modelo, n):
      vista.renderer[n] = gtk.CellRendererText()
      vista.renderer[n].set_property('editable', True)
      vista.renderer[n].set_property('cell-background', 'lightGoldenRodYellow')
      vista.renderer[n].connect('edited', self.col_edited_cb, modelo, n)
      vista.append_column(vista.columna[n])
      vista.columna[n].set_sort_column_id(n)
      vista.columna[n].pack_start(vista.renderer[n], True)
      vista.columna[n].set_attributes(vista.renderer[n], text=n)
      vista.columna[n].set_spacing(8)
      vista.columna[n].set_expand(True)
      vista.columna[n].set_resizable(True)
      vista.columna[n].set_reorderable(True)
      
#********************************************************************
#-----------------------------------------------------------
# Función: Creación de todas las columnas combo (selector)
#
# Parámetros: vista (widget que muestra el treeview)
#             modelo (lista) 
#             n (columna)
#
# Valor de retorno: modeloCombo (lista para los datos del selector)
#-----------------------------------------------------------
     
   def columnaCombo(self, vista, modelo, n):
      modeloCombo=gtk.ListStore(str)
      vista.renderer[n]=gtk.CellRendererCombo()
      vista.renderer[n].set_property('editable', True)
      vista.renderer[n].connect('edited', self.col_edited_cb, modelo, n)
      vista.renderer[n].set_property('model', modeloCombo)
      #vista.renderer[n].set_property('has-entry', False)
      vista.renderer[n].set_property('text-column', 0)
      vista.renderer[n].set_property('cell-background', 'lightGoldenRodYellow')
      vista.append_column(vista.columna[n])
      vista.columna[n].set_sort_column_id(n)
      vista.columna[n].pack_start(vista.renderer[n], True)
      vista.columna[n].set_attributes(vista.renderer[n], text=n)
      vista.columna[n].set_resizable(True)
      #vista.columna[n].set_min_width(150)

      return modeloCombo


#********************************************************************************
#-----------------------------------------------------------
# Función: Muestra los items del menu en la última columna del treeview de 
#          introducción de datos al presionar sobre dicha columna
#
# Parámetros: columna (columna presionada)
#             menu (gtk.Menu)
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def columna_press(self, columna, menu): 
      menu.show_all()
      menu.popup(None, None, None, 1, 0)
      for n in range(9):
         self.checkColum[n].connect('activate', self.activarItem, n)


#*********************************************************** 
#-----------------------------------------------------------
# Función: Activación o desactivación de las columnas según el item 
#          seleccionado en el menu
#
# Parámetros: item (item seleccionado)
#             n (posición en el menu del item seleccionado)
#
# Valor de retorno: -
#-----------------------------------------------------------
        
   def activarItem(self, item, n):
      if item==self.checkColum[n]:
         if self.checkColum[n].get_active():
            self.vistaLista.columna[n+1].set_visible(True)
         else:
            self.vistaLista.columna[n+1].set_visible(False)



#####################################################################################################################
                           # FUNCIONES DE INTRODUCCIÓN, CARGA Y ACTUALIZACIÓN DATOS #
#####################################################################################################################

#-----------------------------------------------------------
# Función: Creación de un nuevo proyecto, eliminación de la lista actual y
#          adicción de una fila vacía a la lista
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------

   def introduccionDatos(self):
      self.directorio=gettext.gettext('Unnamed -PPC-Project') #nombre del proyecto
      self.vPrincipal.set_title(self.directorio)
      # Se limpian las listas y la interfaz para la introducción de nuevos datos
      self.modelo.clear()   
      self.modeloComboS.clear()   
      self.actividad=[]
      self.modeloR.clear()
      self.recurso=[]
      self.modeloAR.clear()
      self.asignacion=[]
      self.tabla=[]
      cont=1
      self.modelo.append([cont, '', '', '', '', '', '', '', '', gettext.gettext('Beta')])  # Se inserta una fila vacia
        
             

#******************************************************************************************************************** 
#-----------------------------------------------------------
# Función: Edicción de filas y adicción de una fila vacía  
#          cuando escribimos sobre la última insertada
#
# Parámetros: renderer (celda)
#             path (fila)
#             new_text (nuevo texto introducido)
#             modelo (interfaz)
#             n (columna)
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def col_edited_cb( self, renderer, path, new_text, modelo, n):
      self.control=1   # Controlamos que el proyecto ha cambiado
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
                     modelo[path][1] = new_text
                     it=self.modeloComboS.get_iter(path)
                     self.modeloComboS.set_value(it, 0, new_text)

                  #else:
                     #print 'actividad repetida'
                     #self.dialogoError('Actividad repetida')
                         
               else:  # Se inserta normalmente
                  modelo[path][1] = new_text
                  self.modeloComboS.append([modelo[path][1]])

         elif n==2:  # Columna de las siguientes
            modelo=self.comprobarSig(modelo, path, new_text)

         else:
            modelo[path][n] = new_text


      else:  # Otras interfaces 
         modelo[path][n] = new_text
                 
      iterador=modelo.get_iter(path)
      proximo=modelo.iter_next(iterador)
      if proximo==None:  #si estamos en la última fila, insertamos otra vací­a
         cont+=1
         # Actividades
         if modelo==self.modelo:                
            if len(modelo)!=len(self.actividad): #siempre debe existir un elemento más en modelo que en actividades     
               modelo.append([cont, '', '', '', '', '', '', '', '', gettext.gettext('Beta')])     
               fila=['', '', [], '', '', '', '', '', '', gettext.gettext('Beta')]
               self.actividad.append(fila) 
            else:
               modelo.append([cont, '', '', '', '', '', '', '', '', gettext.gettext('Beta')])
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


#*****************************************************************
#-----------------------------------------------------------
# Función: Actualización de las tres listas con los nuevos datos introducidos 
#          (lista de actividades, de recursos y de asignacion)
#
# Parámetros: modelo (interfaz)
#             path (fila)
#             n (columna)
# 
# Valor de retorno: -
#-----------------------------------------------------------
     
   def actualizacion(self, modelo, path, n):
         # Actividades
        if modelo==self.modelo:  
            if self.modelo[path][n]=='':
                if n==2:
                     self.actividad[int(path)][2]=[]
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

                            
                # Si se introduce la media, se elimina el resto de duraciones        
                elif n==6:   
                    self.actividad[int(path)][n]=float(self.modelo[path][n])
                    for i in range(3, 6):
                       self.modelo[path][i]=''
                       self.actividad[int(path)][i]=''


                # Si se modifica el tipo de distribución, se actualizan la media y la desviación tí­pica
                elif n==9:  
                    self.actividad[int(path)][9]=self.modelo[path][9]
                    if self.modelo[path][3]!='' or self.modelo[path][4]!='' or self.modelo[path][5]!='':
                       a=float(self.modelo[path][3]) #d.optimista
                       b=float(self.modelo[path][5]) #d.pesimista
                       m=float(self.modelo[path][4]) #d.más probable
                       self.actualizarMediaDTipica(path, self.modelo, self.actividad, a, b, m)
                   

                # Se controla el valor introducido en las siguientes 
                elif n==2:  
                     if self.modelo[path][2]==self.actividad[int(path)][1]:
                         self.modelo[path][2]==''
                         self.actividad[int(path)][2]=[]
                     else: 
                         self.actividad[int(path)][2] = self.texto2Lista(self.modelo[path][2])


                # Si no es ningún caso de los anteriores, se actualiza normalmente
                else:  
                     self.actividad[int(path)][n]=self.modelo[path][n]
 
            #print self.actividad, 'ya modificada'


        # Recursos 
        elif modelo==self.modeloR:   
            # Si el recurso es Renovable    
            if self.modeloR[path][1]==gettext.gettext('Renewable'):
                self.recurso[int(path)][n]=self.modeloR[path][n]
                if self.modeloR[path][n]==self.modeloR[path][2]:
                    self.recurso[int(path)][2]=self.modeloR[path][2]=''
                    self.dialogoRec(gettext.gettext('Renewable'))
                else:
                    self.recurso[int(path)][2]=self.modeloR[path][2]=''

            # Si el recurso es No Renovable    
            elif self.modeloR[path][1]==gettext.gettext('Non renewable'):
                self.recurso[int(path)][n]=self.modeloR[path][n]
                if self.modeloR[path][n]==self.modeloR[path][3]:
                    self.recurso[int(path)][3]=self.modeloR[path][3]=''
                    self.dialogoRec(gettext.gettext('Non renewable'))
                else:
                    self.recurso[int(path)][3]=self.modeloR[path][3]=''

            # Si el recurso es Doblemente restringido o Ilimitado
            else:
                self.recurso[int(path)][n]=self.modeloR[path][n]

            #print self.recurso 

 
        # Recursos necesarios por actividad
        else:
            self.asignacion[int(path)][n]=self.modeloAR[path][n]

            #print self.asignacion


#**************************************************************************************************************
#-----------------------------------------------------------
# Función: Actualización de la media y la desviación típica 
#
# Parámetros: path (fila)
#             modelo (interfaz)
#             actividad (lista de actividades)
#               a (duración optimista)
#         b (duración pesimista)
#         m (duración más probable)
#
# Valor de retorno: -
#-----------------------------------------------------------    

   def actualizarMediaDTipica(self, path, modelo, actividad, a, b, m):
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

 
#**************************************************************************************************************
#-----------------------------------------------------------
# Función: Actualización de los datos con los obtenidos de la   
#          apertura de un fichero con extensión '.prj'
#
# Parámetros: tabla (lista que engloba a las tres listas: 
#             actividad, recurso y asignacion)
#
# Valor de retorno: -
#-----------------------------------------------------------       
     
   def cargaDatos(self, tabla):     
        cont=1
        self._widgets.get_widget('vistaListaDatos').show()
        self.modelo.clear()
        self.modeloComboS.clear()
        # Se actualiza la interfaz de las actividades
        for dato in tabla[0]:      
            dato[0]=cont
            cont+=1
            self.modelo.append(dato)
            self.actualizarColSig(tabla[0])
            self.modeloComboS.append([dato[1]])

        # Se actualiza la lista de las actividades
        self.actividad=tabla[0]    
        for i in range(len(self.actividad)):
            if self.actividad[i][2]==['']:
                self.actividad[i][2]=[]   

        
        # Se actualizan la interfaz y la lista de los recursos
        self.modeloR.clear()
        self.recurso=tabla[1]   
        for dato in tabla[1]:   
            self.modeloR.append(dato)

         
        # Se actualizan la interfaz y la lista de los recursos necesarios por actividad
        self.modeloAR.clear()
        self.asignacion=tabla[2]   
        for dato in tabla[2]:      
             self.modeloAR.append(dato)


        #Se actualiza la columna de los recursos en la interfaz y en la lista de actividades 
        if self.asignacion!=[]:
            mostrarColumnaRes=self.mostrarRec(self.asignacion, 1)
            self.actualizarColR(mostrarColumnaRes)

        #print "%s" % (tabla)


#**************************************************************************************************************
#-----------------------------------------------------------
# Función: Lectura de un fichero con extensión '.txt'
#
# Parámetros: f (fichero)
#
# Valor de retorno: tabla (datos leidos)
#-----------------------------------------------------------

   def leerTxt(self, f):
         tabla=[]
         l=f.readline()
         while l:
             linea=l.split('\t')
             linea[1]=linea[1].split(',')
             tabla.append(linea)
             l=f.readline()

         l=f.readline()
         
         return tabla
   


#*******************************************************************
#-----------------------------------------------------------
# Función: Actualización de los datos con los obtenidos de la   
#          apertura de un fichero con extensión '.txt'
#
# Parámetros: tabla (lista con los datos del fichero)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def cargarTxt(self, tabla):
      cont=1
      self._widgets.get_widget('vistaListaDatos').show()
      for linea in tabla:
         sig=self.lista2Cadena2(linea[1])
         if linea[1]==['']:
            fila=[cont, linea[0], [], linea[2], linea[3], linea[4], '', '', '', gettext.gettext('Beta')]
         else:
            fila=[cont, linea[0], linea[1], linea[2], linea[3], linea[4], '', '', '', gettext.gettext('Beta')]
         fila1=[cont, linea[0], sig, linea[2], linea[3], linea[4], '', '', '', gettext.gettext('Beta')]
         self.actividad.append(fila)
         self.modelo.append(fila1)
         cont+=1
   

#********************************************************************************************************************
#-----------------------------------------------------------
# Función: Control de la introducción de las siguientes  
#
# Parámetros: modelo (interfaz)
#             path (fila)
#             new_tex (nuevo texto introducido)
#
# Valor de retorno: modelo (interfaz)
#-----------------------------------------------------------

   def comprobarSig(self, modelo, path, new_text):
        # Se introducen en una lista las etiquetas de las actividades
        actividades=self.actividades2Lista()

   # Se pasa a una lista las actividades que tengo como siguientes antes de la modificación
        anterior=self.texto2Lista(modelo[path][2]) 
        #print anterior, 'anterior' 

        # Se pasa el nuevo texto a una lista
        modificacion=self.texto2Lista(new_text)
        #print modificacion, 'modificacion'
       
        if modificacion==[]:  # Si no se introduce texto (estamos borrando todas las siguientes)
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

#*************************************************************************************************************************
#-----------------------------------------------------------
# Función: Al modificar la etiqueta de alguna actividad, se modifica  
#          también cuando ésta sea siguiente de alguna otra actividad
#
# Parámetros: modelo (interfaz) 
#             original (etiqueta original)
#             nuevo (etiqueta nueva)
#
# Valor de retorno: modelo (interfaz modificada)
#-----------------------------------------------------------

   def modificarSig(self, modelo, original, nuevo):
         for a in range(len(self.actividad)):
             if original in self.actividad[a][2]: # Si original está como siguiente de alguna actividad
                 #print '1'
                 if len(self.actividad[a][2])==1: # Si original es la única siguiente, se modifica por nuevo
                    #print '2'
                    modelo[a][2]=nuevo
                    self.actividad[a][2]=self.texto2Lista(nuevo)
 
                 else: # Si original no es la única siguiente
                    for m in range(len(self.actividad[a][2])):
                       if original==self.actividad[a][2][m]: # La siguiente que coincida con original, se modifica por nuevo
                          #print '3'
                          self.actividad[a][2][m]=nuevo
                          modelo[a][2]=self.lista2Cadena2(self.actividad[a][2])

         return modelo
    


#*************************************************************************************************************************
#-----------------------------------------------------------
# Función: Actualización de la columna de las siguientes en   
#          la interfaz para los proyectos con extensión '.prj'
#
# Parámetros: datos (lista que almacena los datos de 
#                    las actividades)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def actualizarColSig(self, datos):
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


#*******************************************************************************************************************   
#-----------------------------------------------------------
# Función: Actualización de la columna de recursos en la lista de    
#          actividades y en la interfaz
#
# Parámetros: columnaRec (lista que almacena una lista por
#                   cada actividad con la relacion 
#                   actividad-recurso-unidad necesaria)
#
# Valor de retorno: -
#-----------------------------------------------------------      
     
   def actualizarColR(self, columnaRec):
        # Se actualiza la lista de actividades
        for n in range(len(self.actividad)):
            self.actividad[n][8]=columnaRec[n]

        # Se actualiza la interfaz
        for m in range(len(columnaRec)):
            cadena=self.lista2Cadena(columnaRec, m)
            self.modelo[m][8]=cadena
        self.sumarUnidadesRec(self.asignacion)



#********************************************************************************************************************** 
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #           PSPLIB                        #
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
 
#-----------------------------------------------------------
# Función: Lectura de un proyecto de la librería de proyectos PSPLIB   
#
# Parámetros: f (fichero) 
#
# Valor de retorno: prelaciones (lista que almacena las actividades 
#                                y sus siguientes)
#                   rec (lista que almacena el nombre y las unidades
#                       de recurso)
#                   asig (lista que almacena las duraciones y las 
#                         unid. de recurso necesarias por cada actividad)
#----------------------------------------------------------- 
     
   def leerPSPLIB(self, f):
         prelaciones=[]
         asig=[]
         rec=[]
         l=f.readline()         
         while l:
            # Lectura de las actividades y sus siguientes
            if l[0]=='j' and l[10]=='#':
                l=f.readline()
                while l[0]!='*':                   
                   prel=l.split()[0], l.split()[3:]
                   prelaciones.append(prel)
                   l=f.readline()
            
            # Lectura de la duración de las actividades y de las unidades de recursos necesarias por actividad
            if l[0]=='-':
                l=f.readline()
                while l[0]!='*': 
                   asig.append(l.split())
                   l=f.readline()
         
            # Lectura del nombre, tipo y unidad de los recursos
            if l[0:22]=='RESOURCEAVAILABILITIES':
                l=f.readline()
                while l[0]!='*': 
                   rec.append(l.split())
                   l=f.readline()
            
            l=f.readline()  
         
         return (prelaciones, rec, asig)



#***************************************************************************
#-----------------------------------------------------------
# Función: Actualización de los datos con los obtenidos de la   
#          lectura de un fichero con extensión '.sm' de la librería 
#          de proyectos PSPLIB
#
# Parámetros: prelaciones (lista que almacena las actividades 
#                                y sus siguientes)
#             rec (lista que almacena el nombre y las unidades
#                       de recurso)
#             asig (lista que almacena las duraciones y las 
#                         unid. de recurso necesarias por cada actividad)
#
# Valor de retorno: -
#----------------------------------------------------------- 
     
   def cargarPSPLIB(self, prelaciones, rec, asig):
         # Se actualizan las actividades
         self.modelo.clear()
         self.actividad=[]
         cont=1
         longitud=len(prelaciones)
         self._widgets.get_widget('vistaListaDatos').show()
         #Se actualizan actividades y prelaciones, ignorando la primera y la última
         for prelacion in prelaciones:   
             if prelacion!=prelaciones[0] and prelacion!=prelaciones[longitud-1]:  
                 if prelacion[1]==[str(longitud)]:  #controlamos las actividades cuya siguiente es la última  
                     fila=[cont, prelacion[0], [], '', '', '', '', '', '', gettext.gettext('Beta')]  #fila para lista actividad
                     fila1=[cont, prelacion[0], '', '', '', '', '', '', '', gettext.gettext('Beta')] #fila para interfaz
                 else:
                     fila=[cont, prelacion[0], prelacion[1], '', '', '', '', '', '', gettext.gettext('Beta')]   #fila para lista actividad
                     fila1=[cont, prelacion[0], prelacion[1], '', '', '', '', '', '', gettext.gettext('Beta')]  #fila para interfaz
                 
                 self.actividad.append(fila)
                 self.modelo.append(fila1)
                 # Se actualiza la columna de siguientes en la interfaz
                 self.actualizarColSigPSPLIB(prelaciones)
                 
                 cont+=1  
         
         # Se actualiza la duración de las actividades
         for n in range(len(asig)-1):   
             if asig[n][2]!='0' and asig[n][2]!='0':
                 m=n-1
                 self.actividad[m][6]=float(asig[n][2])
                 self.modelo[m][6]=asig[n][2]
         


         # Se actualizan los recursos
         i=1
         m=0
         self.modeloR.clear()
         self.recurso=[]
         for n in range(len(rec[1])):
             # Si el recurso es Renovable
             if rec[0][m]=='R' or rec[0][m][0]=='R':
                 if rec[0][m]=='R':
                     filaR=[rec[0][m]+rec[0][i], gettext.gettext('Renewable'), '', rec[1][n]] 
                     m+=2
                 else:
                     filaR=[rec[0][m], gettext.gettext('Renewable'), '', rec[1][n]] 
                     m+=1
                 self.recurso.append(filaR)
                 self.modeloR.append(filaR)
                 i+=2
                 

             # Si el recurso es No Renovable
             elif rec[0][m]=='N' or rec[0][m][0]=='N':
                 if rec[0][m]=='N':
                     filaR=[rec[0][m]+rec[0][i], gettext.gettext('Non renewable'), rec[1][n], '']
                     m+=2
                 else:
                     filaR=[rec[0][m], gettext.gettext('Non renewable'), rec[1][n], ''] 
                     m+=1
               
                 self.recurso.append(filaR)
                 self.modeloR.append(filaR)
                 i+=2

             # Si el recurso es Doblemente restringido
             elif rec[0][m]=='D' or rec[0][m][0]=='D':
                 if rec[0][m]=='D':
                     filaR=[rec[0][m]+rec[0][i], gettext.gettext('Double restricted'), rec[1][n], rec[1][n]]
                     m+=2
                 else:
                     filaR=[rec[0][m], gettext.gettext('Double restricted'), rec[1][n], rec[1][n]] 
                     m+=1
                 
                 self.recurso.append(filaR)
                 self.modeloR.append(filaR)
                 i+=2
 
              # NOTA: no tenemos en cuenta si el recurso es Ilimitado porque éste tipo de recurso no existe en 
              #       en la librería de proyectos PSPLIB
           
    

         # Se actualizan los recursos necesarios por actividad
         self.modeloAR.clear()
         self.asignacion=[]
         for n in range(len(asig)):                     
             for m in range(3, 3+len(rec[1])):  #len(self.rec[1]): número de recursos 
                 if asig[n][m] != '0':          #los recursos no usados no se muestran
                     i=m-3
                     filaAR=[asig[n][0], self.recurso[i][0], asig[n][m]] 
                     self.asignacion.append(filaAR)
                     self.modeloAR.append(filaAR)



         #Se actualiza la columna de los recursos en la interfaz y en la lista de actividades 
         if self.asignacion!=[]:
             mostrarColumnaRec=self.mostrarRec(self.asignacion, 0)
             self.actualizarColR(mostrarColumnaRec)


#*****************************************************************************
#-----------------------------------------------------------
# Función: Actualización de la columna de las siguientes en   
#          la interfaz para los proyectos de la librería PSPLIB
#
# Parámetros: prelacion (lista que almacena las actividades 
#                                y sus siguientes)
#
# Valor de retorno: -
#----------------------------------------------------------- 
     
   def actualizarColSigPSPLIB(self, prelacion):
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


#####################################################################################################################
                                        # FUNCIONES DE COMPROBACIÓN #
#####################################################################################################################

#-----------------------------------------------------------
# Función: Comprobación de que los tiempos optimista, pesimista y
#          más probable son correctos
#
# Parámetros: a (d.optimista)
#             b (d.pesimista)
#             m (d.mas probable)
#
# Valor de retorno: 0 (valores incorrectos)
#                   1 (valores correctos)
#----------------------------------------------------------- 
     
   def comprobarDuraciones(self, a, b, m):
         if ( (a<b and m<=b and m>=a) or (a==b and b==m)):
             return 1 
         else:
             return 0

#*************************************************************************************************************************
#-----------------------------------------------------------
# Función: Comprueba si se han introducido actividades repetidas 
#
# Parámetros: actividad (lista de actividades)
#
# Valor de retorno: error (0 si no hay error
#                          1 si hay error) 
#                   repetidas (lista de actividades repetidas)
#-----------------------------------------------------------

   def actividadesRepetidas(self, actividad):
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

#************************************************************************************************************************
#-----------------------------------------------------------
# Función: Comprobación de que las actividades 
#           introducidas en la ventana 'recursos necesarios por 
#           actividad' existen
#
# Parámetros: actividad (lista de actividades)
#
# Valor de retorno: error (0 si no hay error
#                          1 si hay error) 
#----------------------------------------------------------- 

   def comprobarActExisten(self, actividad):
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


#************************************************************************************************************************
#-----------------------------------------------------------
# Función: Comprobación de que los recursos
#          introducidos en la ventana 'recursos necesarios por 
#          actividad' existen
#
# Parámetros: recurso (lista de recursos)
#
# Valor de retorno: error (0 si no hay error
#                          1 si hay error) 
#-----------------------------------------------------------  

   def comprobarRecExisten(self, recurso):
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

         
#####################################################################################################################
                                              # OTRAS FUNCIONES #
#####################################################################################################################
 
#-----------------------------------------------------------
# Función: Suma de las unidades de recurso disponibles
#          por proyecto usadas por las actividades
#
# Parámetros: asignacion (lista que almacena actividad,
#                         recurso y unidades necesarias por actividad)
#
# Valor de retorno: unidadesRec (lista que contiene el recurso y la suma de 
#                               las unidades de dicho recurso disponibles 
#                               por proyecto usadas por las actividades)
#-----------------------------------------------------------  
 
   def sumarUnidadesRec(self, asignacion):
         unidadesRec=[]
         for n in range(len(self.recurso)): 
             if self.recurso[n][1]==gettext.gettext('Non renewable') or self.recurso[n][1]==gettext.gettext('Double restricted'):
                cont=0
                recurso=self.recurso[n][0]
                for m in range(len(asignacion)):
                   if asignacion[m][1]==recurso:
                       cont+=int(asignacion[m][2])
                       conjunto=[recurso, cont]
                unidadesRec.append(conjunto)
         #print unidadesRec
         return unidadesRec


#*************************************************************************************************************************     
#-----------------------------------------------------------
# Función: Almacenamiento en una lista de listas (filas) las relaciones entre    
#          actividades, recursos y unidades de recurso 
#          necesarias por actividad
#
# Parámetros: asignacion (lista que almacena actividad,
#                         recurso y unid. necesarias por act.)
#             num (0: fichero con extensión '.sm'
#                  1: fichero con extensión '.prj')
#
# Valor de retorno: mostrarR (lista que almacena una lista por
#                  cada actividad con la relacion 
#                  actividad-recurso-unidad necesaria)
#-----------------------------------------------------------    
     
   def mostrarRec(self, asignacion, num): 
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

#*******************************************************************************************************************   
#-----------------------------------------------------------
# Función: Extracción en una lista las relaciones entre    
#          actividades, recursos y unidades de recurso 
#          necesarias por actividad
#
# Parámetros: m (fila)
#             asignacion (lista que almacena actividad,
#                         recurso y unidades necesarias por actividad)
#             num (0: fichero con extensión '.sm'
#                  1: fichero con extensión '.prj')
#
# Valor de retorno: mostrar (lista que almacena una lista por
#                   cada actividad con la relacion 
#                   actividad-recurso-unidad necesaria)
#-----------------------------------------------------------    
     
   def colR(self, m, asignacion, num):
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


#*************************************************************************************************************************
#-----------------------------------------------------------
# Función: Se inserta una o varias actividades siguientes  
#
# Parámetros: modelo (interfaz)
#             path (fila)
#             texto (nuevo texto a introducir)
#
# Valor de retorno: -
#------------------------------------------------------------

   def insertamosSiguiente(self, modelo, path, texto):
         if self.actividad[int(path)][2]!=[]:  # Si hay alguna siguiente colocada
                modelo[path][2] = modelo[path][2] + ', ' + texto
                self.actividad[int(path)][2]=modelo[path][2] 
         else:
                modelo[path][2] = texto
                self.actividad[int(path)][2]=modelo[path][2]


#*******************************************************************************************************************   
#-----------------------------------------------------------
# Función: Pasa una lista de listas a formato cadena
#
# Parámetros: listaCadenas (lista de listas)
#             m (posición)
#
# Valor de retorno: cadena (cadena resultado)
#----------------------------------------------------------- 

   def lista2Cadena(self, listaCadenas, m):
            cadena=''
            for n in listaCadenas[m]:
                if cadena!='':
                    cadena+=', '
                    cadena+=n
                else:
                    cadena+=n 
            return cadena
 
#********************************************************************************************************************   
#-----------------------------------------------------------
# Función: Pasa una lista a formato cadena
#
# Parámetros: lista (lista)
#
# Valor de retorno: cadena (cadena resultado)
#----------------------------------------------------------- 

   def lista2Cadena2(self, lista):
          cadena=''
          for n in lista:
                if cadena!='':
                   cadena+=', '
                   cadena+=n
                else:
                   cadena+=n 
     
          return cadena
           
#********************************************************************************************************************
#-----------------------------------------------------------
# Función: Pasa un texto a formato lista 
#
# Parámetros: texto (texto)
#
# Valor de retorno: lista (lista resultado)
#----------------------------------------------------------- 
   
   def texto2Lista(self, texto):
         lista = []
         if texto!='':
            for a in texto.split(','):
               if a!='':
                 lista.append(a.strip())
         return lista


#**********************************************************************************************************************
#-----------------------------------------------------------
# Función: Introduce en una lista todas las etiquetas de las actividades  
#
# Parámetros: -
#
# Valor de retorno: listaAct (lista de actividades)
#-----------------------------------------------------------

   def actividades2Lista(self):
        listaAct=[]
        for n in self.actividad:
             listaAct.append(n[1])
        #print listaAct, 'actividades'
        return listaAct


#***********************************************************************************************************************
#-----------------------------------------------------------
# Función: Cálculo de la media y la desviación típica a partir de la distribución, 
#          del tiempo optimista, pesimista y más probable 
#
# Parámetros: distribucion (tipo de distribución)
#             a (d.optimista)
#             b (d.pesimista)
#             m (d.más probable)
#
# Valor de retorno: media (media calculada)
#                   dTipica (desviación típica calculada)
#----------------------------------------------------------- 
     
   def calcularMediaYDTipica(self, distribucion, a, b, m):
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

#***********************************************************************************************************************       
#-----------------------------------------------------------
# Función: Muestra datos en el Text View correspondiente 
#
# Parámetros: widget (lugar donde mostrar el dato)
#             valor (dato a mostrar)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def mostrarTextView(self, widget, valor):
        bufer=gtk.TextBuffer()
        widget.set_buffer(bufer)
        iterator=bufer.get_iter_at_line(0)
        bufer.set_text(valor) 
                    

#*******************************************************************************************************************
#-----------------------------------------------------------
# Función: Asignación de tí­tulo al proyecto actual
#
# Parámetros: directorio (tí­tulo+directorio)
#
# Valor de retorno: - 
#----------------------------------------------------------- 
      
   def asignarTitulo(self, directorio):
         titulo=basename(directorio)
         ubicacion=directorio[:-(len(titulo)+1)]
         if ubicacion=='': 
              self.vPrincipal.set_title(titulo+' - PPC-Project')
         else:
              self.vPrincipal.set_title(titulo+' ('+ubicacion+')'+ ' - PPC-Project')

               
#####################################################################################################################
                                      # FUNCIONES VENTANAS DE ACCIÓN #
##################################################################################################################### 

      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #          GRAFO PERT                     #
      #++++++++++++++++++++++++++++++++++++++++++++++++++#

#-----------------------------------------------------------
# Función: Creación del grafo Pert y renumeración del mismo 
#
# Parámetros: - 
#
# Valor de retorno: grafoRenumerado (grafo final)
#-----------------------------------------------------------  

   def pertFinal(self):
        # Se genera el grafo Pert
        successors = self.tablaSucesoras(self.actividad)
        grafo = pert.Pert()
        grafo.pert(successors)
        
        # Se extraen los nodos en una lista
        nodos=self.listaNodos(grafo.activities)
        #print nodos, 'nodos'

        # Se calculan los niveles de cada nodo
        niveles=self.demoucron(grafo.activities, nodos)

        # Se renumera el grafo
        grafoRenumerado=self.renumerar(grafo, niveles)
        #print grafoRenumerado, 'grafo renumerado'
        
        return grafoRenumerado

#**********************************************************************************
#-----------------------------------------------------------
# Función: Obtiene un diccionario que contiene las actividades 
#          y sus sucesoras  
#
# Parámetros: actividades (lista de actividades)
#
# Valor de retorno: successors(diccionario con las actividades y sus sucesoras)
#-----------------------------------------------------------             
    
   def tablaSucesoras(self, actividades):
         successors={}
         for n in range(len(actividades)):
             successors[actividades[n][1]]=actividades[n][2]
         return successors
 
#***********************************************************************************
#-----------------------------------------------------------
# Función: Creación de una lista que contenga los nodos del grafo
#
# Parámetros: actividadesGrafo (etiquetas actividades, nodo inicio y fí­n)
#
# Valor de retorno: nodos (lista de nodos)
#-----------------------------------------------------------  

   def listaNodos(self, actividadesGrafo):
        # Se crea una lista con los nodos del grafo
        nodos=[]
        for g in actividadesGrafo:
            #print g[0], g[1]
            if g[0] not in nodos:
                nodos.append(g[0])
            if g[1] not in nodos:
                nodos.append(g[1])

        # Se ordena la lista que contiene los nodos del grafo
        for i in range(1, len(nodos)):
            for j in range(0, len(nodos)-i):
               if nodos[j] > nodos[j+1]:
                   elemento = nodos[j]
                   nodos[j] = nodos[j+1]
                   nodos[j+1] = elemento

        return nodos


#***********************************************************************************
#-----------------------------------------------------------
# Función: Creación de un diccionario que representa las prelaciones 
#          entre los nodos del grafo Pert  
#
# Parámetros: actividadesGrafo (etiquetas actividades, nodo inicio y fí­n)
#             nodos (lista con los nodos del grafo)
#
# Valor de retorno: dPrelaciones (diccionario con las prelaciones)
#-----------------------------------------------------------

   def tablaPrelaciones(self, actividadesGrafo, nodos):
        dPrelaciones={}
        for n in nodos:
           #print n, 'n'
           for m in nodos:
               #print m, 'm'
               if (n,m) in actividadesGrafo:
                   #print '1'
                   dPrelaciones[n,m]=1
               else:
                   #print '0'
                   dPrelaciones[n,m]=0
          
        #print dPrelaciones, 'prelaciones'
        return dPrelaciones
        
#***********************************************************************************
#-----------------------------------------------------------
# Función: Calcula el algoritmo de Demoucron, es decir, divide  
#          el grafo Pert en niveles
#
# Parámetros: actividadesGrafo (etiquetas actividades, nodo inicio y fí­n)
#             nodos (lista con los nodos del grafo)
#
# Valor de retorno: reordenado (diccionario con los niveles del grafo)
#-----------------------------------------------------------

   def demoucron(self, actividadesGrafo, nodos):
         # Se obtiene un diccionario con las prelaciones
         tPrelaciones=self.tablaPrelaciones(actividadesGrafo, nodos)
 
         # Se obtiene un diccionario con la suma de '1' de cada nodo
         v={}       
         for n in nodos:
           cont=0
           for m in nodos:
               if tPrelaciones[n,m]==1:
                  v[n]=cont+1
                  cont+=1
           if n not in v:
                v[n]=0
         #print v, 'v'

         # Se van realizando los respectivos cálculos del algoritmo 
         num=1
         nivel={}
         valor=c=0
         for d in nodos:
            if nivel!={} and valor==c:
               n=nivel[valor]
               #print n, 'n'
               for m in v:
                  if v[m]!='x':
                     for a in n:
                       #print a, 'a'
                       #print v[m], tPrelaciones[m,n], 'antes'
                       v[m]=v[m]-tPrelaciones[m,a]
                       #print v[m], 'despues'
            valor+=1

            # Se establecen los niveles a cada nodo
            for i in v:
               if v[i]==0:
                  c=num
                  v[i]='x'
                  if num not in nivel:
                      nivel[num]=[i]
                  else:
                      nivel[num].append(i)
            num+=1
            #print nivel

         #print nivel, 'nivel'

         # Se reordena el diccionario de los niveles 
         reordenado={}
         n=len(nivel)
         for m in range(1, len(nivel)+1):
             reordenado[n]=nivel[m]
             n-=1
             
         #print reordenado, 'reordenado'
         return reordenado
         

#*************************************************************************************
#-----------------------------------------------------------
# Función: Se renumera el grafo Pert 
#
# Parámetros: grafo (grafo Pert)
#             niveles (niveles de cada nodo del grafo)
#
# Valor de retorno: nuevoGrafo (grafo renumerardo)
#-----------------------------------------------------------
           
   def renumerar(self, grafo, niveles):
         # Se crea un diccionario con la equivalencia entre los nodos originales y los nuevos
         s=1
         nuevosNodos={}
         for m in niveles:
            if len(niveles[m])==1:
                nuevosNodos[niveles[m][0]]=s
                s+=1
            else:
               for a in niveles[m]:
                  nuevosNodos[a]=s            
                  s+=1

         # Se crea un nuevo grafo
         nuevoGrafo = pert.Pert()
         
         # Se modifica 'grafo.graph'
         for n in grafo.graph:
             #print n, 'n'
             for m in nuevosNodos:            
                #print  m, 'm'
                if n==m:
                   if grafo.graph[n]!=[]:
                       for i in range(len(grafo.graph[n])):
                          for a in nuevosNodos:
                             if grafo.graph[n][i]==a:
                                if i==0:
                                   nuevoGrafo.graph[nuevosNodos[m]]=[nuevosNodos[a]]
                                else:                                   
                                   nuevoGrafo.graph[nuevosNodos[m]].append(nuevosNodos[a])
                   else: 
                       nuevoGrafo.graph[nuevosNodos[m]]=[]
         #print nuevoGrafo.graph, 'graph'


         # Se modifica 'grafo.activities'
         for n in grafo.activities:
             #print n, 'n'
             for m in nuevosNodos:            
                #print  m, 'm'
                if n[0]==m:
                    for a in nuevosNodos:
                       if n[1]==a:
                           #print a, 'a1'
                           nuevoGrafo.activities[nuevosNodos[m],nuevosNodos[a]]=grafo.activities[n]
                           #print nuevoGrafo

                elif n[1]==m:
                    for a in nuevosNodos:
                       if n[0]==a:
                           #print a, 'a2'
                           nuevoGrafo.activities[nuevosNodos[a],nuevosNodos[m]]=grafo.activities[n]
                           #print nuevoGrafo


         #print nuevoGrafo.activities, 'activities'
         #print nuevoGrafo, 'grafo renumerado'
         return nuevoGrafo   
                 

    
#**********************************************************************************************************************
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #          ZADERENKO                      #
      #++++++++++++++++++++++++++++++++++++++++++++++++++#

#-----------------------------------------------------------
# Función: Acción usuario para calcular todos los datos relacionados con Zaderenko 
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def ventanaZaderenko(self):
        informacionCaminos=[]

        # Se crea el grafo Pert y se renumera
        grafoRenumerado=self.pertFinal()

        # Nuevos nodos
        nodosN=[]
        for n in range(len(grafoRenumerado.graph)):
           nodosN.append(n+1)

        # Se calcula la matriz de Zaderenko
        mZad=self.mZad(grafoRenumerado.activities, nodosN, 1, []) 

        # Se calculan los tiempos early y last
        early=self.early(nodosN, mZad)      
        last=self.last(nodosN, early, mZad)  

        # duración del proyecto
        tam=len(early)
        duracionProyecto=early[tam-1]
        #print duracionProyecto, 'duracion proyecto'            

        # Se buscan las actividades que son crí­ticas, que serán aquellas cuya holgura total sea 0
        holguras=self.holguras(grafoRenumerado.activities, early, last, []) 
        #print holguras, 'holguras'
        actCriticas=self.actCriticas(holguras, grafoRenumerado.activities)
        #print 'actividades criticas: ', actCriticas
       
        # Se crea un grafo sólo con las actividades crí­ticas y se extraen los caminos del grafo (todos serán crí­ticos)
        caminosCriticos=self.grafoCriticas(actCriticas) 
        #print caminosCriticos, 'caminos criticos'

        # Se extraen todos los caminos (crí­ticos o no) del grafo original
        successors = self.tablaSucesoras(self.actividad)
        g=graph.roy(successors)
        caminos=self.buscarCaminos(g)            
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
        self.zaderenko(early, last, nodosN, mZad)
        self.mostrarCaminosZad(self.modeloZ, criticos, informacionCaminos)
        self.vZaderenko.show()


#*********************************************************************************
#-----------------------------------------------------------
# Función: Creación de la matriz de Zaderenko 
#
# Parámetros: actividadesGrafo (etiquetas actividades, nodo inicio y fí­n)
#             nodos (lista de nodos)
#             control (0: llamada desde Simulación
#                      1: llamada desde Zaderenko u Holguras)
#             duracionSim (duración de la simulación)
#
# Valor de retorno: mZad (matriz de Zaderenko)
#-----------------------------------------------------------  
    
   def mZad(self, actividadesGrafo, nodos, control, duracionSim): 
        mZad=[]
        fila=[]

        # Se inicializa la matriz
        for n in range(len(nodos)):
            fila.append('')
        for n in range(len(nodos)):       
            mZad.append(list(fila))
        
        actividades=[]
        for n in range(len(self.actividad)):
            actividades.append(self.actividad[n][1])
       
        # Se añaden las duraciones en la posición correspondiente
        for g in actividadesGrafo:
            i=g[0]-1
            j=g[1]-1
            if actividadesGrafo[i+1, j+1][0] in actividades:
                 if control==1: # Si es llamada desde Zaderenko
                    for m in range(len(self.actividad)):
                      #print self.actividad[m][1]
                      if actividadesGrafo[i+1, j+1][0]==self.actividad[m][1]:   
                         mZad[j][i]=self.actividad[m][6]

                 else: # Si es llamada desde Simulación
                     for m in range(len(self.actividad)):
                      #print self.actividad[m][1]
                      if actividadesGrafo[i+1, j+1][0]==self.actividad[m][1]:   
                         mZad[j][i]=duracionSim[m]

            else: # Las actividades ficticias tienen duración 0
                    mZad[j][i]=0
        
        #print mZad
        return mZad


#*****************************************************************************        
#-----------------------------------------------------------
# Función: Cálculo de los tiempos early de cada nodo 
#
# Parámetros: nodos (lista de nodos)
#             mZad (matriz de Zaderenko)
#
# Valor de retorno: early (lista con los tiempos early)
#----------------------------------------------------------- 

   def early(self, nodos, mZad):  
        # Se crea una la lista de tiempos early y se inicializa a 0
        early=[]
        for n in range(len(nodos)):
           a=0
           early.append(a)

        # Se calculan los tiempos early y se van introduciendo a la lista
        for n in range(len(nodos)):
            mayor=0
            #print mayor, '******************************'
            for m in range(len(nodos)):
                if m<n and mZad[n][m]!='':
                    aux=float(mZad[n][m])+early[m]
                    #print aux, mZad[n][m], early[m], '--------------'
                    if aux>mayor:
                        mayor=aux
                    aux=0 
                    #print mayor
            early[n]=mayor
            #print early
        for e in range(len(early)):
            early[e]=float('%5.2f'%(float(early[e])))
        
        return early

 #*****************************************************************************        
#-----------------------------------------------------------
# Función: Cálculo de los tiempos last de cada nodo 
#
# Parámetros: nodos (lista de nodos)
#             early (lista con los tiempos early)
#             mZad (matriz de Zaderenko)
#
# Valor de retorno: last (lista con los tiempos last)
#----------------------------------------------------------- 

   def last(self, nodos, early, mZad): 
        #Se cambian filas por columnas en mZad para usarla en el calculo de los tiempos last
        for n in range(len(nodos)):
            for m in range(len(nodos)):
                 if mZad[n][m]!='':
                     mZad[n][m]=''
                 else:
                     mZad[n][m]=mZad[m][n]

        # Se crea una la lista de tiempos last y se inicializa a 0
        last=[]
        for n in range(len(nodos)):
           a=0
           last.append(a)
     
        # Se calculan los tiempos last y se van introduciendo a la lista
        l=len(nodos)-1
        aux=early[l]
        last[l]=early[l]
        for m in range(len(nodos)):
            menor=early[l]
            #print menor, '*************************************************'
            for n in range(len(nodos)):
                if (l-m)<n and mZad[l-m][n]!='':
                    aux=last[n]-float(mZad[l-m][n])
                    #print aux, last[n], mZad[l-m][n], '------------'
                    #print menor, aux
                    if aux<menor:
                        menor=aux
                    aux=0 
                    #print menor
            last[l-m]=menor
        #print last, 'last'  
        for l in range(len(last)):
            last[l]=float('%5.2f'%(float(last[l])))
 
        return last


#***************************************************************
#-----------------------------------------------------------
# Función: Prepara y muestra en la interfaz la matriz de Zaderenko y  
#          los tiempos early y last 
#
# Parámetros: early (lista con los tiempos early)
#             last (lista con los tiempos last)
#             nodos (lista de nodos)
#             mZad (matriz de Zaderenko)
#
# Valor de retorno: -
#----------------------------------------------------------- 
  
   def zaderenko(self, early, last, nodos, mZad):
        # Se prepara la matriz de Zaderenko y los tiempos early y last para mostrarlos en la interfaz
        linea='______________'
        filas=''
        filas+='Early'
        filas+='\t'
        filas+='\t'
        for n in nodos:
            filas+='\t'
            filas+='       '+str(n)
            filas+='\t'

        filas+='\n'
        filas+=linea*(len(nodos)+1)

        for n in range(len(mZad)):
            filas+='\n'
            e='%5.2f'% (early[n])
            filas+=str(e) 
            filas+='\t'
            filas+='\t'
            filas+=str(nodos[n]) 
            filas+='\t'       
            for m in range(len(mZad)):
                filas+='\t'
                if mZad[n][m]!='':
                   m=str('%3.2f'%(float(mZad[n][m])))
                   filas+=str(m)
                else:
                   filas+=str(mZad[n][m])   
                filas+='\t'+'\t'
            filas+='\n'
        filas+='\n'
        filas+=linea*(len(nodos)+1)
        filas+='\n'

        filas+='\t' 
        filas+='\t'
        filas+='Last'
        filas+='\t'
        for n in range(len(last)):
            filas+='\t'
            l='%5.2f'% (last[n])
            filas+='  '+str(l)
            filas+='\t'

        # Se muestran los datos anteriores en la interfaz
        widget=self._widgets.get_widget('vistaZad')
        self.mostrarTextView(widget ,filas)


#******************************************************************************
#-----------------------------------------------------------
# Función: Muestra los caminos del grafo en la interfaz (ventana Zaderenko)
#
# Parámetros: modelo (lista donde se muestran los caminos)
#             criticos (lista caminos criticos)
#             informacionCaminos (lista caminos del grafo, sus duraciones
#                          y sus desviaciones tí­picas)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def mostrarCaminosZad(self, modelo, criticos, informacionCaminos):
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
            
               
       
#**************************************************************************        
#-----------------------------------------------------------
# Función: Cálculo de las actividades criticas 
#
# Parámetros: holguras (lista con las hoguras de cada actividad)
#             actividadesGrafo (etiqueta actividades, nodo inicio y fí­n)

# Valor de retorno: criticas (lista de actividades criticas)
#----------------------------------------------------------- 
#LAS ACTIVIDADES CRITICAS SON AQUELLAS CUYA HOLG. TOTAL ES 0
      
   def actCriticas(self, holguras, actividadesGrafo):  
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

  
#*************************************************************************
#-----------------------------------------------------------
# Función: Creación de un grafo sólo con actividades crí­ticas y extracción de
#          los caminos de dicho grafo, que serán todos crí­ticos 
#
# Parámetros: actCriticas (lista de actividades crí­ticas)
#
# Valor de retorno: caminosCriticos (lista de caminos crí­ticos)
#-----------------------------------------------------------  

   def grafoCriticas(self, actCriticas):
          # Se crea un grafo con las activididades crí­ticas y se extraen los caminos de dicho grafo, que serán crí­ticos
          sucesorasCriticas=self.tablaSucesorasCriticas(actCriticas)
          #print sucesorasCriticas, 'suc criticas'
          gCritico=graph.roy(sucesorasCriticas)
          #print gCritico
          caminosCriticos=[]
          caminos=graph.findAllPaths(gCritico, 'Begin', 'End')

          # Se eliminan 'begin' y 'end' de todos los caminos
          caminosCriticos=[c[1:-1]for c in caminos]

          return caminosCriticos


#*************************************************************************************************************************
#-----------------------------------------------------------
# Función: Obtiene un diccionario que contiene las actividades 
#          crí­ticas y sus sucesoras  
#
# Parámetros: criticas (lista de actividades crí­ticas)
#
# Valor de retorno: sucesorasCriticas(diccionario que almacena 
#                   las actividades críticas y sus sucesoras)
#-----------------------------------------------------------       

   def tablaSucesorasCriticas(self, criticas):
         cr=[]
         for n in criticas:
             cr.append(n[0])
         #print cr, 'cr'

         sucesorasCriticas={}
         for n in cr:
            for m in range(len(self.actividad)):
              #print n, 'n', self.actividad[m][1]
              if n==self.actividad[m][1]:
                 for a in self.actividad[m][2]:
                    #print a
                    if a in cr:
                       if n not in sucesorasCriticas:
                           sucesorasCriticas[n]=[a]
                       else:
                           sucesorasCriticas[n].append(a)

            if n not in sucesorasCriticas:  
                sucesorasCriticas[n]=[]
   
         return sucesorasCriticas


#************************************************************************************************************************
#-----------------------------------------------------------
# Función: Búsqueda de los caminos criticos en todos los caminos
#          del grafo. Se marca con un 1 los crí­ticos y con un 0
#          los no crí­ticos
#
# Parámetros: caminos (lista todos los caminos)
#             caminosCriticos (lista caminos criticos)
#
# Valor de retorno: criticos (lista con los caminos marcados)
#-----------------------------------------------------------  

   def caminosCriticos(self, caminos, caminosCriticos):
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


#************************************************************************************************************************
#-----------------------------------------------------------
# Función: Cálculo de la duración media y la desviación tí­pica
#          de un camino del grafo
#
# Parámetros: camino (camino del grafo)
#
# Valor de retorno: d (duración media)
#                   t (desviación tí­pica)
#----------------------------------------------------------- 
      
   def mediaYdTipica(self, camino):

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
    

#********************************************************************************************************************         
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #              ACTIVIDADES                     #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para mostrar la etiqueta de cada actividad con su
#          nodo inicio y fin en la interfaz
#
# Parámetros: modelo (interfaz)
#             actividadesGrafo (etiqueta actividades, nodo inicio y fí­n)
#             grafo (grafo Pert)
#
# Valor de retorno: -
#----------------------------------------------------------- 
    
   def mostrarActividades(self, modelo, actividadesGrafo, grafo):
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



#********************************************************************************************************************  
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #               HOLGURAS                       #
      #++++++++++++++++++++++++++++++++++++++++++++++++++#      
  
#-----------------------------------------------------------
# Función: Acción usuario para mostrar los tres tipos de
#          holguras: total, libre e independiente
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------

   def ventanaHolguras(self):
        # Se crea el grafo Pert y se renumera
        grafoRenumerado=self.pertFinal()
    
        # Nuevos nodos
        nodosN=[]
        for n in range(len(grafoRenumerado.graph)):
           nodosN.append(n+1)

        # Se calcula la matriz de Zaderenko
        mZad=self.mZad(grafoRenumerado.activities, nodosN, 1, []) 

        # Se calculan los tiempos early y last
        early=self.early(nodosN, mZad) 
        last=self.last(nodosN, early, mZad)

        # Se calculan los tres tipos de holgura y se muestran en la interfaz
        holguras=self.holguras(grafoRenumerado.activities, early, last, []) 
        self.mostrarHolguras(self.modeloH, holguras) 


#*****************************************************************        
#-----------------------------------------------------------
# Función: Cálculo de los tres tipos de holguras
#
# Parámetros: grafo (grafo Pert)
#             early (lista con los tiempos early)
#             last (lista con los tiempos last)
#         duraciones (duraciones simuladas)
#
# Valor de retorno: holguras (lista que contiene cada actividad y sus tres
#                              tipos de holguras)
#-----------------------------------------------------------
    
   def holguras(self, grafo, early, last, duraciones):  
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
      
#********************************************************************         
#-----------------------------------------------------------
# Función: Muestra las hoguras en la interfaz
#
# Parámetros: modelo (lista de actividades)
#             hoguras (lista con los tres tipos de holguras de cada actividad)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def mostrarHolguras(self, modelo, holguras):
        self.vHolguras.show()  

        modelo.clear()
        for n in range(len(holguras)):  
            modelo.append([holguras[n][0], holguras[n][1], holguras[n][2], holguras[n][3]])


#********************************************************************************************************************         
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #           CAMINOS DEL GRAFO                  #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para calcular y mostrar todos los 
#          caminos de un grafo 
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------

   def calcularCaminos(self):
        # Se comprueba que exista algún grafo
        if self.actividad==[]:
           self.dialogoError(gettext.gettext('A graph is needed to calculate its paths'))

        else:
           successors = self.tablaSucesoras(self.actividad)
           roy = graph.roy(successors)
           #print roy, 'grafo'
           
           # Se extraen todos los caminos en una lista
           caminosSinBeginEnd=self.buscarCaminos(roy)

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
           

#*****************************************************************************
#-----------------------------------------------------------
# Función: Búsqueda de los caminos del grafo (crí­ticos o no)
#
# Parámetros: grafo (grafo Pert)
#
# Valor de retorno: caminosSinBeginEnd (lista con todos los caminos del grafo)
#-----------------------------------------------------------  

   def buscarCaminos(self, grafo):  
        caminos=[]
        caminos=graph.findAllPaths(grafo, 'Begin', 'End')

        # Se eliminan 'begin' y 'end' de todos los caminos
        caminosSinBeginEnd=[c[1:-1]for c in caminos]

        # Impresión en terminal para comprobaciones    
        #for camino in caminosSinBeginEnd:
            #print camino
        
        return caminosSinBeginEnd


#*******************************************************************************************************************
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #     RECUROS NECESARIOS POR ACTIVIDAD         #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana de 
#          'recursos necesarios por actividad'
#
# Parámetros: -
#
# Valor de retorno: - 
#----------------------------------------------------------- 

# Nota: Antes de introducir los recursos que cada actividad necesita, deben existir tanto recursos como actividades.

   def asignarRecursos(self):
        # Se comprueba que se hayan introducido actividades
        if self.actividad == []:
            self.dialogoError(gettext.gettext('No activities introduced'))
 
        # Se comprueba que se hayan introducido recursos
        elif self.recurso == []:
            self.dialogoError(gettext.gettext('No resources introduced'))
           
        # Si todo es correcto, se accede a la ventana con normalidad
        else:
            if self.asignacion==[]:
                self.modeloAR.append()
            self.vAsignarRec.show()



#*******************************************************************************************************************
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #              SIMULACIÓN                      #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Simulación de duraciones de cada actividad según  
#          su tipo de distribución
#
# Parámetros: n (número de iteraciones)
#
# Valor de retorno: simulacion (lista con 'n' simulaciones del proyecto)
#----------------------------------------------------------- 

   def simulacion(self, n):
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
                             valor=self.generaAleatoriosUniforme(float(self.actividad[m][3]), float(self.actividad[m][5]))
                       else: # Si d.optimista=d.pesimista
                          valor=self.actividad[m][3]
                    else:
                       self.dialogoError(gettext.gettext('Optimistic, pessimistic and most probable durations of this activity must be introduced')) 
                       return
 
                # Si la actividad tiene una distribución 'beta'
                elif distribucion==gettext.gettext('Beta'):
                     if self.actividad[m][3]!='' and self.actividad[m][4]!='' and self.actividad[m][5]!='':
                        if self.actividad[m][3]!=self.actividad[m][5]!=self.actividad[m][4]:
                             mean, stdev, shape_a, shape_b=self.datosBeta(float(self.actividad[m][3]), float(self.actividad[m][4]), float(self.actividad[m][5]))
                        #print "Mean=", mean, "Stdev=", stdev
                        #print "shape_a=", shape_a, "shape_b=", shape_b
                             valor=self.generaAleatoriosBeta(float(self.actividad[m][3]), float(self.actividad[m][5]), float(shape_a), float(shape_b))
                        else:  # Si d.optimista=d.pesimista=d.mas probable
                           valor=self.actividad[m][3]
                     else:
                       self.dialogoError(gettext.gettext('Optimistic, pessimistic and most probable durations of this activity must be introduced')) 
                       return

                # Si la actividad tiene una distribución 'triangular'
                elif distribucion==gettext.gettext('Triangular'):
                    if self.actividad[m][3]!='' and self.actividad[m][4]!='' and self.actividad[m][5]!='':
                       if self.actividad[m][3]!=self.actividad[m][5]!=self.actividad[m][4]:
                             valor=self.generaAleatoriosTriangular(float(self.actividad[m][3]), float(self.actividad[m][4]), float(self.actividad[m][5]))
                       else:   # Si d.optimista=d.pesimista=d.mas probable
                          valor=self.actividad[m][3]
                    else:
                       self.dialogoError(gettext.gettext('Optimistic, pessimistic and most probable durations of this activity must be introduced')) 
                       return
                # Si la actividad tiene una distribución 'normal'
                else:
                    if self.actividad[m][6]!='' and self.actividad[m][7]!='':
                       if float(self.actividad[m][7])!=0.00:
                             valor=self.generaAleatoriosNormal(float(self.actividad[m][6]), float(self.actividad[m][7]))
                       else:   # Si d.tipica=0
                          valor=self.actividad[m][6]
                    else:
                       self.dialogoError(gettext.gettext('The average duration and the typical deviation of this activity must be introduced')) 
                       return
                sim.append(float(valor))
                #print sim, 'sim'
            simulacion.append(sim)

        return simulacion
 

#***************************************************************
#-----------------------------------------------------------
# Función: Generación de un número aleatorio para una 
#          distribución uniforme
#
# Parámetros: op (duración optimista)
#             pes (duración pesimista)
#
# Valor de retorno: unif (número aleatorio)
#----------------------------------------------------------- 

   def generaAleatoriosUniforme(self, op, pes):
        #print "\n *** Uniform(",op,pes,")"
        unif=random.uniform(op,pes)
        return unif


#******************************************************************
#-----------------------------------------------------------
# Función: Generación de un número aleatorio para una 
#          distribución beta
#
# Parámetros: op (duración optimista)
#             pes (duración pesimista)
#             shape_a (shape factor)
#             shape_b (shapa factor)
#
# Valor de retorno: beta (número aleatorio)
#----------------------------------------------------------- 

   def generaAleatoriosBeta(self, op, pes, shape_a, shape_b):
        #mean, stdev, shape_a, shape_b=self.datosBeta(op, mode, pes)
   #print "Mean=", mean, "Stdev=", stdev
   #print "shape_a=", shape_a, "shape_b=", shape_b
   #for i in range(n):
      beta=random.betavariate(shape_a,shape_b)*(pes-op) + op
      return beta


#*******************************************************************
#-----------------------------------------------------------
# Función: Obtención de datos necesarios para la generación de 
#          números aleatorios para una distribución beta
#
# Parámetros: op (duración optimista)
#             mode (duración más problable)
#             pes (duración pesimista)
#
# Valor de retorno:  mean (duración media)
#                    stdev (desviación tí­pica)
#                    shape_a (shape factor)
#                    shape_b (shape factor)
#----------------------------------------------------------- 

   def datosBeta(self, op, mode, pes):
        #print "\n *** Beta(",op,mode,pes,")"
      mean  = (op + 4*mode + pes) / 6.0
      stdev = (pes - op) / 6.0
      shape_a = ((mean - op) / (pes-op)) * ((mean-op)*(pes-mean)/stdev**2 - 1)
      shape_b = ((pes-mean)/(mean-op)) * shape_a

      return mean, stdev, shape_a, shape_b


#******************************************************************
#-----------------------------------------------------------
# Función: Generación de un número aleatorio para una 
#          distribución triangular
#
# Parámetros: op (duración optimista)
#             mode (duración más problable)
#             pes (duración pesimista)
#
# Valor de retorno: triang (número aleatorio)
#----------------------------------------------------------- 
   
   def generaAleatoriosTriangular(self, op, mode, pes):
      #print "\n *** Triangle(",op,mode,pes,")"
      """
      Generates a random number in a triangular distribution in [op, pes]
      with mode
      """
      unif = random.random()  #[0,1]
        
      if unif <= (mode-op) / (pes-op):
         aux = unif * (pes-op) * (mode-op)
         triang = op + math.sqrt(aux)
      else:
         aux = (pes-op) * (pes-mode) * (1-unif)
         triang = pes - math.sqrt(aux)

      #triang=self.trianglevariate(op,mode,pes) Función no usada
      return triang


#*******************************************************************
#-----------------------------------------------------------
# Función: Generación de un número aleatorio para una 
#          distribución normal
#
# Parámetros: mean (duración media)
#             stdev (desviación tí­pica)
#
# Valor de retorno: norm (número aleatorio)
#----------------------------------------------------------- 

   def generaAleatoriosNormal(self, mean, stdev):
         #print "\n *** Normal(",mean,stdev,")"
      norm=random.gauss(mean,stdev)
      return norm


#*******************************************************************
#-----------------------------------------------------------
# Función: Cálculo de las F.Absolutas y F.Relativas 
#
# Parámetros: dMax (duración máxima)
#             dMin (duración mímima)
#             itTotales (iteraciones totales)
#             N (número de intervalos)
#
# Valor de retorno: Fa (frecuencias absolutas)
#                   Fr (frecuencias relativas)
#----------------------------------------------------------- 

   def calcularFrecuencias(self, dMax, dMin, itTotales, N):
        Fa=[]
        Fr=[]
        # Se inicializa el vector de F.Absolutas
        for n in range(N):
           Fa.append(0)

        # Se calculan las F.Absolutas
        for d in self.duraciones:
            x=self.posicion(d, dMax, dMin, N)
            Fa[x]+=1
        #print Fa, 'Fa'

        # Se calculan las F.Relativas
        for a in Fa:
           r='%2.2f'%(float(a)/itTotales)
           Fr.append(r)
        #print Fr, 'Fr'

        return Fa, Fr

#*******************************************************************
#-----------------------------------------------------------
# Función: Cálculo de la posición de una duración dentro del 
#          vector de F.Absolutas
#
# Parámetros: d (duración)
#             dMax (duración máxima)
#             dMin (duración mí­nima)
#             N (número de intervalos)
#
# Valor de retorno: x (posición)
#----------------------------------------------------------- 

   def posicion(self, d, dMax, dMin, N):
        x = int ( ((d-dMin)/(dMax-dMin)) * N )
        return x


#*******************************************************************
#-----------------------------------------------------------
# Función: Cálculo de la duración correspondiente a una posición 
#          (inversa de la Función anterior)
#
# Parámetros: x (posición)
#             dMax (duración máxima)
#             dMin (duración mí­nima)
#             N (número de intervalos)
#
# Valor de retorno: d (duración)
#----------------------------------------------------------- 

   def duracion(self, x, dMax, dMin, N):
        d = ( x*(dMax-dMin)/N ) + dMin
        return d


#*******************************************************************
#-----------------------------------------------------------
# Función: Prepara la tabla de frecuencias para ser mostrada en  
#          la interfaz
#
# Parámetros: intervalos (intervalos)
#             Fa (lista de frecuencias absolutas)
#             Fr (lista de frecuencias relativas)
#
# Valor de retorno: - 
#-----------------------------------------------------------

   def mostrarFrecuencias(self, intervalos, Fa, Fr):
        lineas=''
        l='___________________'
        lineas+=gettext.gettext('Durations')
        lineas+='\t'
        for n in intervalos:
          lineas+=n
          lineas+='\t'+'\t'
        lineas+='\n'
        lineas+=l*len(intervalos)
        lineas+='\n'
        lineas+='\n'
        lineas+=gettext.gettext('Absolute Freq.')
        lineas+='\t'
        for a in Fa:
           lineas+='\t'
           lineas+=str(a)
           lineas+='\t'+'\t'+'\t'
        lineas+='\n'
        lineas+='\n'
        lineas+=gettext.gettext('Relative Freq.')
        lineas+='\t'
        for r in Fr:
           lineas+='\t'
           lineas+=r
           lineas+='\t'+'\t'+'\t'
       
        widget=self._widgets.get_widget('vistaFrecuencias')
        self.mostrarTextView(widget, lineas)


#*******************************************************************
#-----------------------------------------------------------
# Función: Extrae los caminos crí­ticos, calcula su í­ndice de
#          criticidad y muestra el resultado en la interfaz
#
# Parámetros: grafo (grafo Pert)
#         duraciones (duraciones simuladas)
#             early (lista con los tiempos early)
#             last (lista con los tiempos last)
#         itTotales (iteraciones totales)
#
# Valor de retorno: - 
#-----------------------------------------------------------

   def indiceCriticidad(self, grafo, duraciones, early, last, itTotales):
      #Se extraen los caminos crí­ticos
      holguras=self.holguras(grafo.activities, early, last, duraciones)  # Holguras de cada actividad
      actCriticas=self.actCriticas(holguras, grafo.activities)  # Se extraen las act. crí­ticas
      criticos=self.grafoCriticas(actCriticas) # Se crea un grafo crí­tico y se extraen los caminos

      # Se extraen todos los caminos (crí­ticos o no) del grafo original
      successors = self.tablaSucesoras(self.actividad)
      g=graph.roy(successors)
      caminos=self.buscarCaminos(g) 
   
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


#*******************************************************************
#-----------------------------------------------------------
# Función: Prepara los datos de la simulación para ser mostrados
#          en formato CSV
#
# Parámetros: duraciones (lista con las duraciones de la simulación)
#             iteraciones (número de iteraciones totales)
#             media (duración media)
#             dTipica (desviación tí­pica)
#             modeloCriticidad (lista de caminos e í­ndice de criticidad)
#
# Valor de retorno: s (texto a mostrar en formato CSV) 
#-----------------------------------------------------------

   def datosSimulacion2csv(self, duraciones, iteraciones, media, dTipica, modeloCriticidad): 
        s=''
        s+=gettext.gettext('SIMULATION DATA')
        s+='\n'
        s+='\n'
        s+=gettext.gettext('N, I.CRITICIDAD, PATH')
        s+='\n'
        for n in range(len(modeloCriticidad)):
           s+= modeloCriticidad[n][0]+','+ modeloCriticidad[n][1]+','+'"'+modeloCriticidad[n][2]+'"'
           s+='\n'
        s+='\n'
        s+='\n'
        s+=gettext.gettext('AVERAGE, TYPICAL DEV.')
        s+='\n'
        s+= media+','+dTipica
        s+='\n'
        s+='\n'
        s+=gettext.gettext('TOTAL SIMULATIONS')
        s+='\n'
        s+= iteraciones
        s+='\n'
        s+='\n'
        s+=gettext.gettext('DURATIONS')
        s+='\n'
        for d in duraciones:
           s+= str(d)
           s+='\n'

        #print s
        return s        
 

#********************************************************************
#-----------------------------------------------------------
# Función: Limpia los datos de la ventana de simulación 
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def limpiarVentanaSim(self):
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
        self.mostrarTextView(frecuencias, '')
        self.modeloC.clear()
        if len(self.boxS)>0:
           self.hBoxSim.remove(self.boxS)


#*******************************************************************************************************************
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #            PROBABILIDADES                    #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Se extraen los valores de la media y la desviación típica del camino que va a ser objeto del
#          cálculo de probabilidades, es decir, el camino seleccionado
#
# Parámetros: -
#
# Valor de retorno: media (duración media)
#                   dTipica (desviación tí­pica)
#-----------------------------------------------------------  

   def extraerMediaYDTipica(self):
         vistaListaZ = self._widgets.get_widget('vistaListaZad')
         sel = vistaListaZ.get_selection()
         modo= sel.get_mode()
         modelo, it = sel.get_selected()
         media=modelo.get_value(it, 0)
         dTipica=modelo.get_value(it, 1)

         return media, dTipica


#************************************************************************
#-----------------------------------------------------------
# Función: Cálculo de probabilidades       
#
# Parámetros: dato1 (dato primer Entry)
#             dato2 (dato segundo Entry)
#             media (duración media)
#             dTipica (desviación tí­pica)
#
# Valor de retorno: p (probabilidad calculada)
#-----------------------------------------------------------  

   def calcularProb(self, dato1, dato2, media, dTipica):
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
  

#************************************************************************
#-----------------------------------------------------------
# Función: Cálculo de probabilidades para la simulación      
#
# Parámetros: dato1 (dato primer Entry)
#             dato2 (dato segundo Entry)
#             intervalos (lista de intervalos)
#             itTotales (iteraciones totales)
#
# Valor de retorno: x (probabilidad calculada)
#-----------------------------------------------------------

   def calcularProbSim(self, dato1, dato2, intervalos, itTotales):
      if dato1=='':
           x=0
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
           x=0
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
            x=0
            for n in range(len(intervalos)):
            #print intervalos[n][0], dato2, intervalos[n][1], dato1
               if float(intervalos[n][1])>float(dato1) and float(intervalos[n][0])<float(dato2):
                  #print 'entra'
                  s=self.Fa[n]/float(itTotales)
                  #print s, 's'
                  x+=s
                  #print x, 'suma'
      return x           

#************************************************************************
#-----------------------------------------------------------
# Función: Escribe en el TextView las probabilidades calculadas        
#
# Parámetros: dato (probabilidad a escribir)
#
# Valor de retorno: -
#-----------------------------------------------------------  
         
   def escribirProb(self, dato):
         prob=self._widgets.get_widget('tvProbabilidades')
         prob.set_buffer(self.bufer)
         it1=self.bufer.get_start_iter()
         it2=self.bufer.get_end_iter()
         textoBufer=self.bufer.get_text(it1, it2)
         #print textoBufer, 'bufer'
         completo=textoBufer+'\n'+dato
         #print completo
         self.bufer.set_text(completo) 


#***********************************************************************
#-----------------------------------------------------------
# Función: Limpia los datos de la ventana de probabilidades 
#
# Parámetros: c (0: llamada desde la ventana Zaderenko
#       1: llamada desde la ventana Simulación)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def limpiarVentanaProb(self, c):
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


#####################################################################################################################
                            # FUNCIONES DIALOGOS ABRIR, GUARDAR Y ADVERTENCIA/ERRORES #
#####################################################################################################################          

                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #            DIÁLOGOS ABRIR                    #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Abre un proyecto con extensión '.prj' guardado
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def abrir(self):
        dialogoFicheros = gtk.FileChooserDialog(gettext.gettext("Open File"),None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK ))
        # Se añade un filtro para que el diálogo me muestre sólo los archivos con la extensión '.prj'
        filtro=gtk.FileFilter()
        filtro.add_pattern('*.prj')
        filtro.add_pattern('*.txt')
        dialogoFicheros.add_filter(filtro)
        dialogoFicheros.set_default_response(gtk.RESPONSE_OK)
        resultado = dialogoFicheros.run()
        if resultado == gtk.RESPONSE_OK:
            try: 
                # Se abre el fichero en modo lectura y se coloca el nombre del fichero como tí­tulo del proyecto abierto
                self.directorio=dialogoFicheros.get_filename()
                flectura=open(self.directorio,'r') 
                self.asignarTitulo(self.directorio)
                # Se cargan los datos del fichero 
                tabla=[]
                if self.directorio[-4:] == '.prj':  
                    tabla=pickle.load(flectura)
                    self.cargaDatos(tabla) 
                else: # Fichero de texto
                    tabla=self.leerTxt(flectura)
                    self.cargarTxt(tabla)

            except IOError :
                self.dialogoError(gettext.gettext('The selected file does not exist'))
    
            flectura.close()
        #elif resultado == gtk.RESPONSE_CANCEL:
            #print "No hay elementos seleccionados"

        dialogoFicheros.destroy() 



#********************************************************************************************************************         
#-----------------------------------------------------------
# Función: Abre un fichero de la librería de proyectos 
#          PSPLIB con extensión '.sm'
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def abrirPSPLIB(self):
        dialogoFicheros = gtk.FileChooserDialog(gettext.gettext("Import PSPLIB file"),None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK ))
        # Se añade un filtro para que el diálogo me muestre sólo los archivos con la extensión '.sm'
        filtro=gtk.FileFilter()
        filtro.add_pattern('*.sm')
        dialogoFicheros.add_filter(filtro)
        dialogoFicheros.set_default_response(gtk.RESPONSE_OK)
        resultado = dialogoFicheros.run()
        if resultado == gtk.RESPONSE_OK:
            try: 
                # Se abre el fichero en modo lectura y se coloca el nombre del fichero como tí­tulo del proyecto abierto
                self.directorio=dialogoFicheros.get_filename()
                flectura=open(self.directorio,'r')
                self.asignarTitulo(self.directorio)
                # Se lee el fichero y se extraen los datos necesarios 
                prelaciones, rec, asig=self.leerPSPLIB(flectura)   
                # Se cargan los datos extraidos en las listas correspondientes
                self.cargarPSPLIB(prelaciones, rec, asig)         

            except IOError :
                self.dialogoError(gettext.gettext('The selected file does not exist'))  
 
            flectura.close()
        #elif resultado == gtk.RESPONSE_CANCEL:
            #print "No hay elementos seleccionados"

        dialogoFicheros.destroy() 


#******************************************************************************************************************** 
  
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #            DIÁLOGOS GUARDAR                  #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Salva un proyecto con extensión '.prj'
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------

     
   def guardar(self, g):
        #print self.directorio
        if g==1:
           dialogoGuardar = gtk.FileChooserDialog (gettext.gettext("Save"),None,gtk.FILE_CHOOSER_ACTION_SAVE,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE, gtk.RESPONSE_OK))
           dialogoGuardar.set_default_response(gtk.RESPONSE_OK)
           resultado = dialogoGuardar.run()
        else:
           dialogoGuardar = gtk.FileChooserDialog (gettext.gettext("Save as..."),None,gtk.FILE_CHOOSER_ACTION_SAVE,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE, gtk.RESPONSE_OK))
           dialogoGuardar.set_default_response(gtk.RESPONSE_OK)
           resultado = dialogoGuardar.run()
        if resultado == gtk.RESPONSE_OK:
            try:
                # Se abre el fichero en modo escritura, se añade la extensión '.prj' al final del nombre
                # asignado al proyecto y se coloca el nombre del fichero como tí­tulo del proyecto 
                self.directorio=dialogoGuardar.get_filename()
                print self.directorio[-4:], self.directorio[:-4]
                if self.directorio[-4:] == '.prj':
                    #print '1'
                    fescritura=open(self.directorio,'w')
                    titulo=basename(self.directorio)
                    ubicacion=self.directorio[:-(len(titulo)+1)]
                elif self.directorio[-4:] == '.txt':
                    fescritura=open(self.directorio[:-4]+'.prj','w')
                    titulo=basename(self.directorio+'.prj')
                    ubicacion=self.directorio[:-(len(titulo)-3)]
                else:
                    #print '2', self.directorio
                    fescritura=open(self.directorio+'.prj','w')
                    titulo=basename(self.directorio+'.prj')
                    ubicacion=self.directorio[:-(len(titulo)-3)]
                self.vPrincipal.set_title(titulo+' ('+ubicacion+') '+ '- PPC-Project')
                # Se guardan todos los datos en una lista y se escriben en el fichero
                tabla=[]
                tabla.append(self.actividad)
                tabla.append(self.recurso)
                tabla.append(self.asignacion)
                pickle.dump(tabla, fescritura)

            except IOError :
                self.dialogoError(gettext.gettext('Error saving the file'))    
            fescritura.close()
        #elif resultado == gtk.RESPONSE_CANCEL:  
            #print "No hay elementos seleccionados"

        dialogoGuardar.destroy() 

#********************************************************************************************************************  
#-----------------------------------------------------------
# Función: Salva un proyecto con extensión '.prj' guardado anteriormente
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------       
     
   def guardado(self, nombre):
        if nombre[-4:] != '.prj':
           if nombre[-4:]=='.txt':
              nombre=nombre[:-4]+'.prj'
           else:
              nombre=nombre+'.prj'
        try:
             # Se abre el fichero en modo escritura y se coloca el nombre del fichero como tí­tulo del proyecto 
             fescritura=open(nombre,'w')
             self.asignarTitulo(nombre)
             # Se guardan todos los datos en una lista y se escriben en el fichero  
             tabla=[]
             tabla.append(self.actividad)
             tabla.append(self.recurso)
             tabla.append(self.asignacion)
             pickle.dump(tabla, fescritura)
                 
        except IOError :
             self.dialogoError(gettext.gettext('Error saving the file'))    
        fescritura.close()    
    

#********************************************************************************************************************  
#-----------------------------------------------------------
# Función: Salva texto en formato CSV
#
# Parámetros: texto (texto a guardar)
#
# Valor de retorno: -
#-----------------------------------------------------------   

   def guardarCsv(self, texto):
        dialogoGuardar = gtk.FileChooserDialog (gettext.gettext("Save"),None,gtk.FILE_CHOOSER_ACTION_SAVE,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialogoGuardar.set_default_response(gtk.RESPONSE_OK)
        resultado = dialogoGuardar.run()
        if resultado == gtk.RESPONSE_OK:
            try:
                nombre=dialogoGuardar.get_filename()
                if nombre[-4:]=='.csv':
                    fescritura=open(nombre,'w')
                else:
                    fescritura=open(nombre+'.csv','w')
                fescritura.write(texto)

            except IOError :
                self.dialogoError(gettext.gettext('Error saving the file'))    
            fescritura.close()
        #elif resultado == gtk.RESPONSE_CANCEL:  
            #print "No hay elementos seleccionados"

        dialogoGuardar.destroy() 
        

#********************************************************************************************************************         
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #   DIÁLOGOS DE ADVERTENCIA Y ERRORES          #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Muestra un mensaje de advertencia al intentar salir
#          de la aplicación
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------
         
   def dialogoSalir(self):
        dialogo=gtk.Dialog(gettext.gettext("Attention!!"), None, gtk.MESSAGE_QUESTION, (gettext.gettext("NO"), gtk.RESPONSE_CANCEL, gettext.gettext("YES"), gtk.RESPONSE_OK ))
        label=gtk.Label(gettext.gettext('Are you sure you want to quit PPC-Project?'))
        dialogo.vbox.pack_start(label,True,True,10)
        label.show()
        respuesta=dialogo.run()
        if respuesta==gtk.RESPONSE_OK:
            self.vPrincipal.destroy()
 
        #elif respuesta==gtk.RESPONSE_CANCEL:
            #print "No desea salir de la aplicacion"

        dialogo.destroy()

#********************************************************************************************************************         
#-----------------------------------------------------------
# Función: Muestra un mensaje de advertencia si se intenta cerrar
#          un proyecto abierto no guardado
#
# Parámetros: c ('cerrar': cerrar proyecto
#                'salir': salir de la aplicación)
#
# Valor de retorno: -
#-----------------------------------------------------------
         
   def dialogoProyectoAbierto(self, c):
        dialogo=gtk.Dialog(gettext.gettext("Attention!!"), None, gtk.MESSAGE_QUESTION, (gettext.gettext("NO"), gtk.RESPONSE_CANCEL, gettext.gettext("YES"), gtk.RESPONSE_OK ))
        label=gtk.Label(gettext.gettext('The actual project has been modified. Do you want to save the changes?'))
        dialogo.vbox.pack_start(label,True,True,10)
        label.show()
        respuesta=dialogo.run()
        if respuesta==gtk.RESPONSE_OK:
            self.guardar(1)
 
        elif respuesta==gtk.RESPONSE_CANCEL:
            if c==gettext.gettext('exit'):
               self.dialogoSalir()
            else:
               # Se limpian todas las estructuras de datos
               self.modelo.clear()
               self.actividad=[]
               self.modeloR.clear()
               self.recurso=[]
               self.modeloAR.clear()
               self.asignacion=[]
               self.vPrincipal.set_title(gettext.gettext('PPC-Project'))

        dialogo.destroy()


#********************************************************************************************************************         
#-----------------------------------------------------------
# Función: Muestra un mensaje de advertencia si no se han
#          introducido bien las unidades de recurso
#
# Parámetros: tipo (tipo de recurso)
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def dialogoRec(self, tipo):
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

#********************************************************************************************************************         
#-----------------------------------------------------------
# Función: Muestra un mensaje de error en la apertura del fichero
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def dialogoError(self, cadena):
        dialogo=gtk.Dialog(gettext.gettext("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        label=gtk.Label(cadena)
        dialogo.vbox.pack_start(label,True,True,10)
        label.show()
        respuesta=dialogo.run()

        dialogo.destroy()   


#********************************************************************************************************************         
#-----------------------------------------------------------
# Función: Muestra un mensaje de error si en la introducción
#          de datos hay alguna actividad repetida
#
# Parámetros: repetidas (lista con las actividades repetidas)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def errorActividadesRepetidas(self, repetidas):
        dialogo=gtk.Dialog(gettext.gettext("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        for actividad in repetidas:
            label=gtk.Label(gettext.gettext('The activity ')+' "'+actividad+'"'+gettext.gettext(' is repeated\n'))
            dialogo.vbox.pack_start(label,True,True,5)
            label.show()
        respuesta=dialogo.run()

        dialogo.destroy() 


#********************************************************************************************************************         
#-----------------------------------------------------------
# Función: Muestra un mensaje de error si en la ventana
#          'recursos necesarios por actividad' hay alguna
#          actividad o algun recurso inexistente
#
# Parámetros: datosErroneos (lista con los datos erróneos)
#             cadena (cadena de texto)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def errorRecNecAct(self, datosErroneos, cadena):
        dialogo=gtk.Dialog(gettext.gettext("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        for dato in datosErroneos:
            label=gtk.Label(cadena+' "'+dato+'"'+ gettext.gettext(' does not exist\n'))
            dialogo.vbox.pack_start(label,True,True,5)
            label.show()
        respuesta=dialogo.run()

        dialogo.destroy() 


#####################################################################################################################
                                   # FUNCIONES EJECUCIÓN DE LA APLICACIÓN
#####################################################################################################################  

#-----------------------------------------------------------
# Función: Ejecuta la aplicación
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------

   def run(self):
        self.ejecutarAplicacion()
        gtk.main()
 

#****************************************************************      
             
#-----------------------------------------------------------
# Función: Ejecuta la aplicación recibiendo un archivo '.prj' 
#          por la lí­nea de órdenes o ejecuta la aplicación 
#          normalemente (si no recibe ningún archivo)
#
# Parámetros: -
#
# Valor de retorno: -
#-----------------------------------------------------------

   def ejecutarAplicacion(self):
        if len(sys.argv)>1:
            nombre=sys.argv[1]
            try:
                fichero=open(nombre, 'r')
                # Se crean todos los TreeViews
                self.crearTreeViews()
                # Se asigna el nombre como título del proyecto
                self.directorio=nombre
                self.asignarTitulo(self.directorio)
                # Se cargan los datos en la lista 
                tabla=[]             
                tabla=pickle.load(fichero)
                self.cargaDatos(tabla) 
                fichero.close()

            except IOError:
                self.dialogoError(gettext.gettext('The selected file does not exist'))
                gtk.main_quit()
    
        else:
            self.crearTreeViews()
            #print 'Ejecución de la aplicación normalmente'     



       
#####################################################################################################################
                       # MANEJADORES #
#####################################################################################################################

#-----------------------------------------------------------
# Función: Acción usuario para cerrar la aplicación
#
# Parámetros: ventana (ventana principal)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_wndPrincipal_destroy(self, ventana):
        gtk.main_quit()
   
     
#************************************************************************************************************
                  # MENÚ #
#************************************************************************************************************ 
                               
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                   MENÚ ARCHIVO                     #
      #++++++++++++++++++++++++++++++++++++++++++++++++++#    

#-----------------------------------------------------------
# Función: Acción usuario para abrir un proyecto nuevo
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def on_mnNuevo_activate(self, menu_item):
        self.introduccionDatos()

#-----------------------------------------------------------
# Función: Acción usuario para abrir un proyecto guardado
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnAbrir_activate(self, menu_item):
        self.abrir()

#-----------------------------------------------------------
# Función: Acción usuario para abrir un proyecto de la 
#          librería de proyectos PSPLIB
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnAbrirPSPLIB_activate(self, menu_item):
        self.abrirPSPLIB()
 
#-----------------------------------------------------------
# Función: Acción usuario para salvar un proyecto abierto
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def  on_mnGuardar_activate(self, menu_item):
        # Se comprueba que no haya actividades repetidas
        errorActRepetidas, actividadesRepetidas=self.actividadesRepetidas(self.actividad)
        if errorActRepetidas==0:
             # Si no se ha guardado anteriormente, abrimos el cuadro de diálogo
             if self.directorio==gettext.gettext('Unnamed -PPC-Project'):
                 self.guardar(1)
             # Si ya ha sido guardado antes, se modifica
             else:
                 self.guardado(self.directorio)
        # Si hay actividades repetidas, se muestra un mensaje de error
        else:
            #print actividadesRepetidas
            self.errorActividadesRepetidas(actividadesRepetidas) 

        self.control=0

#-----------------------------------------------------------
# Función: Acción usuario para salvar un proyecto guardado anteriormente
#          con propiedades diferentes (nombre, extensión, ...)
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnGuardarComo_activate(self, menu_item):
        # Se comprueba que no haya actividades repetidas
        errorActRepetidas, actividadesRepetidas=self.actividadesRepetidas(self.actividad)
        if errorActRepetidas==0:
              self.guardar(2)
             
        # Si hay actividades repetidas, se muestra un mensaje de error
        else:
            #print actividadesRepetidas
            self.errorActividadesRepetidas(actividadesRepetidas) 
       
        self.control=0

#-----------------------------------------------------------
# Función: Acción usuario para cerrar un proyecto abierto
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnCerrar_activate(self, menu_item):
        if self.control==0:   # El proyecto actual ha sido guardado
           # Se limpian todas las listas de datos
           self.modelo.clear()
           self.actividad=[]
           self.modeloR.clear()
           self.recurso=[]
           self.modeloAR.clear()
           self.asignacion=[]
           self.vPrincipal.set_title(gettext.gettext('PPC-Project'))
       
        else:                 # El proyecto actual aún no se ha guardado
           self.dialogoProyectoAbierto(gettext.gettext('close'))

#-----------------------------------------------------------
# Función: Acción usuario para salir de la aplicación
#
# Parámetros: *args (argumentos) 
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnSalir_activate(self, *args):
        if self.control==0:   # El proyecto actual ha sido guardado
            self.dialogoSalir()
        else:                 # El proyecto actual aún no se ha guardado
            self.dialogoProyectoAbierto(gettext.gettext('exit'))


#******************************************************************************************************************  
               
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                   MENÚ VER                         #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 
#-----------------------------------------------------------
# Función: Acción usuario para activar o desactivar la barra
#          de herramientas, inicialmente inactiva
#
# Parámetros: checkMenuItem (item a activar o desactivar)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_bHerramientas_activate(self, checkMenuItem):
        checkMenuItem==self.bHerramientas
        if checkMenuItem.get_active():
            self.bHerramientas.show()
        else:
            self.bHerramientas.hide()

#-----------------------------------------------------------
# Función: Acción usuario para que la aplicación ocupe toda
#          la pantalla 
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnPantallaComp_activate(self, menu_item):
        self.vPrincipal.fullscreen()

#-----------------------------------------------------------
# Función: Acción usuario para que la aplicación vuelva a su
#          estado original
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnSalirPantComp_activate(self, menu_item):
        self.vPrincipal.unfullscreen()


#*****************************************************************************************************************
                 
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                   MENÚ ACCIÓN                      #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana de 
#          introducción de recursos
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnCrearRecursos_activate(self, menu_item):
        if self.recurso==[]:
            self.modeloR.append()
        self.vRecursos.show()


#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que 
#          muestra el grafo Roy
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

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


#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que 
#          muestra el grafo Pert
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

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


     
#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que 
#          muestra las actividades y su nodo inicio y fí­n
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnActividades_activate(self, menu_item):
        # Se crea el grafo Pert y se renumera
        grafoRenumerado=self.pertFinal()

        # Se muestran las actividades y su nodo inicio y fí­n  
        self.mostrarActividades(self.modeloA, grafoRenumerado.activities, grafoRenumerado.graph)
     
#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que muestra
#          la matriz de Zaderenko con sus tiempos early y last y
#          todos los caminos del grafo, su duración y desviación tí­pica
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnZaderenko_activate(self, menu_item):
          s=0
          for a in self.actividad:
               if a[6]=='' or a[7]=='':
                    s+=1
                    
          if s>0:
               self.dialogoError(gettext.gettext('There are uncomplete activities'))
          else:
               self.ventanaZaderenko()

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que
#          muestra las holguras de cada actividad
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_mnHolguras_activate(self, menu_item):
          s=0
          for a in self.actividad:
               if a[6]=='' or a[7]=='':
                    s+=1
                    
          if s>0:
               self.dialogoError(gettext.gettext('There are uncomplete activities'))
          else:
               self.ventanaHolguras()

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que muestra
#          los resultados de la simulación de duraciones (tabla
#          de frecuencias, gráfica, ...)
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnSimulacion_activate(self, menu_item):
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
             self.vSimulacion.show()
             self.simTotales=[] # Lista con las simulaciones totales
             self.duraciones=[] # Lista con las duraciones de las simulaciones
             self.criticidad={} # Diccionario con los caminos y su í­ndice de criticidad
             self.intervalos=[] # Lista con los intervalos de las duraciones
               
      

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que 
#          muestra todos los caminos de un grafo
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def on_mnCalcularCaminos_activate(self, menu_item):
        self.calcularCaminos()


#************************************************************************************************************               

                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                   MENÚ AYUDA                       #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que muestra
#          el diálogo de ayuda 
#
# Parámetros: menu_item (item activado)
#
# Valor de retorno: -
#-----------------------------------------------------------
     
   def on_mnAyuda_activate(self, menu_item):
        dialogoAyuda = self.dAyuda
        dialogoAyuda.show()


#************************************************************************************************************
               # BARRA DE HERRAMIENTAS #
#************************************************************************************************************ 

#-----------------------------------------------------------
# Función: Acción usuario para acceder abrir un proyecto nuevo
#
# Parámetros: boton_her (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------                               

   def on_tbNuevo_clicked(self, boton_her):
       self.introduccionDatos()

#-----------------------------------------------------------
# Función: Acción usuario para acceder abrir un proyecto guardado
#
# Parámetros: boton_her (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------        

   def on_tbAbrir_clicked(self, boton_her):
        self.abrir()

#-----------------------------------------------------------
# Función: Acción usuario para acceder salvar un proyecto abierto
#
# Parámetros: boton_her (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------        

   def on_tbGuardar_clicked(self, boton_her):
        # Se comprueba que no haya actividades repetidas
        errorActRepetidas, actividadesRepetidas=self.actividadesRepetidas(self.actividad)
        if errorActRepetidas==0:
             # Si no se ha guardado anteriormente, abrimos el cuadro de diálogo
             if self.directorio==gettext.gettext('Unnamed -PPC-Project'):
                 self.guardar(1)
             # Si ya ha sido guardado antes, se modifica
             else:
                 self.guardado(self.directorio)
        
        # Si hay actividades repetidas, se muestra un mensaje de error
        else:
            #print actividadesRepetidas
            self.errorActividadesRepetidas(actividadesRepetidas) 

        self.control=0

#-----------------------------------------------------------
# Función: Acción usuario para acceder cerrar un proyecto abierto
#
# Parámetros: boton_her (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_tbCerrar_clicked(self, boton_her):
        if self.control==0:   # El proyecto actual ha sido guardado
           # Se limpian todas las listas de datos
           self.modelo.clear()
           self.actividad=[]
           self.modeloR.clear()
           self.recurso=[]
           self.modeloAR.clear()
           self.asignacion=[]
           self.vPrincipal.set_title(gettext.gettext('PPC-Project'))
       
        else:                 # El proyecto actual aún no se ha guardado
                self.dialogoProyectoAbierto(gettext.gettext('close'))

#-----------------------------------------------------------
# Función: Acción usuario para acceder salir de la aplicación
#
# Parámetros: boton_her (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------   
     
   def on_tbSalir_clicked(self, boton_her):  
        self.dialogoSalir()


#************************************************************************************************************
                  # VENTANAS #
#************************************************************************************************************ 

      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                    GRAFO PERT                      #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 
 
#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana que muestra
#          el grafo Pert
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_wndGrafoPert_delete_event(self, ventana, evento):
        ventana.hide()
        return True


#************************************************************************************************************       

      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                     GRAFO ROY                      #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 
 
#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana que muestra
#          el grafo Roy
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_wndGrafoRoy_delete_event(self, ventana, evento):
        ventana.hide()
        return True


#************************************************************************************************************       
                                             
          #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                    ACTIVIDADES                     #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para acceder aceptar los datos
#          que aparecen en la ventana de actividades
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  
 
   def on_btAceptarAct_clicked(self, boton):
        self.vActividades.hide()

#-----------------------------------------------------------
# Función: Acción usuario para acceder cerrar la ventana de actividades
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_wndActividades_delete_event(self, ventana, evento):
        ventana.hide()
        return True


#*********************************************************************************************************       

        #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                     ZADERENKO                      #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Al seleccionar uno de los caminos del grafo que se muestran
#          en la ventana de Zaderenko, se activa el botón 
#          'calcular probabilidad' que aparací­a inactivo inicialmente          
#
# Parámetros: vistaListaZ (widget donde se muestran los caminos)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_vistaListaZad_cursor_changed(self, vistaListaZ):
        vistaListaZ = self._widgets.get_widget('vistaListaZad')
        cursor, columna = vistaListaZ.get_cursor()
        if cursor:
            self._widgets.get_widget('btCalcularProb').set_sensitive(True)
            modelo = vistaListaZ.get_model()
            iterador = modelo.get_iter(cursor)
        else:
            self._widgets.get_widget('btCalcularProb').set_sensitive(False)

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que muestra
#          el cálculo de probabilidades
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_btCalcularProb_clicked(self, boton):
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

#-----------------------------------------------------------
# Función: Acción usuario para aceptar la información 
#          que aparece en la ventana de Zaderenko: matriz de
#          Zaderenko, tiempos early y last, caminos del grafo, ...
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_btAceptarZad_clicked(self, boton):
        self._widgets.get_widget('btCalcularProb').set_sensitive(False)
        self.vZaderenko.hide()

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana que muestra 
#          las holguras de cada actividad
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_btHolgZad_clicked(self, boton):
          s=0
          for a in self.actividad:
               if a[6]=='' or a[7]=='':
                    s+=1
                    
          if s>0:
               self.dialogoError(gettext.gettext('There are uncomplete activities'))
          else:
               self.ventanaHolguras()
    

#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana de Zaderenko
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_wndZaderenko_delete_event(self, ventana, evento):
        self._widgets.get_widget('btCalcularProb').set_sensitive(False)
        ventana.hide()
        return True


#****************************************************************************************************************       

          #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                   HOLGURAS                       #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para aceptar la información 
#          que aparece en la ventana de holguras: los tres
#          tipos de holgura para cada actividad
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_btAceptarHolg_clicked(self, boton):
        self.vHolguras.hide()

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana de Zaderenko
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_btZadHolg_clicked(self, boton):
          s=0
          for a in self.actividad:
               if a[6]=='' or a[7]=='':
                    s+=1
                    
          if s>0:
               self.dialogoError(gettext.gettext('There are uncomplete activities'))
          else:
               self.ventanaZaderenko()


#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana de holguras
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  


   def on_wndHolguras_delete_event(self, ventana, evento):
        ventana.hide()
        return True


#************************************************************************************************************       

           #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                 PROBABILIDADES                   #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario al activar el valor introducido en 
#          el primer gtk.Entry de la ventana de probabilidades          
#
# Parámetros: entry (entry activado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_valor1Prob_activate(self, entry):
         # Se extraen los valores de las u.d.t. de la interfaz
         valor1=self._widgets.get_widget('valor1Prob')   
         dato1=valor1.get_text()
         valor2=self._widgets.get_widget('valor2Prob')   
         dato2=valor2.get_text()

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


#-----------------------------------------------------------
# Función: Acción usuario al activar el valor introducido en 
#          el segundo gtk.Entry de la ventana de probabilidades          
#
# Parámetros: entry (entry activado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_valor2Prob_activate(self, entry):
         # Se extraen los valores de las u.d.t. de la interfaz
         valor1=self._widgets.get_widget('valor1Prob')   
         dato1=valor1.get_text()
         valor2=self._widgets.get_widget('valor2Prob')   
         dato2=valor2.get_text()

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
         if dato1=='':
             mostrarDato=gettext.gettext('P ( Project < ')+str(dato2)+' ) = '+str('%3.3f'%(x))+' ('+prob+')'
         elif dato2=='':
             mostrarDato='P ( '+str(dato1)+gettext.gettext(' < Project ) = ')+str('%3.3f'%(x))+' ('+prob+')'
         else:
             mostrarDato='P ( '+str(dato1)+gettext.gettext(' < Project < ')+str(dato2)+' ) = '+str('%3.3f'%(x))+' ('+prob+')'
         self.escribirProb(mostrarDato)
         

#-----------------------------------------------------------
# Función: Acción usuario al activar el valor introducido en 
#          el tercer gtk.Entry de la ventana de probabilidades          
#
# Parámetros: entry (entry activado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_valor3Prob_activate(self, entry):
         # Se extrae el valor de probabilidad de la interfaz
         valor3=self._widgets.get_widget('valor3Prob')   
         dato3=valor3.get_text()
         #print dato3, 'dato3'
         if dato3[-1:]=='%':
            dato3=float(dato3[:-1])/100

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
               print x, 'x'
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
                

#-----------------------------------------------------------
# Función: Acción usuario para aceptar la información que
#          muestra la ventana de cálculo de probabilidades
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_btAceptarProb_clicked(self, boton):
      titulo=self.vProbabilidades.get_title()
      if titulo==gettext.gettext('Probability related to the path'):
         self.limpiarVentanaProb(0)
      else:
         self.limpiarVentanaProb(1)
         
      self.vProbabilidades.hide()

#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana de cálculo 
#          de probabilidades
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_wndProbabilidades_delete_event(self, ventana, evento):
        titulo=self.vProbabilidades.get_title()
        if titulo==gettext.gettext('Probability related to the path'):
           self.limpiarVentanaProb(0)
        else:
           self.limpiarVentanaProb(1)
  
        ventana.hide()
        return True



#****************************************************************************************************************       

               #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                  SIMULACIÓN                       #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: -
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_btContinuarIterando_clicked(self, boton):
      # Se extrae el número de iteraciones 
        iteracion=self._widgets.get_widget('iteracion')
        it=iteracion.get_text()
        #print it, 'iteraciones'
        if it[:1]=='-':  # Nº iteraciones negativo
           self.dialogoError(gettext.gettext('The number of iterations must be positive'))
        else: # Nº iteraciones positivo
            # Se almacenan las iteraciones totales en una variable y se muestra en la interfaz
              totales=self._widgets.get_widget('iteracionesTotales')
              interfaz=totales.get_text()
              if interfaz!='':
                 itTotales=int(it)+int(interfaz)
              else:
                 itTotales=int(it)
              #print itTotales, 'iteraciones totales'
              totales.set_text(str(itTotales))

            # Se realiza la simulación
              simulacion=self.simulacion(int(it))
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
                    mZad=self.mZad(grafoRenumerado.activities, nodosN, 0, s)
              early=self.early(nodosN, mZad)  
              last=self.last(nodosN, early, mZad)      
              tam=len(early)
              # Se calcula la duración del proyecto para cada simulación
              duracionProyecto=early[tam-1]
              #print duracionProyecto, 'duracion proyecto'  
              self.duraciones.append(duracionProyecto) 
              #print self.duraciones,'duraciones simuladas'
              # Se extraen los caminos crí­ticos y se calcula su í­ndice de criticidad
              self.indiceCriticidad(grafoRenumerado, s, early, last, itTotales)

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
                    valor='['+str('%5.2f'%(self.duracion(n, dMax, dMin, N)))+', '+str('%5.2f'%(self.duracion((n+1), dMax, dMin, N)))+'['       
                    interv.append(valor)
              if self.intervalos==[]:
                 self.intervalos=interv

              # Se calculan las frecuencias
              self.Fa, Fr=self.calcularFrecuencias(dMax, dMin, itTotales, N)

              # Se muestran los intervalos y las frecuencias en forma de tabla en la interfaz
              self.mostrarFrecuencias(self.intervalos, self.Fa, Fr)

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

#-----------------------------------------------------------
# Función: Acción usuario para aceptar la información que
#          muestra la ventana de simulación de duraciones:
#          tabla, gráfica, ....
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_btAceptarSim_clicked(self, boton):
        self.limpiarVentanaSim()
        self.vSimulacion.hide()
       
#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana de 
#          cálculo de probabilidades
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_btProbSim_clicked(self, boton):
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
         widgetMedia.set_sensitive(False)
         widgetdTipica=self._widgets.get_widget('dTipicaProb')
         widgetdTipica.set_text(dt)
         widgetdTipica.set_sensitive(False)

         # Se insensibilizan las casillas resultado
         resultado1=self._widgets.get_widget('resultado1Prob')
         resultado1.set_sensitive(False)
         resultado2=self._widgets.get_widget('resultado2Prob')
         resultado2.set_sensitive(False)

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

#-----------------------------------------------------------
# Función: Acción usuario para salvar la información que
#          muestra la ventana de simulación de duraciones
#          tabla, gráfica, ....
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_btGuardarSim_clicked(self, boton):
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
        simulacionCsv = self.datosSimulacion2csv(self.duraciones, iteraciones, m, dt, self.modeloC)
        
      # Se muestra el diálogo para salvar el archivo
        self.guardarCsv(simulacionCsv)


#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana de simulación 
#          de duraciones
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_wndSimulacion_delete_event(self, ventana, evento):
        self.limpiarVentanaSim()
        ventana.hide()
        return True


#*************************************************************************************************************       

           #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                     RECURSOS                       #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para aceptar la información que
#          muestra la ventana de recursos: nombre, tipo, unidad disponible 
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_btAceptarRec_clicked(self, boton):
        self.vRecursos.hide()
        
#-----------------------------------------------------------
# Función: Acción usuario para cancelar la información que
#          muestra la ventana de recursos: nombre, tipo, unidad disponible. 
#          Si se cancelan los datos, se borran definitivamente
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_btCancelarRec_clicked(self, boton):
        if self.recurso==[]:
            self.modeloR.append()
        self.vRecursos.hide()

#-----------------------------------------------------------
# Función: Acción usuario para acceder a la ventana de recursos
#          necesarios por actividad 
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#----------------------------------------------------------- 

   def on_btAsignarRec_clicked(self, boton):
        self.asignarRecursos()
 
#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana de recursos
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  
   def on_wndRecursos_delete_event(self, ventana, evento):
        ventana.hide()
        return True
 
 
#***************************************************************************************************************       

      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #         RECURSOS NECESARIOS POR ACTIVIDAD        #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para aceptar la información que
#          muestra la ventana de recursos necesarios por
#          actividad: actividad, recurso, unidad necesaria
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------   

   def on_btAceptarAR_clicked(self, boton):
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

                

#-----------------------------------------------------------
# Función: Acción usuario para cancelar la información que
#          muestra la ventana de recursos necesarios por
#          actividad: actividad, recurso, unidad necesaria. 
#          Si se cancelan los datos, se borran definitivamente
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------        

   def on_btCancelarAR_clicked(self, boton):
        self.modeloAR.clear()
        self.asignacion=[]
        self.vAsignarRec.hide()
 
#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana de recursos
#          necesarios por actividad 
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_wndAsignarRec_delete_event(self, ventana, evento):
        ventana.hide()
        return True


#******************************************************************************************************************

      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #               CALCULAR CAMINOS                   #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para aceptar la información que
#          muestra la ventana de calcular caminos
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------   

   def on_btAceptarCaminos_clicked(self, boton):
        self.vCaminos.hide()

#-----------------------------------------------------------
# Función: Acción usuario para exportar los caminos que se
#          muestran en la ventana a formato CSV para 
#          hoja de cálculo
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  
   
   def on_btExportarCsv_clicked(self, boton): 
        # Se buscan todos los caminos 
        successors = self.tablaSucesoras(self.actividad)
        g = graph.roy(successors)
        todosCaminos = graph.findAllPaths(g, 'Begin', 'End')

        # Se pasan a formato CSV
        #pathsInCSV = graph.royPaths2csv2(g)
        pathsInCSV = graph.royPaths2csv([self.actividad[i][1] for i in range(len(self.actividad))], todosCaminos)
        
        # Se muestra el diálogo para salvar el archivo
        self.guardarCsv(pathsInCSV) 
        
#-----------------------------------------------------------
# Función: Acción usuario para cerrar la ventana de calcular
#          caminos
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_wndCaminos_delete_event(self, ventana, evento):
        ventana.hide()
        return True


#********************************************************************************************************************       
     
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                      AYUDA                       #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Función: Acción usuario para aceptar la información que
#          muestra el diálodo de ayuda
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_dAyuda_response(self, False, boton):
        self.dAyuda.hide()

#-----------------------------------------------------------
# Función: Acción usuario para cerrar el diálogo de ayuda 
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  

   def on_dAyuda_delete_event(self, dialogo, evento):
        self.dAyuda.hide()
        return True


#***************************************************************************************************************            


if __name__ == '__main__':
    app = Proyecto()
    app.run()


