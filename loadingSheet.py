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

class loadingSheet(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        #self.scale = loadingSheetScale()
        self.diagram = loadingSheetDiagram()
        self.scrolled_window = gtk.ScrolledWindow(self.diagram.get_hadjustment(), self.diagram.get_vadjustment())
        self.set_homogeneous(False)
        self.pack_start(self.scrolled_window, True, True, 0)
        self.scrolled_window.add(self.diagram)
        #Setting scrollbars policy
        self.scrolled_window.set_policy(gtk.POLICY_ALWAYS,gtk.POLICY_NEVER)
        #self.set_size_request(200,200)
        
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
    def update(self):
        """
        Redraw loading diagram.
        
        """
        self.diagram.queue_draw()   

class loadingSheetDiagram(gtk.Layout):
    def __init__(self):
        gtk.Layout.__init__(self)
        self.cell_width = 0
        self.loading = {}
        self.duration = 0
        self.randomValue = random.random()
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
        self.ctx.translate(20.5,-0.5)
        #Obtaining available width and height
        self.available_width = event.area.width
        self.available_height = event.area.height
        #Drawing
        self.draw(self.ctx)
        return False

    def draw(self, ctx):    
        
        width = (int(self.duration) + 1) * self.cell_width 
        if width > self.available_width:
            self.set_size(width, self.available_height)  
        #Drawing cell lines
        for i in range(0, (max(self.available_width,int(width)) / self.cell_width) + 1):
            ctx.move_to(i * self.cell_width, 0)
            ctx.line_to(i * self.cell_width, self.available_height)
        ctx.set_line_width(1)
        red = float(self.get_style().fg[gtk.STATE_INSENSITIVE].red) / 65535
        green = float(self.get_style().fg[gtk.STATE_INSENSITIVE].green) / 65535
        blue = float(self.get_style().fg[gtk.STATE_INSENSITIVE].blue) / 65535
        ctx.set_source_rgba(red, green, blue, 0.3)
        ctx.stroke()
        # Calculate the greatest use of resources
        greatest = 0
        for resourceList in self.loading.values():
            for time, use in resourceList:
                if use > greatest:
                    greatest = use
        # Drawing the scale
        ctx.set_source_color(self.get_style().fg[gtk.STATE_NORMAL])
        for i in range(5, int(greatest),5):
            x_bearing, y_bearing, txt_width, txt_height = ctx.text_extents(str(i))[:4]
            ctx.move_to(-10.5 - txt_width / 2 - x_bearing, self.available_height - (self.available_height - 20) * i / greatest - txt_height / 2 - y_bearing )
            ctx.show_text(str(i))
        ctx.set_line_width(1);
        ctx.stroke()      
        # Drawing the diagram      
        loadingCopy = copy.deepcopy(self.loading)
        red = 1
        green = 1
        blue = 1
        for resourceList in loadingCopy.values():
            red = self.randomValue * red
            green = self.randomValue * green
            blue = self.randomValue * blue
            while resourceList != []:
                x1, y1 = resourceList.pop(0)
                if resourceList != []:
                    x2, y2 = resourceList[0]
                else:
                    x2 = self.duration
                ctx.line_to (x1 * self.cell_width, self.available_height - (self.available_height - 20) * y1 / greatest)
                ctx.line_to (x2 * self.cell_width, self.available_height - (self.available_height - 20) * y1 / greatest)
                
            ctx.set_line_width(2)
            ctx.set_source_rgb(red, green, blue)
            ctx.stroke()
                
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
