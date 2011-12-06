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

    def __init__(self, color='Green', n=50, stroke_width=3):
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
        cogl.set_source_color(color)
        final_x = 0
        for i, value in enumerate(self.percent[:-1]):
            if i == 0 :
                init_y = height - (value*height)/100
                init_x = i*width/self.n
                cogl.path_move_to(init_x,init_y)
            final_y = height - (self.percent[i+1]*height)/100
            final_x =(i+1)*width/self.n
            cogl.path_line_to(final_x, final_y)
        cogl.path_line_to(final_x, height)
        cogl.path_line_to(0, height)
        cogl.path_close()
        final_x = 0

        for i, value in enumerate(self.percent[:-1]):
            if i == 0 :
                init_y = height - (value*height)/100 - self._stroke_width
                init_x = i*width/self.n
                cogl.path_move_to(init_x,init_y)
            final_y = height - (self.percent[i+1]*height)/100 - self._stroke_width
            final_x =(i+1)*width/self.n
            cogl.path_line_to(final_x, final_y)
        cogl.path_line_to(final_x, height)
        cogl.path_line_to(0, height)
        cogl.path_close()
        cogl.path_fill()

        cogl.set_source_color(clutter.color_from_string('#ffffffff'))

        cogl.path_move_to(0,0)
        cogl.path_line_to(0,height)
        cogl.path_line_to(width,height)
        cogl.path_line_to(width,0)
        cogl.path_close()

        cogl.path_move_to(3,3)
        cogl.path_line_to(3,height-3)
        cogl.path_line_to(width-3,height-3)
        cogl.path_line_to(width-3,3)
        cogl.path_close()
        cogl.path_fill()

        cogl.path_move_to(0,height*0.25)
        cogl.path_line_to(0,height*0.75)
        cogl.path_line_to(width,height*0.75)
        cogl.path_line_to(width,height*0.25)
        cogl.path_close()

        cogl.path_move_to(1,1 + height*0.25)
        cogl.path_line_to(1,height*0.75-1)
        cogl.path_line_to(width-1,height*0.75-1)
        cogl.path_line_to(width-1,1 + height*0.25)
        cogl.path_close()
        cogl.path_fill()

        cogl.path_move_to(0,height*0.5)
        cogl.path_line_to(0,height*0.5+1)
        cogl.path_line_to(width,height*0.5+1)
        cogl.path_line_to(width,height*0.5)
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

