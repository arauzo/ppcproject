#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 PPC-PROJECT
   Multiplatform software tool for education and research in
   project management

 Main program, acting as general controller in the Model-View-Controller squema

 NOTE: this module should not contain:
    * data handling, computations... -> must be placed in Model modules
    * graphic interface details... -> must be placed in View modules


 Copyright 2007-10 University of Cordoba
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

# Python Std. lib.
import os
from datetime import datetime
from copy import deepcopy
import math
import gettext
import operator

# GTK
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk


class _BuilderAdapter(object):
    def __init__(self, builder):
        self._builder = builder

    def get_widget(self, name):
        return self._builder.get_object(name)

    def signal_autoconnect(self, owner):
        self._builder.connect_signals(owner)


class _GladeCompat(object):
    @staticmethod
    def bindtextdomain(app, directory):
        return None


class _GdkCompat(object):
    Rectangle = Gdk.Rectangle


class _KeysymsCompat(object):
    Escape = Gdk.KEY_Escape
    Delete = Gdk.KEY_Delete
    
class _DialogCompatWrapper(object):
    def __init__(self, dialog):
        self._dialog = dialog
        self.vbox = dialog.get_content_area()

    def __getattr__(self, name):
        return getattr(self._dialog, name)




class _GtkCompat(object):
    glade = _GladeCompat()
    gdk = _GdkCompat()
    keysyms = _KeysymsCompat()

    main = staticmethod(Gtk.main)
    main_quit = staticmethod(Gtk.main_quit)

    TextBuffer = Gtk.TextBuffer
    Image = Gtk.Image
    Label = Gtk.Label
    Fixed = Gtk.Fixed
    ListStore = Gtk.ListStore
    TreeViewColumn = Gtk.TreeViewColumn
    CellRendererText = Gtk.CellRendererText
    CellRendererCombo = Gtk.CellRendererCombo
    TreePath = Gtk.TreePath
    Adjustment = Gtk.Adjustment
    Window = Gtk.Window
    FileFilter = Gtk.FileFilter


    FILE_CHOOSER_ACTION_OPEN = Gtk.FileChooserAction.OPEN
    FILE_CHOOSER_ACTION_SAVE = Gtk.FileChooserAction.SAVE

    RESPONSE_OK = Gtk.ResponseType.OK
    RESPONSE_CANCEL = Gtk.ResponseType.CANCEL
    RESPONSE_CLOSE = Gtk.ResponseType.CLOSE

    DIALOG_MODAL = int(Gtk.DialogFlags.MODAL)
    DIALOG_DESTROY_WITH_PARENT = int(Gtk.DialogFlags.DESTROY_WITH_PARENT)

    MESSAGE_ERROR = Gtk.MessageType.ERROR
    MESSAGE_QUESTION = Gtk.MessageType.QUESTION

    BUTTONS_OK = Gtk.ButtonsType.OK

    STOCK_CANCEL = "_Cancel"
    STOCK_OPEN = "_Open"
    STOCK_SAVE = "_Save"
    STOCK_OK = "_OK"
    
    @staticmethod
    def FileChooserDialog(title=None, parent=None, action=None, buttons=None):
        dialog = Gtk.FileChooserDialog(
            title=title,
            parent=parent,
            action=action,
        )
        if buttons:
            dialog.add_buttons(*buttons)
        return dialog


    @staticmethod
    def Dialog(title=None, parent=None, flags=0, buttons=None):
        dialog = Gtk.Dialog(
            title=title,
            parent=parent,
            modal=bool(flags & int(Gtk.DialogFlags.MODAL)),
            destroy_with_parent=bool(flags & int(Gtk.DialogFlags.DESTROY_WITH_PARENT)),
        )
        if buttons:
            dialog.add_buttons(*buttons)
        return _DialogCompatWrapper(dialog)

    @staticmethod
    def MessageDialog(parent=None, flags=0, type=None, buttons=None, message_format=''):
        dialog = Gtk.MessageDialog(
            transient_for=parent,
            modal=bool(flags & int(Gtk.DialogFlags.MODAL)),
            destroy_with_parent=bool(flags & int(Gtk.DialogFlags.DESTROY_WITH_PARENT)),
            message_type=type,
            buttons=buttons if buttons is not None else Gtk.ButtonsType.NONE,
            text=message_format,
        )
        return dialog

    @staticmethod
    def VBox(*args, **kwargs):
        spacing = kwargs.get('spacing', 0)
        return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)

    @staticmethod
    def HBox(*args, **kwargs):
        spacing = kwargs.get('spacing', 0)
        return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing)







gtk = _GtkCompat()
gobject = GObject

# Other external modules
import scipy.stats
from matplotlib import rcParams
rcParams['font.family'] = 'monospace'
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import numpy

# ppcProject modules
import simulation
import pert
import graph
import interface
import fileFormats
import assignment
import kolmogorov_smirnov
from zaderenko import mZad, early, last
from simAnnealing import simulated_annealing
from simAnnealing import resources_availability
from simAnnealing import resources_per_activities
from simAnnealing import calculate_loading_sheet
from projectCoral import get_last_crosl_summary
from projectCoral import project_coral
import algoritmoSharma, algoritmoConjuntos, algoritmoCohenSadeh, algoritmoSalas, algoritmoGentoMunicio
import algoritmoSysloOptimal, algoritmoSysloPolynomial, algoritmoMouhoub
import graph
import timedpert

#import pruebaInterface
#import assignment


class PPCproject(object):
    """ Controler of global events in application """

    def __init__(self, program_dir):
        # Internacionalization
        APP = 'PPC-Project'                   # Program name as domain for gettext translation
        DIR = os.path.join(program_dir, 'po') # Directory containing translations, usually /usr/share/locale
                                              # we set it to directory po under program_dir
        gettext.install(APP, DIR)             # Install function _() to global for all program modules
        gtk.glade.bindtextdomain(APP, DIR)    # Internacionalize .glade

        # Data globaly used in application
        self.actividad  = []
        self.recurso    = []
        self.asignacion = []
        self.optimumSchedule = []
        self.schedules = []
        self.schedule_tab_labels = []

        self.distributionType = None
        self.normal_distribution_cache = {}

        self.bufer = gtk.TextBuffer()
        self.ganttActLoaded = False
        self.interface = interface.Interface(self, program_dir)
        self._widgets = _BuilderAdapter(self.interface.builder)
        self.builder = self.interface.builder
        self._widgets.signal_autoconnect(self)

        self.vBoxProb = self._widgets.get_widget('vbProb')
        self.grafica = gtk.Image()
        self.box = gtk.VBox()
        self.hBoxSim = self._widgets.get_widget('hbSim')
        self.boxS = gtk.VBox()
        self.vPrincipal = self._widgets.get_widget('wndPrincipal')
        self.vIntroduccion = self._widgets.get_widget('wndIntroduccion')
        self.vZaderenko = self._widgets.get_widget('wndZaderenko')
        self.vActividades = self._widgets.get_widget('wndActividades')
        self.vHolguras = self._widgets.get_widget('wndHolguras')
        self.vProbabilidades = self._widgets.get_widget('wndProbabilidades')
        self.vSimulacion = self._widgets.get_widget('wndSimulacion')
        self.wndSimAnnealing = self._widgets.get_widget('wndSimAnnealing')
        self.vRecursos = self._widgets.get_widget('wndRecursos')
        self.vAsignarRec = self._widgets.get_widget('wndAsignarRec')
        self.vCaminos = self._widgets.get_widget('wndCaminos')
        self.vAsignacion = self._widgets.get_widget('wndAsignacion')
        self.vTestKS = self._widgets.get_widget('wndTestKS')
        self.vKSResults = self._widgets.get_widget('wndKSTestResults')

        self.vAvgDuration = self._widgets.get_widget('wndAvgDuration')
        self.vDistNormal = self._widgets.get_widget('wndDistNormal')
        self.vDistTriBeta = self._widgets.get_widget('wndDistTriBeta')
        self.vDistUnif = self._widgets.get_widget('wndDistUnif')


        self.dAyuda = self._widgets.get_widget('dAyuda')
        self.bHerramientas = self._widgets.get_widget('bHerramientas1')

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
        self.resource_algorithm_combo = None
        self.crosl_force_duration_check = None
        self.crosl_use_elite_seeds_check = None
        self.crosl_parameter_widgets = {}
        self.crosl_summary_label = None
        self.resource_controls_scroll = None
        self.resource_algorithm_labels = {
            'annealing': 'Default leveling',
            'professor_crosl': 'CRO-SL',
        }
        self.resource_algorithm_field_labels = {}
        self._setup_resource_algorithm_field_labels()
        self._setup_resource_algorithm_selector()

        self.ntbSchedule = self.interface.ntbSchedule

        self.zadViewList = self._widgets.get_widget('vistaZad')
        self.ventanaScroll = self._widgets.get_widget('scrolledwindow10') #YO

        self.modelo = self.interface.modelo
        self.gantt = self.interface.gantt
        self.ganttSA = self.interface.ganttSA
        self.loadSheet = self.interface.loadSheet
        self.loadTable = self.interface.loadTable
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

        self._widgets.get_widget('mnSalirPantComp').hide()
        graph_activities_menu = self._widgets.get_widget('mnActividades')
        if graph_activities_menu is not None:
            graph_activities_menu.hide()

        self.row_height_signal = self.interface.main_table_treeview.connect("size-allocate", self.cbtreeview)
        self.interface.main_table_treeview.connect('drag-end', self.reorder_gantt)
        #self.modelo.connect('rows-reordered', self.reorder_gantt)
        self.interface.main_table_treeview.connect('button-press-event', self.treeview_menu_invoked, self.interface.main_table_treeview)
        self._widgets.get_widget('vistaListaRec').connect('button-press-event', self.treeview_menu_invoked,
                                                          self._widgets.get_widget('vistaListaRec'))
        self._widgets.get_widget('vistaListaAR').connect('button-press-event', self.treeview_menu_invoked,
                                                         self._widgets.get_widget('vistaListaAR'))



        # Keeps the name of the open file
        # (None = no open file, 'Unnamed' = Project without name yet)
        self.openFilename = None
        self.set_modified_state(False)
        self.set_open_state(False)

        # File format loaders and savers
        #  (the order is used to try when loading unknown type files)
        self.fileFormats = [
            fileFormats.PPCProjectFileFormat(),
            #fileFormats.PPCProjectOLDFileFormat(),
            fileFormats.PSPProjectFileFormat(),
        ]

    def _setup_resource_algorithm_field_labels(self):
        label_ids = (
            'lblSimAnnealing',
            'label7',
            'label6',
            'label9',
            'label2',
            'label8',
            'label3',
            'label4',
            'label10',
            'label11',
        )
        for label_id in label_ids:
            label = self._widgets.get_widget(label_id)
            if label is not None:
                self.resource_algorithm_field_labels[label_id] = {
                    'widget': label,
                    'default': label.get_text(),
                }

    def _setup_resource_algorithm_selector(self):
        """
        Adds an algorithm selector to the leveling/allocation window.

        The original dialog was designed only for simulated annealing. Creating
        this small row at runtime keeps the Glade file stable while allowing the
        user to choose the optimizer from the interface.
        """
        container = self._widgets.get_widget('vbox15')
        if container is None:
            return
        self._setup_resource_controls_scroll(container)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.set_visible(True)
        row.set_border_width(6)

        label = Gtk.Label(label=_('Algorithm:'))
        label.set_visible(True)
        label.set_xalign(0.0)
        row.pack_start(label, False, False, 8)

        combo = Gtk.ComboBoxText()
        combo.set_visible(True)
        combo.set_size_request(180, -1)
        for key in ('annealing', 'professor_crosl'):
            combo.append(key, self.resource_algorithm_labels[key])

        default_algorithm = os.environ.get('PPCPROJECT_RESOURCE_ALGORITHM', 'professor_crosl').lower()
        if default_algorithm not in self.resource_algorithm_labels:
            default_algorithm = 'professor_crosl'
        combo.set_active_id(default_algorithm)
        combo.connect('changed', self.on_resource_algorithm_changed)
        row.pack_start(combo, False, False, 0)

        container.pack_start(row, False, False, 0)
        container.reorder_child(row, 0)

        force_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        force_row.set_visible(False)
        force_row.set_border_width(6)

        force_check = Gtk.CheckButton(label=_('Force duration'))
        force_check.set_visible(True)
        force_check.set_tooltip_text(
            _('Force CRO-SL to use the full allowed project duration')
        )
        force_row.pack_start(force_check, False, False, 8)

        elite_check = Gtk.CheckButton(label=_('Use elite seeds'))
        elite_check.set_visible(True)
        elite_check.set_active(True)
        elite_check.set_tooltip_text(
            _('Load and update the persistent CRO-SL elite seed CSV')
        )
        force_row.pack_start(elite_check, False, False, 8)

        container.pack_start(force_row, False, False, 0)
        container.reorder_child(force_row, 1)
        self.crosl_force_duration_row = force_row
        self.crosl_force_duration_check = force_check
        self.crosl_use_elite_seeds_check = elite_check

        self._setup_crosl_parameters_panel(container)

        container.show_all()

        self.resource_algorithm_combo = combo
        self._setup_crosl_summary_panel(container)
        self.on_resource_algorithm_changed(combo)

    def _setup_resource_controls_scroll(self, container):
        if self.resource_controls_scroll is not None:
            return

        parent = container.get_parent()
        if parent is None:
            return

        parent.remove(container)
        scroll = Gtk.ScrolledWindow()
        scroll.set_visible(True)
        scroll.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC,
        )
        scroll.set_size_request(385, -1)
        scroll.add(container)
        parent.pack_start(scroll, False, False, 0)
        parent.reorder_child(scroll, 0)
        self.resource_controls_scroll = scroll

    def _setup_crosl_parameters_panel(self, container):
        frame = Gtk.Frame(label='CRO-SL parameters')
        frame.set_visible(False)
        frame.set_border_width(6)

        grid = Gtk.Grid()
        grid.set_visible(True)
        grid.set_column_spacing(8)
        grid.set_row_spacing(4)
        grid.set_border_width(6)
        frame.add(grid)

        parameter_specs = [
            ('reef_size_n', 'Reef height (N)', 8, 2, 50, 1, 0),
            ('reef_size_m', 'Reef width (M)', 8, 2, 50, 1, 0),
            ('r_l', 'r_l random larvae', 0.1, 0.0, 1.0, 0.05, 2),
            ('p_0', 'r_0 initial occupation', 0.7, 0.0, 1.0, 0.05, 2),
            ('f_b', 'f_b broadcast spawning', 0.7, 0.0, 1.0, 0.05, 2),
            ('f_a', 'f_a brooding/asexual', 0.1, 0.0, 1.0, 0.05, 2),
            ('f_d', 'f_d depredation fraction', 0.2, 0.0, 1.0, 0.05, 2),
            ('p_d', 'p_d depredation prob.', 0.15, 0.0, 1.0, 0.05, 2),
        ]

        for row_index, spec in enumerate(parameter_specs):
            key, label_text, default, lower, upper, step, digits = spec

            label = Gtk.Label(label=label_text + ':')
            label.set_visible(True)
            label.set_xalign(0.0)

            adjustment = Gtk.Adjustment(
                value=default,
                lower=lower,
                upper=upper,
                step_increment=step,
                page_increment=step,
                page_size=0,
            )
            spin = Gtk.SpinButton()
            spin.set_visible(True)
            spin.set_adjustment(adjustment)
            spin.set_digits(digits)
            spin.set_numeric(True)
            spin.set_size_request(90, -1)

            grid.attach(label, 0, row_index, 1, 1)
            grid.attach(spin, 1, row_index, 1, 1)
            self.crosl_parameter_widgets[key] = spin

        resource_row = len(parameter_specs)
        resource_label = Gtk.Label(label='Resources to optimize (empty = all):')
        resource_label.set_visible(True)
        resource_label.set_xalign(0.0)
        resource_entry = Gtk.Entry()
        resource_entry.set_visible(True)
        resource_entry.set_placeholder_text('Example: R1,R3,R6')
        resource_entry.set_width_chars(18)
        grid.attach(resource_label, 0, resource_row, 1, 1)
        grid.attach(resource_entry, 1, resource_row, 1, 1)
        self.crosl_parameter_widgets['optimized_resources'] = resource_entry

        container.pack_start(frame, False, False, 0)
        container.reorder_child(frame, 2)
        self.crosl_parameters_frame = frame

    def _setup_crosl_summary_panel(self, container):
        frame = Gtk.Frame(label='CRO-SL summary')
        frame.set_visible(False)
        frame.set_border_width(6)

        label = Gtk.Label()
        label.set_visible(True)
        label.set_xalign(0.0)
        label.set_yalign(0.0)
        label.set_line_wrap(True)
        label.set_selectable(True)
        label.set_text('Run CRO-SL to show summary data.')
        frame.add(label)

        container.pack_start(frame, False, False, 0)
        container.reorder_child(frame, 1)
        self.crosl_summary_frame = frame
        self.crosl_summary_label = label

    def get_selected_resource_algorithm(self):
        if self.resource_algorithm_combo is None:
            return os.environ.get('PPCPROJECT_RESOURCE_ALGORITHM', 'professor_crosl').lower()
        selected = self.resource_algorithm_combo.get_active_id()
        return selected or 'professor_crosl'

    def on_resource_algorithm_changed(self, combo):
        resource_algorithm = self.get_selected_resource_algorithm()
        uses_annealing_params = resource_algorithm == 'annealing'

        def set_label(label_id, text):
            label_data = self.resource_algorithm_field_labels.get(label_id)
            if label_data is not None:
                label_data['widget'].set_text(text)

        def set_visible(widget_id, visible):
            widget = self._widgets.get_widget(widget_id)
            if widget is not None:
                widget.set_visible(visible)

        if uses_annealing_params:
            for label_id, label_data in self.resource_algorithm_field_labels.items():
                label_data['widget'].set_text(label_data['default'])
        else:
            set_label('lblSimAnnealing', 'Extra duration:')
            set_label('label9', 'Algorithm:')
            set_label('label8', 'Generations:')
            set_label('label3', 'Best variance:')
            set_label('label4', 'CRO-SL uses internal stopping')
            set_label('label10', 'Executed:')
            set_label('label11', 'generations')

        for widget_id in ('label7', 'label6', 'sbNu', 'sbPhi', 'label2', 'sbMinTempSA'):
            set_visible(widget_id, uses_annealing_params)
        for widget_id in ('lblSimAnnealing', 'sbSlackSA'):
            set_visible(widget_id, True)
        for widget_id in ('label4', 'sbNoImproveIterSA', 'cbIterationSA'):
            set_visible(widget_id, uses_annealing_params)
        if getattr(self, 'crosl_summary_frame', None) is not None:
            self.crosl_summary_frame.set_visible(not uses_annealing_params)
        if getattr(self, 'crosl_force_duration_row', None) is not None:
            self.crosl_force_duration_row.set_visible(not uses_annealing_params)
        if getattr(self, 'crosl_parameters_frame', None) is not None:
            self.crosl_parameters_frame.set_visible(not uses_annealing_params)

        self.sbPhi.set_sensitive(uses_annealing_params)
        self.sbNu.set_sensitive(uses_annealing_params)
        self.sbMinTempSA.set_sensitive(uses_annealing_params)
        self.sbNoImproveIterSA.set_sensitive(uses_annealing_params and not self.cbIterationSA.get_active())
        self.cbIterationSA.set_sensitive(uses_annealing_params)

    def get_crosl_parameters_from_interface(self):
        if not self.crosl_parameter_widgets:
            return {}

        return {
            'size_n': int(self.crosl_parameter_widgets['reef_size_n'].get_value()),
            'size_m': int(self.crosl_parameter_widgets['reef_size_m'].get_value()),
            'optimized_resources': [
                token.strip()
                for token in self.crosl_parameter_widgets['optimized_resources']
                .get_text()
                .replace(';', ',')
                .split(',')
                if token.strip()
            ],
            'r_l': self.crosl_parameter_widgets['r_l'].get_value(),
            'p_0': self.crosl_parameter_widgets['p_0'].get_value(),
            'f_b': self.crosl_parameter_widgets['f_b'].get_value(),
            'f_a': self.crosl_parameter_widgets['f_a'].get_value(),
            'f_d': self.crosl_parameter_widgets['f_d'].get_value(),
            'p_d': self.crosl_parameter_widgets['p_d'].get_value(),
        }

    def update_crosl_summary_panel(self, summary=None):
        if self.crosl_summary_label is None:
            return
        if not summary:
            self.crosl_summary_label.set_text('Run CRO-SL to show summary data.')
            return

        generated = summary.get('generated_larvae', 0)
        settled = summary.get('settled_larvae', 0)
        self.crosl_summary_label.set_text(
            'Best variance: {best:.4f}\n'
            'Optimized resources: {optimized_resources}\n'
            'Avg resource variance: {avg:.4f}\n'
            'Worst resource: {worst} ({worst_var:.4f})\n'
            'Best generation: {best_gen}\n'
            'Execution time: {time:.2f} s\n'
            'Critical/allowed duration: {critical:.2f}/{allowed:.2f}\n'
            'Force allowed duration: {force_duration}\n'
            'Use elite seeds: {use_elite_seeds}\n'
            'Improvement over initial: {improvement:.2f}%\n'
            'Settled larvae: {settled}/{generated} ({settled_rate:.1f}%)\n'
            'Reef: {reef} | Elite size: {elite} | Seed: {seed}\n'
            'Params: r0={p0:.2f}, fb={fb:.2f}, rl={rl:.2f}, fa={fa:.2f}, fd={fd:.2f}, pd={pd:.2f}'.format(
                best=summary.get('best_variance', 0.0),
                optimized_resources=', '.join(
                    str(resource)
                    for resource in summary.get('optimized_resources', [])
                ) or 'all',
                avg=summary.get('avg_resource_variance', 0.0),
                worst=summary.get('worst_resource') or '-',
                worst_var=summary.get('worst_resource_variance', 0.0),
                best_gen=summary.get('best_generation', 0),
                time=summary.get('execution_time', 0.0),
                critical=summary.get('critical_duration', 0.0),
                allowed=summary.get('allowed_duration', 0.0),
                force_duration=(
                    'yes' if summary.get('force_project_duration') else 'no'
                ),
                use_elite_seeds=(
                    'yes' if summary.get('use_elite_seeds') else 'no'
                ),
                improvement=summary.get('improvement_percent', 0.0),
                settled=settled,
                generated=generated,
                settled_rate=summary.get('settled_rate', 0.0),
                reef=summary.get('reef_size', '-'),
                elite=summary.get('elite_size', 0),
                seed=summary.get('seed', '-'),
                p0=summary.get('p_0', 0.0),
                fb=summary.get('f_b', 0.0),
                rl=summary.get('r_l', 0.0),
                fa=summary.get('f_a', 0.0),
                fd=summary.get('f_d', 0.0),
                pd=summary.get('p_d', 0.0),
            )
        )

# TEST code on route to more usable editing table
#        self.interface.main_table_treeview.connect('key-press-event', self.on_vistaListaDatos_key_press_event, self.interface.main_table_treeview)
#    def on_vistaListaDatos_key_press_event(self, treeview, event, data):
#        print 'XXX on_vistaListaDatos_key_press_event', treeview, event, data
#        # Testing code from: http://www.daa.com.au/pipermail/pygtk/2009-June/017134.html
#        path, col = treeview.get_cursor()
#        ## only visible columns!!
#        columns = [c for c in treeview.get_columns() if c.get_visible()]
#        colnum = columns.index(col)
#        if colnum + 1 < len(columns):
#            next_column = columns[colnum + 1]
#            next_field_name = next_column.get_data('field_name')
#            gobject.idle_add(treeview.set_cursor, path, next_column, True)
#        else:
#            tmodel = treeview.get_model()
#            titer = tmodel.iter_next(tmodel.get_iter(path))
#            if titer is None:
#                titer = tmodel.get_iter_first()
#            path = tmodel.get_path(titer)
#
#            next_column = columns[0]
#            next_field_name = next_column.get_data('field_name')
#            gobject.idle_add(treeview.set_cursor, path, next_column, True )
#        return False

    def cbtreeview(self, container, widget):
        """
        Sets Gantt row height according to the activities treeview.
        """
        header_height = self.interface.main_table_treeview.convert_tree_to_widget_coords(0, 1)[1]
        self.gantt.set_header_height(header_height)

        if len(self.modelo) > 0 and self.modelo[0][1] != "":
            path = Gtk.TreePath.new_from_indices([0])
            area = self.interface.main_table_treeview.get_background_area(
                path,
                self.interface.main_table_treeview.columna[0]
            )
            self.gantt.set_row_height(area.height)
            self.interface.main_table_treeview.disconnect(self.row_height_signal)

        return False

    def on_mnAcción_activate(self, item):
        return
    

    def set_open_state(self, value):
        """
        Enable or disable project editing controls (when a project is open or not)

        Parameters: value (True or False)

        Returns: None.
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
            self._widgets.get_widget('stbStatus').push(0, _("No project file opened"))

    def set_modified_state(self, value):
        """
        Enable or disable project saving controls (when project is modified or not)

        Parameters: value (True or False)

        Returns: None.
        """
        self.modified = value

        # Guardar solo cuando hay cambios
        self._widgets.get_widget('mnGuardar').set_sensitive(value)
        self._widgets.get_widget('tbGuardar').set_sensitive(value)

        # Guardar como debe estar disponible siempre que haya proyecto abierto
        self._widgets.get_widget('mnGuardarComo').set_sensitive(self.openFilename is not None or self.actividad != [])

        self._widgets.get_widget('stbStatus').pop(0)
        if value:
            self._widgets.get_widget('stbStatus').push(0, _("Project modified"))
        else:
            self._widgets.get_widget('stbStatus').push(0, _("Project without changes"))




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
        self.normal_distribution_cache = {}
        self.modeloR.clear()
        self.recurso=[]
        self.modeloAR.clear()
        self.asignacion=[]
        cont=1
        # Se inserta una fila vacia
        self.modelo.append([cont, '', '', '', '', '', '', '', 'Beta', ""])
        self.modeloR.append()
        self.modeloAR.append()
        #Minimum schedule
        start_times = pert.get_activities_start_time([], [], [], True)
        self.add_schedule(_("Min"), start_times)
        self.set_schedule(start_times)
        self.set_open_state(True)
        self.set_modified_state(True)
        self.ntbSchedule.show()

    def col_edited_cb(self, renderer, path, new_text, modelo, n):
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
        new_text = '' if new_text is None else str(new_text)
        preVal = None  # Previous value
        if new_text != modelo[int(path)][n]:
            self.set_modified_state(True) # Project data has changed
            #print "cambio '%s' por '%s'" % (modelo[path][n], new_text)
            # Controlamos la introduccion de las siguientes
            if modelo == self.modelo:  # Interfaz de actividades
                actividades=self.actividades2Lista()
                preVal = modelo[path][n]  # Previous Value
                # añadimos las etiquetas de las actividades al selector de las siguientes
                if n == 1:  # Columna de las actividades
                    if new_text == '':
                        self.dialogoError(_('The name of activity must not be empty.'))
                        return
                    else:
                        if new_text not in actividades:
                            if modelo[path][1]!='':  # Si modificamos una actividad
                                #print modelo[path][1], new_text, 'valores a intercambiar'
                                old_activity_name = modelo[path][1]
                                modelo=self.modificarSig(modelo, old_activity_name, new_text)
                                self.gantt.rename_activity(old_activity_name,new_text)
                                self.gantt.update()
                                for row in self.asignacion:
                                    if row[0] == old_activity_name:
                                        row[0] = new_text
                                for row in self.modeloAR:
                                    if row[0] == old_activity_name:
                                        row[0] = new_text
                                if old_activity_name in self.normal_distribution_cache:
                                    self.normal_distribution_cache[new_text] = self.normal_distribution_cache.pop(old_activity_name)
                                modelo[path][1] = new_text
                                it=self.modeloComboS.get_iter(path)
                                self.modeloComboS.set_value(it, 0, new_text)
                                it=self.modeloComboARA.get_iter(path)
                                self.modeloComboARA.set_value(it, 0, new_text)

                            else:  # Se inserta normalmente
                                modelo[path][1] = new_text
                                self.modeloComboS.append([modelo[path][1]])
                                self.modeloComboARA.append([modelo[path][1]])
                                self.gantt.add_activity(new_text)
                                self.gantt.update()

                        else:
                            self.dialogoError(_('Repeated activity.'))
                            return


                elif modelo[int(path)][1] != "":
                    if n == 2:  # Columna de las siguientes
                        modelo = self.comprobarSig(modelo, path, new_text)
                    else:
                        modelo[path][n] = new_text
                else:
                    self.dialogoError(_('Activity name must be introduced first.'))
                    return

            elif modelo == self.modeloR:  # Resources
                if n == 0:
                    recursos = [
                        resource
                        for index, resource in enumerate(self.resources2List())
                        if index != int(path)
                    ]
                    if new_text == '':
                        self.dialogoError(_('The name of resource must not be empty.'))
                        return
                    else:
                        if new_text not in recursos:
                            if preVal:
                                self.update_resource_combo_name(preVal, new_text)
                            elif not self.resource_combo_contains(new_text):
                                self.modeloComboARR.append([new_text])
                            modelo[path][0] = new_text
                        else:
                            self.dialogoError(_('Repeated resource.'))
                            return
                elif modelo[int(path)][0] == "" or modelo[int(path)][0] == None:
                    self.dialogoError(_('Resource name must be introduced first.'))
                    return

                else:
                    modelo[path][n] = new_text

            else:  # Otras interfaces
                modelo[path][n] = new_text

            iterador=modelo.get_iter(path)
            proximo=modelo.iter_next(iterador)
            if proximo == None:  #si estamos en la última fila, insertamos otra vací­a
                # Actividades
                if modelo==self.modelo:
                    #siempre debe existir un elemento más en modelo que en actividades
                    if len(modelo)!=len(self.actividad):
                        modelo.append([modelo[len(modelo)-1][0] + 1, '', '', '', '', '', '', '',
                                       'Beta',""])
                        fila=['', '', [], '', '', '', '', '', 'Beta', 0]
                        self.actividad.append(fila)
                    else:
                        modelo.append([modelo[len(modelo)-1][0] + 1, '', '', '', '', '', '', '',
                                       'Beta',""])
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

            self.actualizacion(modelo, path, n, preVal)
        return

    def reorder_gantt(self, widget, dragContext):
        """
        Reorder Gantt diagram according to activities new order.

        Returns: None.
        """
        act_list = []
        new_order = []
        for index in range(len(self.modelo)):
            if self.modelo[index][1] != "":
                act_list.append(self.modelo[index][1])
                new_order.append(self.modelo[index][0]-1)
            else:
                row_path = index
        if row_path != len(self.modelo) - 1:
            row_cont = self.modelo[row_path][0]
            self.modelo.remove(self.modelo.get_iter(row_path))
            self.modelo.append([row_cont, '', '', '', '', '', '', '', 'Beta', ""])
        new_actividad = []
        for act in act_list:
            for index in range(len(self.actividad)):
                if self.actividad[index][1] == act:
                    found = index
                    break
            new_actividad.append(self.actividad[found])
            self.actividad.remove(new_actividad[-1])
        self.actividad = new_actividad
        self.gantt.reorder(act_list)
        self.gantt.update()
        self.modeloComboS.reorder(new_order)
        self.modeloComboARA.reorder(new_order)
        self.reorder_activities()

    def actualizacion(self, modelo, path, n, preVal):
        """
         Actualización de las tres listas con los nuevos datos introducidos
                  (lista de actividades, de recursos y de asignacion)

         modelo (interfaz)
         path (fila)
         n (columna)
         preVal (Valor Anterior)

         Valor de retorno: -
        """
        gantt_modified = False

        # Actividades
        if modelo == self.modelo:
            if self.modelo[path][n] == '':
                if n == 2:
                    self.actividad[int(path)][2] = []
                    self.gantt.set_activity_prelations(self.actividad[int(path)][1], [])
                    gantt_modified = True
                else:
                    self.actividad[int(path)][n] = self.modelo[path][n]
                    if n == 7 and self.modelo[path][8] == 'Normal' and self.modelo[path][1] != '' and self.modelo[path][6] != '' and self.modelo[path][7] != '':
                        self.normal_distribution_cache[self.modelo[path][1]] = (
                            float(self.modelo[path][6]),
                            float(self.modelo[path][7]),
                        )
            else:
                if n == 1:  # Name of activity
                    self.modelo[path][1] = str(self.modelo[path][1])
                    self.gantt.set_activity_comment(self.modelo[path][1], self.modelo[path][1])
                    self.actividad[int(path)][n] = str(self.modelo[path][n])

                elif n in range(3, 6):  # optimistic, most probable, pessimistic
                    self.actividad[int(path)][n] = float(self.modelo[path][n])

                    if self.modelo[path][3] != '' and self.modelo[path][4] != '' and self.modelo[path][5] != '':
                        a = float(self.modelo[path][3])
                        b = float(self.modelo[path][5])
                        m = float(self.modelo[path][4])

                        ok = ((a < b and m <= b and m >= a) or (a == b and b == m))

                        if ok:
                            self.actualizarMediaDTipica(path, self.modelo, self.actividad, a, b, m)
                            if self.modelo[path][6] != '':
                                self.gantt.set_activity_duration(self.modelo[path][1], float(self.modelo[path][6]))
                                gantt_modified = True
                        else:
                            self.dialogoError(_('Wrong durations introduced.'))
                            self.modelo[path][n] = self.actividad[int(path)][n] = preVal

                elif n == 6:  # mean duration
                    self.actividad[int(path)][n] = float(self.modelo[path][n])
                    for i in range(3, 6):
                        self.modelo[path][i] = ''
                        self.actividad[int(path)][i] = ''
                    if self.modelo[path][8] == 'Normal':
                        self.actividad[int(path)][7] = 0.2 * float(self.modelo[path][6])
                        self.modelo[path][7] = str(self.actividad[int(path)][7])
                        if self.modelo[path][1] != '':
                            self.normal_distribution_cache[self.modelo[path][1]] = (
                                float(self.modelo[path][6]),
                                float(self.modelo[path][7]),
                            )
                    self.gantt.set_activity_duration(self.modelo[path][1], float(self.modelo[path][6]))
                    gantt_modified = True
                    
                elif n == 8:  # distribution type
                    activity_name = self.modelo[path][1]
                    if preVal == 'Normal' and activity_name != '' and self.modelo[path][6] != '' and self.modelo[path][7] != '':
                        self.normal_distribution_cache[activity_name] = (
                            float(self.modelo[path][6]),
                            float(self.modelo[path][7]),
                        )
                    self.actividad[int(path)][8] = self.modelo[path][8]
                    if self.modelo[path][8] == 'Normal':
                        self.actualizarMediaDTipica(path, self.modelo, self.actividad, 0, 0, 0)
                        if activity_name in self.normal_distribution_cache:
                            mean_value, std_value = self.normal_distribution_cache[activity_name]
                            self.actividad[int(path)][6] = mean_value
                            self.modelo[path][6] = str(mean_value)
                            self.actividad[int(path)][7] = std_value
                            self.modelo[path][7] = str(std_value)
                            self.gantt.set_activity_duration(activity_name, float(mean_value))
                            gantt_modified = True
                    elif self.modelo[path][3] != '' and self.modelo[path][4] != '' and self.modelo[path][5] != '':
                        a = float(self.modelo[path][3])
                        b = float(self.modelo[path][5])
                        m = float(self.modelo[path][4])
                        self.actualizarMediaDTipica(path, self.modelo, self.actividad, a, b, m)
                        if self.modelo[path][6] != '':
                            self.gantt.set_activity_duration(self.modelo[path][1], float(self.modelo[path][6]))
                            gantt_modified = True

                elif n == 2:  # following/prelations
                    if self.modelo[path][2] == self.actividad[int(path)][1]:
                        self.modelo[path][2] = ''
                        self.actividad[int(path)][2] = []
                    else:
                        self.actividad[int(path)][2] = self.actString2actList(self.modelo[path][2])
                        self.gantt.set_activity_prelations(
                            self.actividad[int(path)][1],
                            self.actString2actList(self.modelo[path][2])
                        )
                        gantt_modified = True

                elif n == 9:  # start time
                    self.schedules[self.ntbSchedule.get_current_page()][1][str(modelo[path][1])] = float(self.modelo[path][9])
                    gantt_modified = True

                else:
                    self.actividad[int(path)][n] = self.modelo[path][n]
                    if n == 7 and self.modelo[path][8] == 'Normal' and self.modelo[path][1] != '' and self.modelo[path][6] != '' and self.modelo[path][7] != '':
                        self.normal_distribution_cache[self.modelo[path][1]] = (
                            float(self.modelo[path][6]),
                            float(self.modelo[path][7]),
                        )

        # Recursos
        elif modelo == self.modeloR:
            if n == 0:
                for index in range(len(self.asignacion)):
                    if self.asignacion[index][1] == self.recurso[int(path)][0]:
                        self.asignacion[index][1] = self.modeloR[path][n]
                        self.modeloAR[index][1] = self.modeloR[path][n]

            self.recurso[int(path)][n] = self.modeloR[path][n]

            if self.modeloR[path][1] == _('Renewable'):
                if n == 3:
                    self.dialogoRec(_('Renewable'))
                self.recurso[int(path)][3] = self.modeloR[path][3] = ''

            elif self.modeloR[path][1] == _('Non renewable'):
                if n == 2:
                    self.dialogoRec(_('Non renewable'))
                self.recurso[int(path)][2] = self.modeloR[path][2] = ''

            elif self.modeloR[path][1] == _('Unlimited'):
                if n == 2 or n == 3:
                    self.dialogoRec(_('Unlimited'))
                self.recurso[int(path)][3] = self.modeloR[path][3] = ''
                self.recurso[int(path)][2] = self.modeloR[path][2] = ''

        # Recursos necesarios por actividad
        else:
            self.asignacion[int(path)][n] = self.modeloAR[path][n]

        if gantt_modified is True:
            act_list = []
            dur_dic = {}
            pre_dic = {}

            for i in range(len(self.actividad)):
                act_name = str(self.actividad[i][1])
                self.actividad[i][1] = act_name
                act_list.append(act_name)
                dur_dic[act_name] = float(self.actividad[i][6] if self.actividad[i][6] != "" else 0)

                predecessors = self.actividad[i][2]
                if isinstance(predecessors, (list, tuple)):
                    normalized_predecessors = [str(x) for x in predecessors if x != ""]
                elif predecessors == '' or predecessors is None:
                    normalized_predecessors = []
                else:
                    normalized_predecessors = [str(predecessors)]

                self.actividad[i][2] = normalized_predecessors
                pre_dic[act_name] = normalized_predecessors


            changed_activity = str(modelo[path][1])

            if n == 9:
                self.schedules[self.ntbSchedule.get_current_page()][1] = pert.get_activities_start_time(
                    act_list,
                    dur_dic,
                    pre_dic,
                    self.ntbSchedule.get_current_page() == 0,
                    self.schedules[self.ntbSchedule.get_current_page()][1],
                    changed_activity
                )
            elif n == 2:
                self.schedules[0][1] = pert.get_activities_start_time(
                    act_list,
                    dur_dic,
                    pre_dic,
                    True,
                    self.schedules[0][1]
                )
            else:
                self.schedules[0][1] = pert.get_activities_start_time(
                    act_list,
                    dur_dic,
                    pre_dic,
                    True,
                    self.schedules[0][1],
                    changed_activity
                )
                for index in range(1, len(self.schedules)):
                    self.schedules[index][1] = pert.get_activities_start_time(
                        act_list,
                        dur_dic,
                        pre_dic,
                        False,
                        self.schedules[index][1],
                        changed_activity
                    )

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
        if modelo[path][8] == _('Normal'):
            modelo[path][3] = actividad[int(path)][3] = ''
            modelo[path][4] = actividad[int(path)][4] = ''
            modelo[path][5] = actividad[int(path)][5] = ''
            modelo[path][6] = actividad[int(path)][6] = ''
            modelo[path][7] = actividad[int(path)][7] = ''

        # Si la distribución no es Normal, se recalculan los valores
        else:
            media, dTipica=self.calcularMediaYDTipica(modelo[path][8], a, b, m)
            m='%4.3f'%(media)
            actividad[int(path)][6] = modelo[path][6] = m
            dT='%4.3f'%(dTipica)
            actividad[int(path)][7] = modelo[path][7] = dT

    def comprobarSig(self, modelo, path, new_text):
        """
         Control de la introducción de las siguientes

         Parámetros: modelo (interfaz)
                     path (fila)
                     new_tex (nuevo texto introducido)

         Valor de retorno: modelo (interfaz)
        """
        # Se introducen en una lista las etiquetas de las actividades
        actividades = self.actividades2Lista()

        # Se pasa a una lista las actividades que tengo como siguientes antes de la modificación
        anterior = self.actString2actList(modelo[path][2])
        #print anterior, 'anterior'

        # Se pasa el nuevo texto a una lista
        modificacion = self.actString2actList(new_text)
        #print modificacion, 'modificacion'

        if modificacion == [""]:  # Si no se introduce texto (estamos borrando todas las siguientes)
            modelo[path][2] = ''

        else:  # Se introduce texto
            # Si se introduce un sólo dato (es seleccionado del selector,
            # introducido manualmente ó se intentan borran todos las siguientes menos esa)
            if len(modificacion) == 1:
                if modificacion[0] in actividades:  # Si esa etiqueta existe como actividad
                    if modificacion[0] != modelo[path][1]: # Si no coincide con su etiqueta
                        # Si no se encuentra ya introducida como siguiente, la añadimos
                        if modificacion[0] not in anterior:
                            self.insertamosSiguiente(modelo, path, modificacion[0])
                        # Si se encontraba anteriormente, lo más probable es que se intenten borrar todas las
                        # siguientes excepto esa
                        else:
                            modelo[path][2] = modificacion[0]
                            self.actividad[int(path)][2] = modelo[path][2]

            else:  # Al intentar introducir más de un elemento, estoy añadiendo manualmente o intentando borrar
                c = 0  # Controla condiciones erróneas
                d = 0  #    "         "           "
                for n in modificacion:  # Analizamos cada siguiente de la lista de modificacion
                    if n not in actividades:  # Si esa etiqueta existe como actividad
                        c += 1
                    else:
                        if n==modelo[path][1]:  # Si coincide con su etiqueta
                            c += 1
                        else:
                            if n in anterior:  # Si se encuentra ya introducida como siguiente
                                d += 1

                if c == 0: # Si no se da ninguno de los dos primeros casos
                    cadena = ', '.join(modificacion) # Pasamos la lista a cadena para mostrarla en la interfaz
                    if d != 0:  # Si se da el último caso, se sobreescribe
                        modelo[path][2] = cadena
                        self.actividad[int(path)][2] = modelo[path][2]
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
                if len(self.actividad[a][2]) == 1: # Si original es la única siguiente, se modifica por nuevo
                    #print '2'
                    modelo[a][2] = nuevo
                    self.actividad[a][2] = self.actString2actList(nuevo)

                else: # Si original no es la única siguiente
                    for m in range(len(self.actividad[a][2])):
                        # La siguiente que coincida con original, se modifica por nuevo
                        if original == self.actividad[a][2][m]:
                            #print '3'
                            self.actividad[a][2][m] = nuevo
                            modelo[a][2] = ', '.join(self.actividad[a][2])

        return modelo


    def add_schedule(self, name , sch_dic):
        """
        Add new schedule.

        Parameters: name: schedule name.
                    sch_dic: schedule.

        Returns: None.
        """
        if name == None:
            name = "P" + str(len(self.schedules))
        self.schedules.append([name, sch_dic])
        label = gtk.Label(label=name)
        self.schedule_tab_labels.append(label)
        fixed = gtk.Fixed()
        self.ntbSchedule.append_page(fixed, label)
        fixed.show()
        label.show()
        self.set_modified_state(True)

    def set_schedule(self, schedule):
        """
        Set current schedule

        schedule, the schedule to set

        Returns: None.
        """
        display_schedule = self.build_forward_schedule()

        for row in self.modelo:
            if row[1] != "":
                act_name = str(row[1])
                row[9] = '' if act_name not in display_schedule else str(display_schedule[act_name])

        for row in self.actividad:
            act_name = str(row[1])
            if act_name in display_schedule:
                row[9] = display_schedule[act_name]
                self.gantt.set_activity_start_time(act_name, row[9])

        self.gantt.update()

        
    def build_forward_schedule(self):
        """
        Calcula los tiempos de inicio hacia delante a partir de las
        predecesoras almacenadas en self.actividad.
        """
        durations = {}
        predecessors = {}

        for act in self.actividad:
            act_name = str(act[1])
            durations[act_name] = float(act[6]) if act[6] != '' else 0.0

            preds = act[2]
            if isinstance(preds, (list, tuple)):
                predecessors[act_name] = [str(p) for p in preds if p != '']
            elif preds in ('', None):
                predecessors[act_name] = []
            else:
                predecessors[act_name] = [str(preds)]

        schedule = {}
        pending = set(predecessors.keys())

        while pending:
            progress = False

            for act_name in list(pending):
                preds = predecessors[act_name]

                if all(pred in schedule for pred in preds):
                    if preds:
                        schedule[act_name] = max(
                            schedule[pred] + durations.get(pred, 0.0)
                            for pred in preds
                        )
                    else:
                        schedule[act_name] = 0.0

                    pending.remove(act_name)
                    progress = True

            if not progress:
                for act_name in pending:
                    schedule[act_name] = 0.0
                break

        return schedule



    def on_mnTabsDelete_activate(self, widget):
        """
        Delete tab.

        Parameters: widget.

        Returns: None.
        """
        self.schedule_tab_labels.remove(self.schedule_tab_labels[self.clicked_tab])
        if self.clicked_tab == self.ntbSchedule.get_current_page():
            self.ntbSchedule.set_current_page((self.clicked_tab - 1) % self.ntbSchedule.get_n_pages())
        del self.schedules[self.clicked_tab]
        self.ntbSchedule.remove_page(self.clicked_tab)
        self.set_modified_state(True)

    def on_mnTabsNew_activate(self, widget):
        """
        Action when new schedule tab is requested from context menu

        Parameters: widget.

        Returns: None.
        """
        new_sched = deepcopy(self.schedules[0][1])
        self.add_schedule(None, new_sched)


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
            self.actividad[n][8] = columnaRec[n]

        # Se actualiza la interfaz
        for m in range(len(columnaRec)):
            cadena = ', '.join(columnaRec[m])
            self.modelo[m][8] = cadena
        self.sumarUnidadesRec(self.asignacion)



# FUNCIONES DE COMPROBACIÓN #

    def actividadesRepetidas(self, actividad):
        """
        Comprueba si se han introducido actividades repetidas

        Parámetros: actividad (lista de actividades)

        Valor de retorno: error (0 si no hay error
                                 1 si hay error)
                          repetidas (lista de actividades repetidas)
        """
        error = 0
        actividades = []
        repetidas = []
        # Si nos encontramos alguna repetida, la metemos en una lista
        for n in range(len(actividad)):
            if actividad[n][1] not in actividades:
                actividades.append(actividad[n][1])
            else:
                repetidas.append(actividad[n][1])
                error = 1

        return error, repetidas


    def comprobarActExisten(self, actividad):
        """
        Comprobación de que las actividades introducidas en la ventana 'recursos necesarios por actividad' existen

        Parámetros: actividad (lista de actividades)

        Valor de retorno: error (0 si no hay error
                                 1 si hay error)
        """
        error = 0
        actividades = []
        for n in range(len(actividad)):
            actividades.append(actividad[n][1])

        # Si alguna actividad no existe, se añade a una lista
        actividadesErroneas = []
        for fila in self.asignacion:
            if fila[0] not in actividades:
                error = 1
                actividadesErroneas.append(fila[0])

        # Se imprime un mensaje de error con las actividades erróneas
        if actividadesErroneas != []:
            self.errorRecNecAct(actividadesErroneas, _('Activity'))

        return error


    def comprobarRecExisten(self, recurso):
        """
        Comprobación de que los recursos introducidos en la ventana 'recursos necesarios por actividad' existen

        Parámetros: recurso (lista de recursos)

        Valor de retorno: error (0 si no hay error
                                 1 si hay error)
        """
        error = 0
        recursos = []
        for n in range(len(recurso)):
            recursos.append(recurso[n][0])

        # Si alguna actividad no existe, se añade a una lista
        recursosErroneos = []
        for fila in self.asignacion:
            if fila[1] not in recursos:
                error = 1
                recursosErroneos.append(fila[1])

        # Se imprime un mensaje de error con las actividades erróneas
        if recursosErroneos != []:
            self.errorRecNecAct(recursosErroneos, _('Resource'))

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
        unidadesRec = []
        for n in range(len(self.recurso)):
            if (self.recurso[n][1] == _('Non renewable') or
                self.recurso[n][1] == _('Double constrained')):
                cont = 0
                recurso = self.recurso[n][0]
                for m in range(len(asignacion)):
                    if asignacion[m][1] == recurso:
                        cont += int(asignacion[m][2])
                        conjunto = [recurso, cont]
                unidadesRec.append(conjunto)
        #print unidadesRec
        return unidadesRec


    def mostrarRec(self, asignacion, num):
        """
        Almacenamiento en una lista de listas (filas) las relaciones entre  actividades, recursos y unidades de
         recurso necesarias por actividad

        Parámetros: asignacion (lista que almacena actividad, recurso y unid. necesarias por act.)
                    num (0: fichero con extensión '.sm'
                         1: fichero con extensión '.prj')

        Valor de retorno: mostrarR (lista que almacena una lista por cada actividad con la relacion
        actividad-recurso-unidad necesaria)
        """
        mostrarR = []
        i = asignacion.index(asignacion[0])
        # Si el archivo tiene extensión '.sm' (PSPLIB)
        if num == 0:
            i += 2
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
            if num == 0:
                if int(asignacion[n][0]) == m:
                    f='%s(%5.2f)'%(asignacion[n][1], float(asignacion[n][2]))
                    mostrar.append(f)

            # Si el archivo tiene extensión '.prj'
            else:
                if asignacion[n][0] == self.actividad[m][1]:
                    f = '%s(%5.2f)'%(asignacion[n][1], float(asignacion[n][2]))
                    mostrar.append(f)
        m += 1

        return mostrar


    def insertamosSiguiente(self, modelo, path, texto):
        """
        Se inserta una o varias actividades siguientes

        Parámetros: modelo (interfaz)
                    path (fila)
                    texto (nuevo texto a introducir)

        Valor de retorno: -
        """
        if self.actividad[int(path)][2] != []:  # Si hay alguna siguiente colocada
            modelo[path][2] = modelo[path][2] + ', ' + texto
            self.actividad[int(path)][2] = modelo[path][2]
        else:
            modelo[path][2] = texto
            self.actividad[int(path)][2] = modelo[path][2]

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

    def resources2List(self):
        """
         Introduce en una lista todas las etiquetas de los recursos
         Valor de retorno: listaAct (lista de actividades)
        """
        return [n[0] for n in self.recurso]

    def resource_combo_contains(self, resource_name):
        """
        Check whether a resource is already present in the resource assignment combo.
        """
        for row in self.modeloComboARR:
            if row[0] == resource_name:
                return True
        return False

    def update_resource_combo_name(self, old_name, new_name):
        """
        Rename a resource in the resource assignment combo. If the old value is not
        present, the new one is appended so the assignment dialog remains usable.
        """
        for row in self.modeloComboARR:
            if row[0] == old_name:
                row[0] = new_name
                return
        if not self.resource_combo_contains(new_name):
            self.modeloComboARR.append([new_name])

    def remove_resource_from_combo(self, resource_name):
        """
        Remove a resource from the resource assignment combo.
        """
        iterator = self.modeloComboARR.get_iter_first()
        while iterator is not None:
            current = self.modeloComboARR.get_value(iterator, 0)
            if current == resource_name:
                self.modeloComboARR.remove(iterator)
                return
            iterator = self.modeloComboARR.iter_next(iterator)


    def calcularMediaYDTipica(self, distribucion, opt, pes, most): #a, b, m):
        """
         Calculo de la media y la desviación típica a partir de la distribución,
                  del tiempo optimista, pesimista y más probable

          distribucion (tipo de distribución)
          opt (d.optimista)
          pes (d.pesimista)
          most (d.más probable)

         return: (media, dTipica)
        """
        TOLERANCE = 0.0001

        if distribucion == 'Beta':
            media = (opt + 4.0*most + pes) / 6.0
            #dTipica = (pes - opt) / 6.0
            #dTipica = math.sqrt(( 5.0 * (pes - opt)**2 + 8 * ((most-opt)*(pes-most)) ) / (36*7))
            #dTipica = (pes - opt) * math.sqrt(( 5.0 + 8 * (most-opt) * (pes-most) / (pes-opt)**2 ) / (36*7))
            if pes - opt > TOLERANCE:
                shape_a = 1 + 4.0 * (most - opt) / (pes - opt)
                shape_b = 1 + 4.0 * (pes - most) / (pes - opt)
                dTipica = math.sqrt( scipy.stats.beta.var(shape_a, shape_b, loc=opt, scale=(pes-opt)) )
            else:
                dTipica = 0.0

        elif distribucion == 'Triangular':
            media = (opt + most + pes) / 3.0
            dTipica = math.sqrt((opt**2.0 + pes**2.0 + most**2.0 - opt*pes - opt*most - pes*most) / 18.0)

        elif distribucion == 'Uniform':
            media = (opt + pes) / 2.0
            dTipica = math.sqrt(((pes - opt)**2.0) / 12.0)
        else:
            raise Exception('Not expected distribution:' + distribucion)

        # NOTA: La media y la desviación típica de la distribución Normal
        #       no se calculan, se deben introducir manualmente
        # XXX Ver en que casos interesa calcularla y en que casos se recalculan otras casillas.

        return media, dTipica


    def mostrarTextView(self, widget, valor):
        """
        Muestra datos en el Text View correspondiente

        widget (lugar donde mostrar el dato)
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

    def format_zaderenko_cell(self, matrix_value, row_node, column_node, graph_arcs):
        """
        Formatea una celda de la matriz de Zaderenko distinguiendo las
        actividades ficticias de las actividades reales con duracion cero.
        """
        if matrix_value == '':
            return ''

        arc = graph_arcs.get((column_node, row_node))
        if arc is not None and arc[1]:
            return 'F(0)'

        return str(matrix_value)

### FUNCIONES VENTANAS DE ACCIÓN

#          ZADERENKO
    def ventanaZaderenko(self):
        """
        Acción usuario para calcular todos los datos relacionados con Zaderenko
        Valor de retorno: -
        """
        informacionCaminos = []

        grafoRenumerado = self.build_salas_pert_graph()

        nodosN = []
        for n in range(len(grafoRenumerado.successors)):
            nodosN.append(n + 1)

        matrizZad = mZad(self.actividad, grafoRenumerado.arcs, nodosN, 1, [])

        tearly = early(nodosN, matrizZad)
        tlast = last(nodosN, tearly, matrizZad)

        holguras = self.holguras(grafoRenumerado.arcs, tearly, tlast, [])
        actCriticas = self.actCriticas(holguras)
        caminosCriticos = self.grafoCriticas(actCriticas)

        successors = dict(((act[1], act[2]) for act in self.actividad))
        g = graph.roy(successors)
        caminos = [c[1:-1] for c in graph.find_all_paths(g, 'Begin', 'End')]

        criticos = self.caminosCriticos(caminos, caminosCriticos)

        for camino in caminos:
            camino_mostrado = list(reversed(camino))
            media, dTipica = self.mediaYdTipica(camino)
            informacionCaminos.append([camino_mostrado, media, dTipica])


        # Matriz de Zaderenko
        previous_model = self.zadViewList.get_model()
        if previous_model is not None:
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
                row.append(
                    self.format_zaderenko_cell(
                        matrizZad[node][nodes],
                        nodosN[node],
                        nodosN[nodes],
                        grafoRenumerado.arcs,
                    )
                )
            row.append(str(tlast[node]))
            zad_model.append(row)

        column = gtk.TreeViewColumn(_("Early"))
        self.zadViewList.append_column(column)
        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, 'text', 0)
        column.set_min_width(50)

        column = gtk.TreeViewColumn(_("Node"))
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

        column = gtk.TreeViewColumn(_("Last"))
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
                    informacionCaminos (lista caminos del grafo, sus duraciones y sus desviaciones típicas)

        Valor de retorno: -
        """
        caminos_texto = []
        for n in range(len(informacionCaminos)):
            s = ''
            for c in informacionCaminos[n][0]:
                if s != '':
                    s += ' -> '
                s += str(c)
            caminos_texto.append(s)

        modelo.clear()
        for n in range(len(caminos_texto)):
            if criticos[n] == 1:
                modelo.append([
                    str(informacionCaminos[n][1]),
                    str(informacionCaminos[n][2]),
                    caminos_texto[n],
                    True
                ])
            else:
                modelo.append([
                    str(informacionCaminos[n][1]),
                    str(informacionCaminos[n][2]),
                    caminos_texto[n],
                    False
                ])

        self.vistaListaZ.set_model(modelo)

        for column in self.vistaListaZ.get_columns():
            self.vistaListaZ.remove_column(column)

        def colorize_column(column, cell, model, tree_iter, column_index):
            cell.set_property('text', model[tree_iter][column_index])
            if model[tree_iter][3]:
                cell.set_property('cell-background', 'LightCoral')
            else:
                cell.set_property('cell-background-set', False)

        titles = [_("Duration"), _("Typical Dev."), _("Path")]
        self.vistaListaZ.columna = []
        self.vistaListaZ.renderer = []

        for idx, title in enumerate(titles):
            column = gtk.TreeViewColumn(title)
            renderer = gtk.CellRendererText()
            self.vistaListaZ.renderer.append(renderer)
            self.vistaListaZ.columna.append(column)

            column.pack_start(renderer, True)
            column.set_cell_data_func(renderer, colorize_column, idx)
            self.vistaListaZ.append_column(column)



    def actCriticas(self, holguras):
        """
        Identify critical activities

          holguras: [ (nombre_act, total, libre, independiente), ... ]

         return: lista de nombres de las actividades criticas
        """
        TOLERANCE = 0.001
        criticas = []
        for act, total, libre, indep in holguras:
            if -TOLERANCE < total < TOLERANCE:
                criticas.append(act)
        return criticas


    def grafoCriticas(self, actCriticas):
        """
         Creación de un grafo sólo con actividades crí­ticas y extracción de
                  los caminos de dicho grafo, que serán todos crí­ticos

          actCriticas: (lista de actividades crí­ticas)

         Valor de retorno: caminosCriticos (lista de caminos crí­ticos)
        """
        # Se crea un grafo con las activididades crí­ticas y se extraen los caminos de dicho grafo, que serán crí­ticos
        sucesorasCriticas = self.tablaSucesorasCriticas(actCriticas)
        #print sucesorasCriticas, 'sucesorasCriticas'
        gCritico = graph.roy(sucesorasCriticas)
        #print gCritico, 'grafo critico'
        caminosCriticos = []
        caminos = graph.find_all_paths(gCritico, 'Begin', 'End')

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
        cr = []
        for n in criticas:
            cr.append(n)
        #print cr, 'criticas tabla'

        sucesorasCriticas = {}
        for n in cr:
            for m in range(len(self.actividad)):
                if n == self.actividad[m][1]:
                    for a in self.actividad[m][2]:
                        if a in cr:
                            if n not in sucesorasCriticas:
                                sucesorasCriticas[n] = [a]
                            else:
                                sucesorasCriticas[n].append(a)

            if n not in sucesorasCriticas:
                sucesorasCriticas[n] = []

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
        # Se calcula la duración de cada camino.
        d = 0
        for a in camino:
            for n in range(len(self.actividad)):
                if a == self.actividad[n][1] and self.actividad[n][6] != '':
                    d += float(self.actividad[n][6])
                else:  #controlamos las ficticias
                    d += 0

        # Se calcula la desviación típica de cada camino.
        t = 0
        for a in camino:
            for n in range(len(self.actividad)):
                if a == self.actividad[n][1] and self.actividad[n][7] != '':
                    t += float(self.actividad[n][7])**2
                else:  #controlamos las ficticias
                    t += 0
        t = math.sqrt(t)

        return '%5.2f' % (d), '%5.2f' % (t)



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
            modelo.append([str(actividadesGrafo[g][0]), str(g[0]), str(g[1])])

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
        grafoRenumerado = self.build_salas_pert_graph()

        nodosN = []
        for n in range(len(grafoRenumerado.successors)):
            nodosN.append(n + 1)

        matrizZad = mZad(self.actividad, grafoRenumerado.arcs, nodosN, 1, [])

        tearly = early(nodosN, matrizZad)
        tlast = last(nodosN, tearly, matrizZad)

        holguras = self.holguras(grafoRenumerado.arcs, tearly, tlast, [])
        self.mostrarHolguras(self.modeloH, holguras)

        self.vHolguras.hide()
        self.vHolguras.show()



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
        # XXX Pasar a pert.py??
        holguras = []
        for inicio, fin in grafo:
            inicio -= 1
            fin -= 1

            actividades = []
            for n in range(len(self.actividad)):
                actividades.append(self.actividad[n][1])
            #print actividades, 'actividades'

            #print grafo[inicio+1, fin+1]
            if not grafo[inicio+1, fin+1][1]: #XXX quitar [0] in actividades and self.actividad[n][6]!='':
                for n in range(len(self.actividad)):
                    if grafo[inicio+1, fin+1][0]==self.actividad[n][1]:
                        if duraciones==[]: # Es llamada desde cualquier sitio excepto desde simulación
                            t = last[fin] - early[inicio] - float(self.actividad[n][6])
                            l = early[fin] - early[inicio] - float(self.actividad[n][6])
                            i = early[fin] - last[inicio] - float(self.actividad[n][6])
                        else:   # Es llamada desde simulación
                            t = last[fin] - early[inicio] - duraciones[n]
                            l = early[fin] - early[inicio] - duraciones[n]
                            i = early[fin] - last[inicio] - duraciones[n]

            else:  # Si son actividades ficticias (duración 0)
                t = last[fin] - early[inicio]
                l = early[fin] - early[inicio]
                i = early[fin] - last[inicio]


            #holgura = [grafo[inicio+1, fin+1][0], '%5.2f'%(t), '%5.2f'%(l), '%5.2f'%(i)]
            holgura = [grafo[inicio+1, fin+1][0], t, l, i]
            #if grafo[inicio+1, fin+1][0] != 'dummy':
                #print holgura, 'holgura'
            holguras.append(holgura)

        return holguras


    def mostrarHolguras(self, modelo, holguras):
        modelo.clear()
        for n in range(len(holguras)):
            modelo.append([
                str(holguras[n][0]),
                str(holguras[n][1]),
                str(holguras[n][2]),
                str(holguras[n][3]),
            ])


    def indiceCriticidad(self, grafo, duraciones, early, last, itTotales):
        """
        Extrae los caminos crí­ticos, calcula su í­ndice de
                    criticidad y muestra el resultado en la interfaz

        grafo (grafo Pert)
        duraciones (duraciones simuladas)
                early (lista con los tiempos early)
                last (lista con los tiempos last)
        itTotales (iteraciones totales)

        Valor de retorno: -
        """
        #Se extraen los caminos crí­ticos
        holguras = self.holguras(grafo.arcs, early, last, duraciones)  # Holguras de cada actividad
        actCriticas = self.actCriticas(holguras)  # Se extraen las act. crí­ticas
        criticos = self.grafoCriticas(actCriticas) # Se crea un grafo crí­tico y se extraen los caminos

        #print actCriticas, ' actCriticas'

        # Get all paths removing 'begin' y 'end' from each path
        successors = dict(((act[1], act[2]) for act in self.actividad))
        g = graph.roy(successors)
        caminos = [c[1:-1]for c in graph.find_all_paths(g, 'Begin', 'End')]
        #print caminos, ' caminos'

        # Se crea una lista con los caminos críticos de la simulación que son caminos del grafo original
        caminosCriticos = []
        for c in criticos:
            if c in caminos:
                caminosCriticos.append(c)
        #print caminosCriticos, 'caminos criticos'

        # Se pasan todos los caminos a formato cadena
        nuevosCaminos = []
        for c in caminosCriticos:
            s = ''
            for m in c:
                if s != '':
                    s += ' -> '
                    s += str(m)
                else:
                    s += str(m)
            nuevo = [s]
            nuevosCaminos.append(nuevo)
            #print nuevosCaminos, 'formato'

        # Se establece la criticidad de cada camino
        for c in nuevosCaminos:
            if c[0] not in self.criticidad:
                self.criticidad[c[0]] = 1
            else:
                self.criticidad[c[0]] += 1
        #print self.criticidad

        # Se muestran los caminos y el í­ndice de criticidad en la interfaz
        self.modeloC.clear()
        for c in self.criticidad:
            n = self.criticidad[c]
            self.modeloC.append([str(n), str('%3.2f' % ((float(n) / itTotales) * 100)) + '%', str(c)])



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
        modo = sel.get_mode()
        modelo, it = sel.get_selected()
        media = modelo.get_value(it, 0)
        dTipica = modelo.get_value(it, 1)

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
        if dato1 == '': # Si no se introduce el dato1
            x = (float(dato2)-float(media))/float(dTipica)
            p = float(scipy.stats.distributions.norm.cdf(x))


        elif dato2 == '': # Si no se introduce el dato2
            x = (float(dato1)-float(media))/float(dTipica)
            p = float(scipy.stats.distributions.norm.cdf(x))


        else: # Si se introducen los dos datos
            if float(dato1)>float(dato2):
                self.dialogoError(_('The first number must be bigger than the second one.'))
            else:
                x1 = (float(dato1)-float(media))/float(dTipica)
                p1 = float(scipy.stats.distributions.norm.cdf(x1))
                x2 = (float(dato2)-float(media))/float(dTipica)
                p2 = float(scipy.stats.distributions.norm.cdf(x2))
                p = p2-p1

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
        x = 0
        if dato1 == '':
            for n in range(len(intervalos)):
                #print intervalos[n][0], intervalos[n][1], dato2
                if float(intervalos[n][0])<float(dato2):
                    if float(intervalos[n][0])<float(dato2)<float(intervalos[n][1]):
                    #print 'entre'
                        s = self.Fa[n]/float(itTotales)
                        #print s, 's'
                        x += s
                else:
                    s = self.Fa[n]/float(itTotales)
                    #print s, 's'
                    x += s
            #print x, 'suma'

        elif dato2 == '':
            for n in range(len(intervalos)):
                #print intervalos[n][0], intervalos[n][1], dato1
                if float(intervalos[n][1])>float(dato1):
                    if float(intervalos[n][0])<float(dato1)<float(intervalos[n][1]):
                        s = self.Fa[n]/float(itTotales)
                        #print s, 's'
                        x += s
                else:
                    s = self.Fa[n]/float(itTotales)
                    #print s, 's'
                    x += s
            #print x, 'suma'

        else:
            if float(dato1) > float(dato2):
                self.dialogoError(_('The first number must be bigger than the second one.'))
            else:
                for n in range(len(intervalos)):
                    #print intervalos[n][0], dato2, intervalos[n][1], dato1
                    if float(intervalos[n][1])>float(dato1) and float(intervalos[n][0])<float(dato2):
                #print 'entra'
                        s = self.Fa[n]/float(itTotales)
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
        prob = self._widgets.get_widget('tvProbabilidades')
        prob.set_buffer(self.bufer)
        it1 = self.bufer.get_start_iter()
        it2 = self.bufer.get_end_iter()
        textoBufer = self.bufer.get_text(it1, it2)
        #print textoBufer, 'bufer'
        completo = textoBufer + '\n' + dato
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
        probabilidades = self._widgets.get_widget('tvProbabilidades')
        probabilidades.set_buffer(self.bufer)
        it1 = self.bufer.get_start_iter()
        it2 = self.bufer.get_end_iter()
        self.bufer.delete(it1, it2)

        # Se limpian los datos
        valor1 = self._widgets.get_widget('valor1Prob')
        valor1.set_text('')
        valor2 = self._widgets.get_widget('valor2Prob')
        valor2.set_text('')
        valor3 = self._widgets.get_widget('valor3Prob')
        valor3.set_text('')
        resultado1 = self._widgets.get_widget('resultado1Prob')
        resultado1.set_text('')
        resultado2 = self._widgets.get_widget('resultado2Prob')
        resultado2.set_text('')

        # Se elimina el grafico
        if c == 0 and len(self.vBoxProb) > 1:
            self.vBoxProb.remove(self.grafica)
            self.grafica = gtk.Image()
        elif len(self.box) > 0:
            self.vBoxProb.remove(self.box)
            self.box = gtk.VBox()


    def openProject(self, filename):
        """
        Open a project file given by filename
        """
        try:
            data = fileFormats.load_with_some_format(filename, self.fileFormats)

            # If data successfully loaded
            if data:
                self.actividad, schedules, self.recurso, self.asignacion = data
                for res in self.recurso:
                    self.modeloComboARR.append([res[0]])
                    res[1] = _(res[1])

                act_list = []
                dur_dic = {}
                pre_dic = {}

                for act in self.actividad:
                    act_name = str(act[1])
                    act[1] = act_name

                    if isinstance(act[2], (list, tuple)):
                        act[2] = [str(x) for x in act[2]]
                    elif act[2] in ('', None):
                        act[2] = []
                    else:
                        act[2] = [str(act[2])]

                    act_list.append(act_name)
                    dur_dic[act_name] = float(act[6]) if act[6] != '' else 0.0
                    pre_dic[act_name] = act[2]

                    self.gantt.add_activity(act_name, act[2], act[6])
                    self.gantt.set_activity_comment(act_name, act_name)

                min_sched = pert.get_activities_start_time(act_list, dur_dic, pre_dic)
                schedules = [[_('Min'), min_sched]] + schedules

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
                    self.modelo.append([
                        int(act[0]),
                        str(act[1]),
                        ', '.join(map(str, act[2])) if isinstance(act[2], (list, tuple)) else str(act[2]),
                        str(act[3]),
                        str(act[4]),
                        str(act[5]),
                        str(act[6]),
                        str(act[7]),
                        str(act[8]),
                        str(act[9]),
                    ])

                    self.modeloComboS.append([str(act[1])])
                    self.modeloComboARA.append([str(act[1])])
                    if str(act[8]) == 'Normal' and str(act[6]) not in ('', 'None') and str(act[7]) not in ('', 'None'):
                        self.normal_distribution_cache[str(act[1])] = (float(act[6]), float(act[7]))

                # Update interface
                self.openFilename = filename
                self.updateWindowTitle()
                self.set_open_state(True)
                self.set_modified_state(False)
                self._widgets.get_widget('mnGuardarComo').set_sensitive(True)
                self.modelo.append([cont, '', '', '', '', '', '', '', 'Beta', ""])  # Se inserta una fila vacia
                cont += 1
                self.modeloR.append()
                self.modeloAR.append()
                return True
            else:
                self.dialogoError(_('Error reading file:') + filename
                      + ' ' + _('Unknown format'))
                return False

        except IOError:
            self.dialogoError(_('Error reading file:') + filename)
            #traceback.print_exc()
            return False


    def saveProject(self, nombre):
        """
        Saves a project in ppcproject format '.ppc'
        """

        # Here extension should be checked to choose the save format
        # by now we suppose it is .ppc
        if nombre[-4:] != '.ppc':
            nombre = nombre + '.ppc'

        format = fileFormats.PPCProjectFileFormat()

        resources = deepcopy(self.recurso)
        for res in resources:
            if res[1] == _('Renewable'):
                res[1] = 'Renewable'
            elif res[1] == _('Non renewable'):
                res[1] = 'Non renewable'
            elif res[1] == _('Double constrained'):
                res[1] = 'Double constrained'
            else:
                res[1] = 'Unlimited'

        activities = []
        for act in self.actividad:
            if act[6] != '':
                act[6] = float(act[6])
            if act[7] != '':
                act[7] = float(act[7])
            activities.append(act[0:-1])

        try:
            format.save((activities, self.schedules[1:], resources, self.asignacion), nombre)
            # Update interface
            self.openFilename=nombre
            self.updateWindowTitle()
            self.set_modified_state(False)
        except IOError :
            self.dialogoError(_('Error saving the file'))





# --- FUNCIONES DIALOGOS GUARDAR Y ADVERTENCIA/ERRORES #

    def closeProject(self):
        """
        Close the project checking if it has been modified.
        If it has been modified, show a dialog: Save-Discard-Cancel

        Return: True if closed
                False if canceled
        """
        if self.modified == False:  # Project is already saved
            close = True
        else:                       # Project changes need saving
            dialogo = gtk.Dialog(_("Attention!!"),
                                 None,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (_('Discard'), gtk.RESPONSE_CLOSE,
                                  gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_OK )
                                 )
                                 #xxx el dialogo no debe ser modal? Vamos que hasta que el usuario no responda no debe continuar. Corregir mirando doc.
            label = gtk.Label(label=_('Project has been modified. Do you want to save the changes?'))
            dialogo.vbox.pack_start(label, True, True, 10)
            label.show()
            respuesta = dialogo.run()

            if respuesta == gtk.RESPONSE_OK:
                self.saveProject(self.openFilename)
                close = True
            elif respuesta == gtk.RESPONSE_CLOSE:
                close = True
            else:
                close = False

            dialogo.destroy()

        if close:
            # Se limpian todas las listas de datos
            self.openFilename = None
            self.modelo.clear()
            self.actividad = []
            self.modeloR.clear()
            self.recurso = []
            self.modeloAR.clear()
            self.asignacion = []
            self.updateWindowTitle()
            self.gantt.clear()
            self.gantt.update()
            self.modeloComboS.clear()
            self.modeloComboARA.clear()
            self.modeloComboARR.clear()
            while self.ntbSchedule.get_current_page() != -1:
                self.clicked_tab = len(self.schedule_tab_labels) - 1
                self.on_mnTabsDelete_activate(None)
            self.schedules = []
            self.set_open_state(False)
            self.set_modified_state(False)
            self.ntbSchedule.hide()

        return close


    def dialogoRec(self, tipo):
        """
        Muestra un mensaje de advertencia si no se han introducido bien las unidades de recurso

        Parámetros: tipo (tipo de recurso)
        """
        dialogo = gtk.Dialog(_("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        # Si el recurso es Renovable, las unidades deben ser 'por periodo'
        if tipo == _('Renewable'):
            label = gtk.Label(label=_('Renember that the resource is "Renewable"'))
        # Si el recurso es No Renovable, las unidades deben ser 'por proyecto'
        else:
            label = gtk.Label(label=_('Renember that the resource is "Non Renewable"'))
        dialogo.vbox.pack_start(label,True,True,10)
        label.show()
        respuesta = dialogo.run()

        dialogo.destroy()


    def dialogoError(self, cadena):
        """
        Muestra un mensaje de error en la apertura del fichero
        """
        dialogo=gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                                  message_format = cadena,
                                  buttons = gtk.BUTTONS_OK)
        respuesta=dialogo.run()
        dialogo.destroy()


    def errorActividadesRepetidas(self, repetidas):
        """
        Muestra un mensaje de error si en la introducción de datos hay alguna actividad repetida

        Parámetros: repetidas (lista con las actividades repetidas)
        """
        dialogo=gtk.Dialog(_("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        for actividad in repetidas:
            label=gtk.Label(_('The activity ')+' "'+actividad+'"'+_(' is repeated\n'))
            dialogo.vbox.pack_start(label,True,True,5)
            label.show()
        respuesta=dialogo.run()

        dialogo.destroy()


    def errorRecNecAct(self, datosErroneos, cadena):
        """
        Muestra un mensaje de error si en la ventana 'recursos necesarios por actividad' hay alguna
        actividad o algun recurso inexistente

        Parámetros: datosErroneos (lista con los datos erróneos) cadena (cadena de texto)
        """
        dialogo=gtk.Dialog(_("Error!!"), None, gtk.MESSAGE_QUESTION, (gtk.STOCK_OK, gtk.RESPONSE_OK ))
        for dato in datosErroneos:
            label=gtk.Label(cadena+' "'+dato+'"'+ _(' does not exist\n'))
            dialogo.vbox.pack_start(label,True,True,5)
            label.show()
        respuesta=dialogo.run()

        dialogo.destroy()

    def treeview_menu_invoked(self, widget, event, treeview):
        """
        Treeview menu invoked
        """
        if (treeview.get_selection().count_selected_rows() != 0 and
            treeview.get_model()[treeview.get_selection().get_selected_rows()[1][0]][1] != ""):
            if event.button == 3:
                self._widgets.get_widget("ctxTreeviewMenu").popup(None, None, None, event.button, event.time)
            self.treemenu_invoker = treeview

    def delete_activity(self, widget=None):
        """
        Delete an activity when pressed Supr. or context menu
        """
        # XXX This function is created to avoid a bug
        #     The mess of delete_tree_row function below should be fixed with one function to delete
        #         each specific thing
        #     As links from Glade are not fixed delete_tree_row is still called from context menu
        gantt_modified = False
        path = self.interface.main_table_treeview.get_selection().get_selected_rows()[1][0]
        model = self.interface.main_table_treeview.get_model()

        for index in range(len(self.actividad)-1,-1, -1):
            if model[path][1] in self.actividad[index][2]:
                self.actividad[index][2].remove(model[path][1])
                model[index][2] = ", ".join(self.actividad[index][2])
            if self.actividad[index][1] == model[path][1]:
                del self.actividad[index]
        for index in range(len(self.asignacion)-1,-1, -1):
            if self.asignacion[index][1] == model[path][1]:
                del self.asignacion[index]
            if self._widgets.get_widget('vistaListaAR').get_model()[index][1] == model[path][0]:
                self._widgets.get_widget('vistaListaAR').get_model().remove(self._widgets.get_widget('vistaListaAR').get_model().get_iter(index))

        self.gantt.remove_activity(model[path][1])
        gantt_modified = True

        it = self.modeloComboS.get_iter(path)
        self.modeloComboS.remove(it)  # Remove the activity of the comboBox (Next)
        it = self.modeloComboARA.get_iter(path)
        self.modeloComboARA.remove(it)  # Remove the activity of the comboBox (Resources view)

        model.remove(model.get_iter(path))
        self.reorder_activities()

        if gantt_modified == True:
            act_list = []
            dur_dic = {}
            pre_dic = {}
            for i in range(len(self.actividad)):
                act_list.append(self.actividad[i][1])
                dur_dic[self.actividad[i][1]] = float(self.actividad[i][6] if self.actividad[i][6] != "" else 0)
                pre_dic[self.actividad[i][1]] = self.actividad[i][2]
            self.schedules[0][1] = pert.get_activities_start_time(act_list, dur_dic, pre_dic, True,
                                                                   self.schedules[0][1])
            for index in range(1, len(self.schedules)):
                self.schedules[index][1] = pert.get_activities_start_time(act_list, dur_dic, pre_dic, False,
                                                                           self.schedules[index][1])
            self.set_schedule(self.schedules[self.ntbSchedule.get_current_page()][1])
        self.set_modified_state(True)



    def delete_tree_row(self, widget=None):
        """
        Delete treeview row
        """
        gantt_modified = False
        path = self.treemenu_invoker.get_selection().get_selected_rows()[1][0]
        model = self.treemenu_invoker.get_model()
        if self.treemenu_invoker == self.interface.main_table_treeview:
            for index in range(len(self.actividad)-1,-1, -1):
                if model[path][1] in self.actividad[index][2]:
                    self.actividad[index][2].remove(model[path][1])
                    model[index][2] = ", ".join(self.actividad[index][2])
                if self.actividad[index][1] == model[path][1]:
                    del self.actividad[index]
            for index in range(len(self.asignacion)-1,-1, -1):
                if self.asignacion[index][1] == model[path][1]:
                    del self.asignacion[index]
                if self._widgets.get_widget('vistaListaAR').get_model()[index][1] == model[path][0]:
                    self._widgets.get_widget('vistaListaAR').get_model().remove(self._widgets.get_widget('vistaListaAR').get_model().get_iter(index))

            self.gantt.remove_activity(model[path][1])
            gantt_modified = True

            it = self.modeloComboS.get_iter(path)
            self.modeloComboS.remove(it)  # Remove the activity of the comboBox (Next)
            it = self.modeloComboARA.get_iter(path)
            self.modeloComboARA.remove(it)  # Remove the activity of the comboBox (Resources view)

        elif self.treemenu_invoker == self._widgets.get_widget('vistaListaRec'):
            resource_name = model[path][0]
            for index in range(len(self.recurso)-1,-1, -1):
                if self.recurso[index][0] == resource_name:
                    del self.recurso[index]
            for index in range(len(self.asignacion)-1,-1, -1):
                if self.asignacion[index][1] == resource_name:
                    del self.asignacion[index]
            assignment_model = self._widgets.get_widget('vistaListaAR').get_model()
            for index in range(len(assignment_model)-1, -1, -1):
                if assignment_model[index][1] == resource_name:
                    assignment_model.remove(assignment_model.get_iter(index))
            self.remove_resource_from_combo(resource_name)

        else:
            for index in range(len(self.asignacion)-1,-1, -1):
                if self.asignacion[index][0] == model[path][0] and self.asignacion[index][1] == model[path][1]:
                    del self.asignacion[index]

        model.remove(model.get_iter(path))
        if self.treemenu_invoker == self.interface.main_table_treeview:
            self.reorder_activities()
        if gantt_modified == True:
            act_list = []
            dur_dic = {}
            pre_dic = {}
            for i in range(len(self.actividad)):
                act_list.append(self.actividad[i][1])
                dur_dic[self.actividad[i][1]] = float(self.actividad[i][6] if self.actividad[i][6] != "" else 0)
                pre_dic[self.actividad[i][1]] = self.actividad[i][2]
            self.schedules[0][1] = pert.get_activities_start_time(act_list, dur_dic, pre_dic, True,
                                                                   self.schedules[0][1])
            for index in range(1, len(self.schedules)):
                self.schedules[index][1] = pert.get_activities_start_time(act_list, dur_dic, pre_dic, False,
                                                                           self.schedules[index][1])
            self.set_schedule(self.schedules[self.ntbSchedule.get_current_page()][1])
        self.set_modified_state(True)

    def reorder_activities(self):
        """
        Reorder numbers of activities.

        Returns: None.
        """
        it = self.modelo.get_iter_first()
        actNumber = 1
        while it != None:
            self.modelo.set_value(it, 0, actNumber)
            it = self.modelo.iter_next(it)
            actNumber = actNumber + 1


# MANEJADORES #
# --- Menu actions

# File menu actions
    def on_New_activate(self, item):
        """ User ask for new file (from menu or toolbar) """
        self.closeProject()
        self.introduccionDatos()

    def on_Open_activate(self, item):
        """ User ask for open file (from menu or toolbar)
        """

        # Dialog asking for file to open
        dialogoFicheros = gtk.FileChooserDialog(_("Open File"),
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
        ffilter.set_name(''.join([_('All project files') + ' (', ', '.join(pats), ')']))
        dialogoFicheros.add_filter(ffilter)

        # Creates a filter for each supported file format
        for format in self.fileFormats:
            ffilter = gtk.FileFilter()
            for pat in format.filenamePatterns():
                ffilter.add_pattern(pat)
            ffilter.set_name( str(format) )
            dialogoFicheros.add_filter(ffilter)

        # Creates the filter allowing to see all files
        ffilter = gtk.FileFilter()
        ffilter.add_pattern('*')
        ffilter.set_name(_('All files'))
        dialogoFicheros.add_filter(ffilter)

        opened = False
        resultado = gtk.RESPONSE_OK

        # The Dialog window will close after opening a project or click "Cancel"
        while(opened == False and resultado == gtk.RESPONSE_OK):
            dialogoFicheros.set_default_response(gtk.RESPONSE_OK)
            resultado = dialogoFicheros.run()
            if resultado == gtk.RESPONSE_OK:
                # Close open project if any
                closed = self.closeProject()
                if closed:
                    filename = dialogoFicheros.get_filename()
                    opened = self.openProject(filename)
        dialogoFicheros.destroy()

    def on_Save_activate(self, item):
        """
        Save option invoked

        Parameters: item

        Returns: -
        """
        # Se comprueba que no haya actividades repetidas (XXX esto debe ir aqui?)
        errorActRepetidas, actividadesRepetidas=self.actividadesRepetidas(self.actividad)

        if errorActRepetidas==0:
            if self.openFilename=='Unnamed':
                self.on_SaveAs_activate(item)
            else:
                self.saveProject(self.openFilename)
        else:
            self.errorActividadesRepetidas(actividadesRepetidas)

    def on_SaveAs_activate(self, menu_item):
        """
        Save as option invoked

        Parameters: menu_item

        Returns: -
        """
        # Se comprueba que no haya actividades repetidas (xxx esto debe ir aqui?)
        errorActRepetidas, actividadesRepetidas = self.actividadesRepetidas(self.actividad)
        if errorActRepetidas == 0:
            destination_dialog = gtk.FileChooserDialog(_("Save as"),
                                                   None,
                                                   gtk.FILE_CHOOSER_ACTION_SAVE,
                                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_SAVE, gtk.RESPONSE_OK))
            destination_dialog.set_default_response(gtk.RESPONSE_OK)
            resultado = destination_dialog.run()

            if resultado == gtk.RESPONSE_OK:
                self.openFilename = destination_dialog.get_filename()
                self.saveProject(self.openFilename)
            destination_dialog.destroy()
        else:
            self.errorActividadesRepetidas(actividadesRepetidas)


    def on_Close_activate(self, menu_item):
        """
        Close option invoked
        """
        self.closeProject()

    def on_Exit_activate(self, *args):
        """
        Exit option invoked
        """
        closed = self.closeProject()
        if closed:
            #XXX Salir propiamente??
            gtk.main_quit()
            return False
        else:
            return True

# View menu actions

    def on_bHerramientas_activate(self, checkMenuItem):
        """
        Acción usuario para activar o desactivar la barra
        de herramientas, inicialmente inactiva
        """
        checkMenuItem == self.bHerramientas
        if checkMenuItem.get_active():
            self.bHerramientas.show()
        else:
            self.bHerramientas.hide()

    def on_mnPantallaComp_activate(self, menu_item):
        """
        Full screen option invoked
        """
        self.vPrincipal.fullscreen()
        self._widgets.get_widget('mnSalirPantComp').show()
        self._widgets.get_widget('mnPantallaComp').hide()

    def on_mnSalirPantComp_activate(self, menu_item):
        """
        Exit full screen option invoked
        """
        self.vPrincipal.unfullscreen()
        self._widgets.get_widget('mnSalirPantComp').hide()
        self._widgets.get_widget('mnPantallaComp').show()

# Menu actions

    def on_mnCrearRecursos_activate(self, menu_item):
        """
        Create resources option invoked
        """
        self.vRecursos.show()

    def on_mnGrafo_activate(self, menu_item):
        """
        Some drawing Graph menu option invoked
        """
        successors = self.build_successors_from_prelations()
        durations = dict((str(act[1]), float(act[6]) if act[6] != '' else 0.0) for act in self.actividad)

        if menu_item == self._widgets.get_widget('grafoRoy'):
            roy = graph.roy(successors)
            svg_text = graph.graph2image(roy)
            title = 'Roy graph'

        elif menu_item == self._widgets.get_widget('algoritmoSharma'):
            grafo = algoritmoSharma.sharma1998ext(graph.successors2precedents(successors))
            grafoRenumerado = grafo.renumerar()
            svg_text = graph.pert2image(grafoRenumerado)
            title = 'PERT graph Sharma'

        elif menu_item == self._widgets.get_widget('algoritmoConjuntos'):
            grafo = algoritmoConjuntos.algoritmoN(graph.successors2precedents(successors))
            svg_text = graph.pert2image(grafo)
            title = 'PERT-Conjuntos graph'

        elif menu_item == self._widgets.get_widget('algoritmoCohenSadeh'):
            grafo = algoritmoCohenSadeh.cohen_sadeh(graph.successors2precedents(successors))
            svg_text = graph.pert2image(grafo)
            title = 'PERT-CohenSadeh graph'

        elif menu_item == self._widgets.get_widget('algoritmoGentoMunicio'):
            grafo = algoritmoGentoMunicio.gento_municio(graph.successors2precedents(successors))
            svg_text = graph.pert2image(grafo)
            title = 'PERT-GentoMunicio graph'

        elif menu_item == self._widgets.get_widget('algoritmoGentoMunicioT'):
            grafo = algoritmoGentoMunicio.gento_municio(graph.successors2precedents(successors))
            grafo = timedpert.TimedPert((grafo.successors, grafo.arcs), durations)
            svg_text = grafo.timedpert2image()
            title = 'PERT-GentoMunicio graph T'

        elif menu_item == self._widgets.get_widget('algoritmoSalas'):
            grafo = algoritmoSalas.salas(graph.successors2precedents(successors))
            svg_text = graph.pert2image(grafo)
            title = 'PERT-Salas graph'

        elif menu_item == self._widgets.get_widget('algoritmoMouhoub'):
            grafo = algoritmoMouhoub.mouhoub(graph.successors2precedents(successors))
            svg_text = graph.pert2image(grafo)
            title = 'PERT-Mouhoub'

        elif menu_item == self._widgets.get_widget('algoritmoSysloOp'):
            grafo = algoritmoSysloOptimal.sysloOptimal(graph.successors2precedents(successors))
            svg_text = graph.pert2image(grafo)
            title = 'PERT-Syslo optimal'

        elif menu_item == self._widgets.get_widget('algoritmoSysloPo'):
            grafo = algoritmoSysloPolynomial.sysloPolynomial(graph.successors2precedents(successors))
            svg_text = graph.pert2image(grafo)
            title = 'PERT-Syslo optimal'

        else:
            raise Exception('Graph menu option not recognized:' + menu_item.get_label())

        graph_window = interface.GraphWindow(svg_text, title)   
        
    def build_successors_from_prelations(self):
        """
        Construye el diccionario de sucesores a partir de las predecesoras
        almacenadas en self.actividad.
        """
        successors = {}

        for act in self.actividad:
            act_name = str(act[1])
            successors[act_name] = []

        for act in self.actividad:
            act_name = str(act[1])
            predecessors = act[2]

            if isinstance(predecessors, (list, tuple)):
                for pred in predecessors:
                    pred_name = str(pred)
                    if pred_name not in successors:
                        successors[pred_name] = []
                    successors[pred_name].append(act_name)
            elif predecessors not in ('', None):
                pred_name = str(predecessors)
                if pred_name not in successors:
                    successors[pred_name] = []
                successors[pred_name].append(act_name)

        return successors

    def build_reference_pert_graph(self):
        """
        Construye el grafo PERT de referencia para los calculos de Zaderenko,
        holguras y actividades. Se usa Cohen-Sadeh por indicacion docente.
        """
        successors = self.build_successors_from_prelations()
        return algoritmoCohenSadeh.cohen_sadeh(graph.successors2precedents(successors))

    def build_salas_pert_graph(self):
        """
        Compatibilidad con llamadas existentes: devuelve el grafo PERT de
        referencia actualmente seleccionado.
        """
        return self.build_reference_pert_graph()




    def on_mnActividades_activate(self, menu_item):
        """ User ask for activities in PERT graph """
        # Se crea el grafo Pert y se renumera
        grafoRenumerado = self.build_salas_pert_graph()

        # Se muestran las actividades y su nodo inicio y fí­n
        self.mostrarActividades(self.modeloA, grafoRenumerado.arcs, grafoRenumerado.successors)

    def on_mnZaderenko_activate(self, menu_item):
        """
        Zaderenko option invoked
        """
        s=0
        for a in self.actividad:
            if a[6]=='':
                s+=1
        if s>0:
            self.dialogoError(_('There are uncomplete activities'))
        else:
            self.ventanaZaderenko()

    def on_mnHolguras_activate(self, menu_item):
        """ User ask for slacks """
        s = 0
        for a in self.actividad:
            if a[6] == '':
                s += 1

        if s > 0:
            self.dialogoError(_('There are uncomplete activities'))
        else:
            self.ventanaHolguras()

    def on_mnSimulacion_activate(self, menu_item):
        """Acción usuario para acceder a la ventana que muestra
        los resultados de la simulación de duraciones (tabla
        de frecuencias, gráfica, ...)
        """
        s = 0
        m = 0
        u = 0

        for a in self.actividad:
            #name, followers, op, mode, pes, avg, dev, dist = a    #[3:6]

            #if (a[8] == 'Uniform' or a[8] == 'Beta' or #XXX ... es a[8] ponia a[9] ???   #Avanzado, mirar: NamedTuple
                #a[8] == 'Triangular'):
            if a[8] == 'Beta' or a[8] == 'Triangular':
                if a[3]=='' or a[4]=='' or a[5]=='':
                    s+=1
            elif a[8] == 'Uniform':
                if a[3]=='' or a[5]=='':
                    u+=1
            else: #Si no es ninguna de las tres anteriores es la Normal
                if a[6]=='' or a[7]=='':
                    m=+1

        if s > 0 and m == 0:
            self.dialogoError(_('You must introduce the durations: 1') + '\n' + '\t' +
                              _('- Optimistic') + '\n' + '\t' + _('- Most probable') +
                              '\n' + '\t' + _('- Pessimistic'))
        elif u > 0 and m == 0:
            self.dialogoError(_('You must introduce the durations: unifome') + '\n' + '\t' +
                              _('- Optimistic') + '\n' + '\t' + _('- Pessimistic'))
        elif s == 0 and m > 0:
            self.dialogoError(_('You must introduce the durations: 2') + '\n' + '\t' +
                              _('- Average') + '\n' + '\t' + _('- Typical Dev.'))
        elif s > 0 and m > 0:
            self.dialogoError(_('You must introduce the durations: 3') + '\n' + '\t' +
                              _('- Optimistic')+ '\n' + '\t' + _('- Most probable') +
                              '\n' + '\t' + _('- Pessimistic') + '\n' + '\t' +
                              _('- Average') + '\n' + '\t' + _('- Typical Dev.'))
        else:
            self._widgets.get_widget('btProbSim').set_sensitive(False)
            self._widgets.get_widget('btGuardarSim').set_sensitive(False)
            self._widgets.get_widget('btKS').set_sensitive(False)
            self._widgets.get_widget('iOpcion').set_active(0)
            self._widgets.get_widget('iValor').set_text('100')
            self.vSimulacion.show()
            self.simTotales = [] # Lista con las simulaciones totales
            self.duraciones = [] # Lista con las duraciones de las simulaciones
            self.criticidad = {} # Diccionario con los caminos y su í­ndice de criticidad
            self.intervalos = [] # Lista con los intervalos de las duraciones



    def on_mnCalcularCaminos_activate(self, menu_item):
        """ User ask for paths in project """
        if self.actividad == []:
            self.dialogoError(_('A graph is needed to calculate its paths'))
        else:
            successors = dict(((act[1], act[2]) for act in self.actividad))
            roy = graph.roy(successors)

            caminosSinBeginEnd = [c[1:-1] for c in graph.find_all_paths(roy, 'Begin', 'End')]

            numeroCaminos = len(caminosSinBeginEnd)
            camino = _('Number of paths: ') + str(numeroCaminos) + '\n'
            for n in range(len(caminosSinBeginEnd)):
                cadena = ', '.join(map(str, reversed(caminosSinBeginEnd[n])))
                camino += cadena
                camino += '\n'

            self.vCaminos.show()
            widget = self._widgets.get_widget('tvCaminos')
            self.mostrarTextView(widget, camino)



    def on_wndSimAnnealing_delete_event(self, window, event):
        """
        User action to close the window
        """
        self.btResetSA.clicked()
        window.hide()
        return True

    def on_btnSaveSA_clicked (self, menu_item):
        """
        Save the schedule calculated
        """
        optSchDic = {}
        if self.optimumSchedule == []:
            self.dialogoError(_('There is no schedule.'))
            return False
        else:
            for act,startTime,endTime in self.optimumSchedule:
                optSchDic[act] = startTime
        self.add_schedule(None, optSchDic)

    def on_rbAllocation_pressed (self, menu_item):
        """
        Choose allocation
        """
        self.sbSlackSA.set_sensitive(False)

    def on_rbLeveling_pressed (self, menu_item):
        """
        Choose leveling
        """
        self.sbSlackSA.set_sensitive(True)

    def on_cbIterationSA_toggled (self, menu_item):
        """
        Choose unlimited number of iterations without improve
        """
        if self.get_selected_resource_algorithm() != 'annealing':
            self.sbNoImproveIterSA.set_sensitive(False)
            return

        if self.cbIterationSA.get_active():
            self.sbNoImproveIterSA.set_sensitive(False)
        else:
            self.sbNoImproveIterSA.set_sensitive(True)

    def on_mnSimAnnealing_activate(self, menu_item):
        """
        User action to open the simulated annealing window
        """
        self.wndSimAnnealing.show()

    def on_btnSimAnnealingReset_clicked(self,menu_item):
        """
        User action to restart the values of the simulated annealing window fields
        """
        self.ganttActLoaded = False
        self.ganttSA.clear()
        self.loadSheet.clear()
        self.loadTable.clear()
        self.ganttSA.update()
        self.loadSheet.update()
        self.loadTable.update()
        self.entryResultSA.set_text('')
        self.entryMaxTempSA.set_text('')
        self.entryAlpha.set_text('')
        self.cbIterationSA.set_active(False)
        self.sbPhi.set_value(0.9)
        self.sbNu.set_value(0.9)
        self.sbMinTempSA.set_value(0.01)
        self.sbNoImproveIterSA.set_value(100)
        self.sbMaxIterationSA.set_value(100)
        self.sbExecuteTimesSA.set_value(1)
        self.sbSlackSA.set_value(0)
        if self.resource_algorithm_combo is not None:
            self.resource_algorithm_combo.set_active_id('professor_crosl')
            self.on_resource_algorithm_changed(self.resource_algorithm_combo)


    def on_btnSimAnnealingCalculate_clicked(self, menu_item):
        """
        User action to start the simulated annealing algorithm
        """
        self.ganttActLoaded = False
        self.ganttSA.clear()
        self.loadSheet.clear()
        self.loadTable.clear()
        self.ganttSA.update()
        self.loadSheet.update()
        self.loadTable.update()
        self.entryResultSA.set_text('')
        self.entryMaxTempSA.set_text('')
        self.entryAlpha.set_text('')
        self.entryIterations.set_text('')
        self.update_crosl_summary_panel(None)

        rest = {}
        for a in self.actividad:
            if a[6] == '':
                self.dialogoError(_('You must introduce the average duration.'))
                return False
            rest[str(a[1])] = [float(a[6])]

        if self.rbLeveling.get_active():
            leveling = 1
        else:
            leveling = 0

        resources = resources_availability(self.recurso)
        if leveling == 1 and resources == {}:
            self.dialogoError(_('There are not renewable or double constrained resources introduced'))
            return False

        asignation = resources_per_activities(self.asignacion, resources)
        successors = self.build_successors_from_prelations()
        activities = self.altered_last(rest)

        if activities == {}:
            self.dialogoError(_('There are no activities'))
            return False

        crosl_max_project_duration = None
        if self.get_selected_resource_algorithm() == 'professor_crosl':
            crosl_max_project_duration = max(
                [
                    float(activity_data[0]) + float(activity_data[1])
                    for activity_data in activities.values()
                    if len(activity_data) > 1
                ]
                or [0.0]
            )

        phi = self.sbPhi.get_value()
        nu = self.sbNu.get_value()
        minTemperature = self.sbMinTempSA.get_value()
        maxIteration = self.sbMaxIterationSA.get_value()
        times = self.sbExecuteTimesSA.get_value()

        if self.cbIterationSA.get_active():
            noImproveIter = -1
        else:
            noImproveIter = self.sbNoImproveIterSA.get_value()

        resource_algorithm = self.get_selected_resource_algorithm()
        crosl_population_history_file = None
        crosl_generation_history_file = None
        crosl_elite_file = None
        crosl_force_project_duration = False
        crosl_use_elite_seeds = True
        crosl_parameters = {}
        if resource_algorithm == 'professor_crosl':
            if self.crosl_force_duration_check is not None:
                crosl_force_project_duration = self.crosl_force_duration_check.get_active()
            if self.crosl_use_elite_seeds_check is not None:
                crosl_use_elite_seeds = self.crosl_use_elite_seeds_check.get_active()
            crosl_parameters = self.get_crosl_parameters_from_interface()
            results_dir = os.path.join(os.path.dirname(__file__), 'crosl_results')
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            crosl_population_history_file = os.path.join(
                results_dir,
                'crosl_population_history_%s.csv' % timestamp,
            )
            crosl_generation_history_file = os.path.join(
                results_dir,
                'crosl_generation_history_%s.csv' % timestamp,
            )
            if crosl_use_elite_seeds:
                crosl_elite_file = os.path.join(results_dir, 'crosl_elite_seeds.csv')

        if minTemperature <= 0:
            self.dialogoError(_('Minimum temperature must be greater than 0'))
            return False

        if maxIteration <= 0:
            self.dialogoError(_('Maximum iterations must be greater than 0'))
            return False

        if times <= 0:
            self.dialogoError(_('Execute times must be greater than 0'))
            return False

        if resource_algorithm == 'annealing' and noImproveIter != -1 and noImproveIter <= 0:
            self.dialogoError(_('No improve iterations must be greater than 0'))
            return False

        def run_resource_optimizer(run_index=0):
            if resource_algorithm in ('classic', 'crosl', 'professor_crosl'):
                return project_coral(
                    asignation,
                    resources,
                    successors,
                    activities,
                    leveling,
                    mode=resource_algorithm,
                    reef_size=30,
                    n_generations=int(maxIteration),
                    larvae_per_generation=20,
                    mutation_rate=0.25,
                    crossover_mode='random',
                    sexual_rate=0.7,
                    predation_rate=0.1,
                    f_a=0.1,
                    seed=42 + run_index,
                    population_history_file=crosl_population_history_file,
                    population_history_run_id=run_index,
                    generation_history_file=crosl_generation_history_file,
                    elite_file=crosl_elite_file,
                    initialization_file=(
                        crosl_elite_file
                        if crosl_elite_file and os.path.exists(crosl_elite_file)
                        else None
                    ),
                    max_project_duration=crosl_max_project_duration,
                    force_project_duration=crosl_force_project_duration,
                    crosl_parameters=crosl_parameters,
                    use_elite_seeds=crosl_use_elite_seeds,
                )

            return simulated_annealing(
                asignation,
                resources,
                successors,
                activities,
                leveling,
                nu,
                phi,
                minTemperature,
                maxIteration,
                noImproveIter
            )

        self.optimumSchedule, optSchEvaluated, optSchDuration, optSchAlpha, optSchTemp, optSchIt = run_resource_optimizer(0)
        best_crosl_summary = get_last_crosl_summary() if resource_algorithm == 'professor_crosl' else None

        if optSchDuration == 0:
            self.dialogoError(_('Project\'s duration = 0'))
            return False

        if self.optimumSchedule is not None:
            if not self.ganttActLoaded:
                self.ganttActLoaded = True
                self.ganttSA.clear()
                for a in self.actividad:
                    self.ganttSA.add_activity(str(a[1]), [], float(a[6]), 0, 0, 'Activity: ' + str(a[1]))

            for a in range(0, int(times - 1)):
                schedule, schEvaluated, schDuration, schAlpha, schTemp, schIt = run_resource_optimizer(a + 1)
                run_crosl_summary = get_last_crosl_summary() if resource_algorithm == 'professor_crosl' else None

                if optSchEvaluated > schEvaluated:
                    self.optimumSchedule = schedule
                    optSchEvaluated = schEvaluated
                    optSchDuration = schDuration
                    optSchAlpha = schAlpha
                    optSchTemp = schTemp
                    optSchIt = schIt
                    best_crosl_summary = run_crosl_summary

            self.entryResultSA.set_text(str(optSchDuration))
            if resource_algorithm == 'annealing':
                self.entryAlpha.set_text(str(optSchAlpha))
                self.entryMaxTempSA.set_text(str(optSchTemp))
                self.update_crosl_summary_panel(None)
            else:
                self.entryAlpha.set_text(str(round(optSchEvaluated, 4)))
                self.entryMaxTempSA.set_text(self.resource_algorithm_labels.get(resource_algorithm, resource_algorithm))
                self.update_crosl_summary_panel(best_crosl_summary)
            self.entryIterations.set_text(str(optSchIt))

            resources = resources_availability(self.recurso, True)
            asignation = resources_per_activities(self.asignacion, resources)
            optSchLoadSheet = calculate_loading_sheet(self.optimumSchedule, resources, asignation, optSchDuration)
            displayed_load_sheet = optSchLoadSheet
            if resource_algorithm == 'professor_crosl' and best_crosl_summary:
                optimized_resources = set(
                    best_crosl_summary.get('optimized_resources', [])
                )
                if optimized_resources:
                    displayed_load_sheet = {
                        resource: loading
                        for resource, loading in optSchLoadSheet.items()
                        if resource in optimized_resources
                    }
            predecessors = graph.successors2precedents(successors)

            for act, startTime, finalTime in self.optimumSchedule:
                act_name = str(act)
                self.ganttSA.set_activity_start_time(act_name, startTime)
                self.ganttSA.set_activity_prelations(act_name, predecessors.get(act_name, []))

            self.ganttSA.update()

            if asignation != {}:
                self.loadSheet.set_loading(displayed_load_sheet)
                self.loadSheet.set_duration(optSchDuration)
                self.loadSheet.update()

                self.loadTable.set_loading(displayed_load_sheet)
                self.loadTable.set_duration(optSchDuration)
                self.loadTable.update()
        else:
            self.dialogoError(_('Initial temperature not high enough.'))
            return False


    def altered_last(self,rest):
        """
        Calculate last time modified

        Parameters: rest (activities in the project)

        Returns: rest (dictionary of the activities and their characteristics (duration, last time))
        """
        slack = self.sbSlackSA.get_value()
        predecessors = {}
        successors = {}

        for act in self.actividad:
            act_name = str(act[1])
            successors.setdefault(act_name, [])
            if isinstance(act[2], (list, tuple)):
                pred_list = [str(pred) for pred in act[2] if pred != '']
            elif act[2] in ('', None):
                pred_list = []
            else:
                pred_list = [str(act[2])]

            predecessors[act_name] = pred_list
            for pred in pred_list:
                successors.setdefault(pred, [])
                successors[pred].append(act_name)

        early_finish = {}

        def get_early_finish(act_name):
            if act_name in early_finish:
                return early_finish[act_name]
            early_start = max([get_early_finish(pred) for pred in predecessors.get(act_name, [])] or [0])
            early_finish[act_name] = early_start + float(rest[act_name][0])
            return early_finish[act_name]

        project_duration = max([get_early_finish(act_name) for act_name in rest] or [0])
        latest_start = {}

        def get_latest_start(act_name):
            if act_name in latest_start:
                return latest_start[act_name]
            if successors.get(act_name):
                latest_finish = min(get_latest_start(successor) for successor in successors[act_name])
            else:
                latest_finish = project_duration
            latest_start[act_name] = latest_finish - float(rest[act_name][0])
            return latest_start[act_name]

        for act_name in rest:
            rest[act_name] += [get_latest_start(act_name) + slack]

        return rest



# Help menu actions

    def on_mnAyuda_activate(self, menu_item):
        """
        Help option invoked
        """
        dialogoAyuda = self.dAyuda
        dialogoAyuda.show()


# --- Window actions

    def on_wndGrafoPert_delete_event(self, window, event):
        """
        Close Pert Window
        """
        window.hide()
        return True

    def on_wndGrafoRoy_delete_event(self, window, event):
        """
        Close Roy Window
        """
        window.hide()
        return True


# ACTIVIDADES window

    def on_btAceptarAct_clicked(self, boton):
        """
         Acción usuario para acceder aceptar los datos
                  que aparecen en la ventana de actividades
        """
        self.vActividades.hide()

    def on_wndActividades_delete_event(self, ventana, evento):
        """
         Acción usuario para acceder cerrar la ventana de actividades
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

        boton (botón clickeado)
        """
        # Extraigo los valores de la media y la desviación típica del camino que va a ser objeto del
        # cálculo de probabilidades
        media, dTipica = self.extraerMediaYDTipica()

        if float(dTipica) == 0.00:
            texto=_('Path duration is ') + '%5.2f' % (float(media)) + _(' t.u. with 100% probability')
            self.dialogoError(texto)
        else:
            # Se asigna tí­tulo y gráfica a la ventana de probabilidad
            self.vProbabilidades.set_title(_('Probability related to the path'))
            #imagen = self._widgets.get_widget('graficaProb')
            if len(self.vBoxProb)>1:
                self.vBoxProb.remove(self.grafica)
                self.grafica = gtk.Image()

            # XXX We should generate the picture with the same tool than used for interval distribution
            self.grafica.set_from_file(os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),
                                                    'graficaNormal.gif'))
            self.vBoxProb.add(self.grafica)
            self.vBoxProb.show_all()

            # Se muestran la media y desviación típica en la ventana de probabilidades
            widgetMedia = self._widgets.get_widget('mediaProb')
            widgetMedia.set_text(media)
            widgetMedia.set_sensitive(False)
            widgetdTipica = self._widgets.get_widget('dTipicaProb')
            widgetdTipica.set_text(dTipica)
            widgetdTipica.set_sensitive(False)

            # Unsensitivize result entries
            self._widgets.get_widget('resultado1Prob').set_sensitive(False)
            self._widgets.get_widget('resultado2Prob').set_sensitive(False)

            self.vProbabilidades.show()
            self.on_btnIntervalReset_clicked(None)
            self.on_btnProbabilityReset_clicked(None)

    def on_btAceptarZad_clicked(self, boton):
        """
           Acción usuario para aceptar la información
                    que aparece en la ventana de Zaderenko: matriz de
                    Zaderenko, tiempos early y last, caminos del grafo, ...

           boton (botón clickeado)
        """
        self._widgets.get_widget('btCalcularProb').set_sensitive(False)
        self.vZaderenko.hide()

    def on_btHolgZad_clicked(self, boton):
        """
         Acción usuario para acceder a la ventana que muestra
                  las holguras de cada actividad

          boton (botón clickeado)
        """
        s = 0
        for a in self.actividad:
            if a[6] == '' or a[7] == '':
                s += 1

        if s > 0:
            self.dialogoError(_('There are uncomplete activities'))
        else:
            self.ventanaHolguras()

    def on_wndZaderenko_delete_event(self, ventana, evento):
        """
         Acción usuario para cerrar la ventana de Zaderenko
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
        """
        self.vHolguras.hide()

    def on_btZadHolg_clicked(self, boton):
        """
         Acción usuario para acceder a la ventana de Zaderenko
        """
        s = 0
        for a in self.actividad:
            if a[6] == '' or a[7] == '':
                s += 1

        if s > 0:
            self.dialogoError(_('There are uncomplete activities'))
        else:
            self.ventanaZaderenko()


    def on_wndHolguras_delete_event(self, ventana, evento):
        """
         Acción usuario para cerrar la ventana de holguras
        """
        ventana.hide()
        return True


# PROBABILIDADES window

    def on_btnIntervalReset_clicked(self, button):
        """
        Interval Reset button clicked
        """
        widgetMedia = self._widgets.get_widget('mediaProb')
        media = float(widgetMedia.get_text())
        widgetdTipica = self._widgets.get_widget('dTipicaProb')
        dTipica = float(widgetdTipica.get_text())
        self._widgets.get_widget('valor1Prob').set_value(media - 2 * dTipica)
        self._widgets.get_widget('valor2Prob').set_value(media + 2 * dTipica)
        self.on_interval_changed(None)

    def on_interval_changed(self, widget):
        """
        Acción usuario al activar el valor introducido en
                 el primer gtk.Entry de la ventana de probabilidades
        """

        # Se extraen los valores de las u.d.t. de la interfaz
        valor1 = self._widgets.get_widget('valor1Prob')
        dato1 = str(valor1.get_value())
        valor2 = self._widgets.get_widget('valor2Prob')
        dato2 = str(valor2.get_value())
        if valor2.get_value() > valor1.get_value():
            titulo = self.vProbabilidades.get_title()
            if titulo == _('Probability related to the path'):
                # Se extrae la media y la desviación típica de la interfaz
                widgetMedia = self._widgets.get_widget('mediaProb')
                media = widgetMedia.get_text()
                widgetdTipica = self._widgets.get_widget('dTipicaProb')
                dTipica = widgetdTipica.get_text()
                # Se calcula la probabilidad
                x = self.calcularProb(dato1, dato2, media, dTipica)

            else:

                # Extraigo las iteraciones totales
                totales = self._widgets.get_widget('iteracionesTotales')
                itTotales = totales.get_text()

                intervalos = []

                for n in self.intervalos:
                    d = n.split('[')
                    interv = d[1].split(',')
                    intervalos.append(interv)

                # Se calcula la probabilidad
                x=self.calcularProbSim(dato1, dato2, intervalos, itTotales)

            # Se muestra el resultado en la casilla correspondiente
            prob = str('%3.2f'%(x*100))+' %'
            resultado1 = self._widgets.get_widget('resultado1Prob')
            resultado1.set_text(prob)
        else:
            prob=""
            resultado1 = self._widgets.get_widget('resultado1Prob')
            resultado1.set_text(prob)
        return False


    def on_bntIntervalCalculate_clicked(self, button):
        """
        Acción usuario al activar el valor introducido en
                 el primer gtk.Entry de la ventana de probabilidades
        """

        # Se extraen los valores de las u.d.t. de la interfaz
        valor1 = self._widgets.get_widget('valor1Prob')
        dato1 = str(valor1.get_value())
        valor2 = self._widgets.get_widget('valor2Prob')
        dato2 = str(valor2.get_value())

        titulo = self.vProbabilidades.get_title()
        if titulo == _('Probability related to the path'):
            # Se extrae la media y la desviación típica de la interfaz
            widgetMedia = self._widgets.get_widget('mediaProb')
            media = widgetMedia.get_text()
            widgetdTipica = self._widgets.get_widget('dTipicaProb')
            dTipica = widgetdTipica.get_text()

            # Se calcula la probabilidad
            x = self.calcularProb(dato1, dato2, media, dTipica)
            #print dato1, dato2, media, dTipica, x

        else:
                # Extraigo las iteraciones totales
            totales = self._widgets.get_widget('iteracionesTotales')
            itTotales = totales.get_text()

            intervalos = []
            for n in self.intervalos:
                d = n.split('[')
                interv = d[1].split(',')
                intervalos.append(interv)

            # Se calcula la probabilidad
            x = self.calcularProbSim(dato1, dato2, intervalos, itTotales)

        # Se muestra el resultado en la casilla correspondiente
        prob = str('%3.2f'%(x*100))+' %'
        resultado1 = self._widgets.get_widget('resultado1Prob')
        resultado1.set_text(prob)

        # Se muestra el resultado completo en el textView
        if dato2 == '':
            mostrarDato = 'P ( '+str(dato1)+_(' < Project ) = ')+str('%3.3f'%(x))+' ('+prob+')'
        elif dato1 == '':
            mostrarDato = _('P ( Project < ')+str(dato2)+' ) = '+str('%3.3f'%(x))+' ('+prob+')'
        else:
            mostrarDato = 'P ( '+str(dato1)+_(' < Project < ')+str(dato2)+' ) = '+str('%3.3f'%(x))+' ('+prob+')'
        self.escribirProb(mostrarDato)

    def on_btnProbabilityReset_clicked(self, button):
        """
        Probability reset button clicked
        """
        self._widgets.get_widget('valor3Prob').set_value(90)
        self.on_probability_changed(None)

    def on_probability_changed(self, widget):
        """
        Acción usuario al activar el valor introducido en
                 el tercer gtk.Entry de la ventana de probabilidades
        """

        # Se extrae el valor de probabilidad de la interfaz
        valor3 = self._widgets.get_widget('valor3Prob')
        dato3 = float(valor3.get_value() / 100)
        #print dato3, 'dato3'

        x = 0
        titulo = self.vProbabilidades.get_title()
        if titulo == _('Probability related to the path'):
            # Se extrae la media y la desviación típica de la interfaz
            widgetMedia = self._widgets.get_widget('mediaProb')
            media = widgetMedia.get_text()
            widgetdTipica = self._widgets.get_widget('dTipicaProb')
            dTipica = widgetdTipica.get_text()

            valorTabla = float(scipy.stats.distributions.norm.ppf(float(dato3)))
            #print valorTabla

            x = (valorTabla*float(dTipica))+float(media)

        else:
            # Extraigo las iteraciones totales
            totales = self._widgets.get_widget('iteracionesTotales')
            itTotales = totales.get_text()

            intervalos = []
            for n in self.intervalos:
                d = n.split('[')
                interv = d[1].split(',')
                intervalos.append(interv)

            # Se calcula la probabilidad
            suma = 0
            for n in range(len(intervalos)):
                suma += self.Fa[n]/float(itTotales)
                if suma > float(dato3) or suma == float(dato3):
                    x = intervalos[n][1]
                    break

        if x == 0:
            return
        # Se muestra el resultado en la casilla correspondiente
        tiempo = '%5.2f'%(float(x))+' u.d.t.'
        resultado2 = self._widgets.get_widget('resultado2Prob')
        resultado2.set_text(tiempo)

    def on_btnProbabilityCalculate_clicked(self, button):
        """
        Acción usuario al activar el valor introducido en
                 el tercer gtk.Entry de la ventana de probabilidades

        Parámetros: entry (entry activado)
        """

        # Se extrae el valor de probabilidad de la interfaz
        valor3 = self._widgets.get_widget('valor3Prob')
        dato3 = float(valor3.get_value() / 100)
        #print dato3, 'dato3'

        x = 0
        titulo = self.vProbabilidades.get_title()
        if titulo == _('Probability related to the path'):
            # Se extrae la media y la desviación típica de la interfaz
            widgetMedia = self._widgets.get_widget('mediaProb')
            media = widgetMedia.get_text()
            widgetdTipica = self._widgets.get_widget('dTipicaProb')
            dTipica = widgetdTipica.get_text()

            valorTabla = float(scipy.stats.distributions.norm.ppf(float(dato3)))
            #print valorTabla

            x = (valorTabla*float(dTipica))+float(media)

        else:
            # Extraigo las iteraciones totales
            totales = self._widgets.get_widget('iteracionesTotales')
            itTotales = totales.get_text()

            intervalos = []
            for n in self.intervalos:
                d = n.split('[')
                interv = d[1].split(',')
                intervalos.append(interv)

            # Se calcula la probabilidad
            suma = 0
            for n in range(len(intervalos)):
                suma += self.Fa[n]/float(itTotales)
                if suma > float(dato3) or suma == float(dato3):
                    x = intervalos[n][1]
                    break

        if x == 0:
            return
        # Se muestra el resultado en la casilla correspondiente
        tiempo = '%5.2f'%(float(x))+' u.d.t.'
        resultado2 = self._widgets.get_widget('resultado2Prob')
        resultado2.set_text(tiempo)

        # Se muestra el resultado completo en el textView
        prob='%5.2f'%(float(dato3)*100)
        mostrarDato = _('P ( Project < ')+tiempo+' ) = '+str(prob)+' %'

        self.escribirProb(mostrarDato)


    def on_btAceptarProb_clicked(self, boton):
        """
           Acción usuario para aceptar la información que
                    muestra la ventana de cálculo de probabilidades

           Parámetros: boton (botón clickeado)
        """
        titulo = self.vProbabilidades.get_title()
        if titulo == _('Probability related to the path'):
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
        titulo = self.vProbabilidades.get_title()
        if titulo == _('Probability related to the path'):
            self.limpiarVentanaProb(0)
        else:
            self.limpiarVentanaProb(1)

        ventana.hide()
        return True



# --- Simulation window

    def on_btContinuarIterando_clicked(self, boton):
        """
        Clicked on simulate the project a number of iterations
        """
        #Se asignan el numero de iteraciones que se van a realizar
        iteracion = self._widgets.get_widget('iteracion')
        it = iteracion.get_value_as_int()

        # Se almacenan las iteraciones totales en una variable y se muestra en la interfaz
        totales = self._widgets.get_widget('iteracionesTotales')
        interfaz = totales.get_text()
        if interfaz != '':
            itTotales = it + int(interfaz)
        else:
            itTotales = it
        #print itTotales, 'iteraciones totales'
        totales.set_text(str(itTotales))

        # Se realiza la simulación
        simulacion = simulation.simulacion(it, self.actividad)
        self.simTotales += simulacion

        # Se crea el grafo Pert y se renumera
        grafoRenumerado = self.build_salas_pert_graph()

        # Nuevos nodos
        nodosN = []
        for n in range(len(grafoRenumerado.successors)):
            nodosN.append(n+1)

        # Zaderenko
        if simulacion == None:
            return
        else:
            for s in simulacion:
                matrizZad = mZad(self.actividad, grafoRenumerado.arcs, nodosN, 0, s)
                tearly = early(nodosN, matrizZad)
                tlast = last(nodosN, tearly, matrizZad)
                tam = len(tearly)
                # Se calcula la duración del proyecto para cada simulación
                duracionProyecto = tearly[tam-1]
                #print duracionProyecto, 'duracion proyecto'
                self.duraciones.append(duracionProyecto)
                #print self.duraciones,'duraciones simuladas'
                # Se extraen los caminos crí­ticos y se calcula su í­ndice de criticidad
                self.indiceCriticidad(grafoRenumerado, s, tearly, tlast, itTotales)

        # Se añaden la media y la desviación típica a la interfaz
        duracionMedia = numpy.mean(self.duraciones)
        media = self._widgets.get_widget('mediaSim')
        media.set_text(str(duracionMedia))

        desviacionTipica = numpy.std(self.duraciones)
        dTipica = self._widgets.get_widget('dTipicaSim')
        dTipica.set_text(str(desviacionTipica))

        try:
            iOpcion = self._widgets.get_widget('iOpcion')
            opcion = iOpcion.get_active_text()
            iValor = self._widgets.get_widget('iValor') # Número de intervalos
            valor = float(iValor.get_text())
            if (valor > 0):
                n = simulation.nIntervalos(float(max(self.duraciones)+0.000001), float(min(self.duraciones)), valor, str(opcion))

                #Update frecuency intervals and returns intervals values, absolute frecuency and relative frecuency
                self.intervalos, self.Fa, self.Fr = self.interface.update_frecuency_intervals_treeview (n, self.duraciones, itTotales)

                #Draw the histogram
                fig = Figure(figsize=(5,4), dpi=100)
                ax = fig.add_subplot(111)

                n, bins, patches = ax.hist(self.duraciones, n, density=True)
                canvas = FigureCanvas(fig)  # a gtk.DrawingArea
                if len(self.boxS)>0: # Si ya hay introducido un box, que lo borre y lo vuelva a añadir
                    self.hBoxSim.remove(self.boxS)
                    self.boxS=gtk.VBox()

                self.hBoxSim.add(self.boxS)
                self.boxS.pack_start(canvas, True, True, 0)
                self.boxS.show_all()


                # Enable Probability and Save buttons
                self._widgets.get_widget('btProbSim').set_sensitive(True)
                self._widgets.get_widget('btGuardarSim').set_sensitive(True)

                # Enable K-S Test
                self._widgets.get_widget('btKS').set_sensitive(True)
            else:
                self.dialogoError('El valor del intervalo ha de ser mayor que 0')
        except ValueError:
            self.dialogoError('El valor del intervalo ha de ser numérico')

    def on_btProbSim_clicked(self, boton):
        """
        Acción usuario para acceder a la ventana de
                 cálculo de probabilidades

         boton (botón clickeado)
        """
        self.vProbabilidades.set_title(_('Probability related to the simulation'))

        media = self._widgets.get_widget('mediaSim')
        m = media.get_text()
        dTipica = self._widgets.get_widget('dTipicaSim')
        dt = dTipica.get_text()

        widgetMedia = self._widgets.get_widget('mediaProb')
        widgetMedia.set_text(m)
        widgetdTipica = self._widgets.get_widget('dTipicaProb')
        widgetdTipica.set_text(dt)

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        n, bins, patches = ax.hist(self.duraciones, 100, density=True)
        canvas = FigureCanvas(fig)

        if len(self.box) > 0:
            self.vBoxProb.remove(self.box)
            self.box = gtk.VBox()

        self.vBoxProb.add(self.box)

        parent = canvas.get_parent()
        if parent is not None:
            parent.remove(canvas)

        self.box.pack_end(canvas, True, True, 0)
        self.box.show_all()
        self.vProbabilidades.show()
        self.on_btnIntervalReset_clicked(None)
        self.on_btnProbabilityReset_clicked(None)


    def on_btGuardarSim_clicked(self, boton):
        """
        Acción usuario para salvar la información que
                 muestra la ventana de simulación de duraciones
                 tabla, gráfica, ....

         boton (botón clickeado)

        """
        # Se extraen los datos de la interfaz
        # Media y desviación tí­pica
        media = self._widgets.get_widget('mediaSim')
        m = media.get_text()
        dTipica = self._widgets.get_widget('dTipicaSim')
        dt = dTipica.get_text()
        # Iteraciones
        totales = self._widgets.get_widget('iteracionesTotales')
        iteraciones = totales.get_text()

        # Se pasan los datos de la simulación a formato CSV
        simulacionCsv = simulation.datosSimulacion2csv(self.duraciones, iteraciones, m, dt, self.modeloC)

        # Se muestra el diálogo para salvar el archivo
        fileFormats.guardarCsv(simulacionCsv, self)


    def on_wndSimulacion_delete_event(self, ventana, evento):
        """
        User closes simulation window

         ventana (ventana actual)
         evento (evento cerrar)
        """
        self._widgets.get_widget('iteracion').set_text('')
        self._widgets.get_widget('iteracionesTotales').set_text('')
        self._widgets.get_widget('mediaSim').set_text('')
        self._widgets.get_widget('dTipicaSim').set_text('')

        self.modeloC.clear()

        if len(self.boxS) > 0:
            self.hBoxSim.remove(self.boxS)

        ventana.hide()
        return True


# ---Set Average Duration
    def on_setAvgDuration_activate (self, menu_item):
        """ Accion usuario para la eleccion de la
            media
        """
        self._widgets.get_widget('btAsignarAvgDuration').set_sensitive(True)
        self._widgets.get_widget('avgDuration').set_text('')
        self._widgets.get_widget('btCancelAvgDuration').set_sensitive(True)
        self.vAvgDuration.show()

    def on_CloseAvgDuration_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana
        sin introducir valores
        """
        ventana.hide()
        return True

    def on_btAsignarAvgDuration_clicked(self,boton):
        """
        Accion usuario que rellena la tabla
        con el valor de la duraccion media introducido.
        """
        #Se extrae el valor de la duracion media
        avgDuration = float(self._widgets.get_widget('avgDuration').get_text())

        if avgDuration <= 0:
            self.dialogoError(_('los valores deben ser mayor de 0.'))
        else:
            """for m in range(len(self.actividad)):
                previous = self.modelo[m][6]
                self.actividad[m][6] = avgDuration
                self.modelo[m][6] = self.actividad[m][6]
                self.actualizacion(self.modelo, m, 6, previous)"""

            for m in range(len(self.actividad)):
                self.col_edited_cb('edited', m, str(avgDuration), self.modelo, 6)

            self.gantt.update()
            self.set_modified_state(True)
            self.vAvgDuration.hide()
            print('up gant')

    def on_btCancelAvgDuration_clicked(self,boton):
        """ Accion usuario para cancelar
            la opcion de asignacion automática
        """

        self.vAvgDuration.hide()

# --- Choose of distribution
# --- Distribution Normal
    def on_setDistNormal_activate (self, menu_item):
        """ Accion usuario para la eleccion de la
            distribucion normal y poner el mismo valor
            de la media y desviacion tipica a todos
        """
        self.distributionType = 'Normal'
        self._widgets.get_widget('btAsignarDistNormal').set_sensitive(True)
        self._widgets.get_widget('durmed').set_text('')
        self._widgets.get_widget('desTipica').set_text('')
        self._widgets.get_widget('btCancelDistNormal').set_sensitive(True)
        self.vDistNormal.show()

    def on_CloseDistNormal_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana
        sin introducir valores
        """
        ventana.hide()
        return True

    def on_btAsignarDistNormal_clicked(self, boton):
        """
        Accion usuario que rellena la tabla
        con el valor de la duracion media y
        desviacion tipica introducido.
        """
        durmed = float(self._widgets.get_widget('durmed').get_text())
        desTipica = float(self._widgets.get_widget('desTipica').get_text())

        dist = self.distributionType

        if durmed <= 0 or desTipica <= 0:
            self.dialogoError(_('los valores deben ser mayor de 0.'))
        else:
            for m in range(len(self.actividad)):
                previous = self.modelo[m][6]

                self.actividad[m][6] = durmed
                self.modelo[m][6] = str(self.actividad[m][6])
                self.actualizacion(self.modelo, m, 6, previous)

                self.actividad[m][7] = desTipica
                self.modelo[m][7] = str(self.actividad[m][7])
                if self.actividad[m][1] != '':
                    self.normal_distribution_cache[str(self.actividad[m][1])] = (float(durmed), float(desTipica))

                self.actividad[m][8] = dist
                self.modelo[m][8] = str(self.actividad[m][8])

            self.gantt.update()
            self.set_modified_state(True)
            self.vDistNormal.hide()
            print('up gant')


    def on_btCancelDistNormal_clicked(self,boton):
        """ Accion usuario para cancelar
            la opcion de asignacion automática
        """

        self.vDistNormal.hide()

# --- Distribution Triangular and Beta
    def on_selectDistTriangular_activate(self, boton):
        """ Accion usuario para la eleccion de la
            distribucion triangular y poner el mismo valor
            de la optimista, pesimista y mas probable a todos
        """
        self.distributionType = 'Triangular'
        self._widgets.get_widget('btAsignarTriBeta').set_sensitive(True)
        self._widgets.get_widget('optimista').set_text('')
        self._widgets.get_widget('pesimista').set_text('')
        self._widgets.get_widget('probable').set_text('')
        self._widgets.get_widget('btCancelTriBeta').set_sensitive(True)
        self.vDistTriBeta.show()


    def on_selectDistBeta_activate(self, boton):
        """ Accion usuario para la eleccion de la
            distribucion beta y poner el mismo valor
            de la optimista, pesimista y mas probable a todos
        """
        self.distributionType = 'Beta'
        self._widgets.get_widget('btAsignarTriBeta').set_sensitive(True)
        self._widgets.get_widget('optimista').set_text('')
        self._widgets.get_widget('pesimista').set_text('')
        self._widgets.get_widget('probable').set_text('')
        self._widgets.get_widget('btCancelTriBeta').set_sensitive(True)
        self.vDistTriBeta.show()


    def on_CloseTriBeta_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana
        sin introducir valores
        """
        ventana.hide()
        return True


    def on_btAsignarTriBeta_clicked(self, boton):
        """
        Accion usuario que rellena la tabla
        con los valores optimista, pesimista
        y mas probable introducidos.
        """
        optimista = float(self._widgets.get_widget('optimista').get_text())
        pesimista = float(self._widgets.get_widget('pesimista').get_text())
        probable = float(self._widgets.get_widget('probable').get_text())

        if self.distributionType == 'Triangular':
            dist = 'Triangular'
        else:
            dist = 'Beta'

        a = optimista
        b = pesimista
        m = probable

        ok = ((a < b and m <= b and m >= a) or (a == b and b == m))

        if optimista <= 0 or pesimista <= 0 or probable <= 0:
            self.dialogoError(_('Las duraciones deben ser todas mayor que 0'))
        else:
            if ok:
                for idx in range(len(self.actividad)):
                    self.actividad[idx][3] = optimista
                    self.actividad[idx][4] = probable
                    self.actividad[idx][5] = pesimista
                    self.actividad[idx][8] = dist

                    self.modelo[idx][3] = str(optimista)
                    self.modelo[idx][4] = str(probable)
                    self.modelo[idx][5] = str(pesimista)
                    self.modelo[idx][8] = str(dist)

                    self.actualizarMediaDTipica(idx, self.modelo, self.actividad, a, b, m)

                    self.gantt.set_activity_duration(
                        self.modelo[idx][1],
                        float(self.modelo[idx][6]) if self.modelo[idx][6] != '' else 0.0
                    )

                self.gantt.update()
                self.set_modified_state(True)
                self.vDistTriBeta.hide()
            else:
                self.dialogoError(_('Error al introducir los valores.'))



    def on_btCancelTriBeta_clicked(self,boton):
        """ Accion usuario para cancelar
            la opcion de asignacion automática
        """
        self.vDistTriBeta.hide()


# --- Distribution Uniforme
    def on_selectDistUniforme_activate(self, boton):

       self.distributionType = 'Uniform'
       self._widgets.get_widget('btAsignarUniforme').set_sensitive(True)
       self._widgets.get_widget('optimista').set_text('')
       self._widgets.get_widget('pesimista').set_text('')
       self._widgets.get_widget('btCancelUniforme').set_sensitive(True)
       self.vDistUnif.show()

    def on_btAsignarUniforme_clicked(self, boton):
        """
        Accion usuario que rellena la tabla
        con el valor de la optimista y pesimista
        introducido.
        """
        optimistaUnif = float(self._widgets.get_widget('optimistaUnif').get_text())
        pesimistaUnif = float(self._widgets.get_widget('pesimistaUnif').get_text())

        ok = optimistaUnif < pesimistaUnif
        dist = self.distributionType

        print('distribucion ', dist)

        if optimistaUnif <= 0 or pesimistaUnif <= 0:
            self.dialogoError(_('Las duraciones deben ser todas mayor que 0'))
        else:
            if ok:
                for m in range(len(self.actividad)):
                    previous = self.modelo[m][6]

                    self.actividad[m][6] = (optimistaUnif + pesimistaUnif) / 2
                    self.modelo[m][6] = str(self.actividad[m][6])
                    self.actualizacion(self.modelo, m, 6, previous)

                    self.actividad[m][7] = (pesimistaUnif - optimistaUnif) / math.sqrt(12)
                    self.modelo[m][7] = str(self.actividad[m][7])

                    self.actividad[m][3] = optimistaUnif
                    self.modelo[m][3] = str(self.actividad[m][3])

                    self.actividad[m][5] = pesimistaUnif
                    self.modelo[m][5] = str(self.actividad[m][5])

                    self.actividad[m][8] = dist
                    self.modelo[m][8] = str(self.actividad[m][8])

                self.gantt.update()
                self.set_modified_state(True)
                self.vDistUnif.hide()
            else:
                self.dialogoError(_('Error al introducir los valores para la Uniforme.'))



    def on_btCancelUniforme_clicked(self,boton):
        """ Accion usuario para cancelar
            la opcion de asignacion automática
        """
        self.vDistUnif.hide()

    def on_CloseUnif_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana
        sin introducir valores
        """
        ventana.hide()
        return True

# --- Assignment window
    def on_mnAsignacion_activate (self, menu_item):
        """ Accion usuario para activar
            la ventana de asignación automática
            de valores para la distribución
        """
        s = 0
        m = 0

        for a in self.actividad:
            if (a[6] == ''):
                s += 1
            elif (a[6] < 0):
                m += 1

        if s > 0:
            self.dialogoError(_('Todas las duraciones medias han de ser introducidas'))
        elif m > 0:
            self.dialogoError(_('No pueden existir duraciones medias negativas'))
        else:
            self._widgets.get_widget('btAsignar').set_sensitive(True)
            self._widgets.get_widget('proporcionalidad').set_text('0.2')
            self._widgets.get_widget('distribucion').set_active(1)
            self._widgets.get_widget('btCancel').set_sensitive(True)
            #self._widgets.get_widget('btProcedimiento').set_sensitive(True)
            self.vAsignacion.show()

    def on_btAsignar_clicked(self,boton):
        """
        Accion usuario que rellena la tabla
        con los valores calculados a partir
        de la constante de proporcinalidad k
        y la media de cada actividad
        """

        # Se extrae el valor de proporcionalidad
        proporcionalidad = self._widgets.get_widget('proporcionalidad')
        try:
            k = float(proporcionalidad.get_text())

            # Se extrae el tipo de distribución
            distribucion = self._widgets.get_widget('distribucion')
            dist = distribucion.get_active_text()
            #print 'distribucion ', dist
            if dist == 'Beta':
                if (k < 0 or k >= 1):
                    self.dialogoError(_('La constante de proporcionalidad no puede ser negativa, ni mayor que 1'))
                else:
                    assignment.actualizarInterfaz(self.modelo, k, dist, self.actividad)
                    self.set_modified_state(True)
                    self.vAsignacion.hide()
            elif dist == 'Triangular':
                if (k<math.sqrt(1.0/8)):
                    self.dialogoError(_('La constate de proporcionalidad debe de ser mayor'))
                else:
                    assignment.actualizarInterfaz(self.modelo, k, dist, self.actividad)
                    self.set_modified_state(True)
                    self.vAsignacion.hide()
            else:
                assignment.actualizarInterfaz(self.modelo, k, dist, self.actividad)
                self.set_modified_state(True)
                self.vAsignacion.hide()
        #Es lo mismo que el if de arriba, pero el if esta mejorado
        #except ValueError:
            #self.dialogoError('La constante de proporcionalidad ha de ser un numero')
        except assignment.InvalidK:
            self.dialogoError('El valor de k no es valido')

    def on_btCancel_clicked(self,boton):
        """ Accion usuario para cancelar
            la opcion de asignacion automática
        """

        self.vAsignacion.hide()

    def on_wndAsignacion_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de calcular
                 caminos
        """
        ventana.hide()
        return True

    # ---Kolmogorov-Smirnoff test

    def on_btKS_clicked(self, boton):
        """
        Accion usuario para acceder al test de kolmogorov smirnov
        """
        results = kolmogorov_smirnov.evaluate_models(self.actividad, self.duraciones, self.simTotales)

        # Fila 1: PERT
        self._widgets.get_widget('pvalueN').set_text(str(results.get('p_PERT', 'Not defined')))
        self._widgets.get_widget('statisticN').set_text(str(results.get('ksPERT', 'Not defined')))

        # Fila 2: Gamma_ant (la UI la llama "valores extremos", aunque realmente no lo es)
        self._widgets.get_widget('pvalueEV').set_text(str(results.get('p_Gamma_ant', 'Not defined')))
        self._widgets.get_widget('statisticEV').set_text(str(results.get('ksGamma_ant', 'Not defined')))

        # Fila 3: Gamma
        self._widgets.get_widget('pvalueG').set_text(str(results.get('p_Gamma', 'Not defined')))
        self._widgets.get_widget('statisticG').set_text(str(results.get('ksGamma', 'Not defined')))

        self.vTestKS.show()



    def on_btAceptarTest_clicked(self,boton):
        """ Accion usuario para cancelar
            la opcion de asignacion automática
        """
        self.vTestKS.hide()

    def on_wndTestKS_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de calcular
                 caminos
        """
        ventana.hide()
        return True



# --- Resources

    def on_btAsignarRec_clicked(self, boton):
        """
        Acción usuario para acceder a la ventana de recursos
                 necesarios por actividad
        Nota: Antes de introducir los recursos que cada actividad necesita, deben existir tanto recursos como actividades.
        """
        # Se comprueba que se hayan introducido actividades
        if self.actividad == []:
            self.dialogoError(_('No activities introduced'))

        # Se comprueba que se hayan introducido recursos
        elif self.recurso == []:
            self.dialogoError(_('No resources introduced'))

        # Si todo es correcto, se accede a la ventana con normalidad
        else:
            if len(self.modeloAR) == 0:
                self.modeloAR.append(['', '', ''])
                self.asignacion.append(['', '', ''])
            self.vAsignarRec.show()


    def on_wndRecursos_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de recursos
        """
        ventana.hide()
        return True



# --- Necessary resources per activity

    def on_btAceptarAR_clicked(self, boton):
        """
        Acción usuario para aceptar la información que
                 muestra la ventana de recursos necesarios por
                 actividad: actividad, recurso, unidad necesaria
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
        """
        self.modeloAR.clear()
        self.asignacion=[]
        self.vAsignarRec.hide()

    def on_wndAsignarRec_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de recursos
                 necesarios por actividad
        """
        ventana.hide()
        return True


# --- Calculate paths

    def on_btAceptarCaminos_clicked(self, boton):
        """
        Acción usuario para aceptar la información que
                 muestra la ventana de calcular caminos
        """
        self.vCaminos.hide()

    def on_btExportarCsv_clicked(self, boton):
        """
        Export paths to CSV format (for spreadsheet)
        """
        # Generate all paths
        successors = dict(((act[1], act[2]) for act in self.actividad))
        g = graph.roy(successors)
        todosCaminos = graph.find_all_paths(g, 'Begin', 'End')

        # Create CSV and show file dialog
        paths_csv = graph.roy_paths2csv([self.actividad[i][1] for i in range(len(self.actividad))], todosCaminos)
        fileFormats.guardarCsv(paths_csv, self)

    def on_wndCaminos_delete_event(self, ventana, evento):
        """
        Acción usuario para cerrar la ventana de calcular
                 caminos
        """
        ventana.hide()
        return True


# --- Help ---

    def on_dAyuda_response(self, dummy, boton):
        """
        Acción usuario para aceptar la información que
                 muestra el diálodo de ayuda
        """
        self.dAyuda.hide()

    def on_dAyuda_delete_event(self, dialogo, evento):
        """
        Acción usuario para cerrar el diálogo de ayuda
        """
        self.dAyuda.hide()
        return True

    def on_tab_clicked(self, widget, event):
        """
        Tab clicked.
        """
        if event.button == 3:
            for i in range(self.ntbSchedule.get_n_pages()):
                x, y = self.ntbSchedule.translate_coordinates(self.vPrincipal, int(event.x), int(event.y))
                if self.schedule_tab_labels[i].intersect(gtk.gdk.Rectangle(x, y, 1, 1)):
                    self.clicked_tab = i
                    self._widgets.get_widget("mnTabsDelete").set_sensitive(i != 0)
                    self._widgets.get_widget("ctxTabsMenu").popup(None, None, None, event.button, event.time)
                    break

    def on_tab_changed(self, notebook, page, page_num):
        """
        Tab changed.
        """
        self.set_schedule(self.schedules[page_num][1])

    def on_key_pressed(self, widget, event):
        """
        Key pressed.
        Returns: True or false depending if the window should be closed.
        """
        if event.keyval == Gdk.KEY_Escape:
            widget.hide()
            return True
        elif event.keyval == Gdk.KEY_Delete:  # Delete key
            self.delete_activity()  # Delete Activity
            return True
        else:
            return False

def main(filename=None):
    """
    Start PPC project
    """
    program_dir = os.path.dirname( os.path.realpath( __file__ ) )
    app = PPCproject(program_dir)
    if filename:
        app.openProject(filename)
    Gtk.main()


# --- Start running as a program
if __name__ == '__main__':
    import sys
    if   len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print(_('Syntax is:'))
        print(sys.argv[0], '[project_file]')
