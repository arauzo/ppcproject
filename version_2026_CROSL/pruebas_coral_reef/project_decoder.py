#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def repair_start_times(start_times, instance):
    repaired = dict(start_times)
    ordered = sorted(
        instance.activities.keys(),
        key=lambda act: (instance.earliest_start.get(act, 0.0), str(act)),
    )

    for act in ordered:
        min_start = instance.earliest_start.get(act, 0.0)
        for pred in instance.predecessors.get(act, []):
            pred_end = repaired.get(pred, instance.earliest_start.get(pred, 0.0))
            pred_end += instance.duration(pred)
            if pred_end > min_start:
                min_start = pred_end

        max_start = instance.latest_start.get(act, min_start)
        repaired[act] = max(min_start, repaired.get(act, min_start))
        if repaired[act] > max_start:
            repaired[act] = max_start

    for act in reversed(ordered):
        max_start = instance.latest_start.get(act, repaired.get(act, 0.0))
        successors = instance.successors.get(act, [])
        if successors:
            max_start = min(
                repaired[succ] - instance.duration(act)
                for succ in successors
            )
        min_start = instance.earliest_start.get(act, 0.0)
        repaired[act] = min(repaired.get(act, max_start), max_start)
        if repaired[act] < min_start:
            repaired[act] = min_start

    return repaired


def decode_individual(individual, asignation, resources, predecessors, activities, leveling):
    """
    Convierte un individuo de prioridades a un schedule factible.
    """
    resources = copy.deepcopy(resources)
    predecessors = copy.deepcopy(predecessors)
    activities = copy.deepcopy(activities)

    current_time = 0
    executing = {}
    result = []

    while activities:
        possibles = {}

        for act in list(activities.keys()):
            if act not in predecessors:
                possibles[act] = activities[act]

        if possibles:
            ordered = sorted(
                possibles.keys(),
                key=lambda act: individual.priorities.get(act, 0.0),
                reverse=True,
            )

            if leveling == 1:
                for act in ordered[:]:
                    latest_start = possibles[act][1]
                    duration = possibles[act][0]
                    if latest_start == current_time:
                        executing[act] = duration
                        result.append((act, current_time, current_time + duration))
                        del activities[act]
                        ordered.remove(act)

            for act in ordered:
                if act not in activities:
                    continue

                duration = activities[act][0]
                can_execute = True

                if act in asignation and leveling == 0:
                    for resource, amount in asignation[act]:
                        if float(amount) > float(resources[resource]):
                            can_execute = False
                            break

                if can_execute:
                    if act in asignation and leveling == 0:
                        for resource, amount in asignation[act]:
                            resources[resource] = float(resources[resource]) - float(amount)

                    executing[act] = duration
                    result.append((act, current_time, current_time + duration))
                    del activities[act]

        if not executing:
            break

        time_step = min(executing.values())

        if leveling == 0:
            current_time += time_step
        else:
            if time_step <= 1:
                current_time += time_step
            else:
                time_step = 1
                current_time = int(current_time) + time_step

        finished = []
        for act in list(executing.keys()):
            executing[act] = float(executing[act]) - time_step
            if executing[act] == 0:
                finished.append(act)
                del executing[act]

                if act in asignation and leveling == 0:
                    for resource, amount in asignation[act]:
                        resources[resource] = float(resources[resource]) + float(amount)

        for finished_act in finished:
            for act in list(predecessors.keys()):
                if finished_act in predecessors[act]:
                    predecessors[act].remove(finished_act)
                    if predecessors[act] == []:
                        del predecessors[act]

    return result


def decode_start_time_individual(individual, instance):
    start_times = repair_start_times(individual.start_times, instance)
    individual.start_times = start_times
    individual.priorities = start_times

    schedule = []
    feasible = True
    for act in sorted(start_times.keys(), key=lambda item: (start_times[item], str(item))):
        start = start_times[act]
        end = start + instance.duration(act)
        schedule.append((act, start, end))

        if start < instance.earliest_start.get(act, 0.0):
            feasible = False
        if start > instance.latest_start.get(act, start):
            feasible = False
        for pred in instance.predecessors.get(act, []):
            pred_end = start_times[pred] + instance.duration(pred)
            if start < pred_end:
                feasible = False

    return schedule, feasible
