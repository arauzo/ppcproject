#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cairo
import math
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
import copy

class LoadTable(Gtk.Box):
    """
    Class loadTable adaptada a GTK 3
    """
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.table = Table()
        self.set_homogeneous(False)
        self.pack_start(self.table, True, True, 0)
        
    def set_cell_width(self, width):
        self.table.cell_width = width    
        
    def set_loading(self, loading):
        self.table.loading = loading
        
    def set_duration(self, duration):
        self.table.duration = duration
        
    def set_hadjustment(self, adjustment):
        self.table.set_hadjustment(adjustment)
        
    def set_width(self, widget, width):
        self.table.set_width(width)
        
    def update(self):
        self.table.queue_draw()
        
    def clear(self):
        self.table.clear()   

        
class Table(Gtk.Layout):
    def __init__(self):
        super().__init__()
        self.colors = [(1.0, 0.0, 0.0), (0.0, 0.7, 0.0), (0.0, 0.0, 1.0), 
                       (0.8, 0.8, 0.0), (0.5, 0.3, 0.1), (1.0, 0.6, 0.0), 
                       (0.8, 0.1, 0.5), (0.0, 0.4, 0.0), (0.1, 0.1, 0.4), 
                       (1.0, 0.4, 0.4), (0.6, 0.5, 0.9)]
        self.cell_width = 20
        self.width = 0
        self.rowHeight = 20
        self.loading = {}
        self.duration = 0
        self.set_has_tooltip(True)
        self.connect("query-tooltip", self.on_query_tooltip)
        self.connect("draw", self.on_draw)
        
    def set_cell_width(self, width):
        self.cell_width = width
    
    def set_loading(self, loading):
        self.loading = loading
        
    def set_duration(self, duration):
        self.duration = duration
                
    def set_width(self, width):
        self.width = width
        self.queue_draw()
        
    def clear(self):
        self.loading = {}
        self.duration = 0
        self.width = 0
        self.queue_draw()
    
    def on_query_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        # En GTK 3 x e y ya son relativos al widget
        keys = sorted(list(self.loading.keys()))
        if self.rowHeight > 0 and keys:
            try:
                index = int(y // self.rowHeight)
                if index < len(keys):
                    tooltip.set_text(str(keys[index]))
                    return True
            except Exception:
                pass
        return False
            
    def on_draw(self, widget, ctx):
        alloc = widget.get_allocation()
        self.available_width = alloc.width
        self.available_height = alloc.height
        
        if len(self.loading) != 0: 
            self.rowHeight = max(1, (self.available_height - 1) / len(self.loading))
            
        self.set_size(int(self.width), self.available_height)  
        
        # Dibujar líneas de celdas (verticales)
        ctx.translate(0.5, -0.5)
        num_lines = int(max(self.available_width, int(self.width)) / max(1, self.cell_width)) + 1
        for i in range(num_lines):
            ctx.move_to(i * self.cell_width, 0)
            ctx.line_to(i * self.cell_width, self.available_height)
            
        ctx.set_line_width(1)
        style = self.get_style_context()
        fg_insens = style.get_color(Gtk.StateFlags.INSENSITIVE)
        ctx.set_source_rgba(fg_insens.red, fg_insens.green, fg_insens.blue, 0.3)
        ctx.stroke()              
        
        # Dibujar la tabla
        loadingCopy = copy.deepcopy(self.loading)
        colorIndex = 0
        heightIndex = 1
        loadingKeys = sorted(list(loadingCopy.keys()))
        
        fg_normal = style.get_color(Gtk.StateFlags.NORMAL)
        
        for key in loadingKeys:
            points = loadingCopy[key]
            while points:
                x1, y1 = points.pop(0)
                if points:
                    x2, _ = points[0]
                else:
                    x2 = self.duration
                
                # El rectángulo del recurso
                rect_x = x1 * self.cell_width
                rect_w = (x2 - x1) * self.cell_width
                ctx.rectangle(rect_x, heightIndex, rect_w, self.rowHeight)
                
                c = self.colors[colorIndex]
                ctx.set_source_rgba(c[0], c[1], c[2], 0.4)
                ctx.fill_preserve()
                
                # Borde del rectángulo
                ctx.set_line_width(0.5)
                ctx.set_source_rgba(fg_normal.red, fg_normal.green, fg_normal.blue, 0.8)
                ctx.stroke()
                
                # Texto con el valor del uso
                if rect_w > 5: # Solo si cabe algo de texto
                    txt = str(int(y1))
                    xb, yb, tw, th, dx, dy = ctx.text_extents(txt)
                    ctx.move_to(rect_x + rect_w/2 - tw/2 - xb, 
                                heightIndex + self.rowHeight/2 - th/2 - yb)
                    ctx.set_source_rgba(fg_normal.red, fg_normal.green, fg_normal.blue, 1.0)
                    ctx.show_text(txt)
                
            colorIndex = (colorIndex + 1) % len(self.colors)
            heightIndex += self.rowHeight
        
        return False

def main():
    window = Gtk.Window()
    window.set_default_size(600, 400)
    lt = LoadTable()
    window.add(lt)
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()