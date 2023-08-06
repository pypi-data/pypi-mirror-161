# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

from noloadj.optimization.iterationHandler import Iterations
from typing import Callable, Dict, List, Any

'''computes model with the inputs dictionnary, and give the value of output 
variables'''
def computeOnce(model: Callable[..., Dict], inputs: Dict[str, Any],
                outputs: List[str]):
    """
    Computes the outputs of the model according to the values of the given
    input variables.
    :param model: model
    :param inputs: names and values of input variables (dictionary)
    :param outputs: names of output variables (list)
    :return: values of the outputs (list)
    """
    res = model(**inputs)
    dico = {k: v for k, v in res.__iter__()}  # conversion en dictionnaire
    out = [float(dico[vars]) for vars in outputs]     #TODO attraper une
    # exception si la variable n'appartient pas aux sorties du modèle
    # sauvegarde et tracé des résultats uniquement si appel à la fonction et
    # non au gradient
    return out

#TODO : Harmoniser les résultats avec ceux d'une optimisation pour le tracé
# des itérations
'''computes model with the inputs dictionnary and a variable input varying in 
a range, and give the value of output variables'''
def computeParametric(model: Callable[..., Dict], variable: str,
                      range: List[float], inputs: Dict[str, Any],
                      outputs: List[str]):
    """
    Computes the outputs of the model corresponding to the values of the given
    input variables, except one varying in a range of values.
    :param model: model
    :param variable: the input that varies
    :param range: range of values in which the input varies
    :param inputs: names and values of constant input variables (dictionary)
    :param outputs: names of output variables (list)
    :return: values of the outputs (list)
    """
    iter = Iterations([variable], outputs)  # permet de sauvegarder les
    # résultats au fur et à mesure (optionnel)
    for x in range:
        if inputs!=[]:
            res = model(**{variable: x}, **inputs)
        else:
            res = model(*x) # in case of model with only 1 argument
        dico = {k: v for k, v in res.__iter__()}  # conversion en dictionnaire
        out = [dico[vars] for vars in outputs]     #TODO attraper une
        # exception si la variable n'appartient pas aux sorties du modèle
        # sauvegarde et tracé des résultats uniquement si appel à la fonction
        # et non au gradient
        iter.updateData([x], out)
    return iter


from noloadj.optimization.wrapper import Wrapper, Spec
import numpy

def computeJacobian(model: Callable[..., Dict], inputs: Dict[str, Any],
                      objectives: List[str], eq_cstr=[], ineq_cstr=[],
                    parameters={}):
    """
    Displays the values and gradients of outputs corresponding to the values of
    the given inputs.
    :param model: model
    :param inputs: names and values of constant input variables (dictionary)
    :param objectives: names of the objective function(s) (list)
    :param eq_cstr: names of the equality constraints (list)
    :param ineq_cstr: names of the inequality constraints (list)
    :param parameters: free parameters of the optimization problem.
    :return: /
    """
    x0=numpy.array(list(inputs.values()))
    spec = Spec(dict(zip(list(inputs.keys()),
            [None for e in list(inputs.keys())])), {}, objectives=objectives,
                eq_cstr=dict(zip(eq_cstr,[None for e in eq_cstr])),
                ineq_cstr=dict(zip(ineq_cstr,[None for e in ineq_cstr])))
    w = Wrapper(model, spec, parameters)
    print('f_val :',w.f_val(x0))
    print('f_grad :',w.f_grad(x0))
    if spec.eq_cstr!=[]:
        print('eq_cstr_val :',w.eq_cstr_val(x0))
        print('eq_cstr_grad :',w.eq_cstr_grad(x0))
    if spec.ineq_cstr!=[]:
        print('ineq_cstr_val :',w.ineq_cstr_val(x0))
        print('ineq_cstr_grad :',w.ineq_cstr_grad(x0))