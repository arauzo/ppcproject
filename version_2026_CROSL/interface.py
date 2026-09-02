#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface view - PPC-PROJECT
Adaptacion a Python 3 / GTK 3 para TFG
"""

import os.path
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk

import GTKgantt
import loadSheet
import loadTable
import simulation
import svgviewer

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas


class GraphWindow(Gtk.Window):
    def __init__(self, svg_text, title='Graph'):
        super(GraphWindow, self).__init__(title=title)
        self.set_default_size(900, 650)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.viewer = svgviewer.SVGViewer(svg_text)
        scrolled.add(self.viewer)
        self.add(scrolled)

        self.connect('destroy', self._on_destroy)
        self.show_all()

    def _on_destroy(self, *args):
        return False


class _BuilderAdapter(object):
    def __init__(self, builder):
        self._builder = builder

    def get_widget(self, name):
        return self._builder.get_object(name)

    def signal_autoconnect(self, owner):
        self._builder.connect_signals(owner)


class Interface(GObject.Object):
    __gsignals__ = {
        'gantt-width-changed': (GObject.SignalFlags.RUN_FIRST, None, (int,))
    }

    def __init__(self, parent_application, program_dir):
        super(Interface, self).__init__()

        self.parent_application = parent_application
        self.builder = Gtk.Builder()
        self._widgets = _BuilderAdapter(self.builder)

        glade_path = os.path.join(program_dir, 'ppcproject.glade')
        try:
            self.builder.add_from_file(glade_path)
        except Exception as e:
            raise RuntimeError(f"Error cargando glade '{glade_path}': {e}") from e

        # Inicializamos modelos que pueden ser usados por renderers
        self.modeloAR = Gtk.ListStore(str, str, str)
        self.modeloA = Gtk.ListStore(str, str, str)
        self.modeloComboS = Gtk.ListStore(str)
        self.modeloComboARA = Gtk.ListStore(str)
        self.modeloComboARR = Gtk.ListStore(str)

        # --- DIAGRAMA DE GANTT PRINCIPAL ---
        self.gantt = GTKgantt.GTKgantt()

        hpn_panel = self.builder.get_object("hpnPanel")
        if hpn_panel is None:
            raise RuntimeError("No se encontro el widget 'hpnPanel' en el archivo Glade.")

        hpn_panel.pack2(self.gantt, True, True)

        scrolledwindow10 = self.builder.get_object("scrolledwindow10")
        if scrolledwindow10 is None:
            raise RuntimeError("No se encontro el widget 'scrolledwindow10' en el archivo Glade.")

        scroll_v = scrolledwindow10.get_vadjustment()
        self.gantt.set_vadjustment(scroll_v)
        self.gantt.show_all()

        # Inicializacion de tablas
        self.crearTreeViews()
        self.create_simulation_treeviews()

        toolbar = self.builder.get_object('bHerramientas1')
        if toolbar is not None:
            toolbar.show()

        # --- OBTENCION DE WIDGETS (Simulated Annealing) ---
        self.rbLeveling = self.builder.get_object('rbLeveling')
        self.btResetSA = self.builder.get_object('btnSimAnnealingReset')
        self.btSaveSA = self.builder.get_object('btnSaveSA')
        self.entryResultSA = self.builder.get_object('entryResult')
        self.entryAlpha = self.builder.get_object('entryAlpha')
        self.entryMaxTempSA = self.builder.get_object('entryMaxTempSA')
        self.entryIterations = self.builder.get_object('entryIterations')
        self.cbIterationSA = self.builder.get_object('cbIterationSA')
        self.sbSlackSA = self.builder.get_object('sbSlackSA')
        self.sbPhi = self.builder.get_object('sbPhi')
        self.sbNu = self.builder.get_object('sbNu')
        self.sbMinTempSA = self.builder.get_object('sbMinTempSA')
        self.sbMaxIterationSA = self.builder.get_object('sbMaxIterationSA')
        self.sbNoImproveIterSA = self.builder.get_object('sbNoImproveIterSA')
        self.sbExecuteTimesSA = self.builder.get_object('sbExecuteTimesSA')

        self.ntbSchedule = self.builder.get_object('ntbSchedule')
        if self.ntbSchedule is not None:
            self.ntbSchedule.hide()

        # Configuracion de rangos (SpinButtons)
        if self.sbPhi is not None:
            self.sbPhi.set_range(0.001, 0.999)
            self.sbPhi.set_increments(0.001, 0.01)
            self.sbPhi.set_value(0.9)

        if self.sbNu is not None:
            self.sbNu.set_range(0.001, 1)
            self.sbNu.set_increments(0.001, 0.01)
            self.sbNu.set_value(0.9)

        if self.sbMinTempSA is not None:
            self.sbMinTempSA.set_range(0.001, 100)
            self.sbMinTempSA.set_increments(0.001, 0.01)
            self.sbMinTempSA.set_value(0.01)

        # --- GANTT PARA VENTANA DE SA ---
        fixedGanttSA = self.builder.get_object('hbox19')
        if fixedGanttSA is None:
            raise RuntimeError("No se encontro el widget 'hbox19' en el archivo Glade.")

        self.ganttSA = GTKgantt.GTKgantt()
        self.ganttSA.set_row_height(25)
        self.ganttSA.set_header_height(20)
        self.ganttSA.set_cell_width(20)

        hsbSA = self.builder.get_object('hsbSA')
        vsbGantt = self.builder.get_object('vsbGantt')

        if hsbSA is None or vsbGantt is None:
            raise RuntimeError("No se encontraron 'hsbSA' o 'vsbGantt' en el archivo Glade.")

        vsbGantt.set_adjustment(self.ganttSA.diagram.get_vadjustment())
        hsbSA.set_adjustment(self.ganttSA.diagram.get_hadjustment())
        fixedGanttSA.pack_start(self.ganttSA, True, True, 0)
        self.ganttSA.show_all()

        # --- LOADING SHEET / TABLE ---
        hbLoadSheet = self.builder.get_object('hbox37')
        if hbLoadSheet is None:
            raise RuntimeError("No se encontro el widget 'hbox37' en el archivo Glade.")

        self.loadSheet = loadSheet.LoadSheet()
        self.loadSheet.set_cell_width(20)
        hbLoadSheet.pack_start(self.loadSheet, True, True, 0)
        self.loadSheet.set_hadjustment(hsbSA.get_adjustment())
        self.loadSheet.show_all()

        self.ganttSA.diagram.connect("gantt-width-changed", self.on_gantt_width_changed)

        hbLoadTable = self.builder.get_object('hbox30')
        if hbLoadTable is None:
            raise RuntimeError("No se encontro el widget 'hbox30' en el archivo Glade.")

        self.loadTable = loadTable.LoadTable()
        self.loadTable.set_cell_width(20)
        hbLoadTable.pack_end(self.loadTable, True, True, 0)
        self.loadTable.set_hadjustment(hsbSA.get_adjustment())
        self.loadTable.show_all()
        self.ganttSA.diagram.connect("gantt-width-changed", self.on_gantt_width_changed_table)

        # Status y entradas iniciales
        statusbar = self.builder.get_object('stbStatus')
        if statusbar is not None:
            statusbar.push(0, "No project file opened")

        for w in [
            'dTipicaSim', 'mediaSim', 'iteracionesTotales', 'mediaProb',
            'dTipicaProb', 'resultado1Prob', 'resultado2Prob'
        ]:
            widget = self.builder.get_object(w)
            if widget is not None:
                widget.set_sensitive(False)

    def on_gantt_width_changed(self, widget, width):
        self.loadSheet.set_width(widget, width)

    def on_gantt_width_changed_table(self, widget, width):
        self.loadTable.set_width(widget, width)

    def crearTreeViews(self):
        """Creacion de todos los TreeViews con Gtk.ListStore."""
        self.main_table_treeview = self.builder.get_object('vistaListaDatos')
        if self.main_table_treeview is None:
            raise RuntimeError("No se encontro el widget 'vistaListaDatos' en el archivo Glade.")

        self.main_table_treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        columns_titles = [
            '#', 'Activity', 'Previous Act.', 'Optimistic Dur.',
            'Most Probable Dur.', 'Pessimistic Dur.', 'Average Dur.',
            'Typical Dev.', 'Resources', 'Distribution', 'Start Time', 'End Time'
        ]

        self.modelo = Gtk.ListStore(
            int,   # #
            str,   # Activity
            str,   # Following Act.
            str,   # Optimistic Dur.
            str,   # Most Probable Dur.
            str,   # Pessimistic Dur.
            str,   # Average Dur.
            str,   # Typical Dev.
            str,   # Distribution
            str,   # Start Time
        )

        self.main_table_treeview.set_model(self.modelo)

        self.main_table_treeview.cols = []
        for title in columns_titles:
            self.main_table_treeview.cols.append(Gtk.TreeViewColumn(title))

        renderer0 = Gtk.CellRendererText()
        col0 = self.main_table_treeview.cols[0]
        col0.pack_start(renderer0, True)
        col0.add_attribute(renderer0, "text", 0)
        self.main_table_treeview.append_column(col0)

        for i in range(1, 8):
            self.columnaEditable(self.main_table_treeview, self.modelo, i)

        self.main_table_treeview.columna = self.main_table_treeview.get_columns()

        renderer8 = Gtk.CellRendererText()
        col8 = self.main_table_treeview.cols[8]
        col8.pack_start(renderer8, True)
        col8.set_cell_data_func(renderer8, self.resourcesRendererFunc)
        self.main_table_treeview.append_column(col8)

        self.modeloComboD = self.columnaCombo(self.main_table_treeview, self.modelo, 9, offset=True)
        for dist in ['Normal', 'Triangular', 'Beta', 'Uniform']:
            self.modeloComboD.append([dist])

        self.columnaEditable(self.main_table_treeview, self.modelo, 10, offset=True)

        renderer11 = Gtk.CellRendererText()
        col11 = self.main_table_treeview.cols[11]
        col11.pack_start(renderer11, True)
        col11.set_cell_data_func(renderer11, self.endTimeRendererFunc)
        self.main_table_treeview.append_column(col11)

        self.vistaListaZ = self.builder.get_object('vistaListaZad')
        if self.vistaListaZ is not None:
            self.modeloZ = Gtk.ListStore(str, str, str, bool)
            self.vistaListaZ.set_model(self.modeloZ)
            self.columnaNoEditable(self.vistaListaZ, 0, "Duration")
            self.columnaNoEditable(self.vistaListaZ, 1, "Typical Dev.")
            self.columnaNoEditable(self.vistaListaZ, 2, "Path")

        self.vistaListaH = self.builder.get_object('vistaListaHolg')
        if self.vistaListaH is not None:
            self.modeloH = Gtk.ListStore(str, str, str, str)
            self.vistaListaH.set_model(self.modeloH)
            titles_h = ["Activity", "Total Sl.", "Free Sl.", "Independent Sl."]
            for i, title in enumerate(titles_h):
                self.columnaNoEditable(self.vistaListaH, i, title)

        self.vistaListaAR = self.builder.get_object('vistaListaAR')
        if self.vistaListaAR is not None:
            self.vistaListaAR.set_model(self.modeloAR)
            self.vistaListaAR.cols = []
            for title in ['Activity', 'Resource', 'Needed Units']:
                self.vistaListaAR.cols.append(Gtk.TreeViewColumn(title))
            self.columnaComboConModelo(self.vistaListaAR, self.modeloAR, 0, self.modeloComboARA)
            self.columnaComboConModelo(self.vistaListaAR, self.modeloAR, 1, self.modeloComboARR)
            self.columnaEditable(self.vistaListaAR, self.modeloAR, 2)

        self.vistaListaR = self.builder.get_object('vistaListaRec')
        if self.vistaListaR is not None:
            self.modeloR = Gtk.ListStore(str, str, str, str)
            self.vistaListaR.set_model(self.modeloR)
            self.vistaListaR.cols = []
            for title in ['Resource', 'Type', 'Units/Period', 'Units/Project']:
                self.vistaListaR.cols.append(Gtk.TreeViewColumn(title))
            self.columnaEditable(self.vistaListaR, self.modeloR, 0)
            self.modeloComboR = self.columnaCombo(self.vistaListaR, self.modeloR, 1)
            for r_type in ['Renewable', 'Non renewable', 'Double constrained', 'Unlimited']:
                self.modeloComboR.append([r_type])
            self.columnaEditable(self.vistaListaR, self.modeloR, 2)
            self.columnaEditable(self.vistaListaR, self.modeloR, 3)

        self.main_table_treeview.show_all()
        
    def update_frecuency_intervals_treeview(self, n, durations, itTotales):
        """
        Upgrade Treeview for frecuency intervals
        """
        interv = []

        iOpcion = self._widgets.get_widget('iOpcion')
        opcion = iOpcion.get_active_text()

        iValor = self._widgets.get_widget('iValor')
        dmax = float(max(durations) + 0.00001)
        dmin = float(min(durations))
        valor_i = float(iValor.get_text())

        if opcion == 'Number of intervals':
            for ni in range(n):
                valor = (
                    '['
                    + str('%5.2f' % (simulation.duracion(ni, dmax, dmin, n)))
                    + ', '
                    + str('%5.2f' % (simulation.duracion((ni + 1), dmax, dmin, n)))
                    + '['
                )
                interv.append(valor)

        elif opcion == 'Size range':
            mini = dmin - (dmin % valor_i)
            for ni in range(n):
                valor = '[' + str(mini) + ', ' + str(mini + valor_i) + '['
                mini = mini + valor_i
                interv.append(valor)

        self.vistaFrecuencias = self._widgets.get_widget('vistaFrecuencias')

        for col in self.vistaFrecuencias.get_columns():
            self.vistaFrecuencias.remove_column(col)

        column = Gtk.TreeViewColumn(_("Durations"))
        cell = Gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, 'text', 0)
        column.set_min_width(50)
        self.vistaFrecuencias.append_column(column)

        for interval in range(n):
            column = Gtk.TreeViewColumn(interv[interval])
            cell = Gtk.CellRendererText()
            column.pack_start(cell, False)
            column.add_attribute(cell, 'text', interval + 1)
            column.set_min_width(50)
            self.vistaFrecuencias.append_column(column)

        columns_type = [str] * (n + 1)
        self.modeloF = Gtk.ListStore(*columns_type)
        self.vistaFrecuencias.set_model(self.modeloF)

        Fa, Fr = self.update_frecuency_values(dmax, dmin, n, durations, itTotales)
        return interv, Fa, Fr
        
    def update_frecuency_values(self, dmax, dmin, n, durations, itTotales):
        """
        Calcula y muestra las frecuencias absolutas y relativas.
        """
        Fa, Fr = simulation.calcularFrecuencias(durations, dmax, dmin, itTotales, n)

        self.modeloF.append([_("Absolute freq.")] + [str(x) for x in Fa])
        self.modeloF.append([_("Relative freq.")] + [str(x) for x in Fr])

        return Fa, Fr



    def columnaEditable(self, vista, modelo, n, offset=False):
        renderer = Gtk.CellRendererText()
        renderer.set_property('editable', True)
        idx = (n - 1 if offset else n)
        renderer.connect('edited', self.parent_application.col_edited_cb, modelo, idx)

        column = vista.cols[n] if hasattr(vista, 'cols') and n < len(vista.cols) else Gtk.TreeViewColumn(f"Col {n}")
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "text", idx)
        vista.append_column(column)

    def columnaNoEditable(self, vista, n, title):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=n)
        vista.append_column(column)

    def columnaCombo(self, vista, modelo, n, offset=False):
        modeloCombo = Gtk.ListStore(str)
        renderer = Gtk.CellRendererCombo()
        renderer.set_property('editable', True)
        renderer.set_property('model', modeloCombo)
        renderer.set_property('text-column', 0)
        renderer.set_property('has-entry', False)

        idx = (n - 1 if offset else n)
        renderer.connect('edited', self.parent_application.col_edited_cb, modelo, idx)

        column = vista.cols[n] if hasattr(vista, 'cols') else Gtk.TreeViewColumn("Combo")
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "text", idx)
        vista.append_column(column)
        return modeloCombo

    def columnaComboConModelo(self, vista, modelo, n, modeloCombo, offset=False):
        renderer = Gtk.CellRendererCombo()
        renderer.set_property('editable', True)
        renderer.set_property('model', modeloCombo)
        renderer.set_property('text-column', 0)
        renderer.set_property('has-entry', False)
        idx = n + 1 if offset else n
        renderer.connect('edited', self.parent_application.col_edited_cb, modelo, idx)
        column = vista.cols[n] if hasattr(vista, 'cols') else Gtk.TreeViewColumn("Combo")
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "text", idx)
        vista.append_column(column)
        return modeloCombo

    def resourcesRendererFunc(self, column, cell, model, tree_iter, data):
        activity = model.get_value(tree_iter, 1)
        text = ""
        if activity:
            for row in self.modeloAR:
                if row[0] == activity:
                    text += f"{row[1]}: {row[2]}; "
        cell.set_property('text', text)

    def endTimeRendererFunc(self, column, cell, model, tree_iter, data):
        try:
            start = float(model.get_value(tree_iter, 9) or 0)
            duration = float(model.get_value(tree_iter, 6) or 0)
            cell.set_property('text', str(start + duration))
        except Exception:
            cell.set_property('text', "")

    def create_simulation_treeviews(self):
        self.vLCriticidad = self.builder.get_object('vistaListaCriticidad')
        if self.vLCriticidad is None:
            return

        self.modeloC = Gtk.ListStore(str, str, str)
        self.vLCriticidad.set_model(self.modeloC)
        self.columnaNoEditable(self.vLCriticidad, 0, "N")
        self.columnaNoEditable(self.vLCriticidad, 1, "Criticality Int.")
        self.columnaNoEditable(self.vLCriticidad, 2, "Paths")

    def show(self):
        self.main_window = self.builder.get_object('wndPrincipal')
        if self.main_window:
            self.main_window.connect("destroy", Gtk.main_quit)
            self.main_window.show_all()
        else:
            raise RuntimeError("No se encontro la ventana 'wndPrincipal' en el archivo Glade.")


if __name__ == "__main__":
    import sys

    class DummyApp:
        def col_edited_cb(self, *args):
            pass

        def on_gantt_width_changed(self, *args):
            pass

    program_dir = os.path.dirname(os.path.abspath(__file__))

    app = DummyApp()
    ui = Interface(app, program_dir)
    ui.show()

    print("Arrancando interfaz GTK 3...")
    Gtk.main()
