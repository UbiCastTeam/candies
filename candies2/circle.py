#!/usr/bin/env python
# -*- coding: utf-8 -*

import cairo
import math

from gi.repository import GObject
from gi.repository import Clutter

from candies2.utils import get_rgb_color


class Circle(Clutter.Actor):
    '''
    A simple actor drawing a circle using cairo.
    '''

    def __init__(self, color=None, stroke_width=50):
        super(Circle, self).__init__()
        self.color = get_rgb_color(color or 'black')
        self.stroke_width = stroke_width

        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.connect('notify::allocation', self.on_allocation)

    def set_color(self, color):
        self.color = get_rgb_color(color)

    def set_stroke_width(self, width):
        self.stroke_width = width

    def on_allocation(self, *kwargs):
        GObject.idle_add(self.idle_resize)

    def idle_resize(self):
        self.canvas.set_size(*self.get_size())

    def draw(self, canvas, ctx, width, height):
        # reset canvas
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)

        radius = width / 2.
        ctx.arc(radius, radius, radius, 0, math.pi * 2)
        ctx.close_path()
        ctx.set_source_rgb(*self.color)
        ctx.fill()


def tester(stage):
    circle = Circle()
    circle.set_color('red')
    circle.set_size(200, 200)
    circle.set_anchor_point(100, 100)
    circle.set_position(320, 240)
    stage.add_child(circle)


if __name__ == '__main__':
    from test import run_test
    run_test(tester)
