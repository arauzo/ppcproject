#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .leveling_tools import create_path_based_start_times
from .project_individual import ProjectLevelingIndividual


def _ordered_activities(instance):
    return instance.activities_ordered()


def _child_from_values(values, instance):
    return ProjectLevelingIndividual(
        {act: values.get(act, instance.earliest_start.get(act, 0.0)) for act in instance.activities}
    )


def _order_from_individual(individual, instance):
    return sorted(
        instance.activities.keys(),
        key=lambda act: (individual.start_times.get(act, 0.0), str(act)),
    )


def _ranked_times_from_individual(individual, instance):
    return [
        individual.start_times[act]
        for act in _order_from_individual(individual, instance)
    ]


def _child_from_order(order, ranked_times, instance):
    values = {}
    for act, start_time in zip(order, ranked_times):
        values[act] = start_time
    return _child_from_values(values, instance)


def _pmx_order(order1, order2, rng):
    size = len(order1)
    cut1, cut2 = sorted(rng.sample(range(size), 2))
    child = [None] * size
    child[cut1:cut2 + 1] = order1[cut1:cut2 + 1]

    for idx in range(cut1, cut2 + 1):
        candidate = order2[idx]
        if candidate in child:
            continue
        target_idx = idx
        while True:
            mapped = order1[target_idx]
            target_idx = order2.index(mapped)
            if child[target_idx] is None:
                child[target_idx] = candidate
                break

    for idx, value in enumerate(child):
        if value is None:
            child[idx] = order2[idx]
    return child


def _ox_order(order1, order2, rng):
    size = len(order1)
    cut1, cut2 = sorted(rng.sample(range(size), 2))
    child = [None] * size
    child[cut1:cut2 + 1] = order1[cut1:cut2 + 1]

    insert_pos = (cut2 + 1) % size
    for act in order2[cut2 + 1:] + order2[:cut2 + 1]:
        if act in child:
            continue
        child[insert_pos] = act
        insert_pos = (insert_pos + 1) % size
    return child


def _cycle_order(order1, order2):
    size = len(order1)
    child = [None] * size
    use_order1 = True
    remaining = set(range(size))

    while remaining:
        start_idx = min(remaining)
        idx = start_idx
        cycle = []
        while idx not in cycle:
            cycle.append(idx)
            remaining.discard(idx)
            idx = order1.index(order2[idx])

        source = order1 if use_order1 else order2
        for cycle_idx in cycle:
            child[cycle_idx] = source[cycle_idx]
        use_order1 = not use_order1

    return child


def _edge_order(order1, order2, rng):
    edge_table = {act: [] for act in order1}
    size = len(order1)

    for order in (order1, order2):
        for idx, act in enumerate(order):
            neighbors = [order[(idx - 1) % size], order[(idx + 1) % size]]
            for neighbor in neighbors:
                if neighbor in edge_table[act]:
                    edge_table[act].remove(neighbor)
                    edge_table[act].append((neighbor, True))
                elif (neighbor, True) not in edge_table[act]:
                    edge_table[act].append(neighbor)

    current = rng.choice(order1)
    child = [current]
    unused = set(order1)
    unused.remove(current)

    while unused:
        for act in edge_table:
            edge_table[act] = [
                item for item in edge_table[act]
                if (item[0] if isinstance(item, tuple) else item) != current
            ]

        common = [
            item[0] for item in edge_table[current]
            if isinstance(item, tuple) and item[0] in unused
        ]
        candidates = common or [
            item for item in edge_table[current]
            if not isinstance(item, tuple) and item in unused
        ]

        if candidates:
            min_size = min(len(edge_table[candidate]) for candidate in candidates)
            tied = [
                candidate for candidate in candidates
                if len(edge_table[candidate]) == min_size
            ]
            current = rng.choice(tied)
        else:
            current = rng.choice(list(unused))

        child.append(current)
        unused.remove(current)

    return child


def ox_crossover(parent1, parent2, instance, rng):
    """
    Adaptacion OX: cruza el orden de actividades por tiempo de inicio.
    """
    order1 = _order_from_individual(parent1, instance)
    order2 = _order_from_individual(parent2, instance)
    if len(order1) < 2:
        return parent1.copy(), parent2.copy()

    child_order1 = _ox_order(order1, order2, rng)
    child_order2 = _ox_order(order2, order1, rng)
    return (
        _child_from_order(child_order1, _ranked_times_from_individual(parent1, instance), instance),
        _child_from_order(child_order2, _ranked_times_from_individual(parent2, instance), instance),
    )


def pmx_crossover(parent1, parent2, instance, rng):
    """
    Adaptacion PMX: aplica PMX sobre el orden de actividades.
    """
    order1 = _order_from_individual(parent1, instance)
    order2 = _order_from_individual(parent2, instance)
    if len(order1) < 2:
        return parent1.copy(), parent2.copy()

    return (
        _child_from_order(_pmx_order(order1, order2, rng), _ranked_times_from_individual(parent1, instance), instance),
        _child_from_order(_pmx_order(order2, order1, rng), _ranked_times_from_individual(parent2, instance), instance),
    )


def cycle_crossover(parent1, parent2, instance, rng):
    order1 = _order_from_individual(parent1, instance)
    order2 = _order_from_individual(parent2, instance)
    if len(order1) < 2:
        return parent1.copy(), parent2.copy()

    return (
        _child_from_order(_cycle_order(order1, order2), _ranked_times_from_individual(parent1, instance), instance),
        _child_from_order(_cycle_order(order2, order1), _ranked_times_from_individual(parent2, instance), instance),
    )


def edge_crossover(parent1, parent2, instance, rng):
    order1 = _order_from_individual(parent1, instance)
    order2 = _order_from_individual(parent2, instance)
    if len(order1) < 2:
        return parent1.copy(), parent2.copy()

    child_order = _edge_order(order1, order2, rng)
    return (
        _child_from_order(child_order, _ranked_times_from_individual(parent1, instance), instance),
        _child_from_order(child_order, _ranked_times_from_individual(parent2, instance), instance),
    )


def one_point_crossover(parent1, parent2, instance, rng):
    activities = _ordered_activities(instance)
    if len(activities) < 2:
        return parent1.copy(), parent2.copy()

    cut = rng.randint(1, len(activities) - 1)
    child1 = {}
    child2 = {}
    for idx, act in enumerate(activities):
        if idx < cut:
            child1[act] = parent1.start_times[act]
            child2[act] = parent2.start_times[act]
        else:
            child1[act] = parent2.start_times[act]
            child2[act] = parent1.start_times[act]
    return _child_from_values(child1, instance), _child_from_values(child2, instance)


def n_point_crossover(parent1, parent2, instance, rng):
    activities = _ordered_activities(instance)
    if len(activities) < 3:
        return one_point_crossover(parent1, parent2, instance, rng)

    n_cuts = min(3, len(activities) - 1)
    cuts = sorted(rng.sample(range(1, len(activities)), n_cuts))
    cuts.append(len(activities))
    child1 = {}
    child2 = {}
    start = 0
    take_first = True

    for cut in cuts:
        for act in activities[start:cut]:
            if take_first:
                child1[act] = parent1.start_times[act]
                child2[act] = parent2.start_times[act]
            else:
                child1[act] = parent2.start_times[act]
                child2[act] = parent1.start_times[act]
        start = cut
        take_first = not take_first

    return _child_from_values(child1, instance), _child_from_values(child2, instance)


def uniform_crossover(parent1, parent2, instance, rng):
    child1 = {}
    child2 = {}
    for act in _ordered_activities(instance):
        if rng.random() < 0.5:
            child1[act] = parent1.start_times[act]
            child2[act] = parent2.start_times[act]
        else:
            child1[act] = parent2.start_times[act]
            child2[act] = parent1.start_times[act]
    return _child_from_values(child1, instance), _child_from_values(child2, instance)


def switch_crossover(parent1, parent2, instance, rng):
    child1 = {}
    child2 = {}
    for act in _ordered_activities(instance):
        value1 = parent1.start_times[act]
        value2 = parent2.start_times[act]
        alpha = rng.uniform(0.25, 0.75)
        child1[act] = alpha * value1 + (1.0 - alpha) * value2
        child2[act] = alpha * value2 + (1.0 - alpha) * value1
    return _child_from_values(child1, instance), _child_from_values(child2, instance)


def feature_crossover(parent1, parent2, instance, rng):
    child1 = {}
    child2 = {}
    for act in _ordered_activities(instance):
        values = sorted([parent1.start_times[act], parent2.start_times[act]])
        child1[act] = values[0]
        child2[act] = values[1]
    return _child_from_values(child1, instance), _child_from_values(child2, instance)


def twors_mutation(individual, instance, rng):
    acts = _ordered_activities(instance)
    movable = [act for act in acts if instance.latest_start[act] > instance.earliest_start[act]]
    if len(movable) < 2:
        return
    act1, act2 = rng.sample(movable, 2)
    individual.start_times[act1], individual.start_times[act2] = (
        individual.start_times[act2],
        individual.start_times[act1],
    )


def insert_mutation(individual, instance, rng):
    movable = [
        act for act in _ordered_activities(instance)
        if instance.latest_start[act] > instance.earliest_start[act]
    ]
    if not movable:
        return
    act = rng.choice(movable)
    min_start = instance.earliest_start[act]
    max_start = instance.latest_start[act]
    step = rng.choice([-1.0, 1.0])
    individual.start_times[act] = min(
        max_start,
        max(min_start, individual.start_times[act] + step),
    )


def scramble_mutation(individual, instance, rng):
    movable = [
        act for act in _ordered_activities(instance)
        if instance.latest_start[act] > instance.earliest_start[act]
    ]
    if len(movable) < 2:
        return
    size = rng.randint(2, min(5, len(movable)))
    selected = rng.sample(movable, size)
    values = [individual.start_times[act] for act in selected]
    rng.shuffle(values)
    for act, value in zip(selected, values):
        individual.start_times[act] = value


def inversion_mutation(individual, instance, rng):
    movable = [
        act for act in _ordered_activities(instance)
        if instance.latest_start[act] > instance.earliest_start[act]
    ]
    if len(movable) < 2:
        return
    idx1, idx2 = sorted(rng.sample(range(len(movable)), 2))
    selected = movable[idx1:idx2 + 1]
    values = [individual.start_times[act] for act in selected]
    for act, value in zip(selected, reversed(values)):
        individual.start_times[act] = value


def bit_swap_mutation(individual, instance, rng):
    movable = [
        act for act in _ordered_activities(instance)
        if instance.latest_start[act] > instance.earliest_start[act]
    ]
    if not movable:
        return
    act = rng.choice(movable)
    path_based_times = create_path_based_start_times(instance, rng)
    individual.start_times[act] = path_based_times[act]


def exchange_mutation(individual, instance, rng):
    twors_mutation(individual, instance, rng)


def invert_mutation(individual, instance, rng):
    inversion_mutation(individual, instance, rng)


def double_bit_swap_mutation(individual, instance, rng):
    bit_swap_mutation(individual, instance, rng)
    bit_swap_mutation(individual, instance, rng)


def dept_swap_mutation(individual, instance, rng):
    scramble_mutation(individual, instance, rng)


crossover_operator_dict = {
    "PMX": pmx_crossover,
    "OX": ox_crossover,
    "Cycle": cycle_crossover,
    "Edge": edge_crossover,
    "1-point": one_point_crossover,
    "n-point": n_point_crossover,
    "Uniform": uniform_crossover,
    "Switch": switch_crossover,
    "Feature": feature_crossover,
}


mutation_operator_dict = {
    "TWORS": twors_mutation,
    "Insert": insert_mutation,
    "Scramble": scramble_mutation,
    "Inversion": inversion_mutation,
    "Bit-swap": bit_swap_mutation,
    "Exchange": exchange_mutation,
    "Invert": invert_mutation,
    "2_Bit_swap": double_bit_swap_mutation,
    "Dept_swap": dept_swap_mutation,
}
