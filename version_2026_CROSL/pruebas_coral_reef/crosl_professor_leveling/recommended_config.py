#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuracion recomendada para CRO-SL profesor adaptado a nivelacion.

Esta configuracion se fija tras comparar contra simulated annealing y contra
la variante sin elitismo sobre las instancias .sm disponibles.
"""


RECOMMENDED_PARAMETERS = {
    "num_generations": 100,
    "size_n": 8,
    "size_m": 8,
    "p_0": 0.7,
    "f_b": 0.7,
    "r_l": 0.1,
    "f_a": 0.1,
    "f_d": 0.2,
    "p_d": 0.15,
    "k": 3,
    "elitism": 0.05,
    "broadcast_mutation": False,
    "similarity_check_interval": 10,
    "similarity_threshold": 0.5,
    "reset_keep_rate": 0.05,
    "infeasibility_penalty": 1000000.0,
    "pyramidal_search": False,
    "pyramid_step": 10,
    "pyramid_increment_n": 2,
    "pyramid_increment_m": 2,
    "initialization_file": None,
    "elite_file": None,
    "stop_without_improvement": 50,
    "seed": 42,
}


RECOMMENDED_SUBSTRATES = [
    [["OX", "Switch"], ["TWORS"]],
    [["OX", "Switch"], ["TWORS", "Exchange"]],
    [["Switch", "PMX"], ["Dept_swap"]],
    [["Cycle", "PMX"], ["Invert", "Dept_swap"]],
]
