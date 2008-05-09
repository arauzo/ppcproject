#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Interface view
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

import pygtk
pygtk.require('2.0')
import gobject
import gtk
import gtk.glade

import GTKgantt
import loadingSheet
import loadingTable

# Internationalization
import gettext
APP='PPC-Project' #Program name
DIR='po' #Directory containing translations, usually /usr/share/locale
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
gtk.glade.bindtextdomain(APP, DIR)
gtk.glade.textdomain(APP)

class Interface:
   def __init__(self, parent_application):
      self._widgets = gtk.glade.XML('ppcproject.glade')



      self.parent_application = parent_application
      # Adding Gantt Diagram
      self.gantt = GTKgantt.GTKgantt()
      self._widgets.get_widget("hpnPanel").add2(self.gantt)
      self.gantt.set_vadjustment(self._widgets.get_widget("scrolledwindow10").get_vadjustment())
      self.gantt.show_all()
      self.crearTreeViews()
      
      # Obtaining the widget of allocation/balance window
      self.rbBalance = self._widgets.get_widget('rbBalance')
      self.btResetSA = self._widgets.get_widget ('btnSimAnnealingReset')
      self.entryResultSA = self._widgets.get_widget ('entryResult')
      self.entryAlpha = self._widgets.get_widget('entryAlpha')
      self.entryMaxTempSA = self._widgets.get_widget('entryMaxTempSA')
      self.cbIterationSA = self._widgets.get_widget('cbIterationSA')
      self.sbSlackSA = self._widgets.get_widget('sbSlackSA')
      self.sbPhi = self._widgets.get_widget('sbPhi')
      self.sbMu = self._widgets.get_widget('sbMu') 
      self.sbMinTempSA = self._widgets.get_widget('sbMinTempSA')   
      self.sbMaxIterationSA = self._widgets.get_widget('sbMaxIterationSA') 
      self.sbNoImproveIterSA = self._widgets.get_widget('sbNoImproveIterSA')
      self.sbExecuteTimesSA = self._widgets.get_widget('sbExecuteTimesSA')
      
      self.sbPhi.set_range(0.001,0.999)
      self.sbPhi.set_increments(0.001,0.01)
      self.sbPhi.set_value(0.9)
      self.sbMu.set_range(0.001,1)
      self.sbMu.set_increments(0.001,0.01)
      self.sbMu.set_value(0.9)
      self.sbMinTempSA.set_range(0.001,100)
      self.sbMinTempSA.set_increments(0.001,0.01)
      self.sbMinTempSA.set_value(0.1)
      
      hsbSA = self._widgets.get_widget('hsbSA')
      # Adding the loading sheet to simulated annealing window
      hbLoadingSheet = self._widgets.get_widget('hbox20')
      self.loadingSheet = loadingSheet.loadingSheet()
      self.loadingSheet.set_cell_width(20)
      hbLoadingSheet.pack_start(self.loadingSheet)
      self.loadingSheet.show_all()
      
      # Adding the loading table to simulated annealing window
      hbLoadingTable = self._widgets.get_widget('hbox31')
      self.loadingTable = loadingTable.loadingTable()
      self.loadingTable.set_cell_width(20)
      hbLoadingTable.pack_end(self.loadingTable)
      self.loadingTable.show_all()      
      
      # Adding Gantt Diagram to Simulated Annealing window
      fixedGanttSA = self._widgets.get_widget('hbox34')
      self.ganttSA = GTKgantt.GTKgantt()
      self.ganttSA.set_row_height(25)
      self.ganttSA.set_header_height(20)
      self.ganttSA.set_cell_width(20)
      self.ganttSA.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

      self.ganttSA.set_hadjustment(hsbSA.get_adjustment())
      self.loadingSheet.set_hadjustment(hsbSA.get_adjustment())
      self.loadingTable.set_hadjustment(hsbSA.get_adjustment())

      fixedGanttSA.pack_end(self.ganttSA)
      self.ganttSA.show_all()
      
      # Setting status message
      self._widgets.get_widget('stbStatus').push(0, gettext.gettext("No project file opened"))
      # Setting unsensitive GTKEntries
      self._widgets.get_widget('dTipicaSim').set_sensitive(False)
      self._widgets.get_widget('mediaSim').set_sensitive(False)
      self._widgets.get_widget('iteracionesTotales').set_sensitive(False)
      self._widgets.get_widget('mediaProb').set_sensitive(False)
      self._widgets.get_widget('dTipicaProb').set_sensitive(False)
      self._widgets.get_widget('resultado1Prob').set_sensitive(False)
      self._widgets.get_widget('resultado2Prob').set_sensitive(False)

#########  CREAMOS TODOS LOS TREEVIEWS DE LA APLICACIÓN  ##############
   def crearTreeViews(self):
      """
      Creación de todos los TreeViews que se utilizarán
          en la aplicación

      Parámetros: -

      Valor de retorno: -
      """
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
      self.vistaLista.columna[10].set_clickable(True)      self.vistaLista.columna[10].connect('clicked', self.parent_application.columna_press, self.menu) 
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
      
      # TREEVIEW for frequencies in simulation window
      self.vistaFrecuencias=self._widgets.get_widget('vistaFrecuencias')
      columns_type = [str]  * 21
      self.modeloF = gtk.ListStore(*columns_type)
      self.vistaFrecuencias.set_model(self.modeloF)
      #First column
      column = gtk.TreeViewColumn(gettext.gettext("Durations"))
      self.vistaFrecuencias.append_column(column)
      cell = gtk.CellRendererText()
      column.pack_start(cell, False)
      column.add_attribute(cell, 'text', 0)
      column.set_min_width(50)
      #Intervals
      for interval in range(1,21):
         column = gtk.TreeViewColumn("")
         self.vistaFrecuencias.append_column(column)
         cell = gtk.CellRendererText()
         column.pack_start(cell, False)
         column.add_attribute(cell, 'text', interval)
         column.set_min_width(50)

##################### FUNCIONES RELACIONADAS CON LOS TREEVIEW ###########################

   def columnaNoEditableColor(self, n):  
      """
       Creación de las columnas no editables y con color de celda
       Parámetros: n (columna)
       Valor de retorno: -
      """
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


   def columnaNoEditable(self, vista, n):
      """
       Creación de las columnas no editables y 
                sin color de celda 

       Parámetros: vista (widget que muestra el treeview)
                   n (columna)

       Valor de retorno: -
      """
      vista.renderer[n] = gtk.CellRendererText()
      vista.append_column(vista.columna[n])
      vista.columna[n].set_sort_column_id(n)
      vista.columna[n].pack_start(vista.renderer[n], True)
      vista.columna[n].set_attributes(vista.renderer[n], text=n)
      vista.columna[n].set_spacing(8)
      vista.columna[n].set_expand(True)
      vista.columna[n].set_reorderable(True)

#-----------------------------------------------------------                           
     
   def columnaEditable(self, vista, modelo, n):
      """
       Creación de las columnas editables y con color
                de celda

       Parámetros: vista (widget que muestra el treeview)
                   modelo (lista) 
                   n (columna)

       Valor de retorno: -
      """
      vista.renderer[n] = gtk.CellRendererText()
      vista.renderer[n].set_property('editable', True)
      vista.renderer[n].set_property('cell-background', 'lightGoldenRodYellow')
      vista.renderer[n].connect('edited', self.parent_application.col_edited_cb, modelo, n)
      vista.append_column(vista.columna[n])
      vista.columna[n].set_sort_column_id(n)
      vista.columna[n].pack_start(vista.renderer[n], True)
      vista.columna[n].set_attributes(vista.renderer[n], text=n)
      vista.columna[n].set_spacing(8)
      vista.columna[n].set_expand(True)
      vista.columna[n].set_resizable(True)
      vista.columna[n].set_reorderable(True)
      
     
   def columnaCombo(self, vista, modelo, n):
      """
       Creación de todas las columnas combo (selector)

       Parámetros: vista (widget que muestra el treeview)
                   modelo (lista) 
                   n (columna)

       Valor de retorno: modeloCombo (lista para los datos del selector)
      """
      modeloCombo=gtk.ListStore(str)
      vista.renderer[n]=gtk.CellRendererCombo()
      vista.renderer[n].set_property('editable', True)
      vista.renderer[n].connect('edited', self.parent_application.col_edited_cb, modelo, n)
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

