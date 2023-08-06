# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, AnyStr
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
from noloadj.optimization.iterationHandler import Iterations

def plot(iter: List[Iterations], xyLabels, legend: List[AnyStr],
         nb_annotation = 5, joinDots=True):
    """
    Plots a graph.
    :param iter: class Iterations including inputs and outputs at each iteration
    :param xyLabels: labels of axes x and y
    :param legend: legend of the graph
    :param nb_annotation: number of annotations
    :param joinDots: if True, do an interpolation spline.
    :return: /
    """
    n = len(iter)
    fig, ax = plt.subplots()
    # x, y = [sol.oData[0] for sol in iter.iterations],
    # [sol.oData[1] for sol in iter.iterations]
    # line = ax.plot(x, y , '-x')
    fig.suptitle("Pareto front")
    ax.set_xlabel(xyLabels[0])
    ax.set_ylabel(xyLabels[1])
    ax.set_autoscaley_on(True)
    ax.grid()
    # plt.show(block=False)
    markers = ('+', 'x', '*', '.', 'o', 's', 'd', '^', 'v', '>', '<', 'p', 'h')
    for i in range(n):
        iter[i].solutions.sort(key=lambda sol: sol.oData[0])
        # on tri selon l'objectif 1
        #iter[i].solutions.sort(key=lambda sol: sol.oData[1])
        # on tri selon l'objectif 2

        x, y = [sol.oData[0] for sol in iter[i].solutions],\
               [sol.oData[1] for sol in iter[i].solutions]
        plt.scatter(x, y, label=legend[i], marker=markers[i])
        if (nb_annotation!=0):
            for j in range(0,len(x), round(len(x)/nb_annotation)):
                #label = ax.annotate(['%s' % float('%.3g' %x)
                # for x in iter.solutions[i].iData], (x[i], y[i]),
                # xycoords='data', annotation_clip=False)
                dico = dict(zip(iter[i].iNames,
                   ['%s' % float('%.3g' % x)
                   for x in iter[i].solutions[j].iData]))
                #TODO ajouter les contraintes dans l'affichage du pareto...
                # nécessite de passer les specifciations.
                text = str(dico).replace(',', ',\n')
                ax.annotate(text, (x[j], y[j]), xytext=(0, 20),
                        textcoords="offset points",
                         bbox=dict(boxstyle="round", fc="w", alpha=.3),
                                    arrowprops=dict(arrowstyle="->"))
        # Interpolation spline
        if (joinDots):
            tck, u = interpolate.splprep([x, y], s=0)
            unew = np.arange(0, 1.01, 0.01)
            out = interpolate.splev(unew, tck)
            plt.plot(out[0], out[1])
            plt.draw()
        # pour ajuster la taille de la figure en fonction de la taille des
        # annotations
        # fig.subplots_adjust(bottom=0.12, top=0.2, left=0.12, right=1)

        # bbox = label.get_window_extent()
        # ax = plt.gca()
        # bbox_data = bbox.transformed(ax.transData.inverted())
        # ax.update_datalim(bbox_data.corners())
        # ax.autoscale_view()
    ax.legend()
    plt.show(block=True)

    # fig, ax = plt.subplots()
    # # Using set_dashes() to modify dashing of an existing line
    # line1, = ax.plot(x, y, label='Using set_dashes()')
    # line1.set_dashes([2, 2, 10, 2])# 2pt line, 2pt break, 10pt line, 2pt break
    # # Using plot(..., dashes=...) to set the dashing when creating a line
    # line2, = ax.plot(x, y - 0.2, dashes=[6, 2],
    # label='Using the dashes parameter')
    # ax.legend()
    # plt.show()

class AnnotedPareto:
    iter: List[Iterations]
    annot = None
    sc = []
    def __init__(self, iter: List[Iterations], xyLabels, legend: List[AnyStr]):
        self.iter = iter
        self.n = len(iter)
        self.fig, self.ax = plt.subplots()
        self.fig.suptitle("Pareto front")
        self.ax.set_xlabel(xyLabels[0])
        self.ax.set_ylabel(xyLabels[1])
        self.ax.set_autoscaley_on(True)
        self.ax.grid()

        for i in range(self.n):
            iter[i].solutions.sort(key=lambda sol: sol.oData[0])
            # on tri selon l'objectif 1
            x, y = [sol.oData[0] for sol in iter[i].solutions], \
                   [sol.oData[1] for sol in iter[i].solutions]
            self.sc.append(plt.scatter(x, y, label=legend[i]))

            self.annot = self.ax.annotate("", xy=(0, 0), xytext=(0, 20),
                textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
            self.annot.set_visible(False)
            self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
            # Interpolation spline
            tck, u = interpolate.splprep([x, y], s=0)
            unew = np.arange(0, 1.01, 0.01)
            out = interpolate.splev(unew, tck)
            plt.plot(out[0], out[1])
            plt.draw()

        self.ax.legend()
        plt.show(block=True)

    def update_annot(self, ind, i):
        """
        Updates annotation of the graph.
        :param ind: list of annotations 
        :param i: index of the iteration where the annotation takes place. 
        :return: /
        """
        N = ind["ind"][0]
        pos = self.sc[i].get_offsets()[N]
        self.annot.xy = pos
        dico = dict(zip(self.iter[i].iNames,
            ['%s' % float('%.3g' %x) for x in self.iter[i].solutions[N].iData]))
        #text = str(dico)
        text = str(dico).replace(',', ',\n')
        self.annot.set_text(text)
        # annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            ok = False
            for i in range(self.n):
                cont, ind = self.sc[i].contains(event)
                if cont:
                    self.update_annot(ind, i)
                    self.annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                    ok = True
            if (not ok):
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

