#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        return color
    if isinstance(color, Clutter.Color):
        c_color = color
    else:
        c_color = Clutter.color_from_string(color)[1]
    return c_color.red, c_color.green, c_color.blue
