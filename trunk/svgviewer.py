#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic SVG file viewer with zoom
"""
import pygtk
pygtk.require('2.0')
import gtk
import rsvg
import cairo

class SVGViewer(gtk.DrawingArea):
    """
    Create a GTK+ widget to draw an SVG using rsvg and Cairo
    
    XXX Implement pan operation
    XXX Zoom centering to pointer
    XXX Do not allow zoom out over actual size of widget
    XXX Implement scrollable ??
    """
    def __init__(self, svg_text=None):
        super(SVGViewer, self).__init__()
        self.svg = None
        self.svg_text = None
        self.update_svg(svg_text)
        self.connect("expose_event", self.expose_event)
        self.connect("scroll-event", self.mousewheel_scrolled)
        self.add_events(gtk.gdk.SCROLL_MASK)

    def update_svg(self, svg_text):
        self.svg_text = svg_text
        self.zoom_factor = 1.0
        if svg_text != None:
            self.svg = rsvg.Handle(data=svg_text)
            self.update_transformation()
            
    def update_transformation(self):
        rect = self.get_allocation()
        width = rect.width
        height = rect.height
        
        pw, ph, graph_width, graph_height = self.svg.get_dimension_data()
        scale_factor = min(width/graph_width, height/graph_height) # keep proportions
        self.matrix = cairo.Matrix()
        self.matrix.scale(scale_factor, scale_factor)
        
        self.set_size_request(int(graph_width*self.zoom_factor), int(graph_height*self.zoom_factor))

    def expose_event(self, widget, event):
        """Handle the expose-event by drawing"""
        context = widget.window.cairo_create()
         
        # Restrict Cairo to the exposed area; avoid extra work
        # (set a clip region for the expose event)
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()
         
        self.draw(context)
        return False

    def draw(self, cr):
#        # Fill the background with default foreground color (just to see if we are not drawing some area)
#        rect = self.get_allocation()
#        width = rect.width
#        height = rect.height

#        cr.set_source_color(self.style.fg[self.state]) #rgb(0.5, 0.5, 0.5) #grey
#        cr.rectangle(0, 0, width, height)
#        cr.fill()

#        cr.set_source_color(self.style.fg[self.state])
#        cr.rectangle(BORDER_WIDTH, BORDER_WIDTH,
#                    width - 2*BORDER_WIDTH, height - 2*BORDER_WIDTH)
#        cr.set_line_width(5.0)
#        cr.set_line_join(cairo.LINE_JOIN_ROUND)
#        cr.stroke()

        if self.svg != None:
            self.update_transformation()
            cr.transform(self.matrix)
            self.svg.render_cairo(cr)

        return True

    def redraw_canvas(self):
        """Force updating the canvas"""
        if self.window:
            alloc = self.get_allocation()
            rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
            self.window.invalidate_rect(rect, True)
            self.window.process_updates(True)

    def mousewheel_scrolled(self, widget, event):
        """Zoom when mouse wheel is scrolled"""
        if event.type == gtk.gdk.SCROLL:
            # Ctrl-mousewheel (faster zoom)
            if event.state & gtk.gdk.CONTROL_MASK:
                if event.direction == gtk.gdk.SCROLL_UP:
                    self.zoom_factor *= 2.0
                elif event.direction == gtk.gdk.SCROLL_DOWN:
                    self.zoom_factor *= 0.5
            # Mousewheel scroll alone (zoom)
            else:
                if event.direction == gtk.gdk.SCROLL_UP:
                    self.zoom_factor *= 1.25
                elif event.direction == gtk.gdk.SCROLL_DOWN:
                    self.zoom_factor *= 0.8
            zoom_point = event.x, event.y
            self.redraw_canvas()
            return True

