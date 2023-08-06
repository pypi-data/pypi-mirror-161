# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

__author__ = "B.Delinchant / G2ELab"

# Using JAX : Rules
#     For assignment to arrays, use JAX pure fonctional operators instead
#     of A[0] = x : https://jax.readthedocs.io/en/latest/jax.ops.html.
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
def rosenbrock(x,y):
    fobj=(1-x)*(1-x)+100*(y-x*x)**2
    ctr1=(x-1)**3-y+1
    ctr2=x+y-2
    return locals().items()

from noloadj.tutorial.plotTools import plot3D
#plot3D(rosenbrock, [[-1.25,1.25],[-0.5,2.5]], outNames = ['fobj','ctr1','ctr2'])


# Optimize with one equality constraint and an inequality one
from noloadj.optimization.optimProblem import Spec, OptimProblem


spec = Spec(variables={'x':2.0, 'y':2.0},
            bounds={'x':[-1.5, 1.5],'y':[-0.5, 2.5]},
            objectives=['fobj'], eq_cstr={'ctr1':0},
            ineq_cstr={'ctr2':[None, 0]})


optim = OptimProblem(model=rosenbrock, specifications=spec)
result = optim.run()

result.printResults()
result.plotResults(['fobj','ctr1','ctr2'])

#It is also possible to iterate by yourself to get results
for name, value in result.getLastInputs().items():
    print(name, '  \t =', value)
for name, value in result.getLastOutputs().items():
    print(name, '  \t =', value)


# Optimize with one equality constraint and the other one as FreeOutputs
spec = Spec(variables={'x':2.0, 'y':2.0},
            bounds={'x':[-1.5, 1.5],'y':[-0.5, 2.5]},
            objectives=['fobj'],
            eq_cstr={'ctr1': 0},freeOutputs=['ctr2'])

optim = OptimProblem(model=rosenbrock, specifications=spec)
result = optim.run()

result.printResults()
#result.plotResults(['fobj','ctr1'])

#############################
# Rosenbrock function with vectorial constraints
def rosenbrock(x,y):
    fobj=(1-x)*(1-x)+100*(y-x*x)**2
    ctr=[(x-1)**3-y+1 , x+y-2]
    return locals().items()

#Optimize with vectorial inequality constraints
spec = Spec(variables={'x':2.0, 'y':2.0},
            bounds={'x':[-1.5, 1.5],'y':[-0.5, 2.5]},
            objectives=['fobj'],
            ineq_cstr={'ctr':[[None, 0],[None, 0]]})

optim = OptimProblem(model=rosenbrock, specifications=spec)
result = optim.run()

result.printResults()
#result.plotResults(['fobj','ctr'])


#Optimize with vectorial equality constraints
spec = Spec(variables={'x':2.0, 'y':2.0},
            bounds={'x':[-1.5, 1.5],'y':[-0.5, 2.5]},
            objectives=['fobj'],
            eq_cstr={'ctr':[0,0]})

optim = OptimProblem(model=rosenbrock, specifications=spec)
result = optim.run()

result.printResults()
#result.plotResults(['fobj','ctr'])

#############################
# Rosenbrock function with vectorial constraints and inputs
def rosenbrock(X):
    x,y=X[0],X[1]
    fobj=(1-x)*(1-x)+100*(y-x*x)**2
    ctr=[(x-1)**3-y+1 , x+y-2]
    return locals().items()

#Optimize with vectorial inequality constraints
spec = Spec(variables={'X':[2.0,2.0]},
            bounds={'X':[[-1.5, 1.5],[-0.5, 2.5]]},
            objectives=['fobj'],
            ineq_cstr={'ctr':[[None, 0],[None, 0]]})

optim = OptimProblem(model=rosenbrock, specifications=spec)
result = optim.run()

result.printResults()
#result.plotResults(['fobj','ctr'])


