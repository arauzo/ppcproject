#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import operator
import collections
import scipy.stats
import numpy
import graph
import pert

def build_successors_from_prelations(activities):
    successors = {}

    for act in activities:
        act_name = str(act[1])
        successors[act_name] = []

    for act in activities:
        act_name = str(act[1])
        predecessors = act[2]

        if isinstance(predecessors, (list, tuple)):
            for pred in predecessors:
                pred_name = str(pred)
                if pred_name not in successors:
                    successors[pred_name] = []
                successors[pred_name].append(act_name)
        elif predecessors not in ('', None):
            pred_name = str(predecessors)
            if pred_name not in successors:
                successors[pred_name] = []
            successors[pred_name].append(act_name)

    return successors


def evaluate_models(activities, sim_durations, simulaciones, porcentaje=90, pert_graph=None):
    # Normalizar actividades para trabajar siempre con nombres/predecesoras como texto
    normalized_activities = []
    for act in activities:
        act_copy = list(act)
        act_copy[1] = str(act_copy[1])

        if isinstance(act_copy[2], (list, tuple)):
            act_copy[2] = [str(x) for x in act_copy[2] if x != '']
        elif act_copy[2] in ('', None):
            act_copy[2] = []
        else:
            act_copy[2] = [str(act_copy[2])]

        normalized_activities.append(act_copy)

    # Get all paths removing 'begin' y 'end' from each path
    successors = build_successors_from_prelations(normalized_activities)
    aon = graph.roy(successors)
    caminos = [c[1:-1] for c in graph.find_all_paths(aon, 'Begin', 'End')]

    path_data = []
    for camino in caminos:
        media, varianza = pert.mediaYvarianza(camino, normalized_activities)
        path_data.append([camino, float(media), float(varianza)])

    if not path_data:
        return {}

    path_data.sort(key=operator.itemgetter(1, 2))

    crit_path_avg = float(path_data[-1][1])
    crit_path_var = max(0, path_data[-1][2])
    crit_path_stdev = math.sqrt(crit_path_var)

    m_dodin = 0
    m_salas = 0
    sigma_max = 0.0
    sigma_min = None
    sigma_ant = None

    for i in range(len(path_data)):
        if ((crit_path_avg - path_data[i][1]) < max(0.05 * crit_path_avg, 0.02 * crit_path_stdev)):
            m_dodin += 1
            path_std = math.sqrt(max(0, path_data[i][2]))
            if sigma_max < path_std:
                sigma_max = path_std
            if sigma_min is None or sigma_min > path_std:
                sigma_min = path_std

        if ((float(path_data[i][1]) + 0.5 * math.sqrt(max(0, path_data[i][2]))) >= (crit_path_avg - 0.25 * crit_path_stdev)):
            m_salas += 1
            path_std = math.sqrt(max(0, path_data[i][2]))
            if sigma_ant is None or sigma_ant > path_std:
                sigma_ant = path_std

    if sigma_min is None:
        sigma_min = 0.0
    if sigma_ant is None:
        sigma_ant = 0.0

    attributes = collections.OrderedDict()
    attributes['crit_path_avg'] = crit_path_avg
    attributes['crit_path_stdev'] = crit_path_stdev
    attributes['n_paths'] = len(path_data)
    attributes['n_nodes'] = len(pert_graph.successors) if pert_graph else None
    attributes['n_activ'] = len(normalized_activities)
    attributes['m_dodin'] = m_dodin
    attributes['m_salas'] = m_salas
    attributes['sigma_max'] = sigma_max
    attributes['sigma_min'] = sigma_min
    attributes['sigma_ant'] = sigma_ant
    attributes['dist'] = normalized_activities[1][8] if len(normalized_activities) > 1 and len(normalized_activities[1]) > 8 else 'Normal'

    results = collections.OrderedDict(attributes)
    for model in MODELS:
        name, dist, debug_vars = model(attributes)
        if dist is not None:
            try:
                ks_statistic, p_value = scipy.stats.kstest(sim_durations, dist.cdf)
                observed, predicted = observed_predicted(sim_durations, dist.cdf)
                results['ks' + name] = ks_statistic
                results['p_' + name] = p_value
                results['MAE_' + name] = mae(observed, predicted)
                results['RMSE_' + name] = rmse(observed, predicted)
                results['R2_' + name] = rsquared(observed, predicted)
                results['mean' + name] = dist.mean()
                results['sigma' + name] = dist.std()
            except:
                results['ks' + name] = None
                results['p_' + name] = None
        else:
            results['ks' + name] = None
            results['p_' + name] = None

    results['meanSimulation'] = numpy.mean(sim_durations)
    results['sigmaSimulation'] = numpy.std(sim_durations)
    return results

# --- Auxiliares ---
def observed_predicted(rvs, cdf):
    vals = numpy.sort(rvs)
    observed = cdf(vals)
    n = len(vals)
    predicted = numpy.arange(1.0, n+1) / n   
    return observed, predicted

def mae(observed, predicted): return abs(observed - predicted).mean()
def rmse(observed, predicted): return math.sqrt(((observed - predicted)**2).mean())
def rsquared(observed, predicted):
    slope, intercept, r_val, p_val, std_err = scipy.stats.linregress(observed, predicted)
    return r_val**2

# --- Modelos Protegidos ---

def model_pert(attributes):
    # Si la escala es 0, scipy.stats.norm no falla pero cdf da problemas. 
    # Usamos un valor mínimo casi despreciable.
    scale = max(0.0001, attributes['crit_path_stdev'])
    d_normal = scipy.stats.norm(loc=attributes['crit_path_avg'], scale=scale)
    return ('PERT', d_normal, {})

def model_gamma(attributes):
    if attributes.get('sigma_min', 0) <= 0 or attributes.get('m_dodin', 0) <= 0:
        return ('Gamma', None, {'error': 'Varianza nula'})
    try:
        sigma = 0.91154134766017 * attributes['sigma_min']
        log_m = math.log(attributes['m_dodin'])
        if attributes['dist'] == 'Normal':
            media = 1.1336 * attributes['crit_path_avg'] - 0.9153 * attributes['sigma_min'] + 1.0927 * log_m
        else:
            media = 0.9126 * attributes['crit_path_avg'] + 0.7550 * attributes['sigma_min'] + 2.9658 * log_m
        
        if media <= 0: return ('Gamma', None, {})
        beta = sigma**2 / media
        alfa = media / beta
        return ('Gamma', scipy.stats.gamma(alfa, scale=beta), {'alfa': alfa, 'beta': beta})
    except: return ('Gamma', None, {})

def model_gamma_ant(attributes):
    if attributes.get('sigma_ant', 0) <= 0 or attributes.get('m_salas', 0) <= 0:
        return ('Gamma_ant', None, {})
    try:
        sigma_ant = 1.05 * attributes['sigma_ant']
        media_ant = attributes['crit_path_avg'] + math.pi * math.log(attributes['m_salas']) / sigma_ant
        beta_ant = sigma_ant**2 / media_ant
        alfa_ant = media_ant / beta_ant
        return ('Gamma_ant', scipy.stats.gamma(alfa_ant, scale=beta_ant), {'alfa': alfa_ant, 'beta': beta_ant})
    except: return ('Gamma_ant', None, {})

def model_ev(attributes):
    # PROTECCIÓN TOTAL EV
    m = attributes.get('m_dodin', 0)
    std = attributes.get('crit_path_stdev', 0)
    if m <= 1 or std <= 0:
        return ('EV', None, {})
    try:
        log_m = math.log(m)
        sqrt_2logm = (2 * log_m)**0.5
        a = attributes['crit_path_avg'] + std * (sqrt_2logm - 0.5 * (math.log(log_m) + math.log(4 * math.pi)) / sqrt_2logm)
        b = sqrt_2logm / std
        return ('EV', scipy.stats.gumbel_r(loc=a, scale=1/b), {'a': a, 'b': b})
    except: return ('EV', None, {})

MODELS = [model_pert, model_gamma, model_gamma_ant, model_ev]

if __name__ == '__main__':
    pass