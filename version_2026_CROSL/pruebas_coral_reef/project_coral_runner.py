#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from coralReef import run_coral_reef
from coral_sl_project import CROSLProject
from project_instance import ProjectInstance
from sm_project_loader import load_sm_project


DEFAULT_CORAL_PARAMETERS = {
    "reef_size": 20,
    "n_generations": 20,
    "larvae_per_generation": 10,
    "mutation_rate": 0.2,
    "crossover_mode": "random",
    "sexual_rate": 0.7,
    "predation_rate": 0.1,
    "f_a": 0.1,
    "seed": 42,
}


def build_project_instance(activities, predecessors, resources, asignation, leveling=0):
    return ProjectInstance(
        activities=activities,
        predecessors=predecessors,
        resources=resources,
        asignation=asignation,
        leveling=leveling,
    )


def load_project_instance_from_sm(sm_path, leveling=0):
    predecessors, resources, asignation, activities = load_sm_project(sm_path)
    instance = build_project_instance(
        activities=activities,
        predecessors=predecessors,
        resources=resources,
        asignation=asignation,
        leveling=leveling,
    )
    return instance


def normalize_coral_result(result, mode):
    if mode == "classic":
        return {
            "mode": mode,
            "best_individual": result["best_individual"],
            "best_schedule": result["best_schedule"],
            "best_fitness": result["best_fitness"],
            "history": result["history"],
            "population": result["population"],
        }

    return {
        "mode": mode,
        "best_individual": result["best_individual"],
        "best_schedule": result["best_schedule"],
        "best_fitness": result["best_fitness"],
        "history": result["history"],
        "population": result["population"],
        "substrate_stats": result.get("substrate_stats", []),
    }


def run_project_coral(mode, instance, parameters=None):
    params = DEFAULT_CORAL_PARAMETERS.copy()
    if parameters:
        params.update(parameters)

    if mode == "classic":
        result = run_coral_reef(
            asignation=instance.asignation,
            resources=instance.resources,
            predecessors=instance.predecessors,
            activities=instance.activities,
            leveling=instance.leveling,
            reef_size=params["reef_size"],
            n_generations=params["n_generations"],
            larvae_per_generation=params["larvae_per_generation"],
            mutation_rate=params["mutation_rate"],
            crossover_mode=params["crossover_mode"],
            sexual_rate=params["sexual_rate"],
            predation_rate=params["predation_rate"],
            seed=params["seed"],
        )
        return normalize_coral_result(result, mode)

    if mode == "crosl":
        crosl_params = {
            "reef_size": params["reef_size"],
            "n_generations": params["n_generations"],
            "larvae_per_generation": params["larvae_per_generation"],
            "mutation_rate": params["mutation_rate"],
            "sexual_rate": params["sexual_rate"],
            "predation_rate": params["predation_rate"],
            "f_a": params["f_a"],
            "seed": params["seed"],
        }
        result = CROSLProject(crosl_params, instance).run()
        return normalize_coral_result(result, mode)

    raise ValueError(f"Modo de coral no soportado: {mode}")


def run_project_coral_from_sm(sm_path, mode, parameters=None, leveling=0):
    instance = load_project_instance_from_sm(sm_path, leveling=leveling)
    return run_project_coral(mode=mode, instance=instance, parameters=parameters)
