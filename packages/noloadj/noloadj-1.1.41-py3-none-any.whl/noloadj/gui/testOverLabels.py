# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

import matplotlib.pyplot as plt
import numpy as np; np.random.seed(1)
xy=[[9953.617734480407,3702.706978407029],
[16922.340327175214,1312.9071457245577],
[11372.495347912003,2507.8071878541073],
[13438.049356911348,1800.9646536851512]]
names = ['a', 'b']
value = [[1, 2], [2, 3], [3, 4], [4, 5]]

# norm = plt.Normalize(1,4)
# cmap = plt.cm.RdYlGn

fig,ax = plt.subplots()
sc = plt.scatter([data[0] for data in xy] ,[data[1] for data in xy])
#,c=c, s=100, cmap=cmap, norm=norm)

annot = ax.annotate("", xy=(0,0), xytext=(0,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(ind):
    """
    Updates annotation of the graph.
    :param ind: list of annotations 
    :return: /
    """
    n = ind["ind"][0]
    pos = sc.get_offsets()[n]
    annot.xy = pos
    dico = dict(zip(names, value[n]))
    text = str(dico).replace(',', ',\n')
    annot.set_text(str(text))
    #annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
    annot.get_bbox_patch().set_alpha(0.4)


def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

plt.show()
