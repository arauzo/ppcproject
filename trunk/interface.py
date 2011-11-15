#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Interface view
-----------------------------------------------------------------------
 PPC-PROJECT
   Multiplatform software tool for education and research in 
   project management

 Copyright 2007-9 Universidad de Córdoba
 This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published
   by the Free Software Foundation, either version 3 of the License,
   or (at your option) any later version.
 This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os.path

import pygtk
pygtk.require('2.0')
import gobject
import gtk
import gtk.glade

import GTKgantt
import loadSheet
import loadTable
import simulation
import svgviewer

# Internationalization
#import gettext
#APP = 'PPC-Project' #Program name
#DIR = 'po' #Directory containing translations, usually /usr/share/locale
#gettext.bindtextdomain(APP, DIR)
#gettext.textdomain(APP)
#gtk.glade.bindtextdomain(APP, DIR)
#gtk.glade.textdomain(APP)

#XXX Felipe para dibujar el gráfico
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas

class Interface(object):
    __gsignals__ = {'gantt-width-changed' : (gobject.SIGNAL_RUN_FIRST, 
                                             gobject.TYPE_NONE,
                                             (gobject.TYPE_INT, ))}
   
    def __init__(self, parent_application, program_dir):
        """
        Initializes some interface things
        """
        self._widgets = gtk.glade.XML(os.path.join(program_dir, 'ppcproject.glade')) 
        self.parent_application = parent_application

        # Adding Gantt Diagram
        self.gantt = GTKgantt.GTKgantt()
        self._widgets.get_widget("hpnPanel").add2(self.gantt)
        self.gantt.set_vadjustment(self._widgets.get_widget("scrolledwindow10").get_vadjustment())
        self.gantt.show_all()

        self.crearTreeViews()
        self.create_simulation_treeviews()
          
        self._widgets.get_widget('bHerramientas1').show()
          
        # Obtaining the widget of allocation/leveling window
        self.rbLeveling = self._widgets.get_widget('rbLeveling')
        self.btResetSA = self._widgets.get_widget('btnSimAnnealingReset')
        self.btSaveSA = self._widgets.get_widget('btnSaveSA')
        self.entryResultSA = self._widgets.get_widget ('entryResult')
        self.entryAlpha = self._widgets.get_widget('entryAlpha')
        self.entryMaxTempSA = self._widgets.get_widget('entryMaxTempSA')
        self.entryIterations = self._widgets.get_widget('entryIterations')
        self.cbIterationSA = self._widgets.get_widget('cbIterationSA')
        self.sbSlackSA = self._widgets.get_widget('sbSlackSA')
        self.sbPhi = self._widgets.get_widget('sbPhi')
        self.sbNu = self._widgets.get_widget('sbNu') 
        self.sbMinTempSA = self._widgets.get_widget('sbMinTempSA')   
        self.sbMaxIterationSA = self._widgets.get_widget('sbMaxIterationSA') 
        self.sbNoImproveIterSA = self._widgets.get_widget('sbNoImproveIterSA')
        self.sbExecuteTimesSA = self._widgets.get_widget('sbExecuteTimesSA')
          
        self.ntbSchedule = self._widgets.get_widget('ntbSchedule')
        self.ntbSchedule.hide()
          
        gtk.window_set_default_icon_from_file(os.path.join(program_dir, 'ppcproject.svg'))
        self._widgets.get_widget('dAyuda').set_logo(self._widgets.get_widget('dAyuda').get_icon())
          
        self.sbPhi.set_range(0.001, 0.999)
        self.sbPhi.set_increments(0.001, 0.01)
        self.sbPhi.set_value(0.9)
        self.sbNu.set_range(0.001, 1)
        self.sbNu.set_increments(0.001, 0.01)
        self.sbNu.set_value(0.9)
        self.sbMinTempSA.set_range(0.001, 100)
        self.sbMinTempSA.set_increments(0.001, 0.01)
        self.sbMinTempSA.set_value(0.01)
          
        # Adding Gantt Diagram to Simulated Annealing window
        fixedGanttSA = self._widgets.get_widget('hbox19')
        self.ganttSA = GTKgantt.GTKgantt()
        self.ganttSA.set_row_height(25)
        self.ganttSA.set_header_height(20)
        self.ganttSA.set_cell_width(20)
        self.ganttSA.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        self.ganttSA.show_extra_row(False)
        hsbSA = self._widgets.get_widget('hsbSA')
        vsbGantt = self._widgets.get_widget('vsbGantt')
        vsbGantt.set_adjustment(self.ganttSA.diagram.get_vadjustment())
        hsbSA.set_adjustment(self.ganttSA.diagram.get_hadjustment())
        fixedGanttSA.pack_start(self.ganttSA)
        self.ganttSA.show_all()
          
        # Adding the loading sheet to simulated annealing window
        hbLoadSheet = self._widgets.get_widget('hbox37')
        self.loadSheet = loadSheet.LoadSheet()
        self.loadSheet.set_cell_width(20)
        hbLoadSheet.pack_start(self.loadSheet)
        self.loadSheet.set_hadjustment(hsbSA.get_adjustment())
        self.loadSheet.show_all()
        self.ganttSA.diagram.connect("gantt-width-changed", self.loadSheet.set_width)
        # Adding the loading table to simulated annealing window
        hbLoadTable = self._widgets.get_widget('hbox30')
        self.loadTable = loadTable.LoadTable()
        self.loadTable.set_cell_width(20)
        hbLoadTable.pack_end(self.loadTable)
        self.loadTable.set_hadjustment(hsbSA.get_adjustment())
        self.loadTable.show_all()      
        self.ganttSA.diagram.connect("gantt-width-changed", self.loadTable.set_width)

        # Setting status message
        self._widgets.get_widget('stbStatus').push(0, _("No project file opened"))
        # Setting unsensitive GTKEntries
        self._widgets.get_widget('dTipicaSim').set_sensitive(False)
        self._widgets.get_widget('mediaSim').set_sensitive(False)
        self._widgets.get_widget('iteracionesTotales').set_sensitive(False)
        self._widgets.get_widget('mediaProb').set_sensitive(False)
        self._widgets.get_widget('dTipicaProb').set_sensitive(False)
        self._widgets.get_widget('resultado1Prob').set_sensitive(False)
        self._widgets.get_widget('resultado2Prob').set_sensitive(False)


    def crearTreeViews(self):
        """
        Creación de todos los TreeViews que se utilizarán
          en la aplicación

        Parámetros: -

        Valor de retorno: -
        """
        # TreeView for main data table
        self.main_table_treeview = self._widgets.get_widget('vistaListaDatos')
        self.main_table_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        columns = [ _('#'),                   # 0
                    _('Activity'),            # 1
                    _('Following Act.'),      # 2
                    _('Optimistic Dur.'),     # 3
                    _('Most Probable Dur.'),  # 4
                    _('Pessimistic Dur.'),    # 5
                    _('Average Dur.'),        # 6
                    _('Typical Dev.'),        # 7
                    _('Resources'),           # 8
                    _('Distribution'),        # 9
                    _('Start Time'),          #10
                    _('End Time'),            #11
                    ]

        self.modelo = gtk.ListStore(int, str, str, str, str, str, str, str, str, str)
        # XXX Cambiado a float para evitar el problema de la carga
        # XXX Por que hay dos columnas mas de las que tiene el modelo, como estan manejadas??
        #self.modelo = gtk.ListStore(int, str, str, float, float, float, float, float, str, str)
        self.main_table_treeview.set_model(self.modelo)

        self.orden = gtk.TreeModelSort(self.modelo)
        #self.orden.set_sort_column_id(0,gtk.SORT_ASCENDING)

        # Create columns
        self.main_table_treeview.columna = []
        for column_name in columns:
            self.main_table_treeview.columna.append(gtk.TreeViewColumn(column_name))
        # XXX Las dos siguientes variables lista no deberian crearse dentro del objeto TreeView
        self.main_table_treeview.columna.append(gtk.TreeViewColumn()) # Menu column
        self.main_table_treeview.renderer = [None]*12 

        # Create column 0-# (id order number for task)
        self.main_table_treeview.renderer[0] = gtk.CellRendererText()
        self.main_table_treeview.renderer[0].set_property('editable', False)
        self.main_table_treeview.append_column(self.main_table_treeview.columna[0])
        #self.main_table_treeview.columna[0].set_sort_column_id(0)
        self.main_table_treeview.columna[0].pack_start(self.main_table_treeview.renderer[0], True)
        self.main_table_treeview.columna[0].set_attributes(self.main_table_treeview.renderer[0], text=0)
        self.main_table_treeview.columna[0].set_spacing(8)
        self.main_table_treeview.columna[0].set_resizable(False)
        self.main_table_treeview.columna[0].set_expand(False)

        self.columnaEditable(self.main_table_treeview, self.modelo, 1)
        self.modeloComboS = self.columnaCombo(self.main_table_treeview, self.modelo, 2)
        self.columnaEditable(self.main_table_treeview, self.modelo, 3)
        self.columnaEditable(self.main_table_treeview, self.modelo, 4)
        self.columnaEditable(self.main_table_treeview, self.modelo, 5)
        self.columnaEditable(self.main_table_treeview, self.modelo, 6)
        self.columnaEditable(self.main_table_treeview, self.modelo, 7)

        # Create column 8-Resources
        self.main_table_treeview.renderer[8] = gtk.CellRendererText()
        self.main_table_treeview.renderer[8].set_property('editable', False)
        self.main_table_treeview.append_column(self.main_table_treeview.columna[8])
        #self.main_table_treeview.columna[8].set_sort_column_id(8)
        self.main_table_treeview.columna[8].pack_start(self.main_table_treeview.renderer[8], True)
        self.main_table_treeview.columna[8].set_cell_data_func(self.main_table_treeview.renderer[8], self.resourcesRendererFunc)
        self.main_table_treeview.columna[8].set_spacing(8)
        self.main_table_treeview.columna[8].set_expand(True)
        self.main_table_treeview.columna[0].set_expand(False)
        self.main_table_treeview.columna[8].set_resizable(True)

        # Create column 9-Distribution
        self.modeloComboD = self.columnaCombo(self.main_table_treeview, self.modelo, 9, True)
        self.modeloComboD.append([_('Normal')])
        self.modeloComboD.append([_('Triangular')])
        self.modeloComboD.append([_('Beta')])
        self.modeloComboD.append([_('Uniform')])

        self.columnaEditable(self.main_table_treeview, self.modelo, 10, True)

        # Create column 11-End time
        self.main_table_treeview.renderer[11] = gtk.CellRendererText()
        self.main_table_treeview.renderer[11].set_property('editable', False)
        self.main_table_treeview.append_column(self.main_table_treeview.columna[11])
        #self.main_table_treeview.columna[11].set_sort_column_id(11)
        self.main_table_treeview.columna[11].pack_start(self.main_table_treeview.renderer[11], True)
        self.main_table_treeview.columna[11].set_cell_data_func(self.main_table_treeview.renderer[11],
                                                                self.endTimeRendererFunc)
        self.main_table_treeview.columna[11].set_spacing(8)
        self.main_table_treeview.columna[11].set_expand(True)
        self.main_table_treeview.columna[0].set_expand(False)
        self.main_table_treeview.columna[11].set_resizable(True)

        # Default visible or hidden columns
        self.main_table_treeview.columna[0].set_visible(True)
        self.main_table_treeview.columna[1].set_visible(True)
        self.main_table_treeview.columna[2].set_visible(True)
        self.main_table_treeview.columna[3].set_visible(True) 
        self.main_table_treeview.columna[4].set_visible(True)
        self.main_table_treeview.columna[5].set_visible(True)  
        self.main_table_treeview.columna[6].set_visible(True)  
        self.main_table_treeview.columna[7].set_visible(True)  
        self.main_table_treeview.columna[8].set_visible(False) 
        self.main_table_treeview.columna[9].set_visible(True) 
        self.main_table_treeview.columna[10].set_visible(True)  
        self.main_table_treeview.columna[11].set_visible(False) 

        # Menu column to make columns visible or hidden
        menu = gtk.Menu()
        self.imagen = gtk.image_new_from_stock(gtk.STOCK_PROPERTIES, gtk.ICON_SIZE_MENU)
        self.imagen.show()
        self.main_table_treeview.columna[12].set_widget(self.imagen)
        self.main_table_treeview.render = gtk.CellRendererText()
        self.main_table_treeview.append_column(self.main_table_treeview.columna[12])
        self.main_table_treeview.columna[12].pack_start(self.main_table_treeview.render, True)
        self.main_table_treeview.columna[12].set_attributes(self.main_table_treeview.render)
        self.main_table_treeview.columna[12].set_clickable(True)
        self.main_table_treeview.columna[12].connect('clicked', self.columna_press, menu) 
        self.main_table_treeview.columna[12].set_expand(False)

        # Create items for column menu
        for i in range(len(columns)):
            menu_item = gtk.CheckMenuItem(columns[i])
            menu.add(menu_item)
            active = self.main_table_treeview.columna[i].get_visible()
            menu_item.set_active(active)
            menu_item.connect('activate', self.activarItem, i)

        self.main_table_treeview.show_all() 


        # TREEVIEW para los caminos (ventana de ZADERENKO)
        self.vistaListaZ = self._widgets.get_widget('vistaListaZad')
        self.modeloZ = gtk.ListStore(str, str, str, bool)
        self.vistaListaZ.set_model(self.modeloZ)
        self.ordenZ = gtk.TreeModelSort(self.modeloZ)
        #self.ordenZ.set_sort_column_id(0,gtk.SORT_ASCENDING)
        self.vistaListaZ.columna = [None]*3
        self.vistaListaZ.columna[0] = gtk.TreeViewColumn(_('Duration'))
        self.vistaListaZ.columna[1] = gtk.TreeViewColumn(_('Typical Dev.'))
        self.vistaListaZ.columna[2] = gtk.TreeViewColumn(_('Path'))
        self.vistaListaZ.renderer = [None]*3

        self.columnaNoEditable(self.vistaListaZ, 0)
        self.columnaNoEditable(self.vistaListaZ, 1)
        self.columnaNoEditable(self.vistaListaZ, 2)

        for n in range(2):
            self.vistaListaZ.columna[n].set_expand(False)

                 
        # TREEVIEW para las ACTIVIDADES y NODOS
        self.vistaListaA = self._widgets.get_widget('vistaListaAct')
        self.modeloA = gtk.ListStore(str, str, str)
        self.vistaListaA.set_model(self.modeloA)
        self.ordenA = gtk.TreeModelSort(self.modeloA)
        #self.ordenA.set_sort_column_id(0,gtk.SORT_ASCENDING)
        self.vistaListaA.columna = [None]*3
        self.vistaListaA.columna[0] = gtk.TreeViewColumn(_('Activity'))
        self.vistaListaA.columna[1] = gtk.TreeViewColumn(_('First Node'))
        self.vistaListaA.columna[2] = gtk.TreeViewColumn(_('Last Node'))
        self.vistaListaA.renderer = [None]*3

        self.columnaNoEditable(self.vistaListaA, 0)
        self.columnaNoEditable(self.vistaListaA, 1)
        self.columnaNoEditable(self.vistaListaA, 2)


        # TREEVIEW para las HOLGURAS
        self.vistaListaH = self._widgets.get_widget('vistaListaHolg')
        self.modeloH = gtk.ListStore(str, str, str, str)
        self.vistaListaH.set_model(self.modeloH)
        self.ordenH = gtk.TreeModelSort(self.modeloH)
        #self.ordenH.set_sort_column_id(0,gtk.SORT_ASCENDING)
        self.vistaListaH.columna = [None]*4
        self.vistaListaH.columna[0] = gtk.TreeViewColumn(_('Activity'))
        self.vistaListaH.columna[1] = gtk.TreeViewColumn(_('Total Sl.'))
        self.vistaListaH.columna[2] = gtk.TreeViewColumn(_('Free Sl.'))
        self.vistaListaH.columna[3] = gtk.TreeViewColumn(_('Independent Sl.'))
        self.vistaListaH.renderer = [None]*4

        self.columnaNoEditable(self.vistaListaH, 0)
        self.columnaNoEditable(self.vistaListaH, 1)
        self.columnaNoEditable(self.vistaListaH, 2)
        self.columnaNoEditable(self.vistaListaH, 3)


        # TREEVIEW para los RECURSOS
        self.vistaListaR = self._widgets.get_widget('vistaListaRec')
        self.modeloR = gtk.ListStore(str, str, str, str)
        self.vistaListaR.set_model(self.modeloR)
        self.ordenR = gtk.TreeModelSort(self.modeloR)
        #self.ordenR.set_sort_column_id(0,gtk.SORT_ASCENDING)
        self.vistaListaR.columna = [None]*4
        self.vistaListaR.columna[0] = gtk.TreeViewColumn(_('Name'))
        self.vistaListaR.columna[1] = gtk.TreeViewColumn(_('Kind'))
        self.vistaListaR.columna[2] = gtk.TreeViewColumn(_('Project Available Units'))
        self.vistaListaR.columna[3] = gtk.TreeViewColumn(_('Period Available Units'))
        self.vistaListaR.renderer = [None]*4

        self.columnaEditable(self.vistaListaR, self.modeloR, 0)
        self.modeloComboR = self.columnaCombo(self.vistaListaR, self.modeloR, 1)
        self.columnaEditable(self.vistaListaR, self.modeloR, 2)
        self.columnaEditable(self.vistaListaR, self.modeloR, 3)

        # Se añaden los tipos de recursos
        self.modeloComboR.append([_('Renewable')])
        self.modeloComboR.append([_('Non renewable')])
        self.modeloComboR.append([_('Double constrained')])
        self.modeloComboR.append([_('Unlimited')])

        # TREEVIEW para los RECURSOS NECESARIOS POR ACTIVIDAD
        self.vistaListaAR = self._widgets.get_widget('vistaListaAR')
        self.modeloAR = gtk.ListStore(str, str, str)
        self.vistaListaAR.set_model(self.modeloAR)
        self.ordenAR = gtk.TreeModelSort(self.modeloAR)
        #self.ordenAR.set_sort_column_id(0,gtk.SORT_ASCENDING)
        self.vistaListaAR.columna = [None]*3
        self.vistaListaAR.columna[0] = gtk.TreeViewColumn(_('Activity'))
        self.vistaListaAR.columna[1] = gtk.TreeViewColumn(_('Resource'))
        self.vistaListaAR.columna[2] = gtk.TreeViewColumn(_('Needed Units'))
        self.vistaListaAR.renderer = [None]*3

        self.modeloComboARA = self.columnaCombo(self.vistaListaAR, self.modeloAR, 0)
        self.modeloComboARR = self.columnaCombo(self.vistaListaAR, self.modeloAR, 1)
        self.columnaEditable(self.vistaListaAR, self.modeloAR, 2)

    def columna_press(self, columna, menu): 
        """
        Show column menu when last column pressed
  
         columna (columna presionada)
         menu (gtk.Menu)
        """
        menu.show_all()
        menu.popup(None, None, None, 1, 0)
   
   
    def activarItem(self, item, n):
        """
         Activación o desactivación de las columnas según el item 
                  seleccionado en el menu
  
         Parámetros: item (item seleccionado)
                     n (posición en el menu del item seleccionado)
        """
        if item.get_active():
            self.main_table_treeview.columna[n].set_visible(True)
        else:
            self.main_table_treeview.columna[n].set_visible(False)


    def create_simulation_treeviews(self):
        """
        Create TreeViews for simulation window
        """
        # TreeView for paths
        self.vLCriticidad = self._widgets.get_widget('vistaListaCriticidad')
        self.modeloC = gtk.ListStore(str, str, str)
        self.vLCriticidad.set_model(self.modeloC)
        self.ordenC = gtk.TreeModelSort(self.modeloC)
        #self.ordenC.set_sort_column_id(0,gtk.SORT_ASCENDING)
        self.vLCriticidad.columna = [None]*3
        self.vLCriticidad.columna[0] = gtk.TreeViewColumn(_('N'))
        self.vLCriticidad.columna[1] = gtk.TreeViewColumn(_('Criticality Int.'))
        self.vLCriticidad.columna[2] = gtk.TreeViewColumn(_('Paths'))
        self.vLCriticidad.renderer = [None]*3
          
        self.columnaNoEditable(self.vLCriticidad, 0)
        self.columnaNoEditable(self.vLCriticidad, 1)
        self.columnaNoEditable(self.vLCriticidad, 2)

        for n in range(2):
            self.vLCriticidad.columna[n].set_expand(False)
          
        

    def update_frecuency_intervals_treeview (self, n, durations, itTotales):
        # Se calculan los intervalos
        interv = [] # Column interval titles
        iOpcion = self._widgets.get_widget('iOpcion')
        opcion = iOpcion.get_active_text()
        iValor = self._widgets.get_widget('iValor') # Número de intervalos
        dmax = float(max(durations)+0.00001)  # duración máxima
        dmin = float(min(durations))   # duración mí­nima
        valor_i = float(iValor.get_text())

        #n = simulation.nIntervalos(dmax, dmin, valor, str(opcion)) # XXX Felipe habia 20
        #pruebaInterface.create_simulation_treeviews2(self, int(N))
        #print dMax, 'max', dMin, 'min'
        
        if opcion == 'Numero de intervalos':
            for ni in range(n):
                valor = '['+str('%5.2f'%(simulation.duracion(ni, dmax, dmin, n)))+', '+str('%5.2f'%(simulation.duracion((ni+1), dmax, dmin, n)))+'['       
                interv.append(valor)
        elif opcion == 'Tamanio del intervalo':
            mini = dmin - (dmin % valor_i)
            for ni in range(n):
                valor = '['+str(mini)+', '+str(mini + valor_i)+'['
                mini = mini + valor_i
                interv.append(valor)
  
        # TreeView for frequencies
        self.vistaFrecuencias = self._widgets.get_widget('vistaFrecuencias')
        # - Clean old columns
        for col in self.vistaFrecuencias.get_columns():
            self.vistaFrecuencias.remove_column(col)

        # - First column
        column = gtk.TreeViewColumn(_("Durations"))
        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, 'text', 0)
        column.set_min_width(50)
        self.vistaFrecuencias.append_column(column)

        # - Interval columns
        for interval in range(n):
            column = gtk.TreeViewColumn(interv[interval])
            cell = gtk.CellRendererText()
            column.pack_start(cell, False)
            column.add_attribute(cell, 'text', interval+1) # Duration is column 0
            column.set_min_width(50)
            self.vistaFrecuencias.append_column(column)

        # - Set model
        columns_type = [str] * (n+1) # Duration col + n interval cols
        self.modeloF = gtk.ListStore(*columns_type)
        self.vistaFrecuencias.set_model(self.modeloF)

        Fa, Fr = self.update_frecuency_values(dmax, dmin, n, durations, itTotales)
        return interv, Fa, Fr #XXX Felipe antes no estaba

    def update_frecuency_values(self, dmax, dmin, n, durations, itTotales):
    
        # Se calculan las frecuencias
        Fa, Fr = simulation.calcularFrecuencias(durations, dmax, dmin, itTotales, n)
  
        print len(Fa), len(Fr)
        self.modeloF.append([_("Absolute freq.")] + map(str, Fa))
        self.modeloF.append([_("Relative freq.")] + map(str, Fr))
        #self.mostrarFrecuencias(self.intervalos, self.Fa, Fr)
  
        # Dibuja histograma devolviendo los intervalos (bins) y otros datos
        fig = Figure(figsize=(5,4), dpi=100)
        ax = fig.add_subplot(111)
        hBoxSim = self._widgets.get_widget('hbSim') #XXX Felipe
        n, bins, patches = ax.hist(durations, n, normed=1)
        canvas = FigureCanvas(fig)  # a gtk.DrawingArea
        boxS = gtk.VBox()
        print 'Longitud del boxS', len(boxS), '\n'
        if len(boxS)>0: # Si ya hay introducido un box, que lo borre y lo vuelva a añadir
            hBoxSim.remove(boxS)
            boxS = gtk.VBox()

        hBoxSim.add(boxS)
        boxS.pack_start(canvas)
        boxS.show_all()
        return Fa, Fr
        


### FUNCIONES RELACIONADAS CON LOS TREEVIEW

    def resourcesRendererFunc(self, treeviewcolumn, cell_renderer, model, iter):
        """
        Function called by the "Resources" column when its content needs to be shown 

        Parameters: treeviewcolumn: resources column.
                   cell_renderer: cell renderer
                   model: activities model.
                   iter: row pointer.
        """
        activity = model.get_value(iter, 1)
        text = ""
        if activity != "":
            for row in self.modeloAR:
                if row[0] == activity:
                    try:
                        text += row[1] + ": " + row[2] + "; "
                    except:
                        pass
        cell_renderer.set_property('text', text)
        return

    def endTimeRendererFunc(self, treeviewcolumn, cell_renderer, model, iter):
        """
        Function called by the "End Time" column when its content needs to be shown 

        Parameters: treeviewcolumn: end time column.
                   cell_renderer: cell renderer
                   model: activities model.
                   iter: row pointer.

        Return value: -
        """
        start = model.get_value(iter, 9)
        duration = model.get_value(iter, 6)
        if start == "" and duration == "":
            cell_renderer.set_property('text', "")
        else:
            try:
                start = float(start)
            except:
                start = 0
            try:
                duration = float(duration)
            except:
                duration = 0
            cell_renderer.set_property('text', str(start + duration))
        return

    def columnaNoEditable(self, vista, n):
        """
        Create a non-editable column without cell color

         vista (widget que muestra el treeview)
         n (columna)
        """
        vista.renderer[n] = gtk.CellRendererText()
        vista.append_column(vista.columna[n])
        #vista.columna[n].set_sort_column_id(n)
        vista.columna[n].pack_start(vista.renderer[n], True)
        vista.columna[n].set_attributes(vista.renderer[n], text=n)
        vista.columna[n].set_spacing(8)
        vista.columna[n].set_expand(True)
        #vista.columna[n].set_reorderable(True)

    def columnaEditable(self, vista, modelo, n, offset=False):
        """
        Create an editable column with cell color

         vista (widget que muestra el treeview)
         modelo (lista) 
         n (columna)
        """
        vista.renderer[n] = gtk.CellRendererText()
        vista.renderer[n].set_property('editable', True)
        vista.renderer[n].connect('edited', self.parent_application.col_edited_cb, modelo, (n - 1 if offset else n))
        vista.append_column(vista.columna[n])
        #vista.columna[n].set_sort_column_id(n)
        vista.columna[n].pack_start(vista.renderer[n], True)
        vista.columna[n].set_attributes(vista.renderer[n], text=(n - 1 if offset else n))
        vista.columna[n].set_spacing(8)
        vista.columna[n].set_expand(True)
        vista.columna[n].set_resizable(True)
        #vista.columna[n].set_reorderable(True)
      
    def columnaCombo(self, vista, modelo, n, offset=False):
        """
        Create a combo column for a treeview

         vista (widget que muestra el treeview)
         modelo (lista) 
         n (columna)

        Return: modeloCombo (lista para los datos del selector)
        """
        modeloCombo = gtk.ListStore(str)
        vista.renderer[n] = gtk.CellRendererCombo()
        vista.renderer[n].set_property('editable', True)
        vista.renderer[n].connect('edited', self.parent_application.col_edited_cb, modelo, (n - 1 if offset else n))
        vista.renderer[n].set_property('model', modeloCombo)
        #vista.renderer[n].set_property('has-entry', False)
        vista.renderer[n].set_property('text-column', 0)
        vista.append_column(vista.columna[n])
        #vista.columna[n].set_sort_column_id(n)
        vista.columna[n].pack_start(vista.renderer[n], True)
        vista.columna[n].set_attributes(vista.renderer[n], text=(n - 1 if offset else n))
        vista.columna[n].set_resizable(True)
        #vista.columna[n].set_min_width(150)

        return modeloCombo


class GraphWindow(object):
    """
    Shows a window with a graphical representation of a graph and a save button to export the data to a SVG file
    """

    def __init__(self, svg_text, title):
        """
        Create the GTK window
        """
        self.svg_text = svg_text

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_default_size(800, 600)
        self.window.set_title(title)
        self.window.connect("delete_event", self.delete_event)

        # Use SVGViewer to display graph (with zoom)
        self.svg_viewer = svgviewer.SVGViewer(svg_text)

        screen = gtk.ScrolledWindow()
        screen.add_with_viewport(self.svg_viewer)

        self.button = gtk.Button("Save")
        self.button.connect("clicked", self.on_button_save_clicked, None)

        h_box = gtk.HBox(homogeneous=False, spacing=0)
        h_box.pack_start(self.button,    expand=False, fill=False, padding=4)

        v_box = gtk.VBox(homogeneous=False, spacing=0)
        v_box.pack_start(screen, expand=True,  fill=True,  padding=0)
        v_box.pack_start(h_box,   expand=False, fill=False, padding=4)

        self.window.add(v_box)
        self.window.show_all()

    def delete_event(self, widget, event, data=None):
        """ Close window """
        return False

    def on_button_save_clicked(self, button, data=None):
        """
        Save Pert graph image
        """
        finish = False
        while not finish:
            destination_dialog = gtk.FileChooserDialog(_("Save Image"),
                                                   None,
                                                   gtk.FILE_CHOOSER_ACTION_SAVE,
                                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_SAVE, gtk.RESPONSE_OK))
            destination_dialog.set_default_response(gtk.RESPONSE_OK)
            resultado = destination_dialog.run()

            if resultado == gtk.RESPONSE_OK:
                try:
                    filename = destination_dialog.get_filename()
                    filename = filename if filename[-4:] == ".svg" else filename + ".svg"
                    svg_file = open(filename, "wb")
                    svg_file.write(self.svg_text)
                    svg_file.close()
                    finish = True
                except IOError:
                    dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                                               message_format='Error trying to write ' + filename,
                                               buttons=gtk.BUTTONS_OK)
                    dialog.run()
                    dialog.destroy()   
                finally:
                    destination_dialog.destroy()
                
            else:
                destination_dialog.destroy()
                finish = True

