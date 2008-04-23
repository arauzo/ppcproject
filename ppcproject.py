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

import GTKgantt

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
from PSPLIB import leerPSPLIB
from zaderenko import mZad, early, last
from simAnnealing import simulatedAnnealing
from simAnnealing import resourcesAvailability
from simAnnealing import resourcesPerActivities


class PPCproject:
   def __init__(self):

      # Estructuras de datos básicas de la aplicación
      self.actividad  = []
      self.recurso    = []
      self.asignacion = []
      self.tabla      = []
      self.bufer=gtk.TextBuffer()
      self.directorio = gettext.gettext('Unnamed -PPC-Project')
      self.modified=0
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
      self.bHerramientas=self._widgets.get_widget('bHerramientas')

      self.zadViewList = self._widgets.get_widget('vistaZad')
      self.vistaLista = self._widgets.get_widget('vistaListaDatos')
      self.modelo = self.interface.modelo
      self.gantt = self.interface.gantt
      self.modeloR = self.interface.modeloR
      self.modeloAR = self.interface.modeloAR
      self.modeloComboS = self.interface.modeloComboS
      self.modeloA = self.interface.modeloA
      self.modeloZ = self.interface.modeloZ
      self.vistaListaZ = self.interface.vistaListaZ
      self.modeloH = self.interface.modeloH
      self.modeloC = self.interface.modeloC
      self.modeloF = self.interface.modeloF
      self.vistaFrecuencias = self.interface.vistaFrecuencias
      self.checkColum=[None]*9
      for n in range(9):
         self.checkColum[n] = self.interface.checkColum[n]
      self._widgets.get_widget('mnSalirPantComp').hide()
      self.enableProjectControls(False)
      self.row_height_signal = self.vistaLista.connect("expose-event", self.cbtreeview)
      self.vistaLista.connect('drag-end', self.reorder_gantt)
      self.modelo.connect('rows-reordered', self.reorder_gantt)

   def cbtreeview (self, container, widget):
      self.gantt.set_header_height(self.vistaLista.convert_tree_to_widget_coords(0,1)[1])
      if len (self.modelo) > 0 and self.modelo[0][1] != "":
         self.gantt.set_row_height(self.vistaLista.get_background_area(0,self.vistaLista.columna[0]).height)
         self.vistaLista.disconnect(self.row_height_signal)
      return False

   def enableProjectControls(self, value):
      self._widgets.get_widget('mnGuardar').set_sensitive(value)
      self._widgets.get_widget('mnGuardarComo').set_sensitive(value)
      self._widgets.get_widget('mnCerrar').set_sensitive(value)
      self._widgets.get_widget('mnAccion').set_sensitive(value)
      self._widgets.get_widget('tbGuardar').set_sensitive(value)
      self._widgets.get_widget('tbCerrar').set_sensitive(value)
      if (not value):
         self._widgets.get_widget('stbStatus').pop(0)
         self._widgets.get_widget('stbStatus').push(0, gettext.gettext("No project file opened"))

   def set_modified(self, value):
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
      for n in range(9):
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



###################### FUNCIONES DE INTRODUCCIÓN, CARGA Y ACTUALIZACIÓN DATOS ############

   def introduccionDatos(self):
      """
       Creación de un nuevo proyecto, eliminación de la lista actual y
                adicción de una fila vacía a la lista

       Parámetros: -
       Valor de retorno: -
      """
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
                     modelo[path][1] = new_text
                     it=self.modeloComboS.get_iter(path)
                     self.modeloComboS.set_value(it, 0, new_text)
                  #else:
                     #print 'actividad repetida'
                     #self.dialogoError('Actividad repetida')
                         
               else:  # Se inserta normalmente
                  modelo[path][1] = new_text
                  self.modeloComboS.append([modelo[path][1]])
                  self.gantt.add_activity(new_text)
                  self.gantt.update()


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
         if self.modelo[path][n]=='':
               if n==2:
                  self.actividad[int(path)][2]=[]
                  self.gantt.set_activity_prelations(self.actividad[int(path)][1], self.texto2Lista(self.modelo[path][2]))
                  self.gantt.update()
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
                     self.gantt.update()
                           
               # Si se introduce la media, se elimina el resto de duraciones        
               elif n==6:   
                  self.actividad[int(path)][n]=float(self.modelo[path][n])
                  for i in range(3, 6):
                     self.modelo[path][i]=''
                     self.actividad[int(path)][i]=''
                  self.gantt.set_activity_duration(self.modelo[path][1], float(self.modelo[path][6]))
                  self.gantt.update()

               # Si se modifica el tipo de distribución, se actualizan la media y la desviación tí­pica
               elif n==9:  
                  self.actividad[int(path)][9]=self.modelo[path][9]
                  if self.modelo[path][3]!='' or self.modelo[path][4]!='' or self.modelo[path][5]!='':
                     a=float(self.modelo[path][3]) #d.optimista
                     b=float(self.modelo[path][5]) #d.pesimista
                     m=float(self.modelo[path][4]) #d.más probable
                     self.actualizarMediaDTipica(path, self.modelo, self.actividad, a, b, m)
                     self.gantt.set_activity_duration(self.modelo[path][1], float(self.modelo[path][6]))
                     self.gantt.update()                  

               # Se controla el valor introducido en las siguientes 
               elif n==2:  
                  if self.modelo[path][2]==self.actividad[int(path)][1]:
                        self.modelo[path][2]==''
                        self.actividad[int(path)][2]=[]
                  else: 
                        self.actividad[int(path)][2] = self.texto2Lista(self.modelo[path][2])
                        self.gantt.set_activity_prelations(self.actividad[int(path)][1], self.texto2Lista(self.modelo[path][2]))
                        self.gantt.update()

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

 
   def cargaDatos(self, tabla):     
      """
       Actualización de los datos con los obtenidos de la   
                apertura de un fichero con extensión '.prj'

       Parámetros: tabla (lista que engloba a las tres listas: 
                   actividad, recurso y asignacion)
       Valor de retorno: -
      """
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
         self.gantt.add_activity(self.actividad[i][1], self.actividad[i][2], float(self.actividad[i][6]))
      self.gantt.update()      
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

   def leerTxt(self, f):
      """
       Lectura de un fichero con extensión '.txt'

       Parámetros: f (fichero)

       Valor de retorno: tabla (datos leidos)
      """
      tabla=[]
      l=f.readline()
      while l:
            linea=l.split('\t')
            linea[1]=linea[1].split(',')
            tabla.append(linea)
            l=f.readline()

      l=f.readline()
      
      return tabla
   

   def cargarTxt(self, tabla):
      """
       Actualización de los datos con los obtenidos de la   
                apertura de un fichero con extensión '.txt'

       Parámetros: tabla (lista con los datos del fichero)

       Valor de retorno: -
      """
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
         self.gantt.add_activity(fila[1], fila[2], float(fila[5]))
         cont+=1
   

#********************************************************************************************************************
#-----------------------------------------------------------
# Control de la introducción de las siguientes  
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
# Al modificar la etiqueta de alguna actividad, se modifica  
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
# Actualización de la columna de las siguientes en   
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
# Actualización de la columna de recursos en la lista de    
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
      #                    PSPLIB                        #
      #++++++++++++++++++++++++++++++++++++++++++++++++++#

#-----------------------------------------------------------
# Actualización de los datos con los obtenidos de la   
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

         # Update Gantt Diagram
         for row in self.actividad:
             self.gantt.add_activity(row[1], row[2], float(row[6]))         
         self.gantt.update()

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
# Actualización de la columna de las siguientes en   
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
# Comprobación de que los tiempos optimista, pesimista y
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
# Comprueba si se han introducido actividades repetidas 
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
# Comprobación de que las actividades 
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
# Comprobación de que los recursos
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
# Suma de las unidades de recurso disponibles
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
# Almacenamiento en una lista de listas (filas) las relaciones entre    
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
# Extracción en una lista las relaciones entre    
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
# Se inserta una o varias actividades siguientes  
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
# Pasa una lista de listas a formato cadena
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
# Pasa una lista a formato cadena
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
# Pasa un texto a formato lista 
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
# Introduce en una lista todas las etiquetas de las actividades  
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
# Cálculo de la media y la desviación típica a partir de la distribución, 
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
# Muestra datos en el Text View correspondiente 
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
# Asignación de tí­tulo al proyecto actual
#
# Parámetros: directorio (tí­tulo+directorio)
#
# Valor de retorno: - 
#----------------------------------------------------------- 
      
   def asignarTitulo(self, directorio):
         titulo=os.path.basename(directorio)
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
# Creación del grafo Pert y renumeración del mismo 
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
# Obtiene un diccionario que contiene las actividades 
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
# Creación de una lista que contenga los nodos del grafo
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
# Creación de un diccionario que representa las prelaciones 
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
# Calcula el algoritmo de Demoucron, es decir, divide  
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
# Se renumera el grafo Pert 
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
# Acción usuario para calcular todos los datos relacionados con Zaderenko 
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

#******************************************************************************
#-----------------------------------------------------------
# Muestra los caminos del grafo en la interfaz (ventana Zaderenko)
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
# Cálculo de las actividades criticas 
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
# Creación de un grafo sólo con actividades crí­ticas y extracción de
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
# Obtiene un diccionario que contiene las actividades 
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
# Búsqueda de los caminos criticos en todos los caminos
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
# Cálculo de la duración media y la desviación tí­pica
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
# Acción usuario para mostrar la etiqueta de cada actividad con su
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
# Acción usuario para mostrar los tres tipos de
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
        matrizZad = mZad(self.actividad, grafoRenumerado.activities, nodosN, 1, []) 

        # Se calculan los tiempos early y last
        tearly=early(nodosN, matrizZad) 
        tlast=last(nodosN, tearly, matrizZad)

        # Se calculan los tres tipos de holgura y se muestran en la interfaz
        holguras=self.holguras(grafoRenumerado.activities, tearly, tlast, []) 
        self.mostrarHolguras(self.modeloH, holguras) 


#*****************************************************************        
#-----------------------------------------------------------
# Cálculo de los tres tipos de holguras
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
# Muestra las hoguras en la interfaz
#
# Parámetros: modelo (lista de actividades)
#             hoguras (lista con los tres tipos de holguras de cada actividad)
#
# Valor de retorno: -
#-----------------------------------------------------------

   def mostrarHolguras(self, modelo, holguras):
        self.vHolguras.hide()  
        self.vHolguras.show()  

        modelo.clear()
        for n in range(len(holguras)):  
            modelo.append([holguras[n][0], holguras[n][1], holguras[n][2], holguras[n][3]])


#********************************************************************************************************************         
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #           CAMINOS DEL GRAFO                  #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Acción usuario para calcular y mostrar todos los 
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
#*******************************************************************************************************************
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #     RECUROS NECESARIOS POR ACTIVIDAD         #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Acción usuario para acceder a la ventana de 
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
# Simulación de duraciones de cada actividad según  
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

#*******************************************************************
#-----------------------------------------------------------
# Extrae los caminos crí­ticos, calcula su í­ndice de
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

#********************************************************************
#-----------------------------------------------------------
# Limpia los datos de la ventana de simulación 
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
        self.modeloF.clear()
        self.modeloC.clear()
        if len(self.boxS)>0:
           self.hBoxSim.remove(self.boxS)


#*******************************************************************************************************************
                #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #            PROBABILIDADES                    #
      #++++++++++++++++++++++++++++++++++++++++++++++++++# 

#-----------------------------------------------------------
# Se extraen los valores de la media y la desviación típica del camino que va a ser objeto del
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
# Cálculo de probabilidades       
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
# Cálculo de probabilidades para la simulación      
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
# Escribe en el TextView las probabilidades calculadas        
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
# Limpia los datos de la ventana de probabilidades 
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


# --- FUNCIONES DIALOGOS ABRIR, GUARDAR Y ADVERTENCIA/ERRORES #

   def abrir(self):
      """
      Abre un proyecto (con extensión '.prj' guardado)
      
      Debería abrir cualquier fichero desde una opción
      """
      # Close open project if any
      closed = self.closeProject()

      if closed:      
         # Open dialog asking for file to open
         dialogoFicheros = gtk.FileChooserDialog(gettext.gettext("Open File"),
                                                 None,
                                                 gtk.FILE_CHOOSER_ACTION_OPEN,
                                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK)
                                                 )
         filtro=gtk.FileFilter()
         filtro.add_pattern('*.prj')
         filtro.add_pattern('*.txt')
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
                  # Se cargan los datos del fichero 
                  tabla=[]
                  if self.directorio[-4:] == '.prj':  
                     tabla=pickle.load(flectura)
                     self.cargaDatos(tabla)
                  elif self.directorio[-3:] == '.sm':  
                     # Se lee el fichero y se extraen los datos necesarios 
                     prelaciones, rec, asig=leerPSPLIB(flectura)   
                     # Se cargan los datos extraidos en las listas correspondientes
                     self.cargarPSPLIB(prelaciones, rec, asig)       
                  else: # Fichero de texto
                     tabla=self.leerTxt(flectura)
                     self.cargarTxt(tabla)
                  response = True
                  flectura.close()
            except IOError :
                  self.dialogoError(gettext.gettext('The selected file does not exist'))
                  response = False
      
         elif resultado == gtk.RESPONSE_CANCEL:
            response = False

         dialogoFicheros.destroy()
         return (response) 


# --- DIÁLOGOS GUARDAR

   def guardar(self, saveAs=False):
      if saveAs or self.directorio==gettext.gettext('Unnamed -PPC-Project'):
         dialogoGuardar = gtk.FileChooserDialog(gettext.gettext("Save"),
                                                None,
                                                gtk.FILE_CHOOSER_ACTION_SAVE,
                                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
         dialogoGuardar.set_default_response(gtk.RESPONSE_OK)
         resultado = dialogoGuardar.run()

         if resultado == gtk.RESPONSE_OK:
            self.directorio=dialogoGuardar.get_filename()
            self.saveProject(self.directorio)
            self.asignarTitulo(self.directorio)
            self.set_modified(False)
            self.modified = 0

         dialogoGuardar.destroy() 
      else:
         self.saveProject(self.directorio)
         self.modified = 0
         
   def saveProject(self, nombre):
      """
      Saves a project in ppcproject format '.prj'
      """
      if nombre[-4:] != '.prj':
         nombre = nombre + '.prj'

      # Se guardan todos los datos en una lista y se escriben en el fichero  
      tabla=[]
      tabla.append(self.actividad)
      tabla.append(self.recurso)
      tabla.append(self.asignacion)
      try:
         fescritura=open(nombre,'w')
         pickle.dump(tabla, fescritura)
      except IOError :
         self.dialogoError(gettext.gettext('Error saving the file'))    
      fescritura.close()    
    

#********************************************************************************************************************  
#-----------------------------------------------------------
# Salva texto en formato CSV
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
         self.modelo.clear()
         self.actividad=[]
         self.modeloR.clear()
         self.recurso=[]
         self.modeloAR.clear()
         self.asignacion=[]
         self.vPrincipal.set_title(gettext.gettext('PPC-Project'))
         self.modified = 0
         self.gantt.clear()
         self.gantt.update()

      return close

#-----------------------------------------------------------
# Muestra un mensaje de advertencia si no se han
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

#-----------------------------------------------------------
# Muestra un mensaje de error en la apertura del fichero
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


#-----------------------------------------------------------
# Muestra un mensaje de error si en la introducción
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


#-----------------------------------------------------------
# Muestra un mensaje de error si en la ventana
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




# MANEJADORES #
# --- Menu actions

# File menu actions
   def on_New_activate(self, item):
      """ User ask for new file (from menu or toolbar) """
      self.introduccionDatos()
      self.enableProjectControls(True)
      self.set_modified(True)
      self.modified = 1

   def on_Open_activate(self, item):
      """ User ask for open file (from menu or toolbar) """
      if self.abrir():
         self.enableProjectControls(True)
         self.set_modified(False)
         self.modified = 0

   def  on_Save_activate(self, item):
        # Se comprueba que no haya actividades repetidas
        errorActRepetidas, actividadesRepetidas=self.actividadesRepetidas(self.actividad)
        if errorActRepetidas==0:
           self.guardar()
        # Si hay actividades repetidas, se muestra un mensaje de error
        else:
            #print actividadesRepetidas
            self.errorActividadesRepetidas(actividadesRepetidas) 

        self.modified=0
        self.set_modified(False)

   def on_mnGuardarComo_activate(self, menu_item):
        # Se comprueba que no haya actividades repetidas
        errorActRepetidas, actividadesRepetidas=self.actividadesRepetidas(self.actividad)
        if errorActRepetidas==0:
            self.guardar(saveAs=True)
             
        # Si hay actividades repetidas, se muestra un mensaje de error
        else:
            #print actividadesRepetidas
            self.errorActividadesRepetidas(actividadesRepetidas) 
       
        self.modified=0
        self.set_modified(False)

   def on_Close_activate(self, menu_item):
      if self.closeProject():
         self.enableProjectControls(False)

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
        if self.recurso==[]:
            self.modeloR.append()
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
         if a[6]=='' or a[7]=='':
               s+=1
               
      if s>0:
         self.dialogoError(gettext.gettext('There are uncomplete activities'))
      else:
         self.ventanaZaderenko()

   def on_mnHolguras_activate(self, menu_item):
      """ User ask for slacks """
      s=0
      for a in self.actividad:
         if a[6]=='' or a[7]=='':
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
      Returns: -
      """
      
      window.hide()
      return True
      
   def on_mnCOMSOAL_activate(self, menu_item):
      """ 
      User action to open the COMSOAL window
      
      Parameters: menu_item
      
      Returns: -
      """
      
      self.wndSimAnnealing.show()
      
   def on_btnSimAnnealingReset_clicked(self,menu_item):
      """ 
      User action to restart the values of the COMSOAL window fields
      
      Parameters: menu_item
      
      Returns: -
      """
      
      sbTemperature = self._widgets.get_widget('sbTempSA')
      Temperature = sbTemperature.set_value(10000)   
      sbMinTemperature = self._widgets.get_widget('sbMinTempSA')   
      minTemperature = sbMinTemperature.set_value(0.01) 
      sbK = self._widgets.get_widget('sbKSA')
      k = sbK.set_value(0.9)    
      sbNumIterations = self._widgets.get_widget('svMaxIterSA')
      numIterations = sbNumIterations.set_value(100)
      sbSlack = self._widgets.get_widget('sbSlackSA')
      slack = sbSlack.set_value(0)    
      
   
   def on_btnSimAnnealingCalculate_clicked(self, menu_item):
      """ 
      User action to start the COMSOAL algorithm
      
      Parameters: menu_item
      
      Returns: -
      """
      # Add all activities in rest dictionary
      rest={}
      for a in self.actividad:
         if a[6] == '':
            self.dialogoError(gettext.gettext('You must introduce the average duration.'))
            return False
         rest[a[1]] = [a[6]]
         
      asignation = resourcesPerActivities(self.asignacion)
      resources = resourcesAvailability(self.recurso)
      successors = self.tablaSucesoras(self.actividad)
      activities = self.alteredLast(rest)
      
      balRadioButton = self._widgets.get_widget('rbBalance')
      alloRadioButton = self._widgets.get_widget('rbAllocation')
      if balRadioButton.get_active():
         balance = 1
      else:
         balance = 0
      
      sbTemperature = self._widgets.get_widget('sbTempSA')
      Temperature = sbTemperature.get_value()   
      sbMinTemperature = self._widgets.get_widget('sbMinTempSA')   
      minTemperature = sbMinTemperature.get_value() 
      sbK = self._widgets.get_widget('sbKSA')
      k = sbK.get_value()    
      sbNumIterations = self._widgets.get_widget('svMaxIterSA')
      numIterations = sbNumIterations.get_value() 
      
      prog = simulatedAnnealing(asignation,resources,successors,activities,balance,Temperature,minTemperature,k,numIterations) 
      
      entryResult = self._widgets.get_widget('entryResult')
      entryResult.set_text(str(prog[1]))
      
   # Returns a dictionary with the activity's name like keys and duration and modified last time like definitions
   def alteredLast(self,rest):
      """ 
      Modify the last time of the activities with the slack introduced by the user
      
      Parameters: rest (activities in the project)
      
      Returns: rest (list of the activities and their characteristics)
      """
      # Se crea el grafo Pert y se renumera
      grafoRenumerado = self.pertFinal()

      # Nuevos nodos
      nodosN = []
      for n in range(len(grafoRenumerado.graph)):
         nodosN.append(n+1)

      # Se calcula la matriz de Zaderenko
      matrizZad = mZad(self.actividad,grafoRenumerado.activities, nodosN, 1, []) 

      # Se calculan los tiempos early y last
      tearly = early(nodosN, matrizZad)      
      tlast = last(nodosN, tearly, matrizZad)
      
      sbSlack = self._widgets.get_widget('sbSlackSA')
      slack = sbSlack.get_value()      
      # Calculate altered last time
      for a in grafoRenumerado.activities:
         if grafoRenumerado.activities[a][0] != 'dummy':
            rest[grafoRenumerado.activities[a][0]] += [tlast[a[1]-1] + slack - float(rest[grafoRenumerado.activities[a][0]][0])]
      
      return rest
      

#XXX XXX XXX XXX

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

#-----------------------------------------------------------
# Acción usuario para acceder aceptar los datos
#          que aparecen en la ventana de actividades
#
# Parámetros: boton (botón clickeado)
#
# Valor de retorno: -
#-----------------------------------------------------------  
   def on_btAceptarAct_clicked(self, boton):
        self.vActividades.hide()

#-----------------------------------------------------------
# Acción usuario para acceder cerrar la ventana de actividades
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  
   def on_wndActividades_delete_event(self, ventana, evento):
        ventana.hide()
        return True


# ZADERENKO window

#-----------------------------------------------------------
# Al seleccionar uno de los caminos del grafo que se muestran
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
# Acción usuario para acceder a la ventana que muestra
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
# Acción usuario para aceptar la información 
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
# Acción usuario para acceder a la ventana que muestra 
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
# Acción usuario para cerrar la ventana de Zaderenko
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


# HOLGURAS window

#-----------------------------------------------------------
# Acción usuario para aceptar la información 
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
# Acción usuario para acceder a la ventana de Zaderenko
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
# Acción usuario para cerrar la ventana de holguras
#
# Parámetros: ventana (ventana actual)
#             evento (evento cerrar)
#
# Valor de retorno: -
#-----------------------------------------------------------  
   def on_wndHolguras_delete_event(self, ventana, evento):
        ventana.hide()
        return True


# PROBABILIDADES window

   def on_btnIntervalReset_clicked(self, button):
      self._widgets.get_widget('valor1Prob').set_text("")
      self._widgets.get_widget('valor2Prob').set_text("")
      self._widgets.get_widget('resultado1Prob').set_text("")

#-----------------------------------------------------------
# Acción usuario al activar el valor introducido en 
#          el primer gtk.Entry de la ventana de probabilidades          
#
# Parámetros: entry (entry activado)
#
# Valor de retorno: -
#-----------------------------------------------------------  
   def on_bntIntervalCalculate_clicked(self, button):
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

   def on_btnProbabilityReset_clicked(self, button):
      self._widgets.get_widget('valor3Prob').set_text("")
      self._widgets.get_widget('resultado2Prob').set_text("")

#-----------------------------------------------------------
# Acción usuario al activar el valor introducido en 
#          el tercer gtk.Entry de la ventana de probabilidades          
#
# Parámetros: entry (entry activado)
#
# Valor de retorno: -
#-----------------------------------------------------------  
   def on_btnProbabilityCalculate_clicked(self, button):
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
# Acción usuario para aceptar la información que
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
# Acción usuario para cerrar la ventana de cálculo 
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



# --- Simulation window

   def on_btContinuarIterando_clicked(self, boton):
      """
      -

      Parámetros: boton (botón clickeado)

      Valor de retorno: -
      """
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
      self.guardarCsv(simulacionCsv)


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

   def on_btAceptarRec_clicked(self, boton):
      """
      Acción usuario para aceptar la información que
               muestra la ventana de recursos: nombre, tipo, unidad disponible 

      Parámetros: boton (botón clickeado)

      Valor de retorno: -
      """
      self.vRecursos.hide()
        
   def on_btCancelarRec_clicked(self, boton):
      """
      Acción usuario para cancelar la información que
               muestra la ventana de recursos: nombre, tipo, unidad disponible. 
               Si se cancelan los datos, se borran definitivamente

      Parámetros: boton (botón clickeado)

      Valor de retorno: -
      """
      if self.recurso==[]:
         self.modeloR.append()
      self.vRecursos.hide()

   def on_btAsignarRec_clicked(self, boton):
      """
      Acción usuario para acceder a la ventana de recursos
               necesarios por actividad 

      Parámetros: boton (botón clickeado)

      Valor de retorno: -
      """
      self.asignarRecursos()

      
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
      self.guardarCsv(pathsInCSV) 

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

# --- Start running as a program

if __name__ == '__main__':
   app = PPCproject()
   # Se crean todos los TreeViews

   if   len(sys.argv) == 1:
      gtk.main()   elif len(sys.argv) == 2:
      nombre = sys.argv[1]
      try:
         fichero = open(nombre, 'r')
         # Se asigna el nombre como título del proyecto
         app.directorio = nombre
         app.asignarTitulo(app.directorio)
         # Se cargan los datos en la lista 
         tabla = []             
         tabla = pickle.load(fichero)
         app.cargaDatos(tabla) 
         fichero.close()
         gtk.main()

      except IOError:
         print nombre, gettext.gettext('file does not exist')

   else:
      print gettext.gettext('Syntax is:')
      print sys.argv[0], '[project_file]'

