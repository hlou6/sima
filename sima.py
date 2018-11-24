#
# A SIMPLE APPROXIMATE BAYESIAN COMPUTATION PROGRAM
#
# Henri Loukusa, Nov 2018
#




# general modules
from multiprocessing import Process, Lock, Manager
from multiprocessing.managers import BaseManager
import multiprocessing

# other modules of the program
from sima_classes import *
from sima_IO import *
from sima_stats import *

# input script
from sima_input import *

#
# THE MAIN FUNCTION
#

def sample_from_posterior(model,priors,posterior,data,batchruns,limit,lock):

    for run in range(batchruns):
        # sample the priors to get new parameters
        newpars = get_params(model,priors)

        # calculate the summary statistic for the new parameters compared to observed data
        sstat = calc_summary_stat(newpars,model,data,"sq_residual")

        # if the results are close enough, save to accepted parameters (reject otherwise)
        lock.acquire()
        posterior.accept_and_save(limit,newpars,sstat)
        lock.release()

        nall = posterior.get_num_all()
        print(str(nall))

if __name__ == "__main__":

    t0 = calc_running_time(0,"begin")

    # input parameters of the algorithm
    nruns = 100000
    nprocesses = 4
    limit = 0.01
    datafilename = "test.txt"

    # load the problem definition
    data = load_observed_data()
    priors = load_priors()
    model = load_generative_model()

    # make a shared Posterior class instance
    BaseManager.register('Posterior',Posterior)
    manager = BaseManager()
    manager.start()
    posterior = manager.Posterior(nruns)

    (pc,pcr) = print_progress("begin",0,0,0)

    # generate samples in parallel
    lock = Lock()
    batchruns = int(nruns/nprocesses)
    procs = []
    for pr in range(nprocesses):
        procs.append(Process(target=sample_from_posterior, args=(model,priors,posterior,data,batchruns,limit,lock)))
        procs[pr].start()
    for pr in range(nprocesses):
        procs[pr].join()

    # get the data out from the managered posterior class
    posterior = posterior.get_data(nruns)

    # print to stdout
    print_progress("finish",0,0,0)
    print_param_stats(posterior,model)
    calc_running_time(t0,"end")

    # write results to file
    write_posterior_params(posterior,datafilename)



