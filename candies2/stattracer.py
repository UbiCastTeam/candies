#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cairo

import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter
from gi.repository import GObject

from candies2.utils import get_rgba_color, get_clutter_color


class Tracer(Clutter.Actor):
    '''
    Tracer: graphics drawing
    '''

    def __init__(self, color='green', n=50, stroke_width=3, with_scale=False, percent=None):
        super(Tracer, self).__init__()
        self.color = get_rgba_color(color)
        self.grid_color = get_rgba_color('white')
        self.stroke_width = stroke_width
        self.percent = percent or list()
        self.n = n
        self.with_scale = with_scale

        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.connect('notify::allocation', self.on_allocation)

    def update(self, value):
        self.percent.append(value)
        if len(self.percent) > self.n:
            self.percent.pop(0)
        self.canvas.invalidate()

    def set_color(self, color):
        self.color = get_rgba_color(color)
        self.canvas.invalidate()

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

        ctx.set_line_width(self.stroke_width)
        if self.with_scale:
            ctx.set_source_rgba(*self.grid_color)
            # rect
            ctx.rectangle(0, 0, width, height)
            ctx.stroke()
            # 0.25 stroke
            ctx.move_to(0, height * 0.25)
            ctx.line_to(width, height * 0.25)
            ctx.stroke()
            # 0.5 stroke
            ctx.move_to(0, height * 0.5)
            ctx.line_to(width, height * 0.5)
            ctx.stroke()
            # 0.75 stroke
            ctx.move_to(0, height * 0.75)
            ctx.line_to(width, height * 0.75)
            ctx.stroke()

        # stats
        ctx.set_source_rgba(*self.color)
        scale_x = width / float(self.n)
        for i, value in enumerate(self.percent):
            y = height - (value * height) / 100
            x = i * scale_x
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
        ctx.stroke()


def tester(stage):
    stage.set_color(get_clutter_color('#888888'))

    percent = [1, 10, 20, 100, 50, 40, 45, 40, 50, 42]

    t1 = Tracer(color='blue', n=len(percent) - 1, percent=percent, with_scale=True)
    t1.set_size(500, 200)
    t1.set_position(50, 50)
    stage.add_child(t1)
    GObject.timeout_add_seconds(2, t1.set_size, 100, 400)

    t2 = Tracer(color='red', n=(len(percent) - 1) * 2, percent=percent, with_scale=True)
    t2.set_size(500, 200)
    t2.set_position(200, 300)
    stage.add_child(t2)


if __name__ == '__main__':
    from test import run_test
    run_test(tester)
