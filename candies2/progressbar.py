#!/usr/bin/env python
# -*- coding: utf-8 -*

import gobject
import clutter
import os

from clutter import cogl

class ProgressBar(clutter.Actor):
    __gtype_name__ = 'ProgressBar'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'progress': (
            gobject.TYPE_FLOAT, 'Progress', 'Progress value',
            0.0, 1.0, 0.0, gobject.PARAM_READWRITE
        ),
    }

    def __init__(self, texture=None, progress_texture=None):
        clutter.Actor.__init__(self)
        self._radius = 0.0
        self._color = clutter.color_from_string('Black')
        self._border_color = clutter.color_from_string('Grey')
        self._progress_color = clutter.color_from_string('Blue')
        self._border_width = 0.0
        self._texture = texture
        self._progress_texture = progress_texture
        self._progress = 0.0
    
    def set_progress(self, value):
        if value > 1.0: self._progress = 1.0
        elif value < 0.0: self._progress = 0.0
        else: self._progress = value
        self.notify('progress')
        self.queue_relayout()
    
    def get_progress(self):
        return self._progress
    
    def set_texture(self, texture):
        self._texture = texture
        self.queue_redraw()
    
    def set_progress_texture(self, texture):
        self._progress_texture = texture
        self.queue_redraw()
    
    def set_radius(self, radius):
        self._radius = radius
        self.queue_redraw()
    
    def set_inner_color(self, color):
        self._color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_color(self, color):
        self.set_inner_color(color)
    
    def set_border_color(self, color):
        self._border_color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_progress_color(self, color):
        self._progress_color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_border_width(self, width):
        self._border_width = width
        self.queue_redraw()

    def do_set_property(self, pspec, value):
        if pspec.name == 'progress':
            self.set_progress(value)
        elif pspec.name == 'border-color':
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
        if pspec.name == 'progress':
            return self._progress
        elif pspec.name == 'border-color':
            return self._border_color
        elif pspec.name == 'border-width':
            return self._border_width
        elif pspec.name == 'color':
            return self._color
        elif pspec.name == 'radius':
            return self._radius
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def __paint_rectangle(self, width, height, border_color, inner_color=None, progress_color=None):
        # check if size will not cause problem with radius
        radius = self._radius
        if width < 2 * radius:
            radius = int(float(width) / 2.0)
        if height < 2 * radius:
            radius = int(float(height) / 2.0)
        
        # background round rectangle
        clutter.cogl.path_round_rectangle(0, 0, width, height, radius, 1)
        clutter.cogl.path_close()
        clutter.cogl.set_source_color(border_color)
        clutter.cogl.path_fill()
        
        if self._border_width > 0 and inner_color is not None:
            inner_width = int(width - 2*self._border_width)
            inner_height = int(height - 2*self._border_width)
            if inner_width > 0 and inner_height > 0:
                inner_radius = radius - self._border_width
                if inner_width < 2 * inner_radius:
                    new_radius = int(float(inner_width) / 2.0)
                    inner_height -= 2*(inner_radius - new_radius)
                    inner_radius = new_radius
                if inner_height < 2 * inner_radius:
                    new_radius = int(float(inner_height) / 2.0)
                    inner_width -= 2*(inner_radius - new_radius)
                    inner_radius = new_radius
                
                padding_x = int((width - inner_width) / 2.0)
                padding_y = int((height - inner_height) / 2.0)
                
                # foreground round rectangle
                clutter.cogl.path_round_rectangle(padding_x, padding_y, padding_x + inner_width, padding_y + inner_height, inner_radius, 1)
                clutter.cogl.path_close()
                clutter.cogl.set_source_color(inner_color)
                clutter.cogl.path_fill()
                
                # texture
                if self._texture:
                    clutter.cogl.path_round_rectangle(padding_x, padding_y, padding_x + inner_width, padding_y + inner_height, inner_radius, 1)
                    clutter.cogl.path_close()
                    clutter.cogl.set_source_texture(self._texture)
                    clutter.cogl.path_fill()
                
                if progress_color is not None:
                    # progress round rectangle
                    progress_width = int(self._progress * inner_width)
                    progress_height = inner_height
                    if self._progress > 0 and inner_width > 0:
                        progress_radius = inner_radius
                        if progress_width < 2 * progress_radius:
                            new_radius = int(float(progress_width) / 2.0)
                            progress_height -= 2*(progress_radius - new_radius)
                            progress_radius = new_radius
                        if progress_height < 2 * progress_radius:
                            new_radius = int(float(progress_height) / 2.0)
                            progress_width -= 2*(progress_radius - new_radius)
                            progress_radius = new_radius
                        
                        progress_y = int((height - progress_height) / 2.0)
                        clutter.cogl.path_round_rectangle(padding_x, progress_y, padding_x + progress_width, progress_y + progress_height, progress_radius, 1)
                        clutter.cogl.path_close()
                        clutter.cogl.set_source_color(progress_color)
                        clutter.cogl.path_fill()
                        
                        # progress_texture
                        if self._progress_texture:
                            clutter.cogl.path_round_rectangle(padding_x, progress_y, padding_x + progress_width, progress_y + progress_height, progress_radius, 1)
                            clutter.cogl.path_close()
                            clutter.cogl.set_source_texture(self._progress_texture)
                            clutter.cogl.path_fill()
    
    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()
        width = x2 - x1
        height = y2 - y1
        
        inner_color = self._color.copy()
        real_alpha = self.get_paint_opacity() * inner_color.alpha / 255
        inner_color.alpha = real_alpha
        
        border_color = self._border_color.copy()
        real_alpha = self.get_paint_opacity() * border_color.alpha / 255
        border_color.alpha = real_alpha
        
        progress_color = self._progress_color.copy()
        real_alpha = self.get_paint_opacity() * progress_color.alpha / 255
        progress_color.alpha = real_alpha
        
        self.__paint_rectangle(width, height, border_color, inner_color, progress_color)

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return
        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__paint_rectangle(x2 - x1, y2 - y1, pick_color)

    def do_destroy(self):
        self.unparent()

gobject.type_register(ProgressBar)

if __name__ == '__main__':
    def update_label(bar, event, label):
        label.set_text('%d %%' %(bar.get_progress() * 100))
    
    def progress(bar):
        new_progress = round(bar.get_progress() + 0.002, 3)
        bar.set_progress(new_progress)
        return new_progress < 1.0
    
    def on_button_press(stage, event, bar):
        bar.set_progress(0.0)
        gobject.timeout_add(10, progress, bar)
    
    stage = clutter.Stage()
    stage.set_reactive(True)
    stage.connect('destroy', clutter.main_quit)
    
    label = clutter.Text()
    label.set_position(5, 5)
    label.set_text('Click to launch progress...')
    stage.add(label)
    
    bar = ProgressBar()
    bar.set_radius(10)
    bar.set_border_width(5)
    bar.set_color('Cyan')
    bar.set_size(630, 100)
    bar.set_position(5, 30)
    bar.connect('notify::progress', update_label, label)
    stage.add(bar)
    stage.connect('button-press-event', on_button_press, bar)

    stage.show()

    clutter.main()
