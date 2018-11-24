#
# Functions for sampling and general statistics
#



from random import random as rand
import math

from sima_classes import *

#
# Function to sample a prior distribution
#
#  - Only uniform distribution implemented currently
#
def sample_prior_distribution(type,params):

    if (type == "uniform"):
        lo = params[0]
        hi = params[1]
        return lo + rand()*(hi-lo)
    else:
        print("Unknown prior distribution type.")
        return []

#
# Function to get a set of new parameters sampled from the prior distributions
#
def get_params(generative_model,priors):

    params = []

    if not (generative_model.check_par_len(priors)):
        return []

    for par in range(len(generative_model.params)):
        type = priors.type[par]
        distrpars = priors.params[par]
        params.append(sample_prior_distribution(type,distrpars))

    return params

#
# Function to calculate a summary statistic for a set of sampled parameters with the obeerved data
#
def calc_summary_stat(params, generative_model, observed_data, option):
    
    if option=="sq_residual":

        ndata = observed_data.len_data()

        resdiffsum = 0
        ressum = 0
        for i in range(ndata):
            newres = generative_model.calc_result(params,observed_data.vars[i])
            ressum += observed_data.res[i]
            resdiffsum += math.sqrt(math.pow(newres-observed_data.res[i],2.0))

        return resdiffsum/(ressum*ndata)

    else:
        print("Unknown option for the summary statistic.")

