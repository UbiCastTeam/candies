#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gobject
import clutter

from clutter import cogl

class OutlinedRoundRectangle(clutter.Actor):
    __gtype_name__ = 'OutlinedRoundRectangle'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'radius': (
            gobject.TYPE_FLOAT, 'Radius', 'Radius of the round angles',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
    }
    
    def __init__(self):
        clutter.Actor.__init__(self)
        self._color = clutter.color_from_string('Black')
        self._radius = 0.0
    
    def set_radius(self, radius):
        self._radius = radius
        self.queue_redraw()
    
    def set_color(self, color):
        self._color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self.set_color(value)
        elif pspec.name == 'radius':
            self.set_radius(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self._color
        elif pspec.name == 'radius':
            return self._radius
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def __paint_rectangle(self, width, height, color):
        cogl.path_round_rectangle(0, 0, width, height, self._radius, 1)
        cogl.path_close()
        cogl.set_source_color(color)
        cogl.path_stroke()
    
    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()

        paint_color = self._color.copy()
        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha
        
        self.__paint_rectangle(x2 - x1, y2 - y1, paint_color)

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return

        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__paint_rectangle(x2 - x1, y2 - y1, pick_color)
    
    def do_destroy(self):
        self.unparent()


class RoundRectangle(clutter.Actor):
    """
    RoundRectangle (clutter.Actor)

    A simple actor drawing a rectangle with round angles using the clutter.cogl
    primitives.
    """
    __gtype_name__ = 'RoundRectangle'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'radius': (
            gobject.TYPE_FLOAT, 'Radius', 'Radius of the round angles',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
        'border_color': (
            str, 'border color', 'Border color', None, gobject.PARAM_READWRITE
        ),
        'border_width' : (
            gobject.TYPE_FLOAT, 'border width', 'Border width',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
    }

    def __init__(self, texture=None):
        clutter.Actor.__init__(self)
        self._radius = 0.0
        self._color = clutter.color_from_string('Black')
        self._border_color = clutter.color_from_string('Black')
        self._border_width = 0.0
        self._texture = texture
    
    def set_texture(self, texture):
        self._texture = texture
        self.queue_redraw()
    
    def set_radius(self, radius):
        self._radius = radius
        self.queue_redraw()
    
    def set_color(self, color):
        self._color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_border_color(self, color):
        self._border_color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_border_width(self, width):
        self._border_width = width
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
        if border_color is not None and self._border_width > 0.0:
            cogl.path_round_rectangle(0, 0, width, height, self._radius, 1)
            cogl.path_close()
            cogl.set_source_color(border_color)
            cogl.path_fill()
            
            w = self._border_width
            cogl.path_round_rectangle(w, w, width - w, height - w, self._radius - w, 1)
            cogl.path_close()
            cogl.set_source_color(color)
            cogl.path_fill()
            
            # texture
            if self._texture:
                cogl.path_round_rectangle(w, w, width - w, height - w, self._radius - w, 1)
                cogl.path_close()
                cogl.set_source_texture(self._texture)
                cogl.path_fill()
        else:
            cogl.path_round_rectangle(0, 0, width, height, self._radius, 1)
            cogl.path_close()
            cogl.set_source_color(color)
            cogl.path_fill()
    
    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()

        paint_color = self._color.copy()
        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha
        
        border_color = self._border_color.copy()
        real_alpha = self.get_paint_opacity() * border_color.alpha / 255
        border_color.alpha = real_alpha

        self.__paint_rectangle(x2 - x1, y2 - y1, paint_color, border_color)
    
    def do_destroy(self):
        self.unparent()


if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    rect = OutlinedRoundRectangle()
    rect.set_radius(25)
    rect.set_color('#ff0000ff')
    rect.set_size(160, 120)
    rect.set_anchor_point(80, 60)
    rect.set_position(160, 240)
    stage.add(rect)
    
    rect = RoundRectangle()
    rect.set_radius(25)
    rect.set_color('#0000ffff')
    rect.set_border_width(5)
    rect.set_border_color('#00ffffff')
    rect.set_size(160, 120)
    rect.set_anchor_point(80, 60)
    rect.set_position(480, 240)
    stage.add(rect)
    
    test_memory_usage = True
    if test_memory_usage:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
        from pprint import pprint
        
        max_count = 20000
        
        texture_path = '/path/to/an/image'
        texture = cogl.texture_new_from_file(light_path)
        
        def create_test_object():
            t = RoundRectangle(texture = texture)
            return t
        def remove_test_object(obj, stage):
            stage.remove(obj)
            obj.destroy()
            return False
        
        def test_memory(stage, counter, max_count):
            if counter < max_count or max_count == 0:
                counter += 1
                print counter
                tested_object = create_test_object()
                stage.add(tested_object)
                gobject.timeout_add(2, remove_tested_object, tested_object, stage, counter)
            return False
        
        def remove_tested_object(tested_object, stage, counter):
            remove_test_object(tested_object, stage)
            
            gc.collect()
            pprint(gc.garbage)
            
            gobject.timeout_add(2, test_memory, stage, counter, max_count)
            return False
        
        gobject.timeout_add(10, test_memory, stage, 0, max_count)

    stage.show()
    clutter.main()
