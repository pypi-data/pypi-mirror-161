# -*- coding: utf-8 -*-
r"""
This module contains utilities for visualizations of spin configurations.
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as colors
import numpy as np


def truncate_colormap(cmap, minval: float = 0.0, maxval: float = 1.0, n: int = 100):
    r"""
    Returns:
        A new colormap which is a segment of a known color map in matplotlib
    """
    return colors.LinearSegmentedColormap.from_list(
        'trunc({c},{a:.2f},{b:.2f})'.format(c=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))


def get_colormap(which: str = 'hsv_spind') -> mpl.colors.LinearSegmentedColormap:
    r"""
    Returns:
        the desired colormap based on a key string.
    """
    if which == 'hsv_spind':
        mpl.cm.register_cmap('hsv_new', cmap=truncate_colormap(mpl.cm.get_cmap('hsv'), minval=0.6, maxval=0.0))
        return mpl.cm.get_cmap('hsv_new')
    elif which == 'paraview_standard':
        return mpl.cm.get_cmap('viridis')
    elif which == 'coolwarm':
        return mpl.cm.get_cmap('coolwarm')


def HSVtoRGB(vec: np.ndarray, saturation: float = 0.2) -> np.ndarray:
    r"""
    Calculates the bivariate color code varying hue and value for vectors. The oop-component will be visualized by
    the value and the ip-angle by hue. The saturation can be provided as input
    """
    vecnorm = np.linalg.norm(vec)
    H = np.arctan2(vec[1] / vecnorm, vec[0] / vecnorm)
    value = 1 - abs(vec[2] / vecnorm)
    chroma = saturation * value
    # H angle is in interval -pi;pi shift it to 0,2pi
    # also transfer to 0;360
    H = (H + np.pi) * (180 / np.pi)
    Hprime = H / 60
    X = chroma * (1 - abs(Hprime % 2 - 1))
    if 0 <= Hprime < 1:
        r1 = chroma
        g1 = X
        b1 = 0
    elif 1 <= Hprime < 2:
        r1 = X
        g1 = chroma
        b1 = 0
    elif 2 <= Hprime < 3:
        r1 = 0
        g1 = chroma
        b1 = X
    elif 3 <= Hprime < 4:
        r1 = 0
        g1 = X
        b1 = chroma
    elif 4 <= Hprime < 5:
        r1 = X
        g1 = 0
        b1 = chroma
    elif 5 <= Hprime <= 6:
        r1 = chroma
        g1 = 0
        b1 = X
    else:
        raise ValueError
    m = value - chroma
    r = r1 + m
    g = g1 + m
    b = b1 + m
    return np.array([r, g, b])
