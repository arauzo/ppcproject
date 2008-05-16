#!/usr/bin/env python
# -*- coding: utf-8 -*-

# XXX Falta comentario indicando el proposito de este fichero!! XXX
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
    """ XXX Falta comentario indicando el proposito de esta clase """

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
    def set_width(self, widget, width):
        """
        Set width
        
        width: width
        """
        self.table.set_width(width)
    def update(self):
        """
        Redraw loading diagram.
        
        """
        self.table.queue_draw()
    def clear(self):
        """
        Clean loading diagram.
        
        """
        self.table.clear()   

        
class table(gtk.Layout):
    """ XXX Falta comentario indicando el proposito de esta clase """

    def __init__(self):
        gtk.Layout.__init__(self)
        self.colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 1.0, 0.0), (0.5, 0.3, 0.1), (1.0, 0.6, 0.0), (0.8, 0.1, 0.5), (0.0, 0.4, 0.0), (0.1, 0.1, 0.4), (1.0, 0.7, 0.8), (0.6, 0.5, 0.9)]
        self.cell_width = 0
        self.width = 0
        self.rowHeight = 0
        self.loading = {}
        self.duration = 0
        self.set_tooltip_text("")
        self.connect("query-tooltip", self.set_tooltip)
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
        
    def clear(self):
        """
        Clean loading diagram.
        
        """
        self.loading = {}
        self.duration = 0
    
    def set_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        #XXX poner normal sin try y sin queuedraw
        keys = self.loading.keys()
        keys.sort()
        if self.rowHeight != 0:
            try:
                tooltip.set_text(keys[int(y) / self.rowHeight])
            except:
                pass
        self.queue_draw()    
        return True
            
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
        if len(self.loading) != 0: 
            self.rowHeight = (self.available_height - 1) / len(self.loading)
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
        # Drawing the table     
        loadingCopy = copy.deepcopy(self.loading)
        colorIndex = 0
        heightIndex = 1
        loadingKeys = loadingCopy.keys()
        loadingKeys.sort()
        for key in loadingKeys:
            while loadingCopy[key] != []:
                x1, y1 = loadingCopy[key].pop(0)
                if loadingCopy[key] != []:
                    x2, y2 = loadingCopy[key][0]
                else:
                    x2 = self.duration
                # Drawing the rectangle
                ctx.rectangle (x1 * self.cell_width, heightIndex, x2 * self.cell_width - x1 * self.cell_width, self.rowHeight)
                ctx.set_source_rgba(self.colors[colorIndex][0], self.colors[colorIndex][1], self.colors[colorIndex][2],0.3)
                ctx.fill_preserve()
                ctx.set_line_width(1)
                ctx.set_source_color(self.get_style().fg[gtk.STATE_NORMAL])
                ctx.stroke()
                # Drawing the use of resource
                x_bearing, y_bearing, txt_width, txt_height = ctx.text_extents(str(int(y1)))[:4]
                ctx.move_to(x2 * self.cell_width - (x2 * self.cell_width - x1 * self.cell_width) / 2 - txt_width / 2 - x_bearing, heightIndex + self.rowHeight / 2 - txt_height / 2 - y_bearing )
                ctx.show_text(str(int(y1)))
                
            
            colorIndex = (colorIndex + 1) % 11
            heightIndex += self.rowHeight

                
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
