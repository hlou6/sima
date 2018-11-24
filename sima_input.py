
#
# In the absence of input files, this file can be used to define the problem.
#

from sima_classes import *


def get_test_data():

    testresults = [18.0, 24.5, 3.1, 48.3, 75.1, 104.4, 124.7, 27.7, 9.1, 17.4]
    testvar1 = [5, 6, 1, 4, 9, 11, 15, 2, 3, 2]
    testvar2 = [0.1, 0.2, 0.05, 0.9, 0.6, 0.7, 0.6, 1, 0.01, 0.5]
    testdata = ObservedData()
    for i in range(len(testvar1)):
        testdata.vars.append([testvar1[i], testvar2[i]])
    testdata.res = testresults

    return testdata

def get_test_model():

    testmodel = GenerativeModel()

    testmodel.params.append("a")
    testmodel.params.append("b")
    testmodel.params.append("c")

    testmodel.vars.append("x")
    testmodel.vars.append("y")

    testmodel.res.append("z")

    testmodel.set_fun("a*x + b*y + c*x*y")

    return testmodel

def get_test_priors():

    testpriors = Prior()

    testpriors.type.append("uniform")
    testpriors.params.append([1.0, 15.0])
    testpriors.type.append("uniform")
    testpriors.params.append([1.0, 15.0])
    testpriors.type.append("uniform")
    testpriors.params.append([1.0, 15.0])

    return testpriors