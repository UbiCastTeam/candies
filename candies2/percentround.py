#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cairo
import math

import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter
from gi.repository import GObject

from candies2.utils import get_rgba_color


class PercentRound(Clutter.Actor):
    '''
    Simple actor to draw pie charts.
    '''

    def __init__(self, color='black', percent=0, init_percent=0, color2='grey'):
        super(PercentRound, self).__init__()
        self._color = get_rgba_color(color)
        self._color2 = get_rgba_color(color2)
        self.percent = percent
        self.init_percent = init_percent

        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.connect('notify::allocation', self.on_allocation)

    def set_percent(self, percent):
        self.percent = percent
        self.canvas.invalidate()

    def set_init_percent(self, percent):
        self.init_percent = percent
        self.canvas.invalidate()

    def set_color(self, color):
        self._color = get_rgba_color(color)
        self.canvas.invalidate()

    def set_color2(self, color):
        self._color2 = get_rgba_color(color)
        self.canvas.invalidate()

    def on_allocation(self, *kwargs):
        GObject.idle_add(self.idle_resize)

    def idle_resize(self):
        self.canvas.set_size(*self.get_size())

    def draw(self, canvas, ctx, width, height):
        # clear the previous frame
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)

        x = width / 2
        y = height / 2
        radius = min(x, y)
        ctx.new_sub_path()
        ctx.set_source_rgba(*self._color)
        ctx.move_to(x, y)
        init_angle = 2 * math.pi * self.init_percent / 100
        end_angle = 2 * math.pi * (self.init_percent + self.percent) / 100
        if init_angle:
            ctx.line_to(x + math.cos(init_angle) * radius, y + math.sin(init_angle) * radius)
        else:
            ctx.line_to(x + radius, y)
        if init_angle != end_angle:
            ctx.arc(x, y, radius, init_angle, end_angle)
            ctx.close_path()
            ctx.fill()
        else:
            ctx.set_line_width(3)
            ctx.stroke()

        if init_angle:
            ctx.new_sub_path()
            ctx.set_source_rgba(*self._color2)
            ctx.move_to(x, y)
            ctx.arc(x, y, radius, 0, init_angle)
            ctx.close_path()
            ctx.fill()


def tester(stage):
    pc1 = PercentRound(percent=90)
    pc1.set_color('red')
    pc1.set_size(200, 200)
    pc1.set_position(50, 50)
    stage.add_child(pc1)

    pc2 = PercentRound(percent=0)
    pc2.set_color('blue')
    pc2.set_size(200, 200)
    pc2.set_position(50, 300)
    stage.add_child(pc2)

    pc3 = PercentRound(init_percent=25, percent=40)
    pc3.set_color('black')
    pc3.set_size(200, 200)
    pc3.set_position(300, 50)
    stage.add_child(pc3)

    pc4 = PercentRound(init_percent=40, percent=0)
    pc4.set_color('green')
    pc4.set_size(200, 200)
    pc4.set_position(300, 300)
    stage.add_child(pc4)

    def progress(pc):
        new_percent = pc.percent + 1
        pc.set_percent(new_percent)
        return new_percent < 100

    def on_button_press(pc, event):
        pc.set_percent(0)
        GObject.timeout_add(10, progress, pc)

    pc1.set_reactive(True)
    pc1.connect('button-press-event', on_button_press)

    pc2.set_reactive(True)
    pc2.connect('button-press-event', on_button_press)

    pc3.set_reactive(True)
    pc3.connect('button-press-event', on_button_press)

    pc4.set_reactive(True)
    pc4.connect('button-press-event', on_button_press)


if __name__ == '__main__':
    from test import run_test
    run_test(tester)
