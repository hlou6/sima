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

#
# THE MAIN FUNCTION
#



if __name__ == "__main__":

    t0 = calc_running_time(0,"begin")

    # load the problem definition
    (model, data,priors,options) = read_input("sima.inp")

    #
    # begin sampling
    #
    (pc,pcr) = print_progress("begin",0,0,0)

    # select sampling method
    if options.sampling_method == "rejection_sampling":
        # generate samples in parallel for rejection sampling

        # make a shared Posterior class instance
        BaseManager.register('Posterior',Posterior)
        manager = BaseManager()
        manager.start()
        posterior = manager.Posterior(options.get_num_samples())

        lock = Lock()
        procs = []
        for pr in range(options.get_num_processes()):
            procs.append(Process(target=sample_from_posterior_rejection_sampling, args=(model,priors,posterior,data,options,lock)))
            procs[pr].start()
        for pr in range(options.get_num_processes()):
            procs[pr].join()

        # get the data out from the managered posterior class for use with other functions
        posterior = posterior.get_data(options.get_num_samples())

    elif options.sampling_method == "mcmc":
        lock = 0
        posterior = Posterior(options.get_num_samples())
        sample_from_posterior_mcmc(model,priors,posterior,data,options,lock)
        posterior.remove_burn_in(options)

        print("Accepted " + str(100.0*posterior.i_acc/posterior.i_all) + " % samples.")

    else:
        print("Error: unknown sampling method " + str(options.sampling_method))
    #
    # end sampling
    #
    

    # print to stdout
    print_progress("finish",0,0,0)
    print_param_stats(posterior,model)
    calc_running_time(t0,"end")

    # write results to file
    write_posterior_params(posterior,options)



