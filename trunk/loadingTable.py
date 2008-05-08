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
import copy

class loadingTable(gtk.HBox):

    def __init__(self):
        gtk.HBox.__init__(self)
        self.table = table()
        
        self.set_homogeneous(False)
        self.pack_start(self.table, True, True, 0)

        
    def set_cell_width(self, width):
        """
        Set cell width
        
        width: width (pixels)
        """
        self.table.cell_width = width    
    def set_loading(self, loading):
        """
        Set loading
        
        loading: loading (pixels)
        """
        self.table.loading = loading
    def set_duration(self, duration):
        """
        Set duration
        
        duration: duration
        """
        self.table.duration = duration
    def set_hadjustment(self, adjustment):
        """
        Set horizontal adjustment to "adjustment"
        
        adjustment: gtk.Adjustment to be set.
        """
        self.table.set_hadjustment(adjustment)
    def update(self):
        """
        Redraw loading diagram.
        
        """
        self.table.queue_draw()
    def clear(self):
        """
        Clean loading diagram.
        
        """
        self.table.clean()   

class table(gtk.Layout):
    def __init__(self):
        gtk.Layout.__init__(self)
        self.colors = [gtk.gdk.color_parse("#ff0000"), gtk.gdk.color_parse("#00ff00"), gtk.gdk.color_parse("#0000ff"), gtk.gdk.color_parse("#ffff00"), gtk.gdk.color_parse("#8b4513"), gtk.gdk.color_parse("#ffa500"), gtk.gdk.color_parse("#d02090"), gtk.gdk.color_parse("#006400"), gtk.gdk.color_parse("#191970"), gtk.gdk.color_parse("#ffb5c5"), gtk.gdk.color_parse("#9f79ee")]
        self.cell_width = 0
        self.loading = {}
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
    
    def clean(self):
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
        self.ctx.translate(20.5,-0.5)
        #Obtaining available width and height
        self.available_width = event.area.width
        self.available_height = event.area.height
        #Drawing
        self.draw(self.ctx)
        return False

    def draw(self, ctx):    
        rowHeight = (self.available_height - 1) / len(self.loading)
        width = (int(self.duration) + 1) * self.cell_width 
        if width > self.available_width:
            self.set_size(width, self.available_height)       
        # Drawing the table     
        loadingCopy = copy.deepcopy(self.loading)
        colorIndex = 0
        heightIndex = 1
        for resourceList in loadingCopy.values():
            while resourceList != []:
                x1, y1 = resourceList.pop(0)
                if resourceList != []:
                    x2, y2 = resourceList[0]
                else:
                    x2 = self.duration
                # Drawing the rectangle
                ctx.rectangle (x1 * self.cell_width, heightIndex, x2 * self.cell_width - x1 * self.cell_width, rowHeight)
                ctx.set_source_color(self.colors[colorIndex])
                ctx.fill_preserve()
                ctx.set_line_width(1)
                ctx.set_source_color(self.get_style().fg[gtk.STATE_NORMAL])
                ctx.stroke()
                # Drawing the use of resource
                x_bearing, y_bearing, txt_width, txt_height = ctx.text_extents(str(int(y1)))[:4]
                ctx.move_to(x2 * self.cell_width - (x2 * self.cell_width - x1 * self.cell_width) / 2 - txt_width / 2 - x_bearing, heightIndex + rowHeight / 2 - txt_height / 2 - y_bearing )
                ctx.show_text(str(int(y1)))
                
            
            colorIndex = (colorIndex + 1) % 12
            heightIndex += rowHeight

                
def main():
    """
        Example of use.
    """
    window = gtk.Window()
    lt = loadingTable()
    lt.set_cell_width(20)
    window.add(lt)
    window.connect("destroy", gtk.main_quit)
    window.show_all()
    gtk.main()

if __name__ == "__main__":
   main()	
