#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic SVG file viewer with zoom - Adaptado para GTK 3
"""
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Rsvg', '2.0')
from gi.repository import Gtk, Gdk, Rsvg
import cairo

class SVGViewer(Gtk.DrawingArea):
    """
    Create a GTK+ widget to draw an SVG using rsvg and Cairo
    """
    def __init__(self, svg_text=None):
        super(SVGViewer, self).__init__()
        self.svg = None
        self.svg_text = None
        self.zoom_factor = 1.0
        self.matrix = cairo.Matrix()
        
        self.update_svg(svg_text)
        
        # Conectar señales en GTK 3
        self.connect("draw", self.on_draw)
        self.connect("scroll-event", self.mousewheel_scrolled)
        self.add_events(Gdk.EventMask.SCROLL_MASK)

    def update_svg(self, svg_text):
        self.svg_text = svg_text
        self.zoom_factor = 1.0
        if svg_text is not None:
            # En GTK3/librsvg 2.0 se usa Handle.new_from_data
            if isinstance(svg_text, str):
                svg_text = svg_text.encode('utf-8')
            self.svg = Rsvg.Handle.new_from_data(svg_text)
            self.update_transformation()
            
    def update_transformation(self):
        if not self.svg:
            return
            
        rect = self.get_allocation()
        width = rect.width
        height = rect.height
        
        # Obtener dimensiones del SVG
        dimensions = self.svg.get_dimensions()
        graph_width = dimensions.width
        graph_height = dimensions.height
        
        # Evitar división por cero
        if graph_width == 0 or graph_height == 0:
            return

        scale_factor = min(width/graph_width, height/graph_height) * self.zoom_factor
        
        self.matrix = cairo.Matrix()
        self.matrix.scale(scale_factor, scale_factor)
        
        # Actualizar el tamaño solicitado para que los scrollbars (si los hay) funcionen
        self.set_size_request(int(graph_width * scale_factor), int(graph_height * scale_factor))

    def on_draw(self, widget, cr):
        """Handle the draw event (reemplaza a expose_event)"""
        if self.svg is not None:
            self.update_transformation()
            cr.transform(self.matrix)
            self.svg.render_cairo(cr)
        return False

    def redraw_canvas(self):
        """Force updating the canvas"""
        self.queue_draw()

    def mousewheel_scrolled(self, widget, event):
        """Zoom when mouse wheel is scrolled"""
        # En GTK 3 las constantes de dirección están en Gdk.ScrollDirection
        if event.direction == Gdk.ScrollDirection.UP:
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                self.zoom_factor *= 2.0
            else:
                self.zoom_factor *= 1.25
        elif event.direction == Gdk.ScrollDirection.DOWN:
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                self.zoom_factor *= 0.5
            else:
                self.zoom_factor *= 0.8
                
        # Limitar el zoom mínimo para no desaparecer
        self.zoom_factor = max(0.1, self.zoom_factor)
        
        self.redraw_canvas()
        return True

def main():
    window = Gtk.Window()
    window.set_default_size(800, 600)
    # Ejemplo con un SVG mínimo de prueba
    test_svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>'
    viewer = SVGViewer(test_svg)
    window.add(viewer)
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()