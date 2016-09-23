#!/usr/bin/env python
# -*- coding: utf-8 -*

from gi.repository import GObject
from gi.repository import Clutter




class Disk(Clutter.Actor):

    """
    Disk (Clutter.Actor)

    A simple actor drawing a disk using the Clutter.cogl primitives
    """
    __gtype_name__ = 'Disk'
    __gproperties__ = {
        'color': (str, 'color', 'Color', None, GObject.PARAM_READWRITE),
    }

    def __init__(self):
        Clutter.Actor.__init__(self)
        self._color = Clutter.color_from_string('Black')

    def set_color(self, color):
        self._color = Clutter.color_from_string(color)

    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self._color = Clutter.color_from_string(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self._color
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def __paint_circle(self, width, height, color):
        cogl.path_ellipse(width / 2, height / 2, width / 2, height / 2)
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

GObject.type_register(Disk)

if __name__ == '__main__':
    stage = Clutter.Stage()
    stage.set_title('Nihon!')
    stage.set_size(640, 480)
    stage.connect('destroy', Clutter.main_quit)

    disk = Disk()
    disk.set_color('Red')
    disk.set_size(200, 200)
    disk.set_anchor_point(100, 100)
    disk.set_position(320, 240)
    stage.add(disk)

    stage.show()
    Clutter.main()
