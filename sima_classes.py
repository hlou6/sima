
#
# DEFINITIONS OF CLASSES FOR THE SIMPLE ABC PROGRAM
#

# Defines the following classes:
#
#   - class ObservedData:       for the observations of data points
#   - class Prior:              for the priors used in the ABC algorithm
#   - class GenerativeModel:    the model for the data, including its form and 
#   - class Posterior:          for the posterior distribution, collection of samples and calculation of statistics,
#                               as the Posterior class is used in parallel through the multiprocessing.Manager class,
#                               required members must be accessible through class functions

import math


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

    def accept_and_save(self,limit,params,stat):
        if (stat < limit):
            if(params!=[]):
                self.accepted_params[self.i_acc] = params
                self.all_params[self.i_all] = params
                self.accepted_stats[self.i_acc] = stat
                self.all_stats[self.i_all] = stat
                self.i_acc += 1
                self.i_all += 1
            else:
                print("Error: Length of params is 0.")
        else:
            if(params!=[]):
                self.all_params[self.i_all] = params
                self.all_stats[self.i_all] = stat
                self.i_all += 1
            else:
                print("Error: Length of params is 0.")

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
            npars = len(self.all_params[0])
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
            npars = len(self.all_params[0])
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
                    parstddevs[parid] = math.sqrt((1.0/(nacc-1.0))*(x2sum[parid] - (1.0/nacc)*xsum[parid]*xsum[parid]))

                return parstddevs
            else:
                return []
        else:
            return []