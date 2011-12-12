#!/usr/bin/env python
# -*- coding: utf-8 -*

import gobject
import clutter
from clutter import cogl

class Tracer(clutter.Actor):
    """
    Tracer (clutter.Actor)

    """
    __gtype_name__ = 'test'
    __gproperties__ = {
        'color' : (str, 'color', 'Color', None, gobject.PARAM_READWRITE),
    }

    def __init__(self, color='Green', n=25, stroke_width=3):
        clutter.Actor.__init__(self)
        self._stroke_width = stroke_width
        self._color = clutter.color_from_string(color)
        self.percent = list()
        self.n = n

    def update(self, value):
        self.percent.append(value)
        if len(self.percent) > self.n:
            self.percent.pop(0)
        self.queue_redraw()

    def set_color(self, color):
        self._color = clutter.color_from_string(color)
        self.queue_redraw()

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

    def __cogl_path(self, width, height, color):
        cogl.set_source_color(clutter.color_from_string('#ffffffff'))

        #rect
        cogl.path_move_to(0,0)
        cogl.path_line_to(0,height)
        cogl.path_line_to(width,height)
        cogl.path_line_to(width,0)
        cogl.path_line_to(0,0)
        cogl.path_line_to(3,3)
        cogl.path_line_to(3,height-3)
        cogl.path_line_to(width-3,height-3)
        cogl.path_line_to(width-3,3)
        cogl.path_line_to(3,3)
        cogl.path_close()
        cogl.path_fill()
        #0.25 stroke
        cogl.path_rectangle(0,height*0.25,width, height*0.25+1)
        cogl.path_fill()
        cogl.path_close()
        #0.5 stroke
        cogl.path_rectangle(0,height*0.5,width,height*0.5+1)
        cogl.path_close()
        cogl.path_fill()
        #0.75 stroke
        cogl.path_rectangle(0,height*0.75, width, height*0.75+1)
        cogl.path_close()
        cogl.path_fill()

        #stats
        cogl.set_source_color(color)
        for i, value in enumerate(self.percent):
            y = height - (value*height)/100
            if y == 0 : y= self._stroke_width
            x = i*width/self.n
            if i == 0:
                cogl.path_move_to(x,y)
            else :
                cogl.path_line_to(x,y)

        for i, value in enumerate(reversed(self.percent)):
            y = abs(height - (value*height)/100 - self._stroke_width)
            x = (len(self.percent)-i -1)*width/self.n
            cogl.path_line_to(x,y)
        cogl.path_close()
        cogl.path_fill()

    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()
        paint_color = self._color.copy()
        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha
        self.__cogl_path(x2 - x1, y2 - y1, paint_color)

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return
        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__cogl_path(x2 - x1, y2 - y1, pick_color)

gobject.type_register(Tracer)

if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    percent = [1,10,20,100,50,40,30,40,50]

    test = Tracer()
    #test.percent = percent
    test.set_color('Red')
    test.set_size(500, 50)
    test.set_position(10, 240)
    stage.add(test)

    stage.show()
    clutter.main()

