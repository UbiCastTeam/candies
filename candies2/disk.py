#!/usr/bin/env python
# -*- coding: utf-8 -*

import gi
gi.require_version('Clutter', '1.0')
import cairo
import math

from gi.repository import GObject
from gi.repository import Clutter

from candies2.utils import get_rgb_color


class Disk(Clutter.Actor):
    '''
    A simple actor drawing a disk using cairo.
    '''

    def __init__(self, color=None, border_color=None, border_width=5):
        super(Disk, self).__init__()
        self.color = get_rgb_color(color) if color else None
        self.border_color = get_rgb_color(border_color) if border_color else None
        self.border_width = border_width

        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.connect('notify::allocation', self.on_allocation)

    def set_color(self, color):
        self.color = get_rgb_color(color) if color else None
        self.canvas.invalidate()

    def set_border_color(self, color):
        self.border_color = get_rgb_color(color) if color else None
        self.canvas.invalidate()

    def set_border_width(self, width):
        self.border_width = width
        self.canvas.invalidate()

    def on_allocation(self, *kwargs):
        GObject.idle_add(self.idle_resize)

    def idle_resize(self):
        self.canvas.set_size(*self.get_size())

    def draw(self, canvas, ctx, width, height):
        # reset canvas
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        if not self.color and not self.border_color:
            return
        ctx.set_operator(cairo.OPERATOR_OVER)

        x = self.border_width
        y = self.border_width
        w = width - self.border_width * 2
        h = height - self.border_width * 2

        if w == h:
            radius = w / 2.
            ctx.arc(x + radius, y + radius, radius, 0, 2 * math.pi)
        else:
            x_radius = w / 2.
            y_radius = h / 2.
            ctx.save()
            ctx.translate(x + x_radius, y + y_radius)
            ctx.scale(x_radius, y_radius)
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.restore()
        ctx.close_path()
        if self.color:
            ctx.set_source_rgb(*self.color)
            ctx.fill_preserve()  # fill but keep the rectangle
        if self.border_color:
            ctx.set_line_width(self.border_width)
            ctx.set_source_rgb(*self.border_color)
            ctx.stroke()


def tester(stage):
    d1 = Disk(color='blue')
    d1.set_size(200, 200)
    d1.set_position(50, 50)
    stage.add_child(d1)
    GObject.timeout_add_seconds(2, d1.set_size, 100, 400)

    d2 = Disk(border_color='red')
    d2.set_size(200, 200)
    d2.set_position(300, 50)
    stage.add_child(d2)


if __name__ == '__main__':
    from test import run_test
    run_test(tester)
