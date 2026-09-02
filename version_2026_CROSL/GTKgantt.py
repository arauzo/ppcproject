#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cairo
import math
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk


class GTKgantt(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.header = GanttHeader()
        self.diagram = GanttDrawing()

        self.diagram.set_hadjustment(self.header.get_hadjustment())

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hadjustment(self.diagram.get_hadjustment())
        self.scrolled_window.set_vadjustment(self.diagram.get_vadjustment())

        self.pack_start(self.header, False, False, 0)
        self.pack_start(self.scrolled_window, True, True, 0)
        self.scrolled_window.add(self.diagram)

        self.scrolled_window.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.AUTOMATIC)
        self.set_size_request(100, 100)

        self.diagram.connect("gantt-width-changed", self.header.set_width)

    def set_vadjustment(self, adjustment):
        self.diagram.set_vadjustment(adjustment)

    def set_hadjustment(self, adjustment):
        self.diagram.set_hadjustment(adjustment)
        self.header.set_hadjustment(adjustment)

    def set_policy(self, hpol, vpol):
        self.scrolled_window.set_policy(hpol, vpol)

    def set_cell_width(self, num):
        self.header.set_cell_width(num)
        self.diagram.set_cell_width(num)

    def set_row_height(self, num):
        self.diagram.set_row_height(num)

    def set_header_height(self, num):
        self.header.set_height(num)

    def update(self):
        self.diagram.queue_draw()
        self.header.queue_draw()

    def add_activity(self, name, prelations=None, duration=0, start_time=0, slack=0, comment=""):
        if prelations is None:
            prelations = []
        self.diagram.add_activity(name, prelations, duration, start_time, slack, comment)

    def rename_activity(self, old, new):
        if old != new:
            self.diagram.set_activity_name(old, new)

    def set_activity_duration(self, activity, duration):
        self.diagram.set_activity_duration(activity, duration)

    def set_activity_prelations(self, activity, prelations):
        self.diagram.set_activity_prelations(activity, prelations)

    def set_activity_slack(self, activity, slack):
        self.diagram.set_activity_slack(activity, slack)

    def set_activity_comment(self, activity, comment):
        self.diagram.set_activity_comment(activity, comment)

    def set_activity_start_time(self, activity, time):
        self.diagram.set_activity_start_time(activity, time)

    def set_activities_color(self, color):
        self.diagram.set_activities_color(color)

    def set_slack_color(self, color):
        self.diagram.set_slack_color(color)

    def set_thin_slack(self, value):
        self.diagram.set_thin_slack(value)

    def remove_activity(self, activity):
        self.diagram.remove_activity(activity)

    def reorder(self, activities):
        self.diagram.reorder(activities)

    def show_arrows(self, value):
        self.diagram.show_arrows(value)

    def show_extra_row(self, value):
        self.diagram.show_extra_row(value)

    def clear(self):
        self.diagram.clear()
        self.header.set_width(None, 0)


class GanttHeader(Gtk.Layout):
    def __init__(self):
        super().__init__()
        self.width = 25
        self.cell_width = 25
        self.height = 28
        self.connect("draw", self.on_draw)
        self.set_size_request(self.width, self.height)

    def set_cell_width(self, num):
        self.cell_width = num
        self.queue_draw()

    def set_width(self, widget, width):
        self.width = width
        self.set_size_request(width, self.height)
        self.queue_draw()

    def set_height(self, num):
        self.height = num
        self.set_size_request(self.width, self.height)
        self.queue_draw()

    def on_draw(self, widget, context):
        self.available_width = widget.get_allocated_width()
        self.draw_content(context)
        return False

    def draw_content(self, context):
        self.set_size(self.width + self.cell_width, self.height)
        context.translate(0.5, 0.5)

        style = self.get_style_context()
        color = style.get_color(Gtk.StateFlags.NORMAL)
        context.set_source_rgba(color.red, color.green, color.blue, color.alpha)

        limit = int(max(self.available_width, self.width) / self.cell_width) + 1
        for i in range(limit):
            context.rectangle(i * self.cell_width, 0, self.cell_width, self.height - 1)
            txt = str(i)
            xb, yb, tw, th, dx, dy = context.text_extents(txt)
            context.move_to(
                (i + 0.5) * self.cell_width - tw / 2 - xb,
                self.height / 2 - th / 2 - yb,
            )
            context.show_text(txt)

        context.set_line_width(1)
        context.stroke()


class DiagramGraph(object):
    def __init__(self):
        self.activities = []
        self.durations = {}
        self.prelations = {}
        self.start_time = {}
        self.slacks = {}
        self.comments = {}


class GanttDrawing(Gtk.Layout):
    __gsignals__ = {
        'gantt-width-changed': (GObject.SignalFlags.RUN_FIRST, None, (int,))
    }

    def __init__(self):
        super().__init__()
        self.graph = DiagramGraph()
        self.row_height = 25
        self.cell_width = 25
        self.width = 0
        self.modified = 0
        self.activities_color = None
        self.slack_color = None
        self.thin_slack = True
        self.arrows = True
        self.selected = None
        self.extra_row = True

        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.LEAVE_NOTIFY_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK
        )

        self.connect("draw", self.on_draw)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.connect("leave-notify-event", self.on_mouse_leave)

    def set_row_height(self, num):
        self.row_height = num
        self.modified = 1
        self.queue_draw()

    def set_cell_width(self, num):
        self.cell_width = num
        self.modified = 1
        self.queue_draw()

    def on_mouse_move(self, widget, event):
        previous = self.selected
        try:
            idx = int(event.y / self.row_height)
            act = self.graph.activities[idx]
            x_start = self.graph.start_time[act] * self.cell_width
            x_end = (self.graph.start_time[act] + self.graph.durations[act]) * self.cell_width
            if x_start <= event.x <= x_end:
                if act != previous:
                    self.selected = act
                    self.queue_draw()
            else:
                self.selected = None
                if previous:
                    self.queue_draw()
        except Exception:
            self.selected = None
            if previous:
                self.queue_draw()
        return False

    def on_mouse_leave(self, widget, event):
        if self.selected:
            self.selected = None
            self.queue_draw()
        return False

    def get_needed_length(self, context):
        if not self.graph.activities:
            return 0

        lengths = []
        for activity in self.graph.activities:
            comment = str(self.graph.comments.get(activity, ""))
            xb, yb, tw, th, dx, dy = context.text_extents(comment)
            val = (
                (self.graph.start_time[activity] +
                 self.graph.durations[activity] +
                 self.graph.slacks[activity] + 0.25) * self.cell_width
                + 0.5 + xb + tw
            )
            lengths.append(val)

        return int(max(lengths) + 1) if lengths else 0


    def clear(self):
        self.graph = DiagramGraph()
        self.selected = None
        self.width = 0
        self.modified = 1
        self.queue_draw()

    def add_activity(self, name, prelations, duration, start_time, slack, comment):
        if name != "":
            self.graph.activities.append(name)
            self.graph.prelations[name] = prelations if prelations != "" else []
            self.graph.durations[name] = float(duration) if duration != "" else 0
            self.graph.start_time[name] = float(start_time) if start_time != "" else 0
            self.graph.slacks[name] = float(slack) if slack != "" else 0
            self.graph.comments[name] = comment
            self.modified = 1
            self.queue_draw()

    def set_activity_name(self, old, new):
        if old not in self.graph.activities or not new:
            return

        index = self.graph.activities.index(old)
        self.graph.activities[index] = new

        self.graph.durations[new] = self.graph.durations.pop(old, 0)
        self.graph.prelations[new] = self.graph.prelations.pop(old, [])
        self.graph.start_time[new] = self.graph.start_time.pop(old, 0)
        self.graph.slacks[new] = self.graph.slacks.pop(old, 0)
        self.graph.comments[new] = self.graph.comments.pop(old, "")

        for act in self.graph.activities:
            prelations = self.graph.prelations.get(act, [])
            self.graph.prelations[act] = [new if p == old else p for p in prelations]

        if self.selected == old:
            self.selected = new

        self.modified = 1
        self.queue_draw()

    def set_activity_duration(self, activity, duration):
        if activity in self.graph.durations:
            self.graph.durations[activity] = float(duration)
            self.modified = 1
            self.queue_draw()

    def set_activity_prelations(self, activity, prelations):
        if activity in self.graph.prelations:
            self.graph.prelations[activity] = prelations
            self.queue_draw()

    def set_activity_slack(self, activity, slack):
        if activity in self.graph.slacks:
            self.graph.slacks[activity] = float(slack)
            self.modified = 1
            self.queue_draw()

    def set_activity_comment(self, activity, comment):
        if activity in self.graph.comments:
            self.graph.comments[activity] = comment
            self.modified = 1
            self.queue_draw()

    def set_activity_start_time(self, activity, time):
        if activity in self.graph.start_time:
            self.graph.start_time[activity] = float(time)
            self.modified = 1
            self.queue_draw()

    def set_activities_color(self, color):
        self.activities_color = color
        self.queue_draw()

    def set_slack_color(self, color):
        self.slack_color = color
        self.queue_draw()

    def set_thin_slack(self, value):
        self.thin_slack = value
        self.queue_draw()

    def remove_activity(self, activity):
        if activity in self.graph.activities:
            self.graph.activities.remove(activity)
            self.graph.durations.pop(activity, None)
            self.graph.prelations.pop(activity, None)
            self.graph.start_time.pop(activity, None)
            self.graph.slacks.pop(activity, None)
            self.graph.comments.pop(activity, None)
            self.modified = 1
            self.queue_draw()

    def reorder(self, activities):
        self.graph.activities = list(activities)
        self.queue_draw()

    def show_arrows(self, value):
        self.arrows = value
        self.queue_draw()

    def show_extra_row(self, value):
        self.extra_row = value
        self.modified = 1
        self.queue_draw()

    def _draw_arrow_head(self, context, end_x, edge_y, from_above, size=3):
        context.move_to(end_x - size, edge_y)
        context.line_to(end_x, edge_y + (size if from_above else -size))
        context.line_to(end_x + size, edge_y)
        context.close_path()
        context.fill_preserve()
        context.stroke()

    def _draw_relation_origin(self, context, x, y, radius=2.2):
        context.arc(x, y, radius, 0, 2 * math.pi)
        context.fill()

    def _draw_prelations(self, context, style, sel_list):
        if not self.arrows:
            return

        index_by_activity = {
            activity: index for index, activity in enumerate(self.graph.activities)
        }

        text_color = style.get_color(Gtk.StateFlags.NORMAL)
        for activity in self.graph.activities:
            predecessors = self.graph.prelations.get(activity, [])
            if not predecessors:
                continue

            target_index = index_by_activity.get(activity)
            if target_index is None:
                continue

            target_x = self.graph.start_time.get(activity, 0) * self.cell_width

            for predecessor in predecessors:
                pred_index = index_by_activity.get(predecessor)
                if pred_index is None:
                    continue

                pred_end_x = (
                    self.graph.start_time.get(predecessor, 0) +
                    self.graph.durations.get(predecessor, 0)
                ) * self.cell_width
                pred_y = pred_index * self.row_height + (self.row_height / 2.0)

                if self.selected and activity not in sel_list and predecessor not in sel_list:
                    continue
                alpha = 0.9

                context.set_source_rgba(
                    text_color.red,
                    text_color.green,
                    text_color.blue,
                    alpha
                )
                context.set_line_width(1)

                start_x = pred_end_x
                start_y = pred_y
                from_above = target_index > pred_index
                if from_above:
                    target_line_y = (target_index * self.row_height) - 4
                    target_edge_y = (target_index * self.row_height) - 1
                else:
                    target_line_y = ((target_index + 1) * self.row_height) + 3
                    target_edge_y = (target_index + 1) * self.row_height

                context.move_to(start_x, start_y)
                context.line_to(start_x, target_line_y)
                context.line_to(target_x, target_line_y)
                context.stroke()

                context.set_source_rgba(
                    text_color.red,
                    text_color.green,
                    text_color.blue,
                    alpha
                )
                self._draw_relation_origin(context, start_x, start_y)
                self._draw_arrow_head(context, target_x, target_edge_y, from_above)

    def on_draw(self, widget, context):
        if self.graph.activities and self.modified == 1:
            new_width = self.get_needed_length(context)
            if new_width != self.width:
                self.width = new_width
                self.emit("gantt-width-changed", int(self.width))
            self.modified = 0

        height = self.row_height * (len(self.graph.activities) + (1 if self.extra_row else 0))
        self.set_size(self.width, height)

        context.translate(0.5, 0.5)

        style = self.get_style_context()
        fg = style.get_color(Gtk.StateFlags.INSENSITIVE)
        context.set_source_rgba(fg.red, fg.green, fg.blue, 0.2)

        limit = int(max(widget.get_allocated_width(), self.width) / self.cell_width) + 1
        for i in range(limit):
            context.move_to(i * self.cell_width, 0)
            context.line_to(i * self.cell_width, height)

        context.set_line_width(1)
        context.stroke()

        sel_list = []
        if self.selected:
            sel_list = [self.selected] + self.graph.prelations.get(self.selected, [])

        for i, act in enumerate(self.graph.activities):
            y = i * self.row_height

            if self.slack_color is not None:
                context.set_source_rgba(*self.slack_color)
            else:
                context.set_source_rgba(0.5, 0.5, 0.5, 0.3)

            h_x = (self.graph.start_time[act] + self.graph.durations[act]) * self.cell_width
            h_w = self.graph.slacks[act] * self.cell_width
            h_h = (self.row_height / 4) if self.thin_slack else self.row_height - 1
            context.rectangle(h_x, y, h_w, h_h)
            context.fill()

            if self.activities_color is not None:
                r, g, b, a = self.activities_color
                alpha = 0.3 if (self.selected and act not in sel_list) else a
                context.set_source_rgba(r, g, b, alpha)
            else:
                color_bar = Gdk.RGBA(red=0.95, green=0.64, blue=0.52, alpha=1.0)
                alpha = 0.3 if (self.selected and act not in sel_list) else 0.8
                context.set_source_rgba(color_bar.red, color_bar.green, color_bar.blue, alpha)

            a_x = self.graph.start_time[act] * self.cell_width
            a_w = self.graph.durations[act] * self.cell_width
            context.rectangle(a_x, y, a_w, self.row_height - 1)
            context.fill_preserve()

            text_color = style.get_color(Gtk.StateFlags.NORMAL)
            context.set_source_rgba(text_color.red, text_color.green, text_color.blue, 1.0)
            context.set_line_width(1)
            context.stroke()

            context.move_to(
                a_x + a_w + (self.graph.slacks[act] * self.cell_width) + 5,
                y + self.row_height / 1.5
            )
            context.show_text(str(self.graph.comments.get(act, "")))

        self._draw_prelations(context, style, sel_list)

        return False
