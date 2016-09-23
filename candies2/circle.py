#!/usr/bin/env python
# -*- coding: utf-8 -*

from gi.repository import GObject
from gi.repository import Clutter



class Circle(Clutter.Actor):

    """
    Circle (Clutter.Actor)

    A simple actor drawing a circle using the Clutter.cogl primitives
    """
    __gtype_name__ = 'Circle'
    __gproperties__ = {
        'color': (str, 'color', 'Color', None, GObject.PARAM_READWRITE),
    }

    def __init__(self, color='Black', stroke_width=50):
        Clutter.Actor.__init__(self)
        self._color = Clutter.color_from_string(color)
        self._stroke_width = stroke_width

    def set_color(self, color):
        self._color = Clutter.color_from_string(color)

    def set_stroke_width(self, width):
        self._stroke_width = width

    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self._color = self.set_color(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self._color
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def __paint_circle(self, width, height, color):
        cogl.path_arc(width / 2, height / 2, width / 2, height / 2, 0, 360)
        cogl.path_close()
        cogl.path_arc(width / 2, height / 2, (width / 2) -
                      self._stroke_width, (height / 2) - self._stroke_width, 0, 360)
        cogl.path_close()

        cogl.set_source_color(color)
        cogl.path_fill()

    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()

        paint_color = self._color.copy()

        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha

        self.__paint_circle(x2 - x1, y2 - y1, paint_color)

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return

        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__paint_circle(x2 - x1, y2 - y1, pick_color)

GObject.type_register(Circle)

if __name__ == '__main__':
    stage = Clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', Clutter.main_quit)

    circle = Circle()
    circle.set_color('Red')
    circle.set_size(200, 200)
    circle.set_anchor_point(100, 100)
    circle.set_position(320, 240)
    stage.add(circle)

    stage.show()
    Clutter.main()
