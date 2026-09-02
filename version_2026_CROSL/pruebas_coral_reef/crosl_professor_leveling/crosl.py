#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import random
from pathlib import Path

from .leveling_tools import create_random_individual, decode_individual, evaluate_individual
from .operators import crossover_operator_dict, mutation_operator_dict
from .project_individual import ProjectLevelingIndividual
from .recommended_config import RECOMMENDED_SUBSTRATES


DEFAULT_SUBSTRATES = RECOMMENDED_SUBSTRATES


def format_decimal_csv(value, decimals=6):
    if isinstance(value, float):
        return f"{value:.{decimals}f}".replace(".", ",")
    return value


def format_time_csv(value):
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return format_decimal_csv(value)
    return value


def parse_decimal_csv(value):
    if value is None or value == "":
        return None
    return float(str(value).replace(",", "."))


class ProfessorCROSLLeveling:
    """
    Adaptacion del esquema CRO-SL del profesor al problema de nivelacion.
    """

    def __init__(self, instance, parameters=None):
        params = parameters or {}
        self.instance = instance
        self.rng = random.Random(params.get("seed", 42))

        self.num_generations = params.get("num_generations", params.get("n_generations", 100))
        self.size_n = params.get("size_n", 5)
        self.size_m = params.get("size_m", 5)
        self.p_0 = params.get("p_0", 0.7)
        self.f_b = params.get("f_b", 0.7)
        self.r_l = params.get("r_l", 0.1)
        self.f_a = params.get("f_a", 0.1)
        self.f_d = params.get("f_d", 0.2)
        self.p_d = params.get("p_d", 0.15)
        self.k = params.get("k", 3)
        self.elitism = params.get("elitism", 0.05)
        self.broadcast_mutation = params.get("broadcast_mutation", False)
        self.similarity_check_interval = params.get("similarity_check_interval", 0)
        self.similarity_threshold = params.get("similarity_threshold", 0.5)
        self.reset_keep_rate = params.get("reset_keep_rate", 0.05)
        self.infeasibility_penalty = params.get("infeasibility_penalty", 1000000.0)
        self.pyramidal_search = params.get("pyramidal_search", False)
        self.pyramid_step = params.get("pyramid_step", 10)
        self.pyramid_increment_n = params.get("pyramid_increment_n", 2)
        self.pyramid_increment_m = params.get("pyramid_increment_m", 2)
        self.initialization_file = params.get("initialization_file")
        self.elite_file = params.get("elite_file")
        self.population_history_file = params.get("population_history_file")
        self.population_history_run_id = params.get("population_history_run_id", 0)
        self.stop_without_improvement = params.get("stop_without_improvement", None)
        self.substrate_operators = params.get("substrate_operators", DEFAULT_SUBSTRATES)

        self.instance.infeasibility_penalty = self.infeasibility_penalty
        self.layer_size = self.size_n * self.size_m
        self.reef = []
        self.elite = []
        self.history = []
        self._selected_for_brooding = []

    def save_population_snapshot(self, generation):
        if not self.population_history_file:
            return

        path = Path(self.population_history_file)
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)

        activities = list(self.instance.activities.keys())
        fieldnames = [
            "execution",
            "generation",
            "individual",
            "fitness",
        ] + [f"start_{activity}" for activity in activities] + [
            "feasible",
            "duration",
            "layer",
            "position",
            "substrate",
            "schedule",
        ]

        write_header = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
            if write_header:
                writer.writeheader()

            individual_number = 1
            for layer_index, layer in enumerate(self.reef):
                for position, coral in enumerate(layer):
                    if coral == "0":
                        continue

                    if coral.schedule is None:
                        decode_individual(coral, self.instance)

                    duration = max((end for _, _, end in coral.schedule), default=0.0)
                    row = {
                        "execution": self.population_history_run_id + 1,
                        "generation": generation,
                        "individual": individual_number,
                        "layer": layer_index,
                        "position": position,
                        "substrate": coral.substrate,
                        "fitness": format_decimal_csv(coral.fitness),
                        "feasible": coral.feasible,
                        "duration": format_time_csv(duration),
                        "schedule": " | ".join(
                            f"{act}:{format_time_csv(start)}-{format_time_csv(end)}"
                            for act, start, end in coral.schedule
                        ),
                    }
                    row.update(
                        {
                            f"start_{activity}": format_time_csv(coral.start_times.get(activity, ""))
                            for activity in activities
                        }
                    )
                    writer.writerow(row)
                    individual_number += 1

    def load_individuals_from_csv(self, filepath):
        path = Path(filepath)
        if not path.exists():
            return []

        individuals = []
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                start_times = {}
                for activity in self.instance.activities:
                    raw_value = row.get(str(activity), row.get(f"start_{activity}", ""))
                    if raw_value == "":
                        continue
                    start_times[activity] = parse_decimal_csv(raw_value)
                if start_times:
                    individuals.append(
                        evaluate_individual(ProjectLevelingIndividual(start_times), self.instance)
                    )
        return individuals

    def save_elite_to_csv(self):
        if not self.elite_file or not self.elite:
            return

        path = Path(self.elite_file)
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)

        activities = list(self.instance.activities.keys())
        with open(path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["fitness", "feasible"] + [str(activity) for activity in activities]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for coral in sorted(self.elite, key=lambda item: item.fitness):
                row = {
                    "fitness": format_decimal_csv(coral.fitness),
                    "feasible": coral.feasible,
                }
                row.update(
                    {
                        str(activity): format_time_csv(coral.start_times.get(activity, ""))
                        for activity in activities
                    }
                )
                writer.writerow(row)

    def initialize_reef(self):
        self.reef = []
        occupied = max(1, int(self.layer_size * self.p_0))
        loaded_individuals = []
        if self.initialization_file:
            loaded_individuals.extend(self.load_individuals_from_csv(self.initialization_file))
        if self.elite_file:
            loaded_individuals.extend(self.load_individuals_from_csv(self.elite_file))

        loaded_cursor = 0
        for layer_index, _ in enumerate(self.substrate_operators):
            layer = ["0" for _ in range(self.layer_size)]
            positions = self.rng.sample(range(self.layer_size), occupied)
            for position in positions:
                if loaded_cursor < len(loaded_individuals):
                    coral = loaded_individuals[loaded_cursor].copy()
                    loaded_cursor += 1
                else:
                    coral = create_random_individual(self.instance, self.rng)
                coral.substrate = layer_index
                layer[position] = evaluate_individual(coral, self.instance)
            self.reef.append(layer)

    def get_corals(self):
        corals = []
        for layer in self.reef:
            corals.extend([coral for coral in layer if coral != "0"])
        return corals

    def build_stats(self, generation, substrate_stats=None):
        corals = self.get_corals()
        fitness_values = [coral.fitness for coral in corals]
        stats = {
            "generation": generation,
            "best_fitness": min(fitness_values),
            "avg_fitness": sum(fitness_values) / len(fitness_values),
            "worst_fitness": max(fitness_values),
        }
        if substrate_stats is not None:
            stats["substrates"] = substrate_stats
        return stats

    def update_elite(self):
        if self.elitism <= 0:
            return

        corals = sorted(self.get_corals(), key=lambda coral: coral.fitness)
        elite_size = max(1, int(len(corals) * self.elitism))
        combined = sorted(
            self.elite + [coral.copy() for coral in corals],
            key=lambda coral: coral.fitness,
        )

        unique_elite = []
        seen = set()
        for coral in combined:
            signature = self.coral_signature(coral)
            if signature in seen:
                continue
            unique_elite.append(coral.copy())
            seen.add(signature)
            if len(unique_elite) >= elite_size:
                break

        self.elite = unique_elite

    def insert_elite(self):
        if not self.elite:
            return

        for elite_index, elite_coral in enumerate(self.elite):
            layer_index = elite_index % len(self.reef)
            layer = self.reef[layer_index]
            worst_position = None
            worst_fitness = None

            for position, coral in enumerate(layer):
                if coral == "0":
                    worst_position = position
                    break
                if worst_fitness is None or coral.fitness > worst_fitness:
                    worst_fitness = coral.fitness
                    worst_position = position

            clone = elite_coral.copy()
            clone.substrate = layer_index
            layer[worst_position] = clone

    def select_parent(self, layer_index):
        layer_corals = [coral for coral in self.reef[layer_index] if coral != "0"]
        if not layer_corals:
            layer_corals = self.get_corals()
        sample_size = min(3, len(layer_corals))
        candidates = self.rng.sample(layer_corals, sample_size)
        return min(candidates, key=lambda coral: coral.fitness)

    def apply_crossover_chain(self, parent1, parent2, crossover_names):
        child1 = parent1.copy()
        child2 = parent2.copy()
        for name in crossover_names:
            operator = crossover_operator_dict[name]
            child1, child2 = operator(child1, child2, self.instance, self.rng)
        return child1, child2

    def apply_mutation_chain(self, coral, mutation_names):
        larva = coral.copy()
        names = list(mutation_names)
        self.rng.shuffle(names)
        for idx, name in enumerate(names):
            if idx == 0 or self.rng.random() <= 0.5:
                mutation_operator_dict[name](larva, self.instance, self.rng)
        return evaluate_individual(larva, self.instance)

    def coral_signature(self, coral):
        return tuple(
            round(coral.start_times.get(activity, 0.0), 6)
            for activity in self.instance.activities
        )

    def broadcast_spawning(self):
        larvae_by_layer = [[] for _ in self.substrate_operators]
        self._selected_for_brooding = [set() for _ in self.substrate_operators]
        substrate_stats = [
            {
                "name": "+".join(substrate[0]) + " / " + "+".join(substrate[1]),
                "generated": 0,
                "settled": 0,
            }
            for substrate in self.substrate_operators
        ]

        for layer_index, substrate in enumerate(self.substrate_operators):
            layer_corals = [coral for coral in self.reef[layer_index] if coral != "0"]
            n_broadcast = max(1, int(len(layer_corals) * self.f_b))

            for _ in range(n_broadcast):
                parent1 = self.select_parent(layer_index)
                parent2 = self.select_parent(layer_index)
                self._selected_for_brooding[layer_index].add(id(parent1))
                self._selected_for_brooding[layer_index].add(id(parent2))
                crossover_names, mutation_names = substrate
                child1, child2 = self.apply_crossover_chain(parent1, parent2, crossover_names)
                if self.broadcast_mutation:
                    child1 = self.apply_mutation_chain(child1, mutation_names)
                    child2 = self.apply_mutation_chain(child2, mutation_names)
                else:
                    child1 = evaluate_individual(child1, self.instance)
                    child2 = evaluate_individual(child2, self.instance)
                larvae_by_layer[layer_index].append(min([child1, child2], key=lambda coral: coral.fitness))
                substrate_stats[layer_index]["generated"] += 1

        return larvae_by_layer, substrate_stats

    def brooding(self, larvae_by_layer, substrate_stats=None):
        for layer_index, layer in enumerate(self.reef):
            selected = self._selected_for_brooding[layer_index] if layer_index < len(self._selected_for_brooding) else set()
            mutation_names = self.substrate_operators[layer_index][1]
            for coral in [coral for coral in layer if coral != "0"]:
                if id(coral) in selected:
                    continue
                larvae_by_layer[layer_index].append(self.apply_mutation_chain(coral, mutation_names))
                if substrate_stats is not None:
                    substrate_stats[layer_index]["generated"] += 1

    def add_random_larvae(self, larvae_by_layer):
        n_random_larvae = int(sum(len(larvae) for larvae in larvae_by_layer) * self.r_l)
        if n_random_larvae > 0:
            random_layer = []
            for _ in range(n_random_larvae):
                random_layer.append(evaluate_individual(create_random_individual(self.instance, self.rng), self.instance))
            larvae_by_layer.append(random_layer)

    def larvae_setting(self, larvae_by_layer, substrate_stats=None):
        for layer_index, larvae in enumerate(larvae_by_layer):
            target_layer_index = min(layer_index, len(self.reef) - 1)
            layer = self.reef[target_layer_index]

            for larva in larvae:
                placed = False
                for _ in range(self.k):
                    position = self.rng.randint(0, self.layer_size - 1)
                    occupant = layer[position]
                    if occupant == "0" or larva.fitness < occupant.fitness:
                        larva.substrate = target_layer_index
                        layer[position] = larva
                        placed = True
                        if substrate_stats is not None and layer_index < len(substrate_stats):
                            substrate_stats[layer_index]["settled"] += 1
                        break
                if not placed:
                    empty_positions = [idx for idx, coral in enumerate(layer) if coral == "0"]
                    if empty_positions:
                        position = self.rng.choice(empty_positions)
                        larva.substrate = target_layer_index
                        layer[position] = larva
                        if substrate_stats is not None and layer_index < len(substrate_stats):
                            substrate_stats[layer_index]["settled"] += 1

    def asexual_reproduction(self):
        corals = sorted(self.get_corals(), key=lambda coral: coral.fitness)
        n_clones = max(1, int(len(corals) * self.f_a))
        larvae_by_layer = [[] for _ in self.substrate_operators]

        for coral in corals[:n_clones]:
            layer_index = coral.substrate if coral.substrate is not None else 0
            mutation_names = self.substrate_operators[layer_index][1]
            larvae_by_layer[layer_index].append(self.apply_mutation_chain(coral, mutation_names))

        self.larvae_setting(larvae_by_layer)

    def depredation(self):
        if self.rng.random() > self.p_d:
            return

        for layer in self.reef:
            occupied = [
                (idx, coral)
                for idx, coral in enumerate(layer)
                if coral != "0"
            ]
            occupied.sort(key=lambda item: item[1].fitness, reverse=True)
            n_remove = max(1, int(len(occupied) * self.f_d))
            for idx, _ in occupied[:n_remove]:
                layer[idx] = "0"

    def similarity_check(self):
        layers_to_reset = []
        for layer_index, layer in enumerate(self.reef):
            corals = [coral for coral in layer if coral != "0"]
            if not corals:
                continue
            unique = {self.coral_signature(coral) for coral in corals}
            similarity_rate = 1.0 - (len(unique) / len(corals))
            if similarity_rate >= self.similarity_threshold:
                layers_to_reset.append(layer_index)
        return layers_to_reset

    def reset_layer(self, layer_index):
        layer = self.reef[layer_index]
        corals = sorted(
            [coral for coral in layer if coral != "0"],
            key=lambda coral: coral.fitness,
        )
        if not corals:
            return

        if self.reset_keep_rate < 1.0:
            keep_count = max(1, int(len(corals) * self.reset_keep_rate))
        else:
            keep_count = max(1, int(self.reset_keep_rate))

        kept = []
        seen = set()
        for coral in corals:
            signature = self.coral_signature(coral)
            if signature in seen:
                continue
            clone = coral.copy()
            clone.substrate = layer_index
            kept.append(clone)
            seen.add(signature)
            if len(kept) >= keep_count:
                break

        new_layer = ["0" for _ in range(self.layer_size)]
        positions = self.rng.sample(range(self.layer_size), len(kept))
        for position, coral in zip(positions, kept):
            new_layer[position] = coral

        target_occupied = max(1, int(self.layer_size * self.p_0))
        empty_positions = [idx for idx, coral in enumerate(new_layer) if coral == "0"]
        for position in self.rng.sample(empty_positions, max(0, target_occupied - len(kept))):
            coral = create_random_individual(self.instance, self.rng)
            coral.substrate = layer_index
            new_layer[position] = evaluate_individual(coral, self.instance)

        self.reef[layer_index] = new_layer

    def reset_similar_layers(self, generation):
        if self.similarity_check_interval <= 0:
            return []
        if generation <= 1 or generation % self.similarity_check_interval != 0:
            return []

        layers_to_reset = self.similarity_check()
        for layer_index in layers_to_reset:
            self.reset_layer(layer_index)
        return layers_to_reset

    def expand_reef_size(self, generation):
        if not self.pyramidal_search:
            return False
        if self.pyramid_step <= 0 or generation <= 0 or generation % self.pyramid_step != 0:
            return False

        self.size_n += self.pyramid_increment_n
        self.size_m += self.pyramid_increment_m
        new_layer_size = self.size_n * self.size_m
        to_add = new_layer_size - self.layer_size
        if to_add <= 0:
            return False

        for layer_index, layer in enumerate(self.reef):
            layer.extend(["0" for _ in range(to_add)])
            target_occupied = max(1, int(new_layer_size * self.p_0))
            current_occupied = sum(coral != "0" for coral in layer)
            empty_positions = [idx for idx, coral in enumerate(layer) if coral == "0"]
            add_count = min(len(empty_positions), max(0, target_occupied - current_occupied))
            for position in self.rng.sample(empty_positions, add_count):
                coral = create_random_individual(self.instance, self.rng)
                coral.substrate = layer_index
                layer[position] = evaluate_individual(coral, self.instance)

        self.layer_size = new_layer_size
        return True

    def run(self):
        self.initialize_reef()
        self.update_elite()
        self.history = [self.build_stats(0)]
        self.save_population_snapshot(0)
        best_fitness = self.history[0]["best_fitness"]
        generations_without_improvement = 0

        for generation in range(1, self.num_generations + 1):
            reef_expanded = self.expand_reef_size(generation)
            reset_layers = self.reset_similar_layers(generation)
            larvae_by_layer, substrate_stats = self.broadcast_spawning()
            self.brooding(larvae_by_layer, substrate_stats=substrate_stats)
            self.add_random_larvae(larvae_by_layer)
            self.larvae_setting(larvae_by_layer, substrate_stats=substrate_stats)
            self.asexual_reproduction()
            self.depredation()
            self.insert_elite()
            self.update_elite()
            stats = self.build_stats(generation, substrate_stats=substrate_stats)
            stats["reset_layers"] = reset_layers
            stats["reef_size"] = self.layer_size
            stats["reef_expanded"] = reef_expanded
            self.history.append(stats)
            self.save_population_snapshot(generation)

            if stats["best_fitness"] < best_fitness:
                best_fitness = stats["best_fitness"]
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            if (
                self.stop_without_improvement is not None
                and generations_without_improvement >= self.stop_without_improvement
            ):
                break

        best = min(self.get_corals(), key=lambda coral: coral.fitness)
        self.save_elite_to_csv()
        return {
            "best_individual": best,
            "best_schedule": best.schedule,
            "best_fitness": best.fitness,
            "history": self.history,
            "elite": self.elite,
            "generations_executed": self.history[-1]["generation"],
            "population": self.get_corals(),
            "instance": self.instance,
            "population_history_file": self.population_history_file,
        }
