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
def calc_summary_stat(params, generative_model, observed_data, options):
    
    if options.summary_statistic=="sq_residual":

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



#
# POSTERIOR SAMPLING FUNCTIONS
#

# each function must take the following arguments, in this order:
#   model,  priors, posterior, data, opt, lock

def sample_from_posterior_rejection_sampling(model,priors,posterior,data,opt,lock):

    for run in range(opt.get_batch_samples()):
        # sample the priors to get new parameters
        newpars = get_params(model,priors)

        # calculate the summary statistic for the new parameters compared to observed data
        sstat = calc_summary_stat(newpars,model,data,opt)

        # if the results are close enough, save to accepted parameters (reject otherwise)
        lock.acquire()
        posterior.accept_and_save(opt,newpars,sstat,0)
        lock.release()

        nall = posterior.get_num_all()
        print(str(nall))

def sample_from_posterior_mcmc(model,priors,posterior,data,opt,lock):


    while posterior.get_num_accepted() < opt.get_num_samples():

        # sample the priors to get new parameters
        newpars = get_params(model,priors)

        # get the current parameters
        if(posterior.i_acc > 0):
            oldpars = posterior.accepted_params[posterior.i_acc - 1]
            firstrun = False
        else:
            oldpars = newpars
            firstrun = True

        # calculate the summary statistic for the new parameters compared to observed data
        newsstat = calc_summary_stat(newpars,model,data,opt)

        # get the old summary statistic
        if firstrun:
            oldsstat = newsstat
        else:
            oldsstat = posterior.accepted_stats[posterior.i_acc -1]

        # if the results are close enough, save to accepted parameters (reject otherwise)
        posterior.accept_and_save(opt,[oldpars, newpars],[oldsstat, newsstat],firstrun)

        nacc = posterior.get_num_accepted()
        print(str(nacc))