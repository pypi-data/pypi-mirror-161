# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

import matplotlib
#matplotlib.use('TkAgg')
#start all your IPython kernels in inline mode by default by setting the following config options in your config files:
#IPKernelApp.matplotlib=<CaselessStrEnum>
#  Default: None
#  Choices: ['auto', 'gtk', 'gtk3', 'inline', 'nbagg', 'notebook', 'osx', 'qt', 'qt4', 'qt5', 'tk', 'wx']
#  Configure matplotlib for interactive use with the default matplotlib backend.

import matplotlib.pyplot as plt
from typing import List
from noloadj.optimization.iterationHandler import Solution, Iterations
from noloadj.optimization.specifications import Spec
import numpy as np
from noloadj.optimization.Tools import StructList

class DynamicUpdate():

    def __init__(self, spec:Spec):
        plt.ion()  # Turn the interactive mode on.
        self.spec = spec
        self.nbI=len(spec.iNames)
        self.nbO=len(spec.oNames)
        maxVarPlot = 3
        self.nbI = min(maxVarPlot, self.nbI)#TODO faire quelque chose
        # pour afficher proprement plus de 10 variables
        self.nbO = min(maxVarPlot, self.nbO)
        self.lines = [None for _ in range(self.nbI+self.nbO)]
        #Set up plot
        self.figure, self.axes = plt.subplots(self.nbI+self.nbO, 1, sharex=True)
        #TODO faire un subplot avec 2 figures pour séparer inputs and outputs
        plt.xlabel('iterations')
        for i in range(1, self.nbI+1):
            self.lines[i], = self.axes[i].plot([],[],'o')
            self.axes[i].set_ylabel(spec.iNames[i])
            #Autoscale on unknown axis and known lims on the other
            self.axes[i].set_autoscaley_on(True)
            #Other stuff
            self.axes[i].grid()
        for i in range(1, self.nbO+1):
            self.lines[self.nbI+i], = self.axes[self.nbI+i].plot([],[],'o')
            self.axes[self.nbI+i].set_ylabel(spec.oNames[i])
            #Autoscale on unknown axis and known lims on the other
            self.axes[self.nbI+i].set_autoscaley_on(True)
            #Other stuff
            self.axes[self.nbI+i].grid()

    def update(self, sol:List[Solution]):
        """
        Adds the solution given in inputs to the graph.
        :param sol: Solution to add to the graph
        :return: /
        """
        xdata = range(len(sol))
        for i in range(self.nbI):
            #Update data (with the new _and_ the old points)
            self.lines[i].set_xdata(xdata)
            self.lines[i].set_ydata([s.iData[i] for s in sol])
            #affiche les entrées
            #Need both of these in order to rescale
            self.axes[i].relim()
            self.axes[i].autoscale_view()
            #We need to draw *and* flush

        for i in range(self.nbO):
            #Update data (with the new _and_ the old points)
            self.lines[self.nbI+i].set_xdata(xdata)
            self.lines[self.nbI+i].set_ydata([s.oData[i] for s in sol])
            #affiche les sorties
            #Need both of these in order to rescale
            self.axes[self.nbI+i].relim()
            self.axes[self.nbI+i].autoscale_view()
            #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def finalize(self):
        """
        Shows the graph.
        :return: /
        """
        plt.show(block=True)

    def __del__(self):      #ça ne fonctionne pas
        plt.show(block=True)

def show():
    """
    Shows the graph.
    :return: /
    """
    plt.show(block=True)

def plotIO(iter:Iterations,spec:Spec,outputs_names):
    """
    Builds a graph displaying the inputs and outputs of the model.
    :param iter: class Iterations including inputs and outputs (for each
    iteration).
    :param spec: the specifications of the optimization problem
    :param outputs_names: list of outputs names the user wants to plot
    :return: /
    """
    plot("Input optimization convergence", spec, iter.iNames,
         range(1, len(iter.solutions)+1), [sol.iData for sol in iter.solutions])
    sol2=list(np.transpose(np.array([sol.oData for sol in iter.solutions],dtype=object)))
    sol3=[]
    for i in range(len(outputs_names)):
        ind=np.where(iter.oNames==outputs_names[i])[0][0]
        sol3.append(sol2[ind])
    solution=list(np.transpose(sol3))
    plot("Output optimization convergence", spec, outputs_names,
         range(1, len(iter.solutions)+1), solution)
    plt.show()

def plot(title,spec, names,x,y):
    """
    Builds a graph displaying two axes x and y.
    :param title: title of the graph
    :param names: names of axes x and y
    :param x: values on axe x
    :param y: values on axe y
    :return: /
    """
    ind,longueur=[],[]
    for i in range(len(y)): # vectoriel
        if isinstance(y[i],(np.ndarray,list)):
            for j in range(len(y[i])):
                if isinstance(y[i][j],(np.ndarray,list)):
                    if i==0:
                        ind.append(j)
                        longueur.append(len(y[i][j]))
                    y1=StructList(y[i],'unflattened')
                    y[i]=y1.flatten()

    if ind!=[] and longueur!=[]:  # vectoriel
        for i in range(len(ind)):
            nom=names[ind[i]]
            del names[ind[i]]
            for j in range(longueur[i]):
                names.insert(ind[i]+j,nom+'_'+str(j))

    nb=len(names)
    for i in range(nb):
        ytemp=[row[i] for row in y]
        plt.figure()
        plt.title(title+' of '+names[i])
        plt.scatter(x,ytemp)
        plt.xlabel('iterations')
        plt.ylabel(names[i])
        if names[i] in spec.iNames:
            ind=spec.iNames.index(names[i])
            bounds=spec.bounds[ind]
            plt.plot(x,len(x)*[bounds[0]],'orange')
            plt.plot(x,len(x)*[bounds[1]],'orange')
        elif names[i][:len(names[i])-2] in spec.iNames: #entree vectorielle
            ind=spec.iNames.index(names[i][:len(names[i])-2])
            bounds=spec.bounds[ind]
            num = int(names[i][-1])
            plt.plot(x,len(x)*[bounds[num][0]],'orange')
            plt.plot(x,len(x)*[bounds[num][1]],'orange')
        if names[i] in spec.ineq_cstr:
            ind=spec.ineq_cstr.index(names[i])
            bounds=spec.ineq_cstr_bnd.List[ind]
            if bounds[0]!=None:
                plt.plot(x,len(x)*[bounds[0]],'orange')
            if bounds[1]!=None:
                plt.plot(x,len(x)*[bounds[1]],'orange')
        elif names[i][:len(names[i])-2] in spec.ineq_cstr: # contrainte
            # inegalite vectorielle
            ind=spec.ineq_cstr.index(names[i][:len(names[i])-2])
            bounds=spec.ineq_cstr_bnd.List[ind]
            num=int(names[i][-1])
            if bounds[num][0]!=None:
                plt.plot(x,len(x)*[bounds[num][0]],'orange')
            if bounds[num][1]!=None:
                plt.plot(x,len(x)*[bounds[num][1]],'orange')
        plt.grid()

    plt.show(block=False)


def plotXY(iter:Iterations, title = "X-Y Plot"):
    """
    Builds a graph displaying the inputs and outputs of the model, of the
    form "X-Y Plot".
    :param iter: class Iterations including inputs and outputs (for each
    iteration).
    :param title: title of the graph
    :return: /
    """
    #iter.iNames, , [sol.iData for sol in iter.solutions])
    x = [sol.iData for sol in iter.solutions]
    y = [sol.oData for sol in iter.solutions]

    nb=len(iter.oNames)
    maxVarPlot=5
    nb = min(maxVarPlot, nb)# TODO faire quelque chose pour afficher proprement
    # plus de 5 sorties.
    lines = [None for _ in range(nb)]
    figure, axes = plt.subplots(nb, 1, sharex=True)
    figure.suptitle(title)
    plt.xlabel(iter.iNames[0])
    if nb>1 :
        for i in range(nb):
            lines[i], = axes[i].plot(x,[row[i] for row in y],'o-')
            axes[i].set_ylabel(iter.oNames[i])
            #Autoscale on unknown axis and known lims on the other
            axes[i].set_autoscaley_on(True)
            #Other stuff
            axes[i].grid()
    else:
        lines = axes.plot(x, [row[0] for row in y], 'o-')
        axes.set_ylabel(iter.oNames[0])
        # Autoscale on unknown axis and known lims on the other
        axes.set_autoscaley_on(True)
        # Other stuff
        axes.grid()

    plt.show()

