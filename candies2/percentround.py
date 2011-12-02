#!/usr/bin/env python
# -*- coding: utf-8 -*

import gobject
import clutter
from clutter import cogl

class PercentRound(clutter.Actor):
    """
    Test (clutter.Actor)

    """
    __gtype_name__ = 'PercentRound'
    __gproperties__ = {
        'color' : (str, 'color', 'Color', None, gobject.PARAM_READWRITE),
    }

    def __init__(self, color='Black', percent=0):
        clutter.Actor.__init__(self)
        self._color = clutter.color_from_string(color)
        self.percent = percent

    def set_percent(self, percent):
        self.percent = percent
        self.queue_redraw()

    def set_color(self, color):
        self._color = clutter.color_from_string(color)
        self.queue_redraw()

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
        if self.percent != 0 :
            cogl.path_arc(width / 2, height / 2, width / 2, height / 2, 0, self.percent*360/100)
            cogl.path_line_to(width / 2, height / 2)
            cogl.path_line_to(width, height / 2)
        else :
            cogl.path_line(width / 2, height / 2,width, height / 2)
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

gobject.type_register(PercentRound)

if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    circle = PercentRound(percent=90)
    circle.set_color('Red')
    circle.set_size(200, 200)
    circle.set_anchor_point(100, 100)
    circle.set_position(320, 240)
    stage.add(circle)

    stage.show()
    clutter.main()

