#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random


class IndividualProject:
    """
    Individuo para scheduling basado en tiempos de inicio por actividad.
    """

    def __init__(self, start_times):
        self.start_times = start_times
        self.priorities = start_times
        self.schedule = None
        self.fitness = None
        self.feasible = True

    def copy_shallow(self):
        clone = IndividualProject(dict(self.start_times))
        clone.schedule = self.schedule
        clone.fitness = self.fitness
        clone.feasible = self.feasible
        return clone


def create_random_individual(activities, instance=None, rng=None):
    if instance is None:
        return IndividualProject({act: 0.0 for act in activities.keys()})

    generator = rng if rng is not None else random
    start_times = {}
    ordered = sorted(
        activities.keys(),
        key=lambda act: (instance.earliest_start.get(act, 0.0), str(act)),
    )

    for act in ordered:
        min_start = instance.earliest_start.get(act, 0.0)
        max_start = instance.latest_start.get(act, min_start)
        if max_start < min_start:
            max_start = min_start

        if float(min_start).is_integer() and float(max_start).is_integer():
            start_times[act] = float(generator.randint(int(min_start), int(max_start)))
        else:
            start_times[act] = generator.uniform(min_start, max_start)

    return IndividualProject(start_times)
