#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import csv
import random


def format_number(value):
    """
    Formatea numeros para exportacion:
    - 19.0 -> 19
    - 19.25 -> 19.25
    """
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def decode_individual(individual, asignation, resources, predecessors, activities, leveling):
    """
    Decodifica un individuo basado en prioridades a un schedule factible.
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
                key=lambda act: individual.get(act, 0.0),
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


def evaluate_duration(schedule):
    if not schedule:
        return float("inf")
    return max(end_time for _, _, end_time in schedule)


def generate_individual(activities):
    return {act: random.random() for act in activities.keys()}


def mutate_individual(individual, mutation_rate=0.2):
    mutated = copy.deepcopy(individual)
    for act in mutated:
        if random.random() < mutation_rate:
            mutated[act] = random.random()
    return mutated


def crossover_average(parent1, parent2):
    child = {}
    for act in parent1.keys():
        child[act] = (parent1[act] + parent2[act]) / 2.0
    return child


def crossover_random_inheritance(parent1, parent2):
    child = {}
    for act in parent1.keys():
        child[act] = parent1[act] if random.random() < 0.5 else parent2[act]
    return child


def evaluate_individual(individual, asignation, resources, predecessors, activities, leveling):
    schedule = decode_individual(
        individual,
        asignation,
        resources,
        predecessors,
        activities,
        leveling,
    )
    fitness = evaluate_duration(schedule)
    return {
        "individual": individual,
        "schedule": schedule,
        "fitness": fitness,
    }


def generate_population(population_size, activities):
    return [generate_individual(activities) for _ in range(population_size)]


def evaluate_population(population, asignation, resources, predecessors, activities, leveling):
    evaluated = []
    for individual in population:
        evaluated.append(
            evaluate_individual(
                individual,
                asignation,
                resources,
                predecessors,
                activities,
                leveling,
            )
        )
    evaluated.sort(key=lambda item: item["fitness"])
    return evaluated


def select_parents(evaluated_population, n_parents=2):
    """
    Seleccion simple: escoger al azar entre la mitad mejor de la poblacion.
    """
    if len(evaluated_population) < n_parents:
        return evaluated_population

    elite_size = max(1, len(evaluated_population) // 2)
    elite = evaluated_population[:elite_size]
    return random.sample(elite, n_parents)


def reproduce(parent1, parent2, mutation_rate=0.2, crossover_mode="random"):
    if crossover_mode == "average":
        child = crossover_average(parent1["individual"], parent2["individual"])
    else:
        child = crossover_random_inheritance(parent1["individual"], parent2["individual"])

    child = mutate_individual(child, mutation_rate=mutation_rate)
    return child


def reproduce_asexual(parent, mutation_rate=0.2):
    """
    Reproduccion asexual simple: copia mutada de un individuo.
    """
    return mutate_individual(parent["individual"], mutation_rate=mutation_rate)


def settle_larvae(evaluated_population, larvae_evaluated, reef_size, attempts=3):
    """
    Asentamiento tipo coral reef simplificado:
    cada larva intenta asentarse en posiciones aleatorias del arrecife.
    Si mejora al coral ocupante, lo reemplaza.
    """
    reef = evaluated_population[:reef_size]

    for larva in larvae_evaluated:
        settled = False

        for _ in range(attempts):
            idx = random.randint(0, len(reef) - 1)
            if larva["fitness"] < reef[idx]["fitness"]:
                reef[idx] = larva
                settled = True
                break

        if not settled and len(reef) < reef_size:
            reef.append(larva)

    reef.sort(key=lambda item: item["fitness"])
    return reef[:reef_size]


def predation(evaluated_population, predation_rate=0.1):
    """
    Depredacion simple:
    elimina aleatoriamente parte de los peores corales.
    """
    if not evaluated_population:
        return evaluated_population

    reef = evaluated_population[:]
    n_predated = max(1, int(len(reef) * predation_rate))
    worst_slice_start = max(0, len(reef) - n_predated)
    candidates = list(range(worst_slice_start, len(reef)))

    if candidates:
        to_remove = set(random.sample(candidates, min(n_predated, len(candidates))))
        reef = [item for idx, item in enumerate(reef) if idx not in to_remove]

    return reef


def build_generation_stats(evaluated_population, generation_index):
    fitness_values = [item["fitness"] for item in evaluated_population]
    return {
        "generation": generation_index,
        "best_fitness": min(fitness_values),
        "worst_fitness": max(fitness_values),
        "avg_fitness": sum(fitness_values) / len(fitness_values),
    }


def export_history_to_csv(history, filepath):
    """
    Guarda el historial de generaciones en un CSV.
    """
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["generation", "best_fitness", "avg_fitness", "worst_fitness"],
            delimiter=";",
        )
        writer.writeheader()
        for row in history:
            writer.writerow(
                {
                    "generation": format_number(row["generation"]),
                    "best_fitness": format_number(row["best_fitness"]),
                    "avg_fitness": format_number(row["avg_fitness"]),
                    "worst_fitness": format_number(row["worst_fitness"]),
                }
            )


def export_run_summary_to_csv(summary, filepath):
    """
    Guarda un resumen de la ejecucion en un CSV de dos columnas:
    parametro;valor
    """
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["parameter", "value"])
        for key, value in summary.items():
            writer.writerow([key, format_number(value)])


def export_best_individual_to_csv(individual, filepath):
    """
    Guarda el mejor individuo en un CSV con columnas separadas.
    """
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["activity", "priority"])
        for act, priority in sorted(individual.items()):
            writer.writerow([act, format_number(priority)])


def export_best_schedule_to_csv(schedule, filepath):
    """
    Guarda el mejor schedule en un CSV con columnas separadas.
    """
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["activity", "start", "end"])
        for act, start, end in schedule:
            writer.writerow([act, format_number(start), format_number(end)])


def run_coral_reef(
    asignation,
    resources,
    predecessors,
    activities,
    leveling=0,
    reef_size=20,
    n_generations=20,
    larvae_per_generation=10,
    mutation_rate=0.2,
    crossover_mode="random",
    sexual_rate=0.7,
    predation_rate=0.1,
    seed=None,
):
    if seed is not None:
        random.seed(seed)

    population = generate_population(reef_size, activities)
    evaluated_population = evaluate_population(
        population, asignation, resources, predecessors, activities, leveling
    )

    history = [build_generation_stats(evaluated_population, 0)]

    for generation in range(1, n_generations + 1):
        larvae = []

        for _ in range(larvae_per_generation):
            if len(evaluated_population) >= 2 and random.random() < sexual_rate:
                parent1, parent2 = select_parents(evaluated_population, n_parents=2)
                child = reproduce(
                    parent1,
                    parent2,
                    mutation_rate=mutation_rate,
                    crossover_mode=crossover_mode,
                )
            else:
                parent = select_parents(evaluated_population, n_parents=1)[0]
                child = reproduce_asexual(
                    parent,
                    mutation_rate=mutation_rate,
                )
            larvae.append(child)

        larvae_evaluated = evaluate_population(
            larvae, asignation, resources, predecessors, activities, leveling
        )

        evaluated_population = settle_larvae(
            evaluated_population,
            larvae_evaluated,
            reef_size,
            attempts=3,
        )

        evaluated_population = predation(
            evaluated_population,
            predation_rate=predation_rate,
        )

        while len(evaluated_population) < reef_size:
            new_individual = generate_individual(activities)
            evaluated_population.append(
                evaluate_individual(
                    new_individual,
                    asignation,
                    resources,
                    predecessors,
                    activities,
                    leveling,
                )
            )

        evaluated_population.sort(key=lambda item: item["fitness"])
        history.append(build_generation_stats(evaluated_population, generation))

    best = evaluated_population[0]
    return {
        "best_individual": best["individual"],
        "best_schedule": best["schedule"],
        "best_fitness": best["fitness"],
        "history": history,
        "population": evaluated_population,
    }
