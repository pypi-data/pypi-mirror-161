# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0
"""
The aim of these Paretotools functions is to find the longest distance on
axes x or y for every couple of points that can solve the optimization problem.
"""

def getXorYmid(xy, normX, normY):
    """
    Finds the middle point between x and y.
    :param xy: list of tuples including x and y
    :param normX: norm of X
    :param normY: norm of Y
    :return: the index of the objective function, the middle of [XY].
     """
    p1, p2, d = maxDist(xy)
    dX = abs(p2[0]-p1[0])    #on suppose que p2 est bien plus grand que p1
    dY = abs(p2[1] - p1[1])
    if dX/normX > dY/normY:
        return 0, (p1[0]+p2[0])/2
    else:
        return 1, (p1[1] + p2[1]) / 2


def maxDist(a):
    """
    Finds the maximal distance between the coordinates of a.
    :param a: list of tuples including coordinates of a on axes x and y.
    :return: the couple p1 and p2 corresponding to the longest distance mi.
     """
    #a = list(zip(x, y))  # This produces list of tuples
    ax = sorted(a, key=lambda x: x[0])  # Presorting x-wise
    ay = sorted(a, key=lambda x: x[1])  # Presorting y-wise
    p1, p2, mi = max_dist_pair(ax, ay)  # Recursive D&C function
    return p1, p2, mi

def max_dist_pair(ax, ay):
    """
    Finds the maximal distance between the coordinates ax et ay recursively.
    :param ax: list of coordinates on axe x
    :param ay: list of coordinates on axe y
    :return: the couple p1 and p2 corresponding to the longest distance mi.
    """
    ln_ax = len(ax)  # It's quicker to assign variable
    if ln_ax <= 3:
        return brute(ax)  # A call to bruteforce comparison
    mid = ln_ax // 2  # Division without remainder, need int
    Qx = ax[:mid]  # Two-part split
    Rx = ax[mid:]

    # Determine midpoint on x-axis

    midpoint = ax[mid][0]
    Qy = list()
    Ry = list()
    for x in ay:  # split ay into 2 arrays using midpoint
        if x[0] <= midpoint:
           Qy.append(x)
        else:
           Ry.append(x)

    # Call recursively both arrays after split

    (p1, q1, mi1) = max_dist_pair(Qx, Qy)
    (p2, q2, mi2) = max_dist_pair(Rx, Ry)

    # Determine bigger distance between points of 2 arrays

    if mi1 >= mi2:
        d = mi1
        mn = (p1, q1)
    else:
        d = mi2
        mn = (p2, q2)

    # Call function to account for points on the boundary

    (p3, q3, mi3) = max_dist_split_pair(ax, ay, d, mn)

    # Determine biggest distance for the array

    if d >= mi3:
        return mn[0], mn[1], d
    else:
        return p3, q3, mi3

def brute(ax):
    """
    Finds the maximal distance between the 2 coordinates of ax with "hard"
    computation.
    :param ax: list of 2 coordinates on axe x
    :return: the couple p1 and p2 corresponding to the longest distance mi.
    """
    mi = dist(ax[0], ax[1])
    p1 = ax[0]
    p2 = ax[1]
    ln_ax = len(ax)
    if ln_ax == 2:
        return p1, p2, mi
    for i in range(ln_ax-1):
        for j in range(i + 1, ln_ax):
            if i != 0 and j != 1:
                d = dist(ax[i], ax[j])
                if d > mi:  # Update min_dist and points
                    mi = d
                    p1, p2 = ax[i], ax[j]
    return p1, p2, mi

import math
def dist(p1, p2):
    """
    Computes the distance between p1 and p2.
    :param p1: list of coordinates of the first point
    :param p2: list of coordinates of the second point
    :return: the distance between p1 and p2
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def max_dist_split_pair(p_x, p_y, delta, best_pair):
    ln_x = len(p_x)  # store length - quicker
    mx_x = p_x[ln_x // 2][0]  # select midpoint on x-sorted array

    # Create a subarray of points not further than delta from
    # midpoint on x-sorted array

    s_y = [x for x in p_y if mx_x - delta <= x[0] <= mx_x + delta]

    best = delta  # assign best value to delta
    ln_y = len(s_y)  # store length of subarray for quickness
    for i in range(ln_y - 1):
        for j in range(i+1, min(i + 7, ln_y)):
            p, q = s_y[i], s_y[j]
            dst = dist(p, q)
            if dst < best:
                best_pair = p, q
                best = dst
    return best_pair[0], best_pair[1], best

if __name__ == '__main__':
    a = [[9953.86318652108,3702.5292382627013],
    [16922.450708122255,1312.920633183176],
    [13483.690450357713,1790.842361273781],
    [11890.18707155824,2268.764075340589],
    [10963.413555536845,2746.685796235864],
    [10358.889713185245,3224.6075172528217],
    [11347.58068777548,2520.915738089411],
    [12741.29819530203,1977.522534854665],
    [14135.015696837956,1661.5621851434228],
    [15528.733518913752,1456.2150724085136]]

    x=[xy[0] for xy in a]
    y=[xy[1] for xy in a]

    print( maxDist(a) )
    print( getXorYmid(a) )
