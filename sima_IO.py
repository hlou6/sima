#
# Functions for input and output
#

import time

from sima_classes import *


#
# INPUT FUNCTIONS
#

def read_input(filename):

    model = GenerativeModel()
    priors = Prior()
    data = ObservedData()
    options = SimaOptions()

    ifile = open(filename,"r")
    lines = ifile.readlines()
    lines = [x.strip() for x in lines] 

    model_defined = False

    il = 0
    ilen = len(lines)
    while il < ilen:
        line = lines[il]
        if model_defined:
            if line_not_comment(line):
                if line.find("priors:") != -1:

                    priors.type = ["" for x in range(model.num_params())]
                    priors.params = ["" for x in range(model.num_params())]

                    il += 1
                    line = lines[il]
                    while line.find("end priors") == -1:
                        if line_not_comment(line):
                            priors = read_priors_definition(line,priors,model)
                            il += 1
                        else:
                            il += 1
                        line = lines[il]
                elif line.find("observed data:") != -1:

                    data.vars = ["" for x in range(model.num_vars())]

                    il += 1
                    line = lines[il]
                    while line.find("end observed data") == -1:
                        if line_not_comment(line):
                            data = read_observed_data(line,data,model)
                            il += 1
                        else:
                            il += 1
                        line = lines[il]

                    # now the data.vars is in wrong format, change into correct one
                    datavars = []
                    for ivar in range(len(data.vars[0])):
                        instance = []
                        for par in range(model.num_vars()):
                            instance.append(data.vars[par][ivar])
                        datavars.append(instance)
                    data.vars = datavars

                elif(line.find("options:") != -1):
                    il += 1
                    line = lines[il]
                    while line.find("end options") == -1:
                        if line_not_comment(line):
                            options = read_options(line,options)
                            il += 1
                        else:
                            il += 1
                        line = lines[il]

                else: 
                    keyword = line.split(" ")
                    keyword = keyword[0]
                    print("Unknown keyword " + str(keyword) + " in in input file line "+ str(il+1) + ".")

        else:
            if line_not_comment(line):
                if line.find("model:") != -1:
                    il += 1
                    line = lines[il]
                    while line.find("end model") == -1:
                        if line_not_comment(line):
                            model = read_model_definition(line,model)
                            il += 1
                        else:
                            il += 1
                        line = lines[il]

                    model_defined = True
                else:
                    print("Error: generative model must be defined first with the block model.")
        il += 1


    ifile.close()

    return (model, data, priors, options)


#
# Function reads an option definition line and saves it appropriately
#
def read_options(line,options):

    if(line.find("num_samples") != -1):
        npr = options.get_num_processes()
        options.set_num_samples_processes(int(get_one_value(line)),npr)
    elif(line.find("num_processes") != -1):
        nsam = options.get_num_samples()
        options.set_num_samples_processes(nsam,int(get_one_value(line)))
    elif(line.find("sampling_method") != -1):
        options.set_sampling_method(get_one_value(line))
    elif(line.find("summary_statistic") != -1):
        options.set_summary_statistic(get_one_value(line))
    elif(line.find("output_file") != -1):
        options.set_data_file_name(get_one_value(line))
    elif(line.find("proposal_width_relative") != -1):
        options.set_proposal_width_rel(float(get_one_value(line)))
    elif(line.find("proposal_width_minimum") != -1):
        options.set_proposal_width_min(float(get_one_value(line)))
    elif(line.find("burn_in") != -1):
        options.set_burn_in(int(get_one_value(line)))
    elif(line.find("rejection_sampling_tolerance") != -1):
        options.set_rs_limit(float(get_one_value(line)))
    else:
        keyword = line.split(" ")
        keyword = keyword[0]
        print("Unknown keyword " + str(keyword) + " in options definition.")

    return options

#
# Function reads a model definition line and saves it appropriately
#
def read_model_definition(line,model):
    
    if(line.find("params") != -1):
        line = exclude_keyword(line)
        for param in line:
            model.params.append(param)
    elif(line.find("independents") != -1):
        line = exclude_keyword(line)
        for ind in line:
            model.res.append(ind)
    elif(line.find("dependents") != -1):
        line = exclude_keyword(line)
        for dep in line:
            model.vars.append(dep)
    elif(line.find("function") != -1):
        line = line.replace("function ","")
        model.set_fun(line)
    else:
        keyword = line.split(" ")
        keyword = keyword[0]
        print("Unknown keyword " + str(keyword) + " in model definition.")

    return model

#
# Function reads a prior distribution definition and saves it appropriately
#
def read_priors_definition(line,priors,model):

    prd = line.split(" ")

    var = prd[0]
    distr = prd[1]
    lo = float(prd[2])
    hi = float(prd[3])
    params = [lo, hi]

    ipar = 0
    for param in model.params:
        if param == var:
            break
        else:
            ipar += 1

    priors.params[ipar] = params
    priors.type[ipar] = distr

    return priors

#
# Function reads a line of observed data and saves it appropriately
#
def read_observed_data(line,data,model):

    is_var = False

    vardata = line.split(" ")

    var = vardata[0]
    values = [float(x) for x in vardata[1:]]

    ipar = 0
    for param in model.vars:
        if param == var:
            is_var = True
            break
        else:
            ipar += 1

    if is_var:
        data.vars[ipar] = values
    else:
        data.res = values

    return data

#   
# Function excludes the keyword from an input line
#
def exclude_keyword(line):
    line = line.split(" ")
    line = line[1:]
    return line

def get_one_value(line):
    line = line.split(" ")
    return line[1]

#
# Function to find out if the line is not a comment, comments are marked with # and 
# empty lines or lines beginning with space are taken as comments
#
def line_not_comment(line):
    if (len(line) > 0):
        if (line[0] == "#") | (line[0] == " "):
            return False
        else:
            return True
    else:
        return False



#
# OUTPUT FUNCTIONS
#

#
# Function to write the posterior samples to file
#
def write_posterior_params(posterior,options):

    datafilename = options.get_data_file_name()

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

        print("Sampling took " + str(mins) + " minutes and " + str(secs) + " seconds.\n")
        return 0

    else:
        print("Error: unknown option at calc_running_time(): " + str(option))
        return 0

