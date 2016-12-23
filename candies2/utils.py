#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter


def get_clutter_color(color):
    if isinstance(color, Clutter.Color):
        return color
    elif isinstance(color, tuple):
        return Clutter.color_from_string(*color)[1]
    else:
        return Clutter.color_from_string(color)[1]


def get_rgb_color(color):
    if isinstance(color, tuple):
        if len(color) == 3:
            return color
        if len(color) == 4:
            return color[0], color[1], color[2]
        raise ValueError('Incorrect value for color: %s' % color)
    if isinstance(color, Clutter.Color):
        c_color = color
    else:
        c_color = Clutter.color_from_string(color)[1]
    return c_color.red, c_color.green, c_color.blue


def get_rgba_color(color):
    if isinstance(color, tuple):
        if len(color) == 4:
            return color
        if len(color) == 3:
            return color + (255,)
        raise ValueError('Incorrect value for color: %s' % color)
    if isinstance(color, Clutter.Color):
        c_color = color
    else:
        c_color = Clutter.color_from_string(color)[1]
    return c_color.red, c_color.green, c_color.blue, c_color.alpha
