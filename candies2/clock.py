#!/usr/bin/env python
# -*- coding: utf-8 -*

from gi.repository import Clutter

import math


class Clock(Clutter.Actor):
    __gtype_name__ = 'Clock'
    """
    A clock widget
    """

    def __init__(self, date=None, texture=None):
        Clutter.Actor.__init__(self)
        self._date = date
        self._texture = texture
        self._color = Clutter.color_from_string('Black')

    def set_color(self, color):
        self._color = Clutter.color_from_string(color)
        self.queue_redraw()

    def set_texture(self, texture):
        self._texture = texture
        self.queue_redraw()

    def set_date(self, date=None):
        self._date = date
        if date is not None:
            self.queue_redraw()

    def do_paint(self):
        # Clutter.Texture.do_paint(self)

        (x1, y1, x2, y2) = self.get_allocation_box()
        width = x2 - x1
        height = y2 - y1
        hw = width / 2
        hh = height / 2

        center_x = hw
        center_y = hh

        # texture
        if self._texture is not None:
            cogl.path_rectangle(0, 0, width, height)
            cogl.path_close()
            cogl.set_source_texture(self._texture)
            cogl.path_fill()

        # clock hands
        if self._date is not None:
            hour = self._date.hour
            minute = self._date.minute

            # hour
            angle = (60 * hour + minute) / 2 + 270
            left = angle - 14
            right = angle + 14

            angle = angle * (math.pi / 180)
            left = left * (math.pi / 180)
            right = right * (math.pi / 180)

            cogl.path_move_to(center_x, center_y)
            cogl.path_line_to(center_x + (hw / 4) * math.cos(
                left), center_y + (hh / 4) * math.sin(left))
            cogl.path_line_to(center_x + (2 * hw / 3) * math.cos(
                angle), center_y + (2 * hh / 3) * math.sin(angle))
            cogl.path_line_to(center_x + (hw / 4) * math.cos(
                right), center_y + (hh / 4) * math.sin(right))
            cogl.path_line_to(center_x, center_y)
            cogl.path_close()
            cogl.set_source_color(self._color)
            cogl.path_fill()

            # minute
            angle = 6 * minute + 270
            left = angle - 10
            right = angle + 10

            angle = angle * (math.pi / 180)
            left = left * (math.pi / 180)
            right = right * (math.pi / 180)

            cogl.path_move_to(center_x, center_y)
            cogl.path_line_to(center_x + (hw / 3) * math.cos(
                left), center_y + (hh / 3) * math.sin(left))
            cogl.path_line_to(center_x + hw * math.cos(
                angle), center_y + hh * math.sin(angle))
            cogl.path_line_to(center_x + (hw / 3) * math.cos(
                right), center_y + (hh / 3) * math.sin(right))
            cogl.path_line_to(center_x, center_y)
            cogl.path_close()
            cogl.set_source_color(self._color)
            cogl.path_fill()


# main to test
if __name__ == '__main__':
    stage = Clutter.Stage()
    stage.connect('destroy', Clutter.main_quit)

    from gi.repository import GObject, datetime
    t = cogl.texture_new_from_file(
        'clock.png', Clutter.cogl.TEXTURE_NO_SLICING, Clutter.cogl.PIXEL_FORMAT_ANY)
    c = Clock()
    c.set_texture(t)
    c.set_size(400, 400)
    c.set_position(50, 50)
    stage.add(c)

    def update():
        today = datetime.datetime.today()
        # self.actor.set_text(today.strftime('%H:%M\n%d / %m'))
        c.set_date(today)
        return True

    GObject.timeout_add_seconds(60, update)

    stage.show()
    Clutter.main()
