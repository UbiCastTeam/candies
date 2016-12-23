#!/usr/bin/env python
# -*- coding: utf-8 -*
import cairo
import math

import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter
from gi.repository import GObject

from candies2.utils import get_rgb_color, get_clutter_color


class ProgressBar(Clutter.Actor):
    '''
    A progress bar widget using cairo.
    '''
    __gproperties__ = {
        'progress': (
            GObject.TYPE_FLOAT, 'Progress', 'Progress value',
            0.0, 1.0, 0.0, GObject.PARAM_READWRITE
        ),
    }

    def __init__(self, horizontal=True, reverse=False, texture=None, progress_texture=None):
        super(ProgressBar, self).__init__()
        self.radius = 0.0
        self.color = get_rgb_color('Black')
        self.border_color = get_rgb_color('Grey')
        self.progress_color = get_rgb_color('Blue')
        self.border_width = 0.0
        self.texture = cairo.ImageSurface.create_from_png(texture) if texture else None
        self.progress_texture = cairo.ImageSurface.create_from_png(progress_texture) if progress_texture else None
        self.progress = 0.0
        self.horizontal = horizontal
        self.reverse = reverse

        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.connect('notify::allocation', self.on_allocation)

    def set_progress(self, value):
        if value > 1.0:
            self.progress = 1.0
        elif value < 0.0:
            self.progress = 0.0
        else:
            self.progress = value
        self.notify('progress')
        self.canvas.invalidate()

    def get_progress(self):
        return self.progress

    def set_texture(self, image):
        self.texture = cairo.ImageSurface.create_from_png(image) if image else None
        self.canvas.invalidate()

    def set_progress_texture(self, image):
        self.progress_texture = cairo.ImageSurface.create_from_png(image) if image else None
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

    def set_progress_color(self, color):
        self.progress_color = get_rgb_color(color)
        self.canvas.invalidate()

    def set_border_width(self, width):
        self.border_width = width
        self.canvas.invalidate()

    def on_allocation(self, *kwargs):
        GObject.idle_add(self.idle_resize)

    def idle_resize(self):
        self.canvas.set_size(*self.get_size())

    def draw(self, canvas, ctx, width, height):
        # def __paint_rectangle(self, width, height, border_color, inner_color=None, progress_color=None):
        if width <= 0 or height <= 0:
            return
        # check if size will not cause problem with radius
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
        # background round rectangle
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
        # background texture
        if self.texture:
            ctx.stroke_preserve()
            ctx.save()
            width_ratio = float(width) / float(self.texture.get_width())
            height_ratio = float(height) / float(self.texture.get_height())
            ctx.scale(width_ratio, height_ratio)
            ctx.set_source_surface(self.texture)
            ctx.fill()
            ctx.restore()
        else:
            ctx.stroke()

        # progress round rectangle
        if self.progress <= 0:
            return
        x = self.border_width
        y = self.border_width
        width -= self.border_width
        height -= self.border_width
        progress_radius = radius
        progress_radius -= self.border_width / 2.
        if self.horizontal:
            progress_width = int(self.progress * width)
            progress_height = height
            if progress_radius > 0 and progress_width < 2 * progress_radius:
                new_radius = int(float(progress_width) / 2.)
                progress_height -= 2 * (progress_radius - new_radius)
                progress_radius = new_radius
            if progress_radius > 0 and progress_height < 2 * progress_radius:
                new_radius = int(float(progress_height) / 2.)
                progress_width -= 2 * (progress_radius - new_radius)
                progress_radius = new_radius

            progress_x = width - progress_width if self.reverse else 0
            progress_y = int((height - progress_height) / 2.)
        else:
            progress_width = width
            progress_height = int(self.progress * height)
            if progress_radius > 0 and progress_height < 2 * progress_radius:
                new_radius = int(float(progress_height) / 2.)
                progress_width -= 2 * (progress_radius - new_radius)
                progress_radius = new_radius
            if progress_radius > 0 and progress_width < 2 * progress_radius:
                new_radius = int(float(progress_width) / 2.)
                progress_height -= 2 * (progress_radius - new_radius)
                progress_radius = new_radius

            progress_x = int((width - progress_width) / 2.)
            progress_y = height - progress_height if self.reverse else 0

        # progress round rectangle
        if progress_radius > 0:
            ctx.new_sub_path()
            ctx.arc(x + progress_x + progress_width - progress_radius, y + progress_y + progress_height - progress_radius, progress_radius, 0, math.pi / 2)
            ctx.arc(x + progress_x + progress_radius, y + progress_y + progress_height - progress_radius, progress_radius, math.pi / 2, math.pi)
            ctx.arc(x + progress_x + progress_radius, y + progress_y + progress_radius, progress_radius, math.pi, math.pi * 3 / 2)
            ctx.arc(x + progress_x + progress_width - progress_radius, y + progress_y + progress_radius, progress_radius, math.pi * 3 / 2, math.pi * 2)
            ctx.close_path()
        else:
            ctx.rectangle(x + progress_x, y + progress_y, progress_width, progress_height)
        ctx.close_path()
        ctx.set_source_rgb(*self.progress_color)
        # progress_texture
        if self.progress_texture:
            ctx.fill_preserve()
            ctx.save()
            width_ratio = float(width) / float(self.progress_texture.get_width())
            height_ratio = float(height) / float(self.progress_texture.get_height())
            ctx.scale(width_ratio, height_ratio)
            ctx.set_source_surface(self.progress_texture)
            ctx.fill()
            ctx.restore()
        else:
            ctx.fill()


def tester(stage):
    def update_label(bar, event, label):
        label.set_text('%d %%' % (bar.get_progress() * 100))

    def progress(*bars):
        for bar in bars:
            new_progress = round(bar.get_progress() + 0.002, 3)
            bar.set_progress(new_progress)
        return new_progress < 1.0

    def on_button_press(stage, event, *bars):
        for bar in bars:
            bar.set_progress(0.0)
        GObject.timeout_add(10, progress, *bars)

    stage.set_reactive(True)

    label = Clutter.Text()
    label.set_position(50, 10)
    label.set_text('Click to launch progress...')
    stage.add_child(label)

    bar1 = ProgressBar()
    bar1.set_border_radius(10)
    bar1.set_border_width(5)
    bar1.set_border_color('black')
    bar1.set_color('cyan')
    bar1.set_size(600, 100)
    bar1.set_position(50, 50)
    stage.add_child(bar1)

    rect2 = Clutter.Rectangle()
    rect2.set_color(get_clutter_color('gray'))
    rect2.set_size(50, 400)
    rect2.set_position(50, 170)
    stage.add_child(rect2)

    bar2 = ProgressBar(horizontal=False, reverse=True)
    bar2.set_border_radius(10)
    bar2.set_border_width(5)
    bar2.set_border_color('black')
    bar2.set_color('red')
    bar2.set_progress_color('green')
    bar2.set_size(50, 400)
    bar2.set_position(50, 170)
    stage.add_child(bar2)

    bar1.connect('notify::progress', update_label, label)
    stage.connect('button-press-event', on_button_press, bar1, bar2)


if __name__ == '__main__':
    from test import run_test
    run_test(tester)
