#
# Functions for input and output
#

import time

from sima_classes import *
from sima_input import *


#
# INPUT FUNCTIONS
#

# currently only wrappers for the test data in sima_input module

def load_observed_data():

    data =  get_test_data()

    return data

def load_priors():

    priors = get_test_priors()

    return priors

def load_generative_model():

    model = get_test_model()

    return model


#
# OUTPUT FUNCTIONS
#

#
# Function to write the posterior samples to file
#
def write_posterior_params(posterior,datafilename):

    print("Writing the parameters sampled from the posterior to file " + datafilename + "...")

    datafile = open(datafilename,"w")
    for parset in posterior.accepted_params:
        if(parset!= []):
            for par in parset:
                datafile.write(str(par) + " ")
            datafile.write("\n")
    datafile.close()

    print("Done.\n\n")

#
# Function to print out the progress during generation of samples
#
def print_progress(option,nruns,run,pc):

    if option == "begin":
        print("Generating samples from posterior... ")
        pc = 0
        pcr = 0
        return (pc,pcr)
    elif option == "calc":
        pcr = math.ceil(0.1*pc)*10.0
        pc = 100.0*run/nruns
        if pcr < pc:
            print(str(pcr) + "%")
        return (pc,pcr)
    elif option == "finish":
        print("Finished.\n\n")
        return 0


#
# Function to print out the statistics calculated for the model parameters
#
def print_param_stats(posterior,model):
    
    npars = model.num_params()

    # header line
    headerstr = "{0:10s} ".format("param")
    for par in model.params:
        headerstr += " | {0:10s} ".format(par)
    
    # means line
    meanstr = "{0:10s} ".format("mean")
    means = posterior.mean()
    for val in means:
        meanstr += " | {0:10.3f} ".format(val)

    # standard deviations line
    stddevstr = "{0:10s} ".format("stdev")
    stddevs = posterior.stddev()
    for val in stddevs:
        stddevstr += " | {0:10.3f} ".format(val)

    # line of dashes
    dashstr = ""
    for dash in range((npars+1)*13):
        dashstr += "-"

    print(dashstr)
    print(headerstr)
    print(dashstr)
    print(meanstr)
    print(stddevstr)
    print(dashstr)
    print("\n")


#
# Function to calculate and print out the running time
#
def calc_running_time(t0,option):

    if option == "begin":
        t0 = time.time()
        return t0

    elif option =="end":
        tf = time.time()
        mins = int((tf - t0) / 60)
        secs = int(tf - t0 - 60 * mins)

        print("Sampling took " + str(mins) + " minutes and " + str(secs) + "seconds.\n")
        return 0

    else:
        print("Error: unknown option at calc_running_time(): " + str(option))
        return 0

