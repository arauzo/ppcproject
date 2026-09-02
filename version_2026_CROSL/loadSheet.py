#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cairo
import math
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
import copy
import random

class LoadSheet(Gtk.Box):
    """
    Class loadSheet adaptada a GTK 3
    """
    def __init__(self):
        # Inicializamos como Box horizontal
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        self.diagram = LoadSheetDiagram()
        self.scale = LoadSheetScale()
        
        self.set_homogeneous(False)
        self.pack_start(self.scale, False, False, 0)
        self.pack_start(self.diagram, True, True, 0)
        
        # ConexiÃ³n de seÃ±al personalizada
        self.diagram.connect("greatest-calculated", self.scale.set_greatest)
        
    def set_cell_width(self, width):
        self.diagram.cell_width = width
    
    def set_loading(self, loading):
        self.diagram.loading = loading

    def set_duration(self, duration):
        self.diagram.duration = duration
        self.scale.duration = duration
        
    def set_hadjustment(self, adjustment):
        self.diagram.set_hadjustment(adjustment)     

    def set_width(self, widget, width):
        self.diagram.set_width(width)

    def update(self):
        self.diagram.queue_draw()
        self.scale.queue_draw()

    def clear(self):
        self.diagram.clear()   


class LoadSheetScale(Gtk.Layout):
    def __init__(self):
        super().__init__()
        self.greatest = 0
        self.duration = 0
        self.set_size_request(20, 20)
        self.connect("draw", self.on_draw)
        
    def set_greatest(self, widget, greatest):
        self.greatest = greatest
        self.queue_draw()  
        
    def on_draw(self, widget, ctx):
        # En GTK3 el contexto ya viene preparado
        alloc = widget.get_allocation()
        self.available_width = alloc.width
        self.available_height = alloc.height
        
        # Clip para no dibujar fuera
        ctx.rectangle(0, 0, self.available_width, self.available_height)
        ctx.clip()
        
        # Ajuste fino de posiciÃ³n (reemplaza el translate antiguo)
        ctx.translate(20.5, -0.5) 
        self.draw_content(ctx)
        return False
              
    def draw_content(self, ctx):
        if self.greatest <= 0:
            return
            
        step = self.greatest / 5
        style = self.get_style_context()
        color = style.get_color(Gtk.StateFlags.NORMAL)
        ctx.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        
        # Dibujar escala de nÃºmeros
        for i in range(0, int(self.greatest) + 1, max(1, int(step))):
            txt = str(i)
            xb, yb, tw, th, dx, dy = ctx.text_extents(txt)
            # Calculamos posiciÃ³n Y invertida
            y_pos = self.available_height - (self.available_height - 20) * i / self.greatest
            ctx.move_to(-10.5 - tw / 2 - xb, y_pos - th / 2 - yb)
            ctx.show_text(txt)
        
        
class LoadSheetDiagram(Gtk.Layout):
    # DefiniciÃ³n de la seÃ±al para GObject Introspection
    __gsignals__ = {
        'greatest-calculated': (GObject.SignalFlags.RUN_FIRST, None, (int,))
    }

    def __init__(self):
        super().__init__()
        self.colors = [(1.0, 0.0, 0.0), (0.0, 0.7, 0.0), (0.0, 0.0, 1.0), 
                       (0.8, 0.8, 0.0), (0.5, 0.3, 0.1), (1.0, 0.6, 0.0), 
                       (0.8, 0.1, 0.5), (0.0, 0.4, 0.0), (0.1, 0.1, 0.4), 
                       (1.0, 0.4, 0.4), (0.6, 0.5, 0.9)]
        self.cell_width = 20
        self.loading = {}
        self.width = 0
        self.duration = 0
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
    
    def calculate_greatest(self):
        greatest = 0
        for resourceList in list(self.loading.values()):
            for time, use in resourceList:
                if use > greatest:
                    greatest = use
        self.emit("greatest-calculated", int(greatest))
        return greatest
    
    def clear(self):
        self.loading = {}
        self.duration = 0
        self.width = 0
        self.queue_draw()
            
    def on_draw(self, widget, ctx):
        alloc = widget.get_allocation()
        self.available_width = alloc.width
        self.available_height = alloc.height
        
        self.set_size(int(self.width), self.available_height)  
        ctx.translate(0.5, -0.5)
        
        # Dibujar lÃ­neas de celdas (verticales)
        num_lines = int(max(self.available_width, int(self.width)) / max(1, self.cell_width)) + 1
        for i in range(num_lines):
            ctx.move_to(i * self.cell_width, 0)
            ctx.line_to(i * self.cell_width, self.available_height)
        
        ctx.set_line_width(1)
        style = self.get_style_context()
        fg = style.get_color(Gtk.StateFlags.INSENSITIVE)
        ctx.set_source_rgba(fg.red, fg.green, fg.blue, 0.3)
        ctx.stroke()

        greatest = self.calculate_greatest()
        if greatest <= 0: return False

        # LÃ­neas de escala horizontales (discontinuas)
        step = greatest / 5
        ctx.save()
        ctx.set_dash([5.0], 5.0)
        for i in range(0, int(greatest) + 1, max(1, int(step))):
            y_pos = self.available_height - (self.available_height - 20) * i / greatest
            ctx.move_to(0, y_pos)
            ctx.line_to(max(self.available_width, int(self.width)), y_pos)
            ctx.stroke()
        ctx.restore()

        # Dibujar el diagrama de cargas
        loadingCopy = copy.deepcopy(self.loading)
        colorIndex = 0
        loadingKeys = sorted(list(loadingCopy.keys()))
        
        for key in loadingKeys:
            points = loadingCopy[key]
            if not points: continue
            
            ctx.set_line_width(2)
            c = self.colors[colorIndex]
            ctx.set_source_rgba(c[0], c[1], c[2], 0.7)
            
            # Mover al primer punto
            x_init, y_init = points[0]
            ctx.move_to(x_init * self.cell_width, self.available_height - (self.available_height - 20) * y_init / greatest)
            
            for i in range(len(points)):
                x1, y1 = points[i]
                if i + 1 < len(points):
                    x2, _ = points[i+1]
                else:
                    x2 = self.duration
                
                # Dibujar escalÃ³n horizontal
                ctx.line_to(x1 * self.cell_width, self.available_height - (self.available_height - 20) * y1 / greatest)
                ctx.line_to(x2 * self.cell_width, self.available_height - (self.available_height - 20) * y1 / greatest)
                
            ctx.stroke()
            colorIndex = (colorIndex + 1) % len(self.colors)
        
        return False

def main():
    window = Gtk.Window()
    window.set_default_size(400, 200)
    ls = LoadSheet()
    ls.set_cell_width(20)
    window.add(ls)
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
