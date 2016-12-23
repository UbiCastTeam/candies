#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cairo
import math
import os

import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter
from gi.repository import GObject

from candies2.utils import get_rgb_color, get_clutter_color


class RoundRectangle(Clutter.Actor):
    '''
    A simple actor drawing a rectangle with round angles using cairo.
    '''

    def __init__(self, **params):
        super(RoundRectangle, self).__init__()
        self.color = get_rgb_color(params.get('color', 'black'))
        self.border_color = get_rgb_color(params.get('border_color', 'blue'))
        self.border_width = params.get('border_width', 0.0)
        self.border_radius = params.get('border_radius', 0.0)
        self.texture = params.get('texture')

        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.connect('notify::allocation', self.on_allocation)

    def set_texture(self, texture):
        self.texture = texture
        self.canvas.invalidate()

    def set_border_radius(self, radius):
        self.border_radius = radius
        self.canvas.invalidate()

    def set_color(self, color):
        self.color = get_rgb_color(color)
        self.canvas.invalidate()

    def set_border_color(self, color):
        self.border_color = get_rgb_color(color)
        self.canvas.invalidate()

    def set_border_width(self, width):
        self.border_width = width
        self.canvas.invalidate()

    def on_allocation(self, *kwargs):
        GObject.idle_add(self.idle_resize)

    def idle_resize(self):
        self.canvas.set_size(*self.get_size())

    def draw(self, canvas, ctx, width, height):
        radius = self.border_radius
        if radius > 0 and (width < radius * 2 or height < radius * 2):
            radius = min((width, height)) / 2

        # clear the previous frame
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)

        x = self.border_width / 2.
        y = self.border_width / 2.
        width -= self.border_width
        height -= self.border_width
        if radius > 0:
            ctx.new_sub_path()
            ctx.arc(x + width - radius, y + height - radius, radius, 0, math.pi / 2)
            ctx.arc(x + radius, y + height - radius, radius, math.pi / 2, math.pi)
            ctx.arc(x + radius, y + radius, radius, math.pi, math.pi * 3 / 2)
            ctx.arc(x + width - radius, y + radius, radius, math.pi * 3 / 2, math.pi * 2)
            ctx.close_path()
        else:
            ctx.rectangle(x, y, width, height)

        ctx.set_source_rgb(*self.color)
        ctx.fill_preserve()  # fill but keep the rectangle
        ctx.set_line_width(self.border_width)
        ctx.set_source_rgb(*self.border_color)
        ctx.stroke()


def tester(stage):
    rr1 = RoundRectangle()
    rr1.set_border_radius(10)
    rr1.set_color('blue')
    rr1.set_border_width(5)
    rr1.set_border_color('cyan')
    rr1.set_size(200, 400)
    rr1.set_position(300, 50)
    stage.add_child(rr1)
    GObject.timeout_add_seconds(2, rr1.set_size, 300, 200)

    rect1 = Clutter.Rectangle()
    rect1.set_color(get_clutter_color('gray'))
    rect1.set_size(200, 400)
    rect1.set_position(50, 50)
    stage.add_child(rect1)

    rr2 = RoundRectangle()
    rr2.set_border_radius(25)
    rr2.set_color('blue')
    rr2.set_border_width(5)
    rr2.set_border_color('cyan')
    rr2.set_size(200, 400)
    rr2.set_position(50, 50)
    stage.add_child(rr2)

    rect2 = Clutter.Rectangle()
    rect2.set_color(get_clutter_color('#ffffffaa'))
    rect2.set_size(190, 390)
    rect2.set_position(55, 55)
    stage.add_child(rect2)

    test_memory_usage = False
    if test_memory_usage:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)

        max_count = 20000

        texture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'logo.png')
        texture = Clutter.Texture.new_from_file(texture_path)

        def create_test_object():
            t = RoundRectangle(texture=texture)
            return t

        def remove_test_object(obj, stage):
            stage.remove_child(obj)
            obj.destroy()
            return False

        def test_memory(stage, counter, max_count):
            if counter < max_count or max_count == 0:
                counter += 1
                print counter
                tested_object = create_test_object()
                stage.add_child(tested_object)
                GObject.timeout_add(2, remove_tested_object, tested_object, stage, counter)
            return False

        def remove_tested_object(tested_object, stage, counter):
            remove_test_object(tested_object, stage)

            gc.collect()

            GObject.timeout_add(2, test_memory, stage, counter, max_count)
            return False

        GObject.timeout_add(10, test_memory, stage, 0, max_count)


if __name__ == '__main__':
    from test import run_test
    run_test(tester)
