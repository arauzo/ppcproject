#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy

from project_individual import IndividualProject


def _random_start_for(act, rng, instance):
    min_start = instance.earliest_start.get(act, 0.0)
    max_start = instance.latest_start.get(act, min_start)
    if max_start < min_start:
        max_start = min_start
    if float(min_start).is_integer() and float(max_start).is_integer():
        return float(rng.randint(int(min_start), int(max_start)))
    return rng.uniform(min_start, max_start)


def random_reset_mutation(individual, rng, mutation_rate=0.2, instance=None):
    mutated = copy.deepcopy(individual.start_times)
    for act in mutated:
        if rng.random() < mutation_rate:
            mutated[act] = _random_start_for(act, rng, instance) if instance else rng.random()
    return IndividualProject(mutated)


def small_perturbation_mutation(individual, rng, mutation_rate=0.2, step=0.15, instance=None):
    mutated = copy.deepcopy(individual.start_times)
    for act in mutated:
        if rng.random() < mutation_rate:
            if instance:
                min_start = instance.earliest_start.get(act, 0.0)
                max_start = instance.latest_start.get(act, min_start)
                span = max(1.0, max_start - min_start)
                delta = rng.uniform(-step * span, step * span)
                mutated[act] = min(max_start, max(min_start, mutated[act] + delta))
            else:
                mutated[act] = min(1.0, max(0.0, mutated[act] + rng.uniform(-step, step)))
    return IndividualProject(mutated)


def aggressive_reset_mutation(individual, rng, mutation_rate=0.35, instance=None):
    mutated = copy.deepcopy(individual.start_times)
    for act in mutated:
        if rng.random() < mutation_rate:
            mutated[act] = _random_start_for(act, rng, instance) if instance else rng.random()
    return IndividualProject(mutated)


def swap_priorities_mutation(individual, rng, mutation_rate=0.2, instance=None):
    mutated = copy.deepcopy(individual.start_times)
    acts = list(mutated.keys())
    if len(acts) < 2:
        return IndividualProject(mutated)

    if rng.random() < mutation_rate:
        act1, act2 = rng.sample(acts, 2)
        mutated[act1], mutated[act2] = mutated[act2], mutated[act1]

    return IndividualProject(mutated)


def resource_guided_mutation(individual, rng, mutation_rate=0.2, instance=None):
    """
    Mutacion guiada por scheduling:
    refuerza o debilita actividades con mas presion de recursos y mas impacto
    estructural (muchos sucesores directos).
    """
    mutated = copy.deepcopy(individual.start_times)
    if instance is None:
        return IndividualProject(mutated)

    schedule = individual.schedule or []
    start_times = {act: start for act, start, _ in schedule}
    end_times = {act: end for act, _, end in schedule}
    project_duration = max(end_times.values(), default=1.0)

    resource_pressure = {}
    for act in mutated:
        pressure = 0.0
        for resource, amount in instance.asignation.get(act, []):
            availability = float(instance.resources.get(resource, 1.0) or 1.0)
            pressure += float(amount) / availability
        resource_pressure[act] = pressure

    successor_count = {act: 0 for act in mutated}
    for act, preds in instance.predecessors.items():
        for pred in preds:
            if pred in successor_count:
                successor_count[pred] += 1

    timing_score = {}
    for act in mutated:
        start = start_times.get(act, 0.0)
        end = end_times.get(act, start)
        late_factor = end / project_duration if project_duration else 0.0
        early_factor = 1.0 - min(1.0, start / project_duration) if project_duration else 1.0
        timing_score[act] = 0.6 * late_factor + 0.4 * early_factor

    ranked = sorted(
        mutated.keys(),
        key=lambda act: (
            resource_pressure.get(act, 0.0),
            successor_count.get(act, 0),
            timing_score.get(act, 0.0),
        ),
        reverse=True,
    )
    focus_size = max(1, len(ranked) // 4)
    focus = ranked[:focus_size]

    for act in focus:
        if rng.random() < mutation_rate:
            min_start = instance.earliest_start.get(act, 0.0)
            max_start = instance.latest_start.get(act, min_start)
            span = max(1.0, max_start - min_start)
            mutated[act] = min(max_start, max(min_start, mutated[act] + rng.uniform(-0.35 * span, 0.35 * span)))

    for act in mutated:
        if act not in focus and rng.random() < (mutation_rate * 0.25):
            min_start = instance.earliest_start.get(act, 0.0)
            max_start = instance.latest_start.get(act, min_start)
            span = max(1.0, max_start - min_start)
            mutated[act] = min(max_start, max(min_start, mutated[act] + rng.uniform(-0.10 * span, 0.10 * span)))

    return IndividualProject(mutated)


mutation_operator_dict = {
    "random_reset": random_reset_mutation,
    "perturbation": small_perturbation_mutation,
    "aggressive_reset": aggressive_reset_mutation,
    "swap": swap_priorities_mutation,
    "resource_guided": resource_guided_mutation,
}
