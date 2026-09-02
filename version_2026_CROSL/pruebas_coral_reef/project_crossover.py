#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from project_individual import IndividualProject


def crossover_average(parent1, parent2):
    child = {}
    for act in parent1.start_times.keys():
        child[act] = (parent1.start_times[act] + parent2.start_times[act]) / 2.0
    return IndividualProject(child)


def crossover_random_inheritance(parent1, parent2, rng):
    child = {}
    for act in parent1.start_times.keys():
        child[act] = (
            parent1.start_times[act]
            if rng.random() < 0.5
            else parent2.start_times[act]
        )
    return IndividualProject(child)


def crossover_weighted_average(parent1, parent2, rng):
    alpha = rng.uniform(0.25, 0.75)
    child = {}
    for act in parent1.start_times.keys():
        child[act] = (
            alpha * parent1.start_times[act]
            + (1.0 - alpha) * parent2.start_times[act]
        )
    return IndividualProject(child)


crossover_operator_dict = {
    "average": crossover_average,
    "random": crossover_random_inheritance,
    "weighted": crossover_weighted_average,
}
