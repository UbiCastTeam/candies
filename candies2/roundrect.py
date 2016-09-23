#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from gi.repository import GObject
from gi.repository import Clutter
from gi.repository import Cogl


class OutlinedRoundRectangle(Clutter.Actor):
    __gtype_name__ = 'OutlinedRoundRectangle'
    __gproperties__ = {
        'color': (
            str, 'color', 'Color', None, GObject.PARAM_READWRITE
        ),
        'radius': (
            GObject.TYPE_FLOAT, 'Radius', 'Radius of the round angles',
            0.0, sys.maxint, 0.0, GObject.PARAM_READWRITE
        ),
        'width': (
            GObject.TYPE_FLOAT, 'width', 'Width',
            0.0, sys.maxint, 0.0, GObject.PARAM_READWRITE
        ),
    }

    def __init__(self):
        Clutter.Actor.__init__(self)
        self._allocation_box = (0, 0, 0, 0)
        self._radius = 0.0
        self._color = Clutter.color_from_string('Black')[1]
        self._width = 0.0

    def get_Clutter_color(self, color):
        if isinstance(color, Clutter.Color):
            return color
        elif isinstance(color, tuple):
            return Clutter.color_from_string(*color)[1]
        else:
            return Clutter.color_from_string(color)[1]

    def set_radius(self, radius):
        self._radius = radius
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[
                                     0], self._allocation_box[3] - self._allocation_box[1])
        self.queue_redraw()

    def set_color(self, color):
        self._color = self.get_Clutter_color(color)
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[
                                     0], self._allocation_box[3] - self._allocation_box[1])
        self.queue_redraw()

    def set_width(self, width):
        self._width = width
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[
                                     0], self._allocation_box[3] - self._allocation_box[1])
        self.queue_redraw()

    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self.set_color(value)
        elif pspec.name == 'radius':
            self.set_radius(value)
        elif pspec.name == 'width':
            self.set_width(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self._color
        elif pspec.name == 'radius':
            return self._radius
        elif pspec.name == 'width':
            return self._width
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def _calculate_paint_values(self, width, height):
        self._real_color = self._color.copy()
        real_alpha = int(
            round(self.get_paint_opacity() * self._real_color.alpha / 255.))
        self._real_color.alpha = real_alpha

        self._external_radius = self._radius + self._width
        self._internal_width = width - 2 * self._width
        self._internal_height = height - 2 * self._width

        self._width_minus_external_radius = width - self._external_radius
        self._height_minus_external_radius = height - self._external_radius

        self._width_plus_radius = self._width + self._radius
        self._width_plus_internal_height_minus_radius = self._width + \
            self._internal_height - self._radius
        self._width_plus_internal_width_minus_radius = self._width + \
            self._internal_width - self._radius
        self._width_plus_internal_height = self._width + self._internal_height
        self._width_plus_internal_width = self._width + self._internal_width

    def do_paint(self):
        abox = self.get_allocation_box()
        x1, y1, x2, y2 = abox.x1, abox.y1, abox.x2, abox.y2
        width = x2 - x1
        height = y2 - y1
        if self._allocation_box != (x1, y1, x2, y2):
            self._calculate_paint_values(width, height)
            self._allocation_box = (x1, y1, x2, y2)

        # external rectangle
        Cogl.path_line(self._external_radius,
                       0, self._width_minus_external_radius, 0)
        Cogl.path_arc(self._width_minus_external_radius, self._external_radius,
                      self._external_radius, self._external_radius, -90, 0)
        Cogl.path_line_to(width, self._height_minus_external_radius)
        Cogl.path_arc(self._width_minus_external_radius, self._height_minus_external_radius,
                      self._external_radius, self._external_radius, 0, 90)
        Cogl.path_line_to(self._external_radius, height)
        Cogl.path_arc(self._external_radius, self._height_minus_external_radius,
                      self._external_radius, self._external_radius, 90, 180)
        Cogl.path_line_to(0, self._external_radius)
        Cogl.path_arc(self._external_radius, self._external_radius,
                      self._external_radius, self._external_radius, 180, 270)

        # internal rectangle
        Cogl.path_line_to(self._width, self._width_plus_radius)
        Cogl.path_line_to(
            self._width, self._width_plus_internal_height_minus_radius)
        Cogl.path_arc(self._width_plus_radius, self._width_plus_internal_height_minus_radius,
                      self._radius, self._radius, -180, -270)
        Cogl.path_line_to(
            self._width_plus_internal_width_minus_radius, self._width_plus_internal_height)
        Cogl.path_arc(self._width_plus_internal_width_minus_radius,
                      self._width_plus_internal_height_minus_radius, self._radius, self._radius, -270, -360)
        Cogl.path_line_to(
            self._width_plus_internal_width, self._width_plus_radius)
        Cogl.path_arc(self._width_plus_internal_width_minus_radius,
                      self._width_plus_radius, self._radius, self._radius, 0, -90)
        Cogl.path_line_to(self._width_plus_radius, self._width)
        Cogl.path_arc(self._width_plus_radius, self._width_plus_radius,
                      self._radius, self._radius, -90, -180)

        Cogl.path_close()
        Cogl.set_source_color(self._real_color)
        Cogl.path_fill()

    def do_destroy(self):
        self.unparent()


class RoundRectangle(Clutter.Actor):

    """
    RoundRectangle (Clutter.Actor)

    A simple actor drawing a rectangle with round angles using the Clutter.Cogl
    primitives.
    """
    __gtype_name__ = 'RoundRectangle'
    __gproperties__ = {
        'color': (
            str, 'color', 'Color', None, GObject.PARAM_READWRITE
        ),
        'radius': (
            GObject.TYPE_FLOAT, 'Radius', 'Radius of the round angles',
            0.0, sys.maxint, 0.0, GObject.PARAM_READWRITE
        ),
        'border_color': (
            str, 'border color', 'Border color', None, GObject.PARAM_READWRITE
        ),
        'border_width': (
            GObject.TYPE_FLOAT, 'border width', 'Border width',
            0.0, sys.maxint, 0.0, GObject.PARAM_READWRITE
        ),
    }

    def __init__(self, texture=None):
        Clutter.Actor.__init__(self)
        self._allocation_box = (0, 0, 0, 0)
        self._radius = 0.0
        self._paint_radius_size = 0.
        self._paint_radius = 0.
        self._paint_double_border_width = 0.
        self._paint_width_minus_border_width = 0.
        self._paint_height_minus_border_width = 0.
        self._paint_radius_minus_border_width = 0.
        self._color = Clutter.color_from_string('Black')[1]
        self._border_color = Clutter.color_from_string('Black')[1]
        self._border_width = 0.0
        self._texture = texture

    def get_Clutter_color(self, color):
        if isinstance(color, Clutter.Color):
            return color
        elif isinstance(color, tuple):
            return Clutter.color_from_string(*color)[1]
        else:
            return Clutter.color_from_string(color)[1]

    def set_texture(self, texture):
        self._texture = texture
        self.queue_redraw()

    def set_radius(self, radius):
        self._radius = radius
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[
                                     0], self._allocation_box[3] - self._allocation_box[1])
        self.queue_redraw()

    def set_inner_color(self, color):
        self._color = self.get_Clutter_color(color)
        self.queue_redraw()

    def set_color(self, color):
        self.set_inner_color(color)

    def set_border_color(self, color):
        self._border_color = self.get_Clutter_color(color)
        self.queue_redraw()

    def set_border_width(self, width):
        self._border_width = width
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[
                                     0], self._allocation_box[3] - self._allocation_box[1])
        self.queue_redraw()

    def do_set_property(self, pspec, value):
        if pspec.name == 'border-color':
            self.set_border_color(value)
        elif pspec.name == 'border-width':
            self.set_border_width(value)
        elif pspec.name == 'color':
            self.set_color(value)
        elif pspec.name == 'radius':
            self.set_radius(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'border-color':
            return self._border_color
        elif pspec.name == 'border-width':
            return self._border_width
        elif pspec.name == 'color':
            return self._color
        elif pspec.name == 'radius':
            return self._radius
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def __paint_rectangle(self, width, height, color, border_color=None):
        if border_color is not None and self._border_width > 0 and self._paint_double_border_width < width and self._paint_double_border_width < height:
            Cogl.rectangle(0, 0, width, height)
            # Cogl.path_round_rectangle(0, 0, width, height, self._paint_radius, 1)
            Cogl.path_close()
            Cogl.set_source_color(border_color)
            Cogl.path_fill()

            Cogl.rectangle(0, 0, width, height)
            # Cogl.path_round_rectangle(self._border_width, self._border_width, self._paint_width_minus_border_width, self._paint_height_minus_border_width, self._paint_radius_minus_border_width, 1)
            Cogl.path_close()
            Cogl.set_source_color(color)
            Cogl.path_fill()

            # texture
            if self._texture:
                Cogl.rectangle(self._border_width, self._border_width, self._border_width + self._paint_width_minus_border_width, self._border_width + self._paint_height_minus_border_width)
                # Cogl.path_round_rectangle(self._border_width, self._border_width, self._paint_width_minus_border_width, self._paint_height_minus_border_width, self._paint_radius_minus_border_width, 1)
                Cogl.path_close()
                Cogl.set_source_texture(self._texture)
                Cogl.path_fill()
        else:
            Cogl.rectangle(0, 0, width, height)
            # Cogl.path_round_rectangle(0, 0, width, height, self._paint_radius, 1)
            Cogl.path_close()
            Cogl.set_source_color(color)
            Cogl.path_fill()

    def do_paint(self):
        abox = self.get_allocation_box()
        x1, y1, x2, y2 = abox.x1, abox.y1, abox.x2, abox.y2
        width = x2 - x1
        height = y2 - y1
        if self._allocation_box != (x1, y1, x2, y2):
            self._calculate_paint_values(width, height)
            self._allocation_box = (x1, y1, x2, y2)

        paint_color = self._color.copy()
        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha

        border_color = self._border_color.copy()
        real_alpha = self.get_paint_opacity() * border_color.alpha / 255
        border_color.alpha = real_alpha

        self.__paint_rectangle(width, height, paint_color, border_color)

    def _calculate_paint_values(self, width, height):
        self._paint_radius_size = 2 * self._radius
        if self._paint_radius_size <= width and self._paint_radius_size <= height:
            self._paint_radius = self._radius
        elif self._paint_radius_size > width and self._paint_radius_size <= height:
            self._paint_radius = width / 2.0
        elif self._paint_radius_size <= width and self._paint_radius_size > height:
            self._paint_radius = height / 2.0
        else:
            self._paint_radius = min(width, height) / 2.0
        self._paint_double_border_width = 2 * self._border_width
        self._paint_width_minus_border_width = width - self._border_width
        self._paint_height_minus_border_width = height - self._border_width
        self._paint_radius_minus_border_width = self._paint_radius - \
            self._border_width

    def do_destroy(self):
        self.unparent()


def tester(stage):
    rect = OutlinedRoundRectangle()
    rect.set_radius(10)
    rect.set_width(5)
    rect.set_color('#ff0000ff')
    rect.set_size(160, 120)
    rect.set_anchor_point(80, 60)
    rect.set_position(160, 240)
    stage.add_child(rect)

    hack = dict(radius=10, width=5)

    def set_width(rect):
        hack["width"] += 1
        rect.set_width(hack["width"])
        if hack["width"] > 30:
            rect.set_width(10)
            return False
        return True

    def set_radius(rect):
        hack["radius"] += 5
        rect.set_radius(hack["radius"])
        if hack["radius"] > 60:
            rect.set_radius(20)
            GObject.timeout_add_seconds(1, set_width, rect)
            return False
        return True
    GObject.timeout_add_seconds(1, set_radius, rect)

    rect = RoundRectangle()
    rect.set_radius(25)
    rect.set_color('#0000ffff')
    rect.set_border_width(5)
    rect.set_border_color('#00ffffff')
    rect.set_size(160, 120)
    rect.set_anchor_point(80, 60)
    rect.set_position(480, 240)
    stage.add_child(rect)

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
                GObject.timeout_add(
                    2, remove_tested_object, tested_object, stage, counter)
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
