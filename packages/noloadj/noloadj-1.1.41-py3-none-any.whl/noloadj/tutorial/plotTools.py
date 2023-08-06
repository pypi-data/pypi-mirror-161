# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

#Plot
def plot3D(func, plotRange=[[-1,1],[-1,1]], outNames = ['fobj'], nbpts=30,
           parameters=()):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
    from matplotlib import cm
    import numpy as np
    
    
    
    xmin = plotRange[0][0]
    xmax = plotRange[0][1]
    ymin = plotRange[1][0]
    ymax = plotRange[1][1]
    nbX = (xmax-xmin)/nbpts
    nbY = (ymax-ymin)/nbpts
    X = np.arange(xmin, xmax, nbX)
    Y = np.arange(ymin, ymax, nbY)
    X, Y = np.meshgrid(X, Y)
    res = func(X,Y,*parameters)
    dico = {k: v for k, v in res.__iter__()}  # conversion en dictionnaire
    
    for i, name in enumerate(outNames):
        Z = dico[name]
        plt.figure()
        ax = plt.axes(projection="3d")
        plt.title(name)
        plt.xlabel('X')
        plt.ylabel('Y')
        surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                linewidth=0, antialiased=False)
    plt.show()
