# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

__author__ = "B.Delinchant / G2ELab"

# Using JAX : Rules
#     For assignment to arrays, use JAX pure fonctional operators instead
#     of A[0] = x : https://jax.readthedocs.io/en/latest/jax.ops.html.
#     Do not put a JAX array in a numpy method, and do not put a numpy array
#     in a JAX method.
#     Assignements on dataframe (from pandas library) do not work with
#     JAX array.
#     "if" structure does not work with JIT functionnality, use cond function
#     from jax.lax package :
#     https://jax.readthedocs.io/en/latest/jax.lax.html#control-flow-operators
#     Implicit casting of lists to arrays A = np.sum([x, y]), use
#     A = np.sum(np.array([x, y])) instead.

#https://en.wikipedia.org/wiki/Test_functions_for_optimization

import jax.numpy as np
import math
def ackley(x,y):
    fobj = -20 * np.exp(-0.2 * np.sqrt(0.5 * (np.square(x) + np.square(y)))) -\
           np.exp(0.5 * (np.cos(2 * math.pi * x) + np.cos(2 * math.pi * y))) +\
           math.exp(1) + 20
    return locals().items()

def rosenbrock(x,y):
    fobj = pow(1- x,2) + 100.0*pow(y - x*x,2)
    return locals().items()

model = ackley
#model = rosenbrock

from noloadj.tutorial.plotTools import plot3D
plot3D(model, [[-5,5],[-5,5]])

#Optimize
from noloadj.optimization.optimProblem import Spec, OptimProblem
#This function is non derivable in [0,0] that can lead to convergence issue.
#Initial guess must be different from [0,0]
spec = Spec(variables={'x':2, 'y':2}, bounds={'x':[-5, 5], 'y':[-5, 5]},
            objectives=['fobj'])
optim = OptimProblem(model=model, specifications=spec)
result = optim.run()

result.printResults()
result.plotResults(['fobj'])

#It is also possible to iterate by yourself to get results
for name, value in result.getLastInputs().items():
    print(name, '  \t =', value)
for name, value in result.getLastOutputs().items():
    print(name, '  \t =', value)
