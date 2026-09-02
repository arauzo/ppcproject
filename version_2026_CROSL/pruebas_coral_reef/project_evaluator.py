#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from project_decoder import decode_individual, decode_start_time_individual


def evaluate_duration(schedule):
    if not schedule:
        return float("inf")
    return max(end_time for _, _, end_time in schedule)


def evaluate_individual(individual, instance):
    if hasattr(individual, "start_times"):
        schedule, feasible = decode_start_time_individual(individual, instance)
        fitness = evaluate_leveling_variance(schedule, instance)
        if not feasible:
            fitness = float("inf")
    else:
        schedule = decode_individual(
            individual,
            instance.asignation,
            instance.resources,
            instance.predecessors,
            instance.activities,
            instance.leveling,
        )
        fitness = evaluate_duration(schedule)
        feasible = fitness != float("inf")

    individual.schedule = schedule
    individual.fitness = fitness
    individual.feasible = feasible and fitness != float("inf")
    return individual


def evaluate_population(population, instance):
    evaluated = [evaluate_individual(individual, instance) for individual in population]
    evaluated.sort(key=lambda item: item.fitness)
    return evaluated


def evaluate_leveling_variance(schedule, instance):
    if not schedule:
        return float("inf")

    horizon = int(max(end_time for _, _, end_time in schedule))
    if horizon <= 0:
        return 0.0

    loads = {
        resource: [0.0 for _ in range(horizon)]
        for resource in instance.resources
    }

    for act, start, end in schedule:
        start_i = int(start)
        end_i = int(end)
        for resource, amount in instance.asignation.get(act, []):
            if resource not in loads:
                loads[resource] = [0.0 for _ in range(horizon)]
            for time in range(max(0, start_i), min(horizon, end_i)):
                loads[resource][time] += float(amount)

    variance_sum = 0.0
    for resource_load in loads.values():
        if not resource_load:
            continue
        avg = sum(resource_load) / len(resource_load)
        variance_sum += sum((value - avg) ** 2 for value in resource_load) / len(resource_load)

    return variance_sum
