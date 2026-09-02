#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
description...
"""
import os
import pert
import subprocess
import shutil
import algoritmoGentoMunicio


def _find_dot_executable():
    candidates = [
        shutil.which('dot'),
        r'C:\Program Files\Graphviz\bin\dot.exe',
        r'C:\Program Files (x86)\Graphviz\bin\dot.exe',
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "Graphviz 'dot' was not found. Install Graphviz or add dot.exe to PATH."
    )

class TimedPert(pert.Pert):
    """
    PERT class to store pert graph data with durations

    durations = {activity : duration, ...}
    early = early time of the activities
    last = last time of the activities
    """
    def __init__(self, pertGraph=None, durations=None):
        super(TimedPert, self).__init__(pertGraph)
        self.construct = algoritmoGentoMunicio.gento_municio

        if pertGraph is not None:
            self.durations = {}
            for key, value in durations.items():
                if value == '' or value is None:
                    self.durations[key] = 0.0
                else:
                    self.durations[key] = float(value)

            self.early = self.calculate_early()
            self.last = self.calculate_last()

    def calculate_early(self):
        """
        Calculate early times
        returns: dictionary with the early times
        """
        # XXX Assumes nodes numbered from 1 to N.  Ok with precondition: renumbered??
        # XXX Then, it should use a list instead of a dict
        early = {}

        # Initialize early times for all nodes to 0
        for node in range(1, self.number_of_nodes()+1):
            early[node] = 0

        # Check from second node to last
        for node in range(2, self.number_of_nodes()+1):
            n_predecessors = self.pre(node)
            # Check predecessor nodes of each node
            for n_predecessor in n_predecessors:
                # Get activity between nodes
                arc = self.arcs[(n_predecessor, node)]
                activity, dummy = arc
                # Check if dummy
                if dummy:
                    if early[n_predecessor] > early[node]:
                        early[node] = early[n_predecessor]
                else:
                    if (early[n_predecessor]+self.durations[activity]
                        > early[node]):
                        early[node] = (early[n_predecessor]
                                       +self.durations[activity])
        return early

    def calculate_last(self):
        """
        Calculate last times
        Precondition: early times must have been already calculated
        returns: dictionary with the last times
        """
        last = {}

        # Initialize last times for all nodes to max early time
        for node in range(1, self.number_of_nodes()+1):
            last[node] = self.early[self.end_node()]

        # check from penultimate node to first
        for node in range(self.number_of_nodes()-1, 0, -1):
            n_successors = self.suc(node)
            # Check successors nodes of each node
            for n_successor in n_successors:
                arc = self.arcs[(node, n_successor)]
                activity, dummy = arc
                # Check if dummy
                if dummy:
                    if last[n_successor] < last[node]:
                        last[node] = last[n_successor]
                else:
                    if last[n_successor]-self.durations[activity] < last[node]:
                        last[node] = last[n_successor]-self.durations[activity]
        return last

    def timedpert2dot(self):
        """
        TimedPert Graph to txt dot format
        returns: string with text of dot language to draw the graph
        """
        txt = """digraph G {
        rankdir=LR;
        node[shape=Mrecord];
        """
        for node in self.successors:
            txt += (
                '"' + str(node) + '"'
                + '[label="{{' + str(node) + '|{'
                + str(self.early[node]) + '|'
                + str(self.last[node]) + '}}}"];\n'
            )
        txt += '\n'

        for act, sig in self.successors.items():
            for act_sig in sig:
                activity, is_dummy = self.arcs[(act, act_sig)]
                label_text = str(activity)

                txt += '"' + str(act) + '"' + '->' + '"' + str(act_sig) + '"'
                txt += '[label="' + label_text

                if is_dummy:
                    txt += '",style=dashed'
                else:
                    txt += '=' + str(self.durations[activity]) + '"'

                txt += '];\n'
        txt += '}\n'

        return txt



    def timedpert2image(self, file_format='svg'):
        """
        Graph drawed to image bytes using Graphviz.
        """
        dot_executable = _find_dot_executable()
        process = subprocess.Popen(
            [dot_executable, '-T', file_format],
            bufsize=-1,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        graph_image, stderr_data = process.communicate(self.timedpert2dot().encode('utf-8'))
        if process.returncode != 0:
            raise RuntimeError(
                'Graphviz execution failed: {}'.format(
                    stderr_data.decode('utf-8', errors='ignore')
                )
            )
        return graph_image

