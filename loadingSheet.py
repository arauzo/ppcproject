#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Gantt diagram drawing GTK widget
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

import cairo
import math
import gtk
import gtk.gdk
import gobject
import GTKgantt
import copy
import random

class loadingSheet(gtk.HBox):

    def __init__(self):
        gtk.HBox.__init__(self)
        self.diagram = loadingSheetDiagram()
        self.scale = loadingSheetScale()
        
        self.set_homogeneous(False)
        self.pack_start(self.scale, False, False, 0)
        self.pack_start(self.diagram, True, True, 0)
        
        self.diagram.connect("greatest-calculated", self.scale.set_greatest)
        
    def set_cell_width(self, width):
        """
        Set cell width
        
        width: width (pixels)
        """
        self.diagram.cell_width = width
    
    def set_loading(self, loading):
        """
        Set loading
        
        loading: loading (pixels)
        """
        self.diagram.loading = loading
    def set_duration(self, duration):
        """
        Set duration
        
        duration: duration
        """
        self.diagram.duration = duration
        self.scale.duration = duration
        
    def set_hadjustment(self, adjustment):
        """
        Set horizontal adjustment to "adjustment"
        
        adjustment: gtk.Adjustment to be set.
        """
        self.diagram.set_hadjustment(adjustment)     
    def set_width(self, widget, width):
        """
        Set width
        
        width: width
        """
        self.diagram.set_width(width)
    def update(self):
        """
        Redraw loading diagram.
        
        """
        self.diagram.queue_draw()
        self.scale.queue_draw()
    def clear(self):
        """
        Clean loading diagram.
        
        """
        self.diagram.clear()   

class loadingSheetScale(gtk.Layout):
    def __init__(self):
        gtk.Layout.__init__(self)
        #Connecting signals
        self.greatest = 0
        self.duration = 0
        self.set_size_request(20,20)
        self.connect("expose-event", self.expose)
        
    def set_greatest(self,widget,greatest):
        self.greatest = greatest
        self.queue_draw()  
        
    def expose (self,widget,event):
        """
        Function called when the widget needs to be drawn
        
        widget:
        event:

        Returns: False
        """
        #Creating Cairo drawing context
        self.ctx = self.bin_window.cairo_create()
        #Setting context size to available size
        #self.ctx.rectangle(event.area.x, event.area.y, 20, event.area.height)
        #self.ctx.clip()
        self.ctx.translate(20.5,-0.5)
        #Obtaining available width and height
        self.available_width = event.area.width
        self.available_height = event.area.height
        #Drawing
        self.draw(self.ctx)
        return False
              
    def draw(self,ctx):
        step = self.greatest / 5
        # Drawing the scale
        ctx.set_source_color(self.get_style().fg[gtk.STATE_NORMAL])
        for i in range(int(step), int(self.greatest),5):
            x_bearing, y_bearing, txt_width, txt_height = ctx.text_extents(str(i))[:4]
            ctx.move_to(-10.5 - txt_width / 2 - x_bearing, self.available_height - (self.available_height - 20) * i / self.greatest - txt_height / 2 - y_bearing )

            ctx.show_text(str(i))
            
        
class loadingSheetDiagram(gtk.Layout):
    __gsignals__ = {'greatest-calculated' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,(gobject.TYPE_INT,))}
    def __init__(self):
        gtk.Layout.__init__(self)
        self.colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 1.0, 0.0), (0.5, 0.3, 0.1), (1.0, 0.6, 0.0), (0.8, 0.1, 0.5), (0.0, 0.4, 0.0), (0.1, 0.1, 0.4), (1.0, 0.7, 0.8), (0.6, 0.5, 0.9)]
        self.cell_width = 0
        self.loading = {}
        self.width = 0
        self.duration = 0
        self.connect("expose-event", self.expose)
        
    def set_cell_width(self, width):
        """
        Set cell width
        
        width: width (pixels)
        """
        self.cell_width = width
    
    def set_loading(self, loading):
        """
        Set loading
        
        loading: loading
        """
        self.loading = loading
        
    def set_duration(self, duration):
        """
        Set duration
        
        duration: duration
        """
        self.duration = duration
    
    def set_width(self, width):
        """
        Set width
        
        width: width
        """
        self.width = width
        self.queue_draw()
    
    def calculate_greatest(self):
        greatest = 0
        for resourceList in self.loading.values():
            for time, use in resourceList:
                if use > greatest:
                    greatest = use
        self.emit("greatest_calculated",greatest)
        return greatest
    
    def clear(self):
        """
        Clean loading diagram.
        
        """
        self.loading = {}
        self.duration = 0
            
    def expose (self,widget,event):
        """
        Function called when the widget needs to be drawn
        
        widget:
        event:

        Returns: False
        """
        #Creating Cairo drawing context
        self.ctx = self.bin_window.cairo_create()
        #Setting context size to available size
        self.ctx.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        self.ctx.clip()
        self.ctx.translate(0.5,-0.5)
        #Obtaining available width and height
        self.available_width = event.area.width
        self.available_height = event.area.height
        #Drawing
        self.draw(self.ctx)
        return False

    def draw(self, ctx):  
        self.set_size(self.width, self.available_height)  
        #Drawing cell lines
        for i in range(0, (max(self.available_width,int(self.width)) / self.cell_width) + 1):
            ctx.move_to(i * self.cell_width, 0)
            ctx.line_to(i * self.cell_width, self.available_height)
        ctx.set_line_width(1)
        red = float(self.get_style().fg[gtk.STATE_INSENSITIVE].red) / 65535
        green = float(self.get_style().fg[gtk.STATE_INSENSITIVE].green) / 65535
        blue = float(self.get_style().fg[gtk.STATE_INSENSITIVE].blue) / 65535
        ctx.set_source_rgba(red, green, blue, 0.3)
        ctx.stroke()
        greatest = self.calculate_greatest()   
        # Drawing scale lines
        step = greatest / 5
        ctx.save()
        ctx.set_dash([5],5)
        for i in range(int(step), int(greatest),5):
            ctx.move_to(0, self.available_height - (self.available_height - 20) * i / greatest)
            ctx.line_to(max(self.available_width,int(self.width)), self.available_height - (self.available_height - 20) * i / greatest)
            ctx.set_source_rgba(red,green,blue,0.3)
            ctx.stroke()

        ctx.restore()
        # Drawing the diagram
        loadingCopy = copy.deepcopy(self.loading)
        colorIndex = 0
        loadingKeys = loadingCopy.keys()
        loadingKeys.sort()
        for key in loadingKeys:
            while loadingCopy[key] != []:
                x1, y1 = loadingCopy[key].pop(0)
                if loadingCopy[key] != []:
                    x2, y2 = loadingCopy[key][0]
                else:
                    x2 = self.duration
                ctx.line_to (x1 * self.cell_width, self.available_height - (self.available_height - 20) * y1 / greatest)
                ctx.line_to (x2 * self.cell_width, self.available_height - (self.available_height - 20) * y1 / greatest)
                
            ctx.set_line_width(2)
            ctx.set_source_rgba(self.colors[colorIndex][0], self.colors[colorIndex][1], self.colors[colorIndex][2],0.5)
            ctx.stroke()
            colorIndex = (colorIndex + 1) % 11

                
def main():
    """
        Example of use.
    """
    window = gtk.Window()
    ls = loadingSheet()
    ls.set_cell_width(20)
    window.add(ls)
    window.connect("destroy", gtk.main_quit)
    window.show_all()
    gtk.main()

if __name__ == "__main__":
   main()	
