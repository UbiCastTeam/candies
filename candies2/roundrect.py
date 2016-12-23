#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import cairo
import math

from gi.repository import GObject
from gi.repository import Clutter
from candies2.utils import get_rgb_color


class RoundRectangle(Clutter.Actor):
    """
    RoundRectangle (Clutter.Actor)

    A simple actor drawing a rectangle with round angles using the Clutter.Cogl
    primitives.
    """

    def __init__(self, **params):
        super(RoundRectangle, self).__init__()
        self.inner_color = get_rgb_color(params.get('inner_color', 'black'))
        self.border_color = get_rgb_color(params.get('border_color', 'black'))
        self.border_width = params.get('border_width', 0.0)
        self.border_radius = params.get('border_radius', 0.0)
        self.texture = params.get('texture')

        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.connect('notify::allocation', self.on_allocation)

    def set_texture(self, texture):
        self.texture = texture
        self.queue_redraw()

    def set_border_radius(self, radius):
        self.border_radius = radius
        self.queue_redraw()

    def set_radius(self, radius):
        self.set_border_radius(radius)

    def set_inner_color(self, color):
        self.inner_color = get_rgb_color(color)
        self.queue_redraw()

    def set_color(self, color):
        self.set_inner_color(color)

    def set_border_color(self, color):
        self.border_color = get_rgb_color(color)
        self.queue_redraw()

    def set_border_width(self, width):
        self.border_width = width
        self.queue_redraw()

    def on_allocation(self, *kwargs):
        GObject.idle_add(self.idle_resize)

    def idle_resize(self):
        self.canvas.set_size(*self.get_size())

    def draw(self, canvas, ctx, width, height):
        radius = self.border_radius
        if width <= radius * 2 or height <= radius * 2:
            radius = min((width, height)) / 2

        # clear the previous frame
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()

        ctx.set_operator(cairo.OPERATOR_OVER)
        x = self.border_width
        y = self.border_width
        w = width - self.border_width * 2
        h = height - self.border_width * 2
        ctx.new_sub_path()
        ctx.arc(x + w - radius, y + h - radius, radius, 0, math.pi / 2)
        ctx.arc(x + radius, y + h - radius, radius, math.pi / 2, math.pi)
        ctx.arc(x + radius, y + radius, radius, math.pi, math.pi * 3 / 2)
        ctx.arc(x + w - radius, y + radius, radius, math.pi * 3 / 2, math.pi * 2)
        ctx.close_path()

        ctx.set_source_rgb(*self.inner_color)
        ctx.fill_preserve()  # fill but keep the rectangle
        ctx.set_line_width(self.border_width)
        ctx.set_source_rgb(*self.border_color)
        ctx.stroke()


def tester(stage):
    rect = RoundRectangle()
    rect.set_radius(25)
    rect.set_inner_color('#0000ffff')
    rect.set_border_width(5)
    rect.set_border_color('#00ffffff')
    rect.set_size(160, 120)
    rect.set_anchor_point(80, 60)
    rect.set_position(480, 240)
    stage.add_child(rect)
    GObject.timeout_add_seconds(2, rect.set_size, 300, 400)

    test_memory_usage = False
    if test_memory_usage:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
        from pprint import pprint

        max_count = 20000

        texture = Clutter.Texture.new_from_file(os.path.expanduser('~/.face'))

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
            pprint(gc.garbage)

            GObject.timeout_add(2, test_memory, stage, counter, max_count)
            return False

        GObject.timeout_add(10, test_memory, stage, 0, max_count)


if __name__ == '__main__':
    from test import run_test
    run_test(tester)
