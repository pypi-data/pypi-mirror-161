# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

__author__ = "B.Delinchant / G2ELab"

# Using JAX : Rules
#     For assignment to arrays, use JAX pure fonctional operators instead of
#     A[0] = x : https://jax.readthedocs.io/en/latest/jax.ops.html.
#     Do not put a JAX array in a numpy method, and do not put a numpy array
#     in a JAX method.
#     Assignements on dataframe (from pandas library) do not work with JAX
#     array.
#     "if" structure does not work with JIT functionnality, use cond function
#     from jax.lax package :
#     https://jax.readthedocs.io/en/latest/jax.lax.html#control-flow-operators
#     Implicit casting of lists to arrays A = np.sum([x, y]), use
#     A = np.sum(np.array([x, y])) instead.

#https://en.wikipedia.org/wiki/Test_functions_for_optimization

import jax.numpy as np
def simionescu(x, y, rr, rs, n):
    fobj = 0.1 * x * y
    ctr = x * x + y * y - np.power(rr + rs * np.cos(n * np.arctan(x / y)), 2)
    return locals().items()

from noloadj.tutorial.plotTools import plot3D
#plot3D(simionescu, [[-1.25,1.25],[-1.25,1.25]], outNames = ['fobj','ctr'],
# parameters = (1,0.2,8))


#Optimize
from noloadj.optimization.optimProblem import Spec, OptimProblem
#This function is non defined in [0,0], initial guess must be different
# from [0,0]
spec = Spec(variables={'x':0, 'y':1}, bounds={'x':[-1.25, 1.25],
        'y':[-1.25, 1.25]}, objectives=['fobj'], ineq_cstr={'ctr':[None, 0]}
            #inequality constraints
            )
optim = OptimProblem(model=simionescu, specifications=spec,
                     parameters={'rr':1, 'rs':0.2, 'n':8})
result = optim.run()

result.printResults()
result.plotResults(['fobj','ctr'])

#It is also possible to iterate by yourself to get results
for name, value in result.getLastInputs().items():
    print(name, '  \t =', value)
for name, value in result.getLastOutputs().items():
    print(name, '  \t =', value)
