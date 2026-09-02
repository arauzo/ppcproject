#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import sys
import time

from graph import successors2precedents


CORAL_DIR = os.path.join(os.path.dirname(__file__), 'pruebas_coral_reef')
if CORAL_DIR not in sys.path:
    sys.path.insert(0, CORAL_DIR)

from project_coral_runner import build_project_instance, run_project_coral  # noqa: E402
from crosl_professor_leveling.crosl import ProfessorCROSLLeveling  # noqa: E402
from crosl_professor_leveling.leveling_tools import resource_variance_summary  # noqa: E402
from crosl_professor_leveling.project_instance import ProjectLevelingInstance  # noqa: E402
from crosl_professor_leveling.recommended_config import RECOMMENDED_PARAMETERS  # noqa: E402


LAST_CROSL_SUMMARY = {}


def get_last_crosl_summary():
    return dict(LAST_CROSL_SUMMARY)


def _format_csv_number(value, decimals=6):
    if isinstance(value, float):
        return f'{value:.{decimals}f}'.replace('.', ',')
    return value


def _export_generation_history(history, filepath, execution):
    if not filepath:
        return

    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    write_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
    initial_best = history[0].get('best_fitness', 0.0) if history else 0.0
    best_so_far = None

    with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                'execution',
                'generation',
                'best_fitness',
                'avg_fitness',
                'worst_fitness',
                'improvement_from_initial_percent',
                'best_improved',
            ],
            delimiter=';',
        )
        if write_header:
            writer.writeheader()

        for row in history:
            best_fitness = row.get('best_fitness', 0.0)
            improved = best_so_far is None or best_fitness < best_so_far
            if improved:
                best_so_far = best_fitness
            improvement = (
                ((initial_best - best_fitness) / initial_best) * 100.0
                if initial_best else 0.0
            )
            writer.writerow(
                {
                    'execution': execution,
                    'generation': row.get('generation', 0),
                    'best_fitness': _format_csv_number(best_fitness),
                    'avg_fitness': _format_csv_number(row.get('avg_fitness', 0.0)),
                    'worst_fitness': _format_csv_number(row.get('worst_fitness', 0.0)),
                    'improvement_from_initial_percent': _format_csv_number(improvement),
                    'best_improved': improved,
                }
            )


def _summarize_professor_crosl(result, parameters, seed, elapsed_time):
    schedule = result.get('best_schedule') or []
    instance = result.get('instance')
    history = result.get('history') or []
    variances = resource_variance_summary(schedule, instance) if instance is not None else {}
    variance_items = sorted(
        variances.items(),
        key=lambda item: item[1].get('variance', 0.0),
    )
    best_resource = variance_items[0] if variance_items else (None, {})
    worst_resource = variance_items[-1] if variance_items else (None, {})

    best_fitness = result.get('best_fitness', 0.0)
    initial_fitness = history[0].get('best_fitness', best_fitness) if history else best_fitness
    if initial_fitness:
        improvement = ((initial_fitness - best_fitness) / initial_fitness) * 100.0
    else:
        improvement = 0.0

    best_generation = 0
    if history:
        best_generation = min(
            history,
            key=lambda item: item.get('best_fitness', float('inf')),
        ).get('generation', 0)

    generated_larvae = 0
    settled_larvae = 0
    for stats in history:
        for substrate in stats.get('substrates', []):
            generated_larvae += substrate.get('generated', 0)
            settled_larvae += substrate.get('settled', 0)
    settled_rate = (settled_larvae / generated_larvae * 100.0) if generated_larvae else 0.0

    size_n = parameters.get('size_n', 0)
    size_m = parameters.get('size_m', 0)
    elite_ratio = parameters.get('elitism', 0.0)
    reef_slots = size_n * size_m * len(parameters.get('substrate_operators', []))
    elite_size = max(1, int(reef_slots * elite_ratio)) if elite_ratio > 0 and reef_slots > 0 else 0

    return {
        'best_variance': best_fitness,
        'optimized_resources': list(
            getattr(instance, 'optimized_resources', [])
        ) if instance is not None else [],
        'avg_resource_variance': (
            sum(item['variance'] for item in variances.values()) / len(variances)
            if variances else 0.0
        ),
        'best_resource': best_resource[0],
        'best_resource_variance': best_resource[1].get('variance', 0.0),
        'worst_resource': worst_resource[0],
        'worst_resource_variance': worst_resource[1].get('variance', 0.0),
        'best_generation': best_generation,
        'generations_executed': result.get('generations_executed', 0),
        'execution_time': elapsed_time,
        'improvement_percent': improvement,
        'settled_larvae': settled_larvae,
        'generated_larvae': generated_larvae,
        'settled_rate': settled_rate,
        'reef_size': '%sx%s' % (size_n, size_m),
        'elite_size': elite_size,
        'seed': seed,
        'p_0': parameters.get('p_0', 0.0),
        'f_b': parameters.get('f_b', 0.0),
        'r_l': parameters.get('r_l', 0.0),
        'f_a': parameters.get('f_a', 0.0),
        'f_d': parameters.get('f_d', 0.0),
        'p_d': parameters.get('p_d', 0.0),
        'critical_duration': (
            getattr(instance, 'critical_project_duration', 0.0)
            if instance is not None else 0.0
        ),
        'allowed_duration': (
            getattr(instance, 'project_duration', 0.0)
            if instance is not None else 0.0
        ),
        'force_project_duration': (
            getattr(instance, 'force_project_duration', False)
            if instance is not None else False
        ),
    }


def project_coral(
    asignation,
    resources,
    successors,
    activities,
    leveling,
    mode='classic',
    reef_size=20,
    n_generations=20,
    larvae_per_generation=10,
    mutation_rate=0.2,
    crossover_mode='random',
    sexual_rate=0.7,
    predation_rate=0.1,
    f_a=0.1,
    seed=42,
    population_history_file=None,
    population_history_run_id=0,
    generation_history_file=None,
    elite_file=None,
    initialization_file=None,
    max_project_duration=None,
    force_project_duration=False,
    crosl_parameters=None,
    use_elite_seeds=True,
):
    """
    Adaptador para ejecutar los algoritmos coral con una firma similar a
    simulated_annealing(), de forma que la integracion en ppcproject.py sea
    sencilla.

    Devuelve:
        schedule, evaluated, duration, alpha, temp, iterations
    """
    predecessors = successors2precedents(successors)
    for act in list(predecessors.keys()):
        if predecessors[act] == []:
            del predecessors[act]

    if mode == 'professor_crosl':
        global LAST_CROSL_SUMMARY
        parameters = RECOMMENDED_PARAMETERS.copy()
        if crosl_parameters:
            parameters.update(crosl_parameters)
        instance = ProjectLevelingInstance(
            activities=activities,
            predecessors=predecessors,
            resources=resources,
            asignation=asignation,
            max_project_duration=max_project_duration,
            force_project_duration=force_project_duration,
            optimized_resource_count=parameters.get('optimized_resource_count', 0),
            optimized_resources=parameters.get('optimized_resources'),
        )
        parameters.update(
            {
                'num_generations': int(n_generations),
                'seed': seed,
                'elite_file': elite_file,
                'initialization_file': initialization_file,
                'population_history_file': population_history_file,
                'population_history_run_id': population_history_run_id,
            }
        )
        start_time = time.perf_counter()
        result = ProfessorCROSLLeveling(instance, parameters).run()
        elapsed_time = time.perf_counter() - start_time
        _export_generation_history(
            result.get('history', []),
            generation_history_file,
            population_history_run_id + 1,
        )
        schedule = result['best_schedule']
        duration = 0
        if schedule:
            duration = max(end_time for _, _, end_time in schedule)
        evaluated = result['best_fitness']
        alpha = None
        temp = None
        iterations = result.get('generations_executed', int(n_generations))
        LAST_CROSL_SUMMARY = _summarize_professor_crosl(result, parameters, seed, elapsed_time)
        LAST_CROSL_SUMMARY['population_history_file'] = population_history_file
        LAST_CROSL_SUMMARY['generation_history_file'] = generation_history_file
        LAST_CROSL_SUMMARY['elite_file'] = elite_file
        LAST_CROSL_SUMMARY['use_elite_seeds'] = use_elite_seeds
        return schedule, evaluated, duration, alpha, temp, iterations

    instance = build_project_instance(
        activities=activities,
        predecessors=predecessors,
        resources=resources,
        asignation=asignation,
        leveling=leveling,
    )

    result = run_project_coral(
        mode=mode,
        instance=instance,
        parameters={
            'reef_size': reef_size,
            'n_generations': n_generations,
            'larvae_per_generation': larvae_per_generation,
            'mutation_rate': mutation_rate,
            'crossover_mode': crossover_mode,
            'sexual_rate': sexual_rate,
            'predation_rate': predation_rate,
            'f_a': f_a,
            'seed': seed,
        },
    )

    schedule = result['best_schedule']
    duration = 0
    if schedule:
        duration = max(end_time for _, _, end_time in schedule)

    evaluated = result['best_fitness']
    alpha = None
    temp = None
    iterations = max(0, len(result.get('history', [])) - 1)

    return schedule, evaluated, duration, alpha, temp, iterations
