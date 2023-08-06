from typing import List

import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon


def plotpoly(obj):
    """ plotpoly figure outs what the obj is and routes it to the appropriate plotter()
    How often do I get lists? And what should I do in those cases?
    TODO: If dictionary, plot every key?
    If it's a list, should I try to plot it as a whole, and then if that doesn't work, iterate through the list and plot what i can?
    """
    if isinstance(obj, np.ndarray):
        plot_ndarray_poly(obj)
    elif isinstance(obj, Polygon):
        plot_shapely_poly(obj)
    elif isinstance(obj, MultiPolygon):
        plot_shapely_multipoly(obj)
    elif isinstance(obj, dict):
        for _, v in obj.items():
            plotpoly(v)
    elif isinstance(obj, list): # or List?
        try:
            plt.plot(*zip(*obj))
        except TypeError:
            for item in obj:
                plotpoly(item)
    elif isinstance(obj, tuple):
        """
        example:
        x = np.array([1, 3, 5, 7, 9, 6, 4, 1])
        y = np.array([1, 9, 8, 6, 4, 3, 2, 1])
        plotpoly(x, y)
        """
        plt.plot(*obj)
    else:
        print("type not understood")
        print(type(obj))
        print(obj)


def plot_ndarray_poly(arr: np.ndarray):
    """ If it's a numpy array, we'll simply wrap in in a shapely geometry first. """
    poly = Polygon(np.concatenate(arr, axis=0))
    plot_shapely_poly(poly)


def plot_shapely_poly(poly, reverse_y=True):
    # x, y = poly.exterior.xy
    if reverse_y:
        plt.gca().invert_yaxis()
    plt.plot(*poly.exterior.xy)
    plt.show()


def plot_shapely_multipoly(multipoly, reverse_y=True):
    if reverse_y:
        plt.gca().invert_yaxis()
    for geom in multipoly.geoms:
        plt.plot(*geom.exterior.xy)

    plt.gca().axis("equal")
    plt.show()
