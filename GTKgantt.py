#!/usr/bin/env python
"""

Interface:
   -set_vadjustment(adjustment)
   -set_row_height(num)
   -update()
   -add_activity(name, prelations, duration, start_time)
   -rename_activity(old, new)
   -set_activity_duration(activity, duration)
   -set_activity_prelations(activity, prelations)
   -set_activity_start_time(activity, time)
   -set_activity_comment(activity, comment)
   -set_activity_slack(activity, slack)
   -remove_activity(activity)
   -reorder(activities)
   -clear()

"""
import cairo
import math
import gtk
import gtk.gdk
import gobject

class GTKgantt(gtk.VBox):
   def __init__(self):
      gtk.VBox.__init__(self)
      self.set_homogeneous(False)
      self.header = GanttHeader()
      self.diagram = GanttDrawing()
      self.diagram.set_hadjustment(self.header.get_hadjustment())
      self.scrolled_window = gtk.ScrolledWindow(self.diagram.get_hadjustment(), self.diagram.get_vadjustment())
      self.pack_start(self.header, False, False, 0)
      self.pack_start(self.scrolled_window, True, True, 0)
      self.scrolled_window.set_policy(gtk.POLICY_ALWAYS,gtk.POLICY_AUTOMATIC)
      self.scrolled_window.add(self.diagram)
      self.set_size_request(100,100)
      self.diagram.connect("gantt-width-changed", self.header.set_width)
   def set_vadjustment(self, adjustment):
      self.diagram.set_vadjustment(adjustment)
   def set_row_height(self,num):
      self.diagram.set_row_height(num)
      self.header.set_cell_width(num)
      self.set_size_request(num, num)
   def update(self):
      self.diagram.queue_draw()
      self.header.queue_draw()
   def add_activity(self, name, prelations, duration = 0, start_time = 0, slack = 0, comment = ""):
      self.diagram.add_activity(name, prelations, duration, start_time, slack, comment)
   def rename_activity(self,old,new):
      if (old != new):
         self.diagram.set_activity_name(old,new)
   def set_activity_duration(self, activity, duration):
      self.diagram.set_activity_duration(activity,duration)
   def set_activity_prelations(self,activity,prelations):
      self.diagram.set_activity_prelations(activity,prelations)
   def set_activity_slack(self,activity,slack):
      self.diagram.set_activity_slack(activity,slack)
   def set_activity_comment(self,activity,comment):
      self.diagram.set_activity_comment(activity,comment)
   def set_activity_start_time(self,activity,time):
      self.diagram.set_activity_start_time(activity,time)
   def remove_activity(self, activity):
      self.diagram.remove_activity(activity)
   def reorder(self,activities):
      self.diagram.reorder(activities)
   def clear(self):
      self.diagram.clear()
      self.header.set_width(0)
      self.update()

class GanttHeader(gtk.Layout):
   """
   Properties:
      -Project Duration.
      -Cell width.
   """
   def __init__(self):
      gtk.Layout.__init__(self)
      self.connect("expose-event", self.expose)
      self.width = self.cell_width = 25
      self.set_size_request(self.cell_width, self.cell_width + 2)

   def set_cell_width(self,num):
      self.cell_width = num
      self.set_size_request(self.width, num + 2)

   def set_width(self, widget, width):
      if width != self.width:
         self.width = width
         self.set_size_request(width, self.cell_width + 2)

   def expose (self,widget,event):
      #Creating Cairo drawing context
      self.context = self.bin_window.cairo_create()
      #Setting context size to available size
      self.context.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
      self.context.clip()
      #Obtaining available width
      self.available_width = event.area.width
      #Drawing
      self.draw(self.context)
      return False

   def draw(self, context):
      #Obtaining needed width and height
      height = self.cell_width + 2
      #Setting Layout size
      self.set_size(self.width + self.cell_width, height)
      #Drawing squares with numbers inside
      for i in range(0, max(self.available_width, self.width) / self.cell_width + 1):
         context.rectangle(i * self.cell_width + 0.5, 0.5, self.cell_width, self.cell_width+1)
         x_bearing, y_bearing, txt_width, txt_height = context.text_extents(str(i+1))[:4]
         context.move_to((i + 0.5) * self.cell_width + 0.5 - txt_width / 2 - x_bearing, self.cell_width / 2 - txt_height / 2 - y_bearing + 0.5)
         context.show_text(str(i+1))
      context.set_line_width(1);
      context.set_source_rgb(0, 0, 0)
      context.stroke()

class Diagram_graph():
   activities = []
   durations={}
   prelations={}
   start_time={}
   slacks = {}
   comments = {}

class GanttDrawing(gtk.Layout):
   __gsignals__ = {'gantt-width-changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,(gobject.TYPE_INT,))}
   def __init__(self):
      gtk.Layout.__init__(self)
      self.connect("expose-event", self.expose)
      self.graph = Diagram_graph()
      self.row_height = 25
      self.width = 0
      self.modified = 0

   def set_row_height(self,num):
      self.row_height = num
      self.set_size_request(self.width ,num)

   def get_needed_length (self, context):
      lengths = []
      for activity in self.graph.activities:
         x_bearing, y_bearing, txt_width, txt_height = context.text_extents(self.graph.comments[activity])[:4]
         lengths.append( (self.graph.start_time[activity] + self.graph.durations[activity] + self.graph.slacks[activity] + 0.25)* self.row_height + 0.5 + x_bearing + txt_width)
      return(int(max(lengths)+1))

   def clear(self):
      del self.graph
      self.graph = Graph()

   def add_activity(self, name, prelations, duration, start_time, slack, comment):
      if (name != ""):
         self.graph.activities.append(name)
         if (prelations == ""):
            prelations = []
         self.graph.prelations[name] = prelations
         if (duration == ""):
            duration = 0
         self.graph.durations[name] = duration
         if (start_time == ""):
            start_time = 0
         self.graph.start_time[name] = start_time
         if (slack == ""):
            slack = 0
         self.graph.slacks[name] = slack
         self.graph.comments[name] = comment
         self.modified = 1

   def set_activity_name(self,activity,name):
      for act in self.graph.activities:
         if activity in self.graph.prelations[act]:
            self.graph.prelations[act].remove(activity)
            self.graph.prelations[act].append(name)
      self.graph.activities[self.graph.activities.index(activity)] = name

   def set_activity_duration(self, activity, duration):
      self.graph.durations[activity] = duration
      self.modified = 1

   def set_activity_prelations(self,activity,prelations):
      self.graph.prelations[activity] = prelation

   def set_activity_slack(self,activity,slack):
      self.graph.slacks[activity] = slack
      self.modified = 1

   def set_activity_comment(self,activity,comment):
      self.graph.comments[activity] = comment
      self.modified = 1

   def set_activity_start_time(self, activity, time):
      self.graph.start_time[activity] = time
      self.modified = 1

   def remove_activity(self, activity):
      if activity in self.graph.activities:
         for act in self.graph.activities:
            if activity in self.graph.prelations[act]:
               self.graph.prelations[act].remove(activity)
         self.graph.activities.remove(activity)
         self.modified = 1

   def reorder(self,activities):
      self.graph.activities = activities

   def expose (self,widget,event):
      #Creating Cairo drawing context
      self.context = self.bin_window.cairo_create()
      #Setting context size to available size
      self.context.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
      self.context.clip()
      #Obtaining available width
      self.available_width = event.area.width
      self.available_height = event.area.height
      #Drawing
      self.draw(self.context)
      return False

   def draw(self, context):
      if self.graph.activities != [] and self.modified == 1:
         width = self.get_needed_length(context)
         if width != self.width:
            self.set_size_request(width, self.row_height)
            self.width = width
            self.emit("gantt-width-changed",width)
            self.modified = 0
      height = self.row_height * len(self.graph.activities)
      self.set_size(self.width, height)
      for i in range(0, max(self.available_width, self.width) / self.row_height + 1):
         context.move_to(i * self.row_height + 0.5,-0.5)
         context.line_to(i * self.row_height + 0.5, max(self.available_height, height, self.get_vadjustment().upper) + 0.5)
      context.set_line_width(1)
      context.set_source_rgb(0.7, 0.7, 0.7)
      context.stroke()
      for activity in self.graph.activities:
         context.rectangle((self.graph.start_time[activity]+self.graph.durations[activity])* self.row_height + 0.5, self.graph.activities.index(activity) * self.row_height + 0.5, self.graph.slacks[activity] * self.row_height , self.row_height - 1 )
      context.set_line_width(1)
      context.set_source_rgba(0.7, 0.1, 0.1,0.6)
      context.fill_preserve()
      context.set_source_rgb(0, 0, 0)
      context.stroke()
      for activity in self.graph.activities:
         context.rectangle(self.graph.start_time[activity]* self.row_height + 0.5, self.graph.activities.index(activity) * self.row_height + 0.5, self.graph.durations[activity] * self.row_height , self.row_height - 1 )
         x_bearing, y_bearing, txt_width, txt_height = context.text_extents(self.graph.comments[activity])[:4]
         context.move_to((self.graph.start_time[activity] + self.graph.durations[activity] + self.graph.slacks[activity] + 0.25)* self.row_height + 0.5 + x_bearing, (self.graph.activities.index(activity)+ 1) * self.row_height - 0.5 + y_bearing + 0.5)
         context.show_text(self.graph.comments[activity])
      context.set_line_width(1)
      context.set_source_rgba(0.7, 0.8, 0.1,0.6)
      context.fill_preserve()
      context.set_source_rgb(0, 0, 0)
      context.stroke()
      for activity in self.graph.activities:
         x = (self.graph.start_time[activity] + self.graph.durations[activity]) * self.row_height + 0.5
         y = (self.graph.activities.index(activity) + 0.5) * self.row_height - 0.5
         context.set_source_rgb(0, 0, 0)
         for children in self.graph.prelations[activity]:
            id_actividad2 = self.graph.activities.index(children)
            context.arc(x,y, self.row_height / 8, 0 , 2 * math.pi )
            context.fill()
            context.move_to(x,y)
            y2 = (id_actividad2) * self.row_height - 3.5
            context.line_to(x, y2 )
            context.move_to(x,y2)
            x2 = self.graph.start_time[children] * self.row_height + 0.5
            context.line_to(x2, y2)
            context.stroke()
            v1 = x2 - 3.5
            v2 = x2 + 3.5
            context.move_to(v1, y2)
            context.line_to(x2, self.row_height * id_actividad2 - 0.5)
            context.rel_line_to(3, -3)
            context.close_path()
            context.fill_preserve()
            context.stroke()

def main():
   window = gtk.Window()
   gantt = GTKgantt()
   gantt.add_activity("A", ["B", "C"], 5,0, 0, "Initial Activity")
   gantt.add_activity("B", ["D"], 3, 5, 11)
   gantt.add_activity("C", ["D","E","F","G"], 2, 5,  0 , "Critical Activity")
   gantt.add_activity("D", ["J"], 4, 8, 11)
   gantt.add_activity("E", ["J"], 6, 7, 10, "Not so important activity")
   gantt.add_activity("F", ["H"], 3, 7, 15)
   gantt.add_activity("G", ["I"], 9, 7, 0, "Critical Activity")
   gantt.add_activity("H", [], 1, 15, 10)
   gantt.add_activity("I", [], 10, 16, 0, "Final Activity")
   gantt.add_activity("J", ["H"], 2, 13, 10)
   gantt.set_row_height(25)
   window.add(gantt)
   window.connect("destroy", gtk.main_quit)
   gantt.update()
   window.show_all()
   gtk.main()

if __name__ == "__main__":
   main()	
