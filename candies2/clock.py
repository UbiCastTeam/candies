#!/usr/bin/env python
# -*- coding: utf-8 -*
import cairo
import datetime
import math
import os

from gi.repository import Clutter
from gi.repository import GObject

from candies2.utils import get_rgb_color, get_clutter_color


class Clock(Clutter.Actor):
    '''
    A clock widget
    '''

    def __init__(self, color=None, image=None):
        super(Clock, self).__init__()
        if not image:
            image = os.path.join(os.path.dirname(__file__), 'images', 'clock.png')
        self.texture = cairo.ImageSurface.create_from_png(image)
        self.color = get_rgb_color(color or 'black')
        self.date = datetime.datetime.now()

        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.connect('notify::allocation', self.on_allocation)

        GObject.timeout_add_seconds(61 - self.date.second, self.update)

    def set_color(self, color):
        self.color = get_rgb_color(color)
        self.canvas.invalidate()

    def set_texture(self, texture):
        self.texture = texture
        self.canvas.invalidate()

    def update(self):
        self.date = datetime.datetime.now()
        self.canvas.invalidate()
        GObject.timeout_add_seconds(61 - self.date.second, self.update)

    def on_allocation(self, *kwargs):
        GObject.idle_add(self.idle_resize)

    def idle_resize(self):
        self.canvas.set_size(*self.get_size())

    def draw(self, canvas, ctx, width, height):
        hw = width / 2
        hh = height / 2

        center_x = hw
        center_y = hh

        # clock hands
        hour = self.date.hour
        minute = self.date.minute

        # hour
        angle = (60 * hour + minute) / 2 + 270
        left = angle - 14
        right = angle + 14

        angle = angle * (math.pi / 180)
        left = left * (math.pi / 180)
        right = right * (math.pi / 180)

        # reset canvas
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)

        # texture
        ctx.save()
        img_height = self.texture.get_height()
        img_width = self.texture.get_width()
        width_ratio = float(width) / float(img_width)
        height_ratio = float(height) / float(img_height)
        ctx.rectangle(0, 0, width, height)
        ctx.close_path()
        ctx.scale(width_ratio, height_ratio)
        ctx.set_source_surface(self.texture)
        ctx.fill()
        ctx.restore()

        ctx.move_to(center_x, center_y)
        ctx.line_to(center_x + (hw / 4) * math.cos(left), center_y + (hh / 4) * math.sin(left))
        ctx.line_to(center_x + (2 * hw / 3) * math.cos(angle), center_y + (2 * hh / 3) * math.sin(angle))
        ctx.line_to(center_x + (hw / 4) * math.cos(right), center_y + (hh / 4) * math.sin(right))
        ctx.line_to(center_x, center_y)
        ctx.close_path()
        ctx.set_source_rgb(*self.color)
        ctx.fill()

        # minute
        angle = 6 * minute + 270
        left = angle - 10
        right = angle + 10

        angle = angle * (math.pi / 180)
        left = left * (math.pi / 180)
        right = right * (math.pi / 180)

        ctx.move_to(center_x, center_y)
        ctx.line_to(center_x + (hw / 3) * math.cos(left), center_y + (hh / 3) * math.sin(left))
        ctx.line_to(center_x + hw * math.cos(angle), center_y + hh * math.sin(angle))
        ctx.line_to(center_x + (hw / 3) * math.cos(right), center_y + (hh / 3) * math.sin(right))
        ctx.line_to(center_x, center_y)
        ctx.close_path()
        ctx.set_source_rgb(*self.color)
        ctx.fill()


def tester(stage):
    c = Clock()
    c.set_color('white')
    c.set_size(400, 400)
    c.set_position(50, 50)
    stage.add_child(c)
    stage.set_color(get_clutter_color('#888888'))


if __name__ == '__main__':
    from test import run_test
    run_test(tester)
