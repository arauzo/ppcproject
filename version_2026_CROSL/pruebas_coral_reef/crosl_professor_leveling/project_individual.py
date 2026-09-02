#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ProjectLevelingIndividual:
    """
    Coral codificado como tiempos de inicio de actividades.
    """

    def __init__(self, start_times):
        self.start_times = dict(start_times)
        self.schedule = None
        self.fitness = None
        self.feasible = True
        self.substrate = None

    def copy(self):
        clone = ProjectLevelingIndividual(self.start_times)
        clone.schedule = self.schedule
        clone.fitness = self.fitness
        clone.feasible = self.feasible
        clone.substrate = self.substrate
        return clone

    def get_fitness(self):
        return self.fitness

    def is_feasible(self):
        return self.feasible

