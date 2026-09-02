#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math

from .project_individual import ProjectLevelingIndividual


def random_start_for(activity, instance, rng):
    min_start = math.ceil(instance.earliest_start.get(activity, 0.0))
    max_start = math.floor(instance.latest_start.get(activity, min_start))
    if max_start < min_start:
        max_start = min_start

    return float(rng.randint(int(min_start), int(max_start)))


def create_random_individual(instance, rng):
    return ProjectLevelingIndividual(create_path_based_start_times(instance, rng))


def create_path_based_start_times(instance, rng):
    delays = {act: 0.0 for act in instance.activities}

    for path in instance.non_critical_paths:
        assign_random_path_delays(path["activities"], path["slack"], delays, rng)

    start_times = {
        act: instance.earliest_start.get(act, 0.0) + delays.get(act, 0.0)
        for act in instance.activities
    }
    return repair_start_times(start_times, instance)


def assign_random_path_delays(path_activities, path_slack, delays, rng):
    remaining_slack = float(path_slack)
    pending_activities = list(path_activities)

    while remaining_slack > 0 and pending_activities:
        activity = rng.choice(pending_activities)
        pending_activities.remove(activity)

        max_new_delay = max(0.0, remaining_slack)
        current_delay = delays.get(activity, 0.0)
        sampled_delay = sample_delay(max_new_delay, rng)

        if sampled_delay > current_delay:
            remaining_slack -= sampled_delay - current_delay
            delays[activity] = sampled_delay


def sample_delay(max_delay, rng):
    if max_delay <= 0:
        return 0.0
    return float(rng.randint(0, int(math.floor(max_delay))))


def _integer_bounds(activity, instance):
    min_start = math.ceil(instance.earliest_start.get(activity, 0.0))
    max_start = math.floor(instance.latest_start.get(activity, min_start))
    if max_start < min_start:
        max_start = min_start
    return float(min_start), float(max_start)


def _snap_to_integer(value):
    return float(round(value))


def repair_start_times(start_times, instance):
    repaired = {
        act: _snap_to_integer(value)
        for act, value in dict(start_times).items()
    }
    ordered = instance.activities_ordered()

    for act in ordered:
        min_start, max_start = _integer_bounds(act, instance)
        for pred in instance.predecessors.get(act, []):
            pred_end = repaired.get(pred, instance.earliest_start[pred])
            pred_end += instance.duration(pred)
            min_start = max(min_start, math.ceil(pred_end))

        repaired[act] = max(min_start, repaired.get(act, min_start))
        repaired[act] = min(max_start, repaired[act])
        repaired[act] = _snap_to_integer(repaired[act])

    for act in reversed(ordered):
        min_start, max_start = _integer_bounds(act, instance)
        successors = instance.successors.get(act, [])
        if successors:
            max_start = min(
                math.floor(repaired[succ] - instance.duration(act))
                for succ in successors
            )

        repaired[act] = min(repaired.get(act, max_start), max_start)
        repaired[act] = max(min_start, repaired[act])
        repaired[act] = _snap_to_integer(repaired[act])

    return repaired


def decode_individual(individual, instance):
    individual.start_times = repair_start_times(individual.start_times, instance)
    schedule = []
    feasible = True

    for act in sorted(
        individual.start_times.keys(),
        key=lambda item: (individual.start_times[item], str(item)),
    ):
        start = individual.start_times[act]
        end = start + instance.duration(act)
        schedule.append((act, start, end))

        if start < instance.earliest_start.get(act, 0.0):
            feasible = False
        if start > instance.latest_start.get(act, start):
            feasible = False
        for pred in instance.predecessors.get(act, []):
            pred_end = individual.start_times[pred] + instance.duration(pred)
            if start < pred_end:
                feasible = False

    duration = max((end for _, _, end in schedule), default=0.0)
    if duration > instance.project_duration:
        feasible = False
    if getattr(instance, "force_project_duration", False):
        if abs(duration - instance.project_duration) > 1e-6:
            feasible = False

    individual.schedule = schedule
    individual.feasible = feasible
    return schedule, feasible


def evaluate_leveling_variance(schedule, instance):
    summary = resource_variance_summary(schedule, instance)
    optimized_resources = getattr(instance, "optimized_resources", None)
    if not optimized_resources:
        optimized_resources = summary.keys()
    return sum(
        summary[resource]["variance"]
        for resource in optimized_resources
        if resource in summary
    )


def compute_resource_loads(schedule, instance):
    if not schedule:
        return {}

    horizon = int(max(end for _, _, end in schedule))
    if horizon <= 0:
        return {resource: [] for resource in instance.resources}

    loads = {
        resource: [0.0 for _ in range(horizon)]
        for resource in instance.resources
    }

    for act, start, end in schedule:
        for resource, amount in instance.asignation.get(act, []):
            loads.setdefault(resource, [0.0 for _ in range(horizon)])
            for time in range(max(0, int(start)), min(horizon, int(end))):
                loads[resource][time] += float(amount)
    return loads


def resource_variance_summary(schedule, instance):
    loads = compute_resource_loads(schedule, instance)
    summary = {}
    for resource, resource_load in loads.items():
        if not resource_load:
            summary[resource] = {
                "avg": 0.0,
                "variance": 0.0,
                "max": 0.0,
                "total": 0.0,
            }
            continue
        avg = sum(resource_load) / len(resource_load)
        variance = sum((value - avg) ** 2 for value in resource_load) / len(resource_load)
        summary[resource] = {
            "avg": avg,
            "variance": variance,
            "max": max(resource_load),
            "total": sum(resource_load),
        }
    return summary


def evaluate_individual(individual, instance):
    schedule, feasible = decode_individual(individual, instance)
    individual.fitness = evaluate_leveling_variance(schedule, instance)
    if not feasible:
        penalty = getattr(instance, "infeasibility_penalty", 1000000.0)
        individual.fitness += penalty + infeasibility_score(individual, instance) * penalty
    return individual


def infeasibility_score(individual, instance):
    score = 0.0
    for act, start in individual.start_times.items():
        if start < instance.earliest_start.get(act, 0.0):
            score += instance.earliest_start[act] - start
        if start > instance.latest_start.get(act, start):
            score += start - instance.latest_start[act]
        for pred in instance.predecessors.get(act, []):
            pred_end = individual.start_times[pred] + instance.duration(pred)
            if start < pred_end:
                score += pred_end - start

    if individual.schedule:
        duration = max(end for _, _, end in individual.schedule)
        if getattr(instance, "force_project_duration", False):
            score += abs(duration - instance.project_duration)
        elif duration > instance.project_duration:
            score += duration - instance.project_duration
    return score
