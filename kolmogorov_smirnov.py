#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Models to estimate project duration and test the distribution estimated

 PPC-PROJECT
   Multiplatform software tool for education and research in
   project management

 Copyright 2007-13 Universidad de Córdoba
 This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published
   by the Free Software Foundation, either version 3 of the License,
   or (at your option) any later version.
 This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import math
import operator
import collections

import scipy.stats
import numpy

import graph
import pert


def evaluate_models(activities, sim_durations, simulaciones, porcentaje=90, pert_graph=None):
    """
    Using the data from a simulation compare the results with those achieved by the several models 
    defined. The comparison is done by testing the fitting of the distribution with the 
    kolmogorov_smirnov test 

    activities (project activities)
    sim_durations (vector with the duration resulting from the simulation)
    simulaciones (vector with the simulations of each activity in each iteration)
    porcentaje (the mark we want to establish to determine how many paths have turned out critical)

    return: results (dictionary with all attributes and test results)
    """
    # Get all paths removing 'begin' y 'end' from each path
    successors = dict(((act[1], act[2]) for act in activities))
    aon = graph.roy(successors)
    caminos = [c[1:-1] for c in graph.find_all_paths(aon, 'Begin', 'End')]

    # List with all paths, their duration and variance (ordered by increasing duration and variance)
    path_data = []
    for camino in caminos:   
        media, varianza = pert.mediaYvarianza(camino, activities) 
        path_data.append([camino, float(media), float(varianza)])
    path_data.sort(key=operator.itemgetter(1, 2))

    # Critical path average and std deviation (according to PERT Normal estimate)
    crit_path_avg = float(path_data[-1][1])
    crit_path_stdev = math.sqrt(path_data[-1][2]) 

    # Number of predominant paths is calculated according to Dodin (m_dodin) and to ours (m_salas),
    m_dodin = 0
    m_salas = 0
    # Std. dev for selected paths
    sigma_max = None
    sigma_min = None
    sigma_ant = None    

    for i in range(len(path_data)):
        # Considered critical by Dodin
        if ((crit_path_avg - path_data[i][1]) < max(0.05*crit_path_avg, 0.02* crit_path_stdev)):
            m_dodin += 1
            path_stddev = math.sqrt(path_data[i][2])
            if sigma_max == None or sigma_max < path_stddev:
                sigma_max = path_stddev
            if sigma_min == None or sigma_min > path_stddev:
                sigma_min = path_stddev

        # Considered critical by Salas
        if ((float(path_data[i][1]) + 0.5*math.sqrt(path_data[i][2])) >= (crit_path_avg - 0.25* crit_path_stdev)):
            m_salas += 1
            path_stdev = math.sqrt(path_data[i][2])
            if sigma_ant == None or sigma_ant > path_stdev:
                sigma_ant = path_stdev

    # Store variables to be used to create models
    attributes = collections.OrderedDict()
    attributes['crit_path_avg'] = crit_path_avg
    attributes['crit_path_stdev'] = crit_path_stdev

    attributes['n_paths'] = len(path_data)
    if pert_graph:
        attributes['n_nodes'] = len(pert_graph.successors)
    else:
        attributes['n_nodes'] = None
    attributes['n_activ'] = len(activities)

    attributes['m_dodin'] = m_dodin
    attributes['m_salas'] = m_salas

    attributes['sigma_max'] = sigma_max
    attributes['sigma_min'] = sigma_min
    attributes['sigma_ant'] = sigma_min

    attributes['dist'] = activities[1][8] # for Gamma (which is a 'mutant', a dual model)

    # Create and test the models
    results = collections.OrderedDict(attributes)
    for model in MODELS:
        name, dist, debug_vars = model(attributes)
        print "*** MODEL:", name, "***"
        if dist != None:
            ks_statistic, p_value = scipy.stats.kstest(sim_durations, dist.cdf)        
            observed, predicted = observed_predicted(sim_durations, dist.cdf)
            results['ks' + name] = ks_statistic
            results['p_' + name] = p_value
            results['MAE_' + name] = mae(observed, predicted)
            results['RMSE_' + name] = rmse(observed, predicted)
            results['RRMSE_' + name] = rrmse(observed, predicted)
            results['R2_' + name] = rsquared(observed, predicted)
            results['NSE_' + name] = nse(observed, predicted)
            results['Wilmott_' + name] = wilmott(observed, predicted)
            results['PBIAS_' + name] = pbias(observed, predicted)
            results['mean' + name] = dist.mean()
            results['sigma' + name] = dist.std()
            for var in debug_vars:
                results[var + name] = debug_vars[var] 
        else:
            results['ks' + name] = None
            results['p_' + name] = None
            results['MAE_' + name] = None
            results['RMSE_' + name] = None
            results['RRMSE_' + name] = None
            results['R2_' + name] = None
            results['NSE_' + name] = None
            results['Wilmott_' + name] = None
            results['PBIAS_' + name] = None
            results['mean' + name] = None
            results['sigma' + name] = None

    # Include average and std of the simulation
    results['meanSimulation'] = numpy.mean(sim_durations)
    results['sigmaSimulation'] = numpy.std(sim_durations)

    return results


# --- Measures of goodness of fit
def observed_predicted(rvs, cdf):
    """
    Transform simulation measures into probability observed and predicted

    rvs, data
    cdf, estimated distribution
    """
    # (taken from Dmin of scipy.stats.kstest)
    vals = numpy.sort(rvs)
    print "Vals:", vals.mean()
    print "CDF", cdf.im_self.mean(), cdf.im_self.std()
    observed = cdf(vals)
    n = len(vals)
    predicted = numpy.arange(1.0, n+1) / n   
#    print "Obs:", observed.mean(), observed
#    print "Pred:", predicted.mean(), predicted
    return observed, predicted

def mae(observed, predicted):
    """
    Mean Average Error 
    """
    return abs(observed - predicted).mean()
    
def rmse(observed, predicted):
    """
    Root Mean Squared Error
    """
    errors_sqr = (observed - predicted)**2
    return math.sqrt( errors_sqr.mean() )
    
def rsquared(observed, predicted):
    """
    R^2
    """
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(observed, predicted)
    return r_value**2

def nse(observed, predicted):
    """
    Efficiency coeficient of Nash and Sutcliffe (1970), ver Pushpalatha2012a_review.
    
    [-inf, 1.0] (<0 the mean is better estimator, 1.0 perfect fit)
    """
    errors_sqr = (observed - predicted)**2
    obs_mean = observed.mean()
    return 1 - sum(errors_sqr) / sum((observed - obs_mean)**2)

def wilmott(observed, predicted):
    """
    Concordance coeficient of Wilmott (1984), ver Krause2005Efficiency.
    """
    errors_sqr = (observed - predicted)**2
    obs_mean = observed.mean()
    return 1 - sum(errors_sqr) / sum( (abs(predicted - obs_mean) + abs(observed - obs_mean))**2 )
    
def pbias(observed, predicted):
    """
    PBIAS, ver Moriasi2007model.

    Deviation of prediction expressed as a percentage
    """
    return 100 * sum(observed - predicted) / sum(observed)

def rrmse(observed, predicted):
    """
    Relative RMSE
    """
    return rmse(observed, predicted) / observed.mean()
    
#MEASURES = [ ('MAE', mae), 
#             rmse]

# --- Definition of the models to predict duration random variable
def model_gamma(attributes):
    """
    Estimate the duration random variable of a project with a Gamma distribution using a model 
    created by Salas et al.
    
    return: ('Gamma' (the name), 
             the scipy.stat.distribution, 
             alfa and beta (as debug variables in a dictionary)
    """
    sigma = 0.91154134766017  * attributes['sigma_min']
    
    if attributes['dist'] == 'Normal':
        media = (  1.1336004782864 * attributes['crit_path_avg'] 
                 - 0.9153232086309 * attributes['sigma_min']
                 + 1.0927284342627 * math.log(attributes['m_dodin']) )
    else :
        media = (  0.91263355372917 * attributes['crit_path_avg'] 
                 + 0.75501704782379 * attributes['sigma_min']
                 + 2.96581038327203 * math.log(attributes['m_dodin']) )

    beta = sigma**2 / media
    alfa = media / beta

    d_gamma = scipy.stats.gamma(alfa, scale=beta)

    return ('Gamma', d_gamma, {'alfa' : alfa, 'beta' : beta}) 

def model_gamma_ant(attributes):
    """
    Estimate the duration random variable of a project with a Gamma distribution using an ad hoc 
    previous model created by Salas et al. 
    
    return: ('GammaAnt' (the name), 
             the scipy.stat.distribution, 
             alfa and beta (as debug variables in a dictionary)
    """
    # Gamma previous model
    sigma_ant = attributes['sigma_ant']
    media_ant = attributes['crit_path_avg'] +  math.pi * math.log(attributes['m_salas']) / sigma_ant
    beta_ant = sigma_ant**2 / media_ant
    alfa_ant = media_ant / beta_ant

    d_gamma_ant = scipy.stats.gamma(alfa_ant, scale=beta_ant)
    return ('GammaAnt', d_gamma_ant, {'alfa' : alfa_ant, 'beta' : beta_ant}) 


def model_pert(attributes):
    """
    PERT method to estimate the duration random variable of a project with a Normal distribution
    
    return: ('PERT' (the name), 
             the scipy.stat.distribution, 
             no debug variables in a dictionary
    """
    d_normal = scipy.stats.norm(loc=attributes['crit_path_avg'], scale=attributes['crit_path_stdev'])
    return ('PERT', d_normal, {}) 

def model_ev(attributes):
    """
    Dodin estimate of the duration random variable of a project with Extreme Values distribution
    
    return: ('EV' (the name), 
             the scipy.stat.distribution, 
             media and std (as debug variables in a dictionary)
    """
    if attributes['m_dodin'] > 1:
        a = (attributes['crit_path_avg'] + attributes['crit_path_stdev'] 
             * ( (2 * math.log(attributes['m_dodin']))**0.5 
                 - 0.5 * (math.log(math.log(attributes['m_dodin'])) 
                          + math.log(4 * math.pi)) / (2 * math.log(attributes['m_dodin']))**0.5 
               )
            )
               
        b = ((2 * math.log(attributes['m_dodin']))**0.5) / attributes['crit_path_stdev']

        if (a != 0 and b !=0):
            d_ev = scipy.stats.gumbel_r(loc=a, scale=1 / b)
        else:
            d_ev = None
    else:
        d_ev = None

    return ('EV', d_ev, {}) 

MODELS = [  model_pert, 
            model_gamma, 
            model_gamma_ant, 
            model_ev,
         ]

# If the program is run directly, test cases
if __name__ == '__main__':
    pass 


