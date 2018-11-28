
#
# DEFINITIONS OF CLASSES FOR THE SIMPLE ABC PROGRAM
#

# Defines the following classes:
#
#   - class SimaOptions:        options of the program
#   - class ObservedData:       for the observations of data points
#   - class Prior:              for the priors used in the ABC algorithm
#   - class GenerativeModel:    the model for the data, including its form and 
#   - class Posterior:          for the posterior distribution, collection of samples and calculation of statistics,
#                               as the Posterior class is used in parallel through the multiprocessing.Manager class,
#                               required members must be accessible through class functions

import math
from random import random as rand

class SimaOptions:

    def __init__(self):
        self.sampling_method = ""
        self.summary_statistic = ""
        self.rejection_sampling_acceptance_limit = 0
        self.burn_in = 1000
        self.mcmc_proposal_width_rel = 0
        self.mcmc_proposal_width_min = 0
        self.num_samples = 0
        self.num_processes = 0
        self.batch_samples = 0
        self.datafilename = ""

    def get_burn_in(self):
        return self.burn_in

    def set_burn_in(self,bi):
        self.burn_in = bi

    def set_proposal_width_rel(self,width):
        self.mcmc_proposal_width_rel = width

    def get_proposal_width_rel(self):
        return self.mcmc_proposal_width_rel

    def set_proposal_width_min(self,width):
        self.mcmc_proposal_width_min = width

    def get_proposal_width_min(self):
        return self.mcmc_proposal_width_min

    def set_data_file_name(self,name):
        self.datafilename = name

    def get_data_file_name(self):
        return self.datafilename

    def set_num_samples_processes(self,nsamples,nprocesses):
        self.num_samples = nsamples + self.burn_in
        self.num_processes = nprocesses
        bsampl = int(nsamples/nprocesses)
        if abs(nsamples/nprocesses - float(bsampl)) < 1e-20:
            self.batch_samples = bsampl
        else:
            print("Error: number of samples is not divisible by number of processes. The desired number of samples will not be calculated.")
            self.batch_samples = bsampl

    def get_num_samples(self):
        return self.num_samples

    def get_num_processes(self):
        return self.num_processes

    def get_batch_samples(self):
        return self.batch_samples

    def set_sampling_method(self,method):
        self.sampling_method = method

    def get_sampling_method(self):
        return self.sampling_method

    def set_summary_statistic(self,stat):
        self.summary_statistic = stat

    def get_summary_statistic(self):
        return self.summary_statistic

    def set_rs_limit(self,limit):
        self.rejection_sampling_acceptance_limit = limit

    def get_rs_limit(self):
        return self.rejection_sampling_acceptance_limit

class ObservedData:
    def __init__(self):
        self.vars = []
        self.res = []

    def num_vars(self):
        return len(self.var)

    def len_data(self):
        return len(self.res)

class Prior:
    def __init__(self):
        self.type = []
        self.params = []

class GenerativeModel:

    def __init__(self):
        self.params = []
        self.vars = []
        self.res = []
        self.par_distr_type = []
        self.par_distr_params = []
        self.fun = []
        self.funexpr = []

    def num_params(self):
        return len(self.params)

    def num_vars(self):
        return len(self.vars)

    def check_par_len(self,priors):
        if(len(self.params) != len(priors.params)):
            print("Error: length of model.params is different from prior.params")
            return 0
        if(len(priors.type) != len(priors.params)):
            print("Error: length of prior.params is different from prior.type")
            return 0
        return 1

    # setter for the model, transforms the function automatically to executable form
    def set_fun(self,expr):
        self.fun = expr
        self.funexpr_transform()

    # transforms the model in self.fun to a form usable with exec(), calcd value in result variable
    def funexpr_transform(self):
        funexpr = "result = " + str(self.fun)
        for i in range(len(self.params)):
            parstr = "params[" + str(i) + "]"
            funexpr = funexpr.replace(self.params[i],parstr)
        for i in range(len(self.vars)):
            varstr = "vars[" + str(i) + "]"
            funexpr = funexpr.replace(self.vars[i],varstr)

        self.funexpr = funexpr

    # calculates a value with the model in self.fun (actually the transformed one in self.funexpr)
    def calc_result(self,params, vars):
        ldict = {}
        exec(self.funexpr,locals(),ldict)
        return ldict['result']

class Posterior:

    def __init__(self,len):
        self.accepted_params = [[] for x in range(len)]
        self.accepted_stats = [[] for x in range(len)]
        self.i_acc = 0
        self.all_params = [[] for x in range(len)]
        self.all_stats = [[] for x in range(len)]
        self.i_all = 0

    def accept_and_save(self,options,params,stat,firstrun):

        if options.sampling_method == "rejection_sampling":
            # rejection sampling, assume that we have a single statistic
            # length of stat = 1
            if (stat < options.rejection_sampling_acceptance_limit):
                self.save_rs_accept(params,stat)
            else:
                self.save_rs_reject(params,stat)

        elif options.sampling_method == "mcmc":
            # markov chain monte carlo, assume we have two statistics
            
            if firstrun:
                # on first run, accept always
                self.save_mcmc_accept(params[0],stat[0])
            else:
                # otherwise, check acceptance

                # extract new and old params and stats
                oldpars = params[0]
                newpars = params[1]
                oldstat = stat[0]
                newstat = stat[1]

                # calculate acceptance ratio, defined this way alpha > 1 has smaller summary statistic for new params
                alpha = oldstat/newstat

                if (alpha >= 1) :
                    # accept always if alpha >= 1
                    self.save_mcmc_accept(newpars,newstat)
                else:
                    # accept with the probability (1 - alpha) (should be alpha?)
                    rnum = rand()
                    if rnum > alpha: # why this works this way??? related to the definition of the acceptance ratio, but how
                        self.save_mcmc_accept(newpars,newstat)
                    else:
                        self.save_mcmc_reject()

    def save_mcmc_accept(self,params,stat):
        if(params!=[]):
            self.accepted_params[self.i_acc] = params
            self.accepted_stats[self.i_acc] = stat
            self.i_acc += 1
            self.i_all += 1
        else:
            print("Error: Length of params is 0.")

    def save_mcmc_reject(self):
        self.i_all += 1

    def save_rs_accept(self,params,stat):
        if(params!=[]):
            self.accepted_params[self.i_acc] = params
            self.all_params[self.i_all] = params
            self.accepted_stats[self.i_acc] = stat
            self.all_stats[self.i_all] = stat
            self.i_acc += 1
            self.i_all += 1
        else:
            print("Error: Length of params is 0.")
    
    def save_rs_reject(self,params,stat):
        if(params!=[]):
            self.all_params[self.i_all] = params
            self.all_stats[self.i_all] = stat
            self.i_all += 1
        else:
            print("Error: Length of params is 0.")

    def remove_burn_in(self, opt):
        bip = opt.get_burn_in()
        nacc = self.get_num_accepted()

        self.accepted_params = self.accepted_params[bip:nacc]
        self.accepted_stats = self.accepted_stats[bip:nacc]
        self.i_acc -= bip
        self.all_params = self.all_params[bip:nacc]
        self.all_stats = self.all_stats[bip:nacc]
        self.i_all -= bip

    # Copies the data of the posterior class to another instance, used to get the data out after parallel processing
    def get_data(self,nruns):
        posterior = Posterior(nruns)
        posterior.accepted_params = self.accepted_params
        posterior.all_params = self.all_params
        posterior.accepted_stats = self.accepted_stats
        posterior.all_stats = self.all_stats
        posterior.i_acc = self.i_acc
        posterior.i_all = self.i_all
        return posterior

    def get_num_accepted(self):
        return self.i_acc

    def get_num_all(self):
        return self.i_all

    def mean(self):
        if(self.accepted_params != []):
            npars = len(self.accepted_params[0])
            nacc = self.i_acc

            if nacc != 0:
                parmeans = [0 for x in range(npars)]
                for i in range(nacc):
                    for parid in range(npars):
                        parmeans[parid] += self.accepted_params[i][parid]

                for parid in range(npars):
                    parmeans[parid] = parmeans[parid]/nacc

                return parmeans
            else:
                return []

        else:
            return []

    def stddev(self):
        if(self.accepted_params != []):
            npars = len(self.accepted_params[0])
            nacc = self.i_acc

            if nacc != 0:
                xsum = [0 for x in range(npars)]
                x2sum = [0 for x in range(npars)]
                for i in range(nacc):
                    for parid in range(npars):
                        xsum[parid] += self.accepted_params[i][parid]
                        x2sum[parid] += self.accepted_params[i][parid]*self.accepted_params[i][parid]

                parstddevs = [0 for x in range(npars)]
                for parid in range(npars):
                    term = (1.0/(nacc-1.0))*(x2sum[parid] - (1.0/nacc)*xsum[parid]*xsum[parid])
                    parstddevs[parid] = math.sqrt(term)

                return parstddevs
            else:
                return []
        else:
            return []