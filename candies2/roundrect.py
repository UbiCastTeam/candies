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
        'width' : (
            gobject.TYPE_FLOAT, 'width', 'Width',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
    }
    
    def __init__(self):
        clutter.Actor.__init__(self)
        self._allocation_box = (0, 0, 0, 0)
        self._radius = 0.0
        self._color = clutter.color_from_string('Black')
        self._width = 0.0
    
    def get_clutter_color(self, color):
        if isinstance(color, tuple):
            c = clutter.Color(*color)
        else:
            c = clutter.color_from_string(color)
        return c
    
    def set_radius(self, radius):
        self._radius = radius
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[0], self._allocation_box[3] - self._allocation_box[1])
        self.queue_redraw()
    
    def set_color(self, color):
        self._color = self.get_clutter_color(color)
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[0], self._allocation_box[3] - self._allocation_box[1])
        self.queue_redraw()
    
    def set_width(self, width):
        self._width = width
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[0], self._allocation_box[3] - self._allocation_box[1])
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
        real_alpha = int(round(self.get_paint_opacity() * self._real_color.alpha / 255.))
        self._real_color.alpha = real_alpha
        
        self._external_radius = self._radius + self._width
        self._internal_width = width - 2 * self._width
        self._internal_height = height - 2 * self._width
        
        self._width_minus_external_radius = width - self._external_radius
        self._height_minus_external_radius = height - self._external_radius
        
        self._width_plus_radius = self._width + self._radius
        self._width_plus_internal_height_minus_radius = self._width + self._internal_height - self._radius
        self._width_plus_internal_width_minus_radius = self._width + self._internal_width - self._radius
        self._width_plus_internal_height = self._width + self._internal_height
        self._width_plus_internal_width = self._width + self._internal_width
    
    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()
        width = x2 - x1
        height = y2 - y1
        if self._allocation_box != (x1, y1, x2, y2):
            self._calculate_paint_values(width, height)
            self._allocation_box = (x1, y1, x2, y2)
        
        # external rectangle
        cogl.path_line(self._external_radius, 0, self._width_minus_external_radius, 0)
        cogl.path_arc(self._width_minus_external_radius, self._external_radius, self._external_radius, self._external_radius, -90, 0)
        cogl.path_line_to(width, self._height_minus_external_radius)
        cogl.path_arc(self._width_minus_external_radius, self._height_minus_external_radius, self._external_radius, self._external_radius, 0, 90)
        cogl.path_line_to(self._external_radius, height)
        cogl.path_arc(self._external_radius, self._height_minus_external_radius, self._external_radius, self._external_radius, 90, 180)
        cogl.path_line_to(0, self._external_radius)
        cogl.path_arc(self._external_radius, self._external_radius, self._external_radius, self._external_radius, 180, 270)
        
        # internal rectangle
        cogl.path_line_to(self._width, self._width_plus_radius)
        cogl.path_line_to(self._width, self._width_plus_internal_height_minus_radius)
        cogl.path_arc(self._width_plus_radius, self._width_plus_internal_height_minus_radius, self._radius, self._radius, -180, -270)
        cogl.path_line_to(self._width_plus_internal_width_minus_radius, self._width_plus_internal_height)
        cogl.path_arc(self._width_plus_internal_width_minus_radius, self._width_plus_internal_height_minus_radius, self._radius, self._radius, -270, -360)
        cogl.path_line_to(self._width_plus_internal_width, self._width_plus_radius)
        cogl.path_arc(self._width_plus_internal_width_minus_radius, self._width_plus_radius, self._radius, self._radius, 0, -90)
        cogl.path_line_to(self._width_plus_radius, self._width)
        cogl.path_arc(self._width_plus_radius, self._width_plus_radius, self._radius, self._radius, -90, -180)
        
        cogl.path_close()
        cogl.set_source_color(self._real_color)
        cogl.path_fill()
    
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
        self._allocation_box = (0, 0, 0, 0)
        self._radius = 0.0
        self._paint_radius_size = 0.
        self._paint_radius = 0.
        self._paint_double_border_width = 0.
        self._paint_width_minus_border_width = 0.
        self._paint_height_minus_border_width = 0.
        self._paint_radius_minus_border_width = 0.
        self._color = clutter.color_from_string('Black')
        self._border_color = clutter.color_from_string('Black')
        self._border_width = 0.0
        self._texture = texture
    
    def get_clutter_color(self, color):
        if isinstance(color, tuple):
            c = clutter.Color(*color)
        else:
            c = clutter.color_from_string(color)
        return c
    
    def set_texture(self, texture):
        self._texture = texture
        self.queue_redraw()
    
    def set_radius(self, radius):
        self._radius = radius
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[0], self._allocation_box[3] - self._allocation_box[1])
        self.queue_redraw()
    
    def set_inner_color(self, color):
        self._color = self.get_clutter_color(color)
        self.queue_redraw()
    
    def set_color(self, color):
        self.set_inner_color(color)
    
    def set_border_color(self, color):
        self._border_color = self.get_clutter_color(color)
        self.queue_redraw()
    
    def set_border_width(self, width):
        self._border_width = width
        self._calculate_paint_values(self._allocation_box[2] - self._allocation_box[0], self._allocation_box[3] - self._allocation_box[1])
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
            cogl.path_round_rectangle(0, 0, width, height, self._paint_radius, 1)
            cogl.path_close()
            cogl.set_source_color(border_color)
            cogl.path_fill()
            
            cogl.path_round_rectangle(self._border_width, self._border_width, self._paint_width_minus_border_width, self._paint_height_minus_border_width, self._paint_radius_minus_border_width, 1)
            cogl.path_close()
            cogl.set_source_color(color)
            cogl.path_fill()
            
            # texture
            if self._texture:
                cogl.path_round_rectangle(self._border_width, self._border_width, self._paint_width_minus_border_width, self._paint_height_minus_border_width, self._paint_radius_minus_border_width, 1)
                cogl.path_close()
                cogl.set_source_texture(self._texture)
                cogl.path_fill()
        else:
            cogl.path_round_rectangle(0, 0, width, height, self._paint_radius, 1)
            cogl.path_close()
            cogl.set_source_color(color)
            cogl.path_fill()
    
    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()
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
        self._paint_radius_minus_border_width = self._paint_radius - self._border_width
    
    def do_destroy(self):
        self.unparent()


if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    rect = OutlinedRoundRectangle()
    rect.set_radius(10)
    rect.set_width(5)
    rect.set_color('#ff0000ff')
    rect.set_size(160, 120)
    rect.set_anchor_point(80, 60)
    rect.set_position(160, 240)
    stage.add(rect)
    
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
            gobject.timeout_add_seconds(1, set_width, rect)
            return False
        return True
    gobject.timeout_add_seconds(1, set_radius, rect)
    
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
        texture = cogl.texture_new_from_file(texture_path, clutter.cogl.TEXTURE_NO_SLICING, clutter.cogl.PIXEL_FORMAT_ANY)
        
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

