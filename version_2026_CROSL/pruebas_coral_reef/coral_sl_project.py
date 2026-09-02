#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

from project_crossover import crossover_operator_dict
from project_evaluator import evaluate_population
from project_individual import create_random_individual
from project_mutation import mutation_operator_dict


class CROSLProject:
    """
    Primera version modular de CRO-SL para scheduling de proyectos.
    Mantiene el comportamiento del prototipo actual, pero ya preparado
    para organizar operadores por substratos.
    """

    def __init__(self, parameters, instance):
        self.instance = instance
        self.parameters = parameters
        self.rng = random.Random(parameters.get("seed"))

        self.reef_size = parameters.get("reef_size", 20)
        self.n_generations = parameters.get("n_generations", 20)
        self.larvae_per_generation = parameters.get("larvae_per_generation", 10)
        self.sexual_rate = parameters.get("sexual_rate", 0.7)
        self.predation_rate = parameters.get("predation_rate", 0.1)

        self.substrate_operators = parameters.get(
            "substrate_operators",
            [
                {
                    "name": "random_explorer",
                    "fraction": 0.30,
                    "crossover": "random",
                    "mutation": ["aggressive_reset"],
                    "mutation_rate": 0.30,
                },
                {
                    "name": "average_refiner",
                    "fraction": 0.25,
                    "crossover": "average",
                    "mutation": ["random_reset"],
                    "mutation_rate": 0.18,
                },
                {
                    "name": "random_reset",
                    "fraction": 0.25,
                    "crossover": "random",
                    "mutation": ["random_reset"],
                    "mutation_rate": 0.20,
                },
                {
                    "name": "average_explorer",
                    "fraction": 0.20,
                    "crossover": "average",
                    "mutation": ["aggressive_reset"],
                    "mutation_rate": 0.24,
                },
            ],
        )

        self.population = []
        self.history = []
        self.substrate_stats = []

    def initialize_reef(self):
        self.population = [
            create_random_individual(self.instance.activities, self.instance, self.rng)
            for _ in range(self.reef_size)
        ]
        self.population = evaluate_population(self.population, self.instance)

    def build_generation_stats(self, generation_index, substrate_stats=None):
        fitness_values = [item.fitness for item in self.population]
        stats = {
            "generation": generation_index,
            "best_fitness": min(fitness_values),
            "worst_fitness": max(fitness_values),
            "avg_fitness": sum(fitness_values) / len(fitness_values),
        }
        if substrate_stats is not None:
            stats["substrates"] = substrate_stats
        return stats

    def select_parents(self, n_parents=2):
        if len(self.population) < n_parents:
            return self.population

        elite_size = max(1, len(self.population) // 2)
        elite = self.population[:elite_size]
        return self.rng.sample(elite, n_parents)

    def apply_mutations(self, individual, mutation_names, mutation_rate=None):
        result = individual
        effective_rate = mutation_rate
        if effective_rate is None:
            effective_rate = self.parameters.get("mutation_rate", 0.2)
        for mutation_name in mutation_names:
            mutation_fn = mutation_operator_dict[mutation_name]
            result = mutation_fn(
                result,
                self.rng,
                mutation_rate=effective_rate,
                instance=self.instance,
            )
        return result

    def build_substrate_plan(self):
        n_substrates = len(self.substrate_operators)
        if n_substrates == 0:
            return []

        raw_counts = []
        assigned = 0
        for substrate in self.substrate_operators[:-1]:
            fraction = substrate.get("fraction", 1.0 / n_substrates)
            count = int(round(self.larvae_per_generation * fraction))
            raw_counts.append(max(0, count))
            assigned += raw_counts[-1]

        raw_counts.append(max(0, self.larvae_per_generation - assigned))

        if sum(raw_counts) == 0:
            raw_counts[-1] = self.larvae_per_generation

        diff = self.larvae_per_generation - sum(raw_counts)
        raw_counts[-1] += diff

        return list(zip(self.substrate_operators, raw_counts))

    def broadcast_spawning(self):
        larvae = []
        substrate_stats = []
        for substrate, n_larvae in self.build_substrate_plan():
            generated = 0
            for _ in range(n_larvae):
                if len(self.population) >= 2 and self.rng.random() < self.sexual_rate:
                    parent1, parent2 = self.select_parents(2)
                    crossover_name = substrate["crossover"]
                    crossover_fn = crossover_operator_dict[crossover_name]
                    if crossover_name == "average":
                        child = crossover_fn(parent1, parent2)
                    else:
                        child = crossover_fn(parent1, parent2, self.rng)
                else:
                    parent = self.select_parents(1)[0]
                    child = parent.copy_shallow()

                child = self.apply_mutations(
                    child,
                    substrate["mutation"],
                    mutation_rate=substrate.get("mutation_rate"),
                )
                larvae.append(child)
                generated += 1

            substrate_stats.append(
                {
                    "name": substrate.get("name", "substrate"),
                    "generated": generated,
                    "settled": 0,
                }
            )

        return evaluate_population(larvae, self.instance), substrate_stats

    def settle_larvae(self, larvae_evaluated, substrate_stats=None, attempts=3):
        reef = self.population[: self.reef_size]
        substrate_index = 0
        substrate_offsets = []
        if substrate_stats is not None:
            offset = 0
            for item in substrate_stats:
                substrate_offsets.append((offset, offset + item["generated"]))
                offset += item["generated"]

        for larva_idx, larva in enumerate(larvae_evaluated):
            settled = False
            for _ in range(attempts):
                idx = self.rng.randint(0, len(reef) - 1)
                if larva.fitness < reef[idx].fitness:
                    reef[idx] = larva
                    settled = True
                    if substrate_stats is not None:
                        for substrate_index, (start, end) in enumerate(substrate_offsets):
                            if start <= larva_idx < end:
                                substrate_stats[substrate_index]["settled"] += 1
                                break
                    break
            if not settled and len(reef) < self.reef_size:
                reef.append(larva)
                if substrate_stats is not None:
                    for substrate_index, (start, end) in enumerate(substrate_offsets):
                        if start <= larva_idx < end:
                            substrate_stats[substrate_index]["settled"] += 1
                            break

        reef.sort(key=lambda item: item.fitness)
        self.population = reef[: self.reef_size]

    def asexual_reproduction(self):
        n_duplicates = max(1, int(self.reef_size * self.parameters.get("f_a", 0.1)))
        best = self.population[:n_duplicates]
        clones = [
            self.apply_mutations(coral.copy_shallow(), ["random_reset"])
            for coral in best
        ]
        clones = evaluate_population(clones, self.instance)
        self.settle_larvae(clones, attempts=3)

    def predation(self):
        if not self.population:
            return

        n_predated = max(1, int(len(self.population) * self.predation_rate))
        worst_slice_start = max(0, len(self.population) - n_predated)
        candidates = list(range(worst_slice_start, len(self.population)))
        to_remove = set(self.rng.sample(candidates, min(n_predated, len(candidates))))
        self.population = [
            item for idx, item in enumerate(self.population) if idx not in to_remove
        ]

        while len(self.population) < self.reef_size:
            new_individual = create_random_individual(
                self.instance.activities,
                self.instance,
                self.rng,
            )
            self.population.append(new_individual)

        self.population = evaluate_population(self.population, self.instance)

    def run(self):
        self.initialize_reef()
        self.history = [self.build_generation_stats(0, substrate_stats=[])]

        for generation in range(1, self.n_generations + 1):
            larvae, substrate_stats = self.broadcast_spawning()
            self.settle_larvae(larvae, substrate_stats=substrate_stats, attempts=3)
            self.asexual_reproduction()
            self.predation()
            self.population.sort(key=lambda item: item.fitness)
            self.substrate_stats.append(
                {
                    "generation": generation,
                    "substrates": substrate_stats,
                }
            )
            self.history.append(self.build_generation_stats(generation, substrate_stats=substrate_stats))

        best = self.population[0]
        return {
            "best_individual": best,
            "best_schedule": best.schedule,
            "best_fitness": best.fitness,
            "history": self.history,
            "substrate_stats": self.substrate_stats,
            "population": self.population,
        }
