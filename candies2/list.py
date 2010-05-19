#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
import re
import gobject
import clutter
from buttons import ClassicButton

class ButtonList(clutter.Actor, clutter.Container):
    __gtype_name__ = 'ButtonList'
    __gproperties__ = {
        'font_name' : ( \
            str, 'font', 'Font name', None, gobject.PARAM_READWRITE \
        ),
    }
    __gsignals__ = {
        'select-event' : ( \
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () \
        ),
    }
    button_class = ClassicButton
    selected_color = 'LightYellow'
    selected_border_color = 'Yellow'
    
    def __init__(self, spacing=0.0, button_height=None, font_name=None, multiselect=False):
        clutter.Actor.__init__(self)
        self._buttons = list()
        self.spacing = spacing
        self.button_height = button_height
        self._font_name = font_name
        self.multiselect = multiselect
        self.selection = list()
        self.props.request_mode = clutter.REQUEST_WIDTH_FOR_HEIGHT
    
    def do_set_property (self, pspec, value):
        if pspec.name == 'font_name':
            self._font_name = value
            for btn in self._buttons:
                btn.label.set_font_name(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def do_get_property (self, pspec):
        if pspec.name == 'font_name':
            return self._font_name
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def add(self, *labels):
        for label in labels:
            button = self.button_class(label)
            if self._font_name is not None:
                button.label.set_font_name(self._font_name)
            button.set_parent(self)
            button.set_reactive(True)
            button.connect('button-press-event', self.on_button_press)
            self._buttons.append(button)
    
    def do_remove(self, *children):
        for child in children:
            if child in self._buttons:
                self._buttons.remove(child)
                child.unparent()
    
    def clear(self):
        for btn in self._buttons:
            btn.destroy()
        self._buttons = list()
        self.selection = list()
    
    def on_button_press(self, button, event):
        if self.multiselect:
            if button in self.selection:
                button.rect.set_color(button.default_color)
                button.rect.set_border_color(button.default_border_color)
                self.selection.remove(button)
            else:
                button.rect.set_color(self.selected_color)
                button.rect.set_border_color(self.selected_border_color)
                self.selection.append(button)
        else:
            for btn in self.selection:
                btn.rect.set_color(btn.default_color)
                btn.rect.set_border_color(btn.default_border_color)
            button.rect.set_color(self.selected_color)
            button.rect.set_border_color(self.selected_border_color)
            self.selection = [button,]
        self.emit('select-event')
        return True
    
    def _compute_preferred_size(self):
        min_w = min_h = nat_w = nat_h = 0.0
        for btn in self._buttons:
            s = btn.get_preferred_size()
            min_w = max(min_w, s[0])
            min_h += s[1]
            nat_w = max(nat_w, s[2])
            nat_h += s[3]
        nb_buttons = len(self._buttons)
        if self.button_height is not None:
            nat_h = self.button_height * nb_buttons 
            min_h = nat_h
        if nb_buttons > 1:
            total_spacing = (nb_buttons - 1) * self.spacing
            min_h += total_spacing
            nat_h += total_spacing
        return min_w, min_h, nat_w, nat_h
    
    def do_get_preferred_width(self, for_height):
        preferred = self._compute_preferred_size()
        return preferred[0], preferred[2]
    
    def do_get_preferred_height(self, for_width):
        preferred = self._compute_preferred_size()
        return preferred[1], preferred[3]
    
    def do_allocate(self, box, flags):
        list_width = box.x2 - box.x1
        
        y = 0.0
        for button in self._buttons:
            button.set_width(list_width)
            btnbox = clutter.ActorBox()
            btnbox.x1 = 0.0
            btnbox.y1 = y
            btnbox.x2 = list_width
            if self.button_height is None:
                y += button.get_preferred_height(list_width)[1]
            else:
                button.set_height(self.button_height)
                y += self.button_height
            btnbox.y2 = y
            button.allocate(btnbox, flags)
            y += self.spacing
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for btn in self._buttons:
            func(btn, data)
    
    def do_paint(self):
        for btn in self._buttons:
            btn.paint()
    
    def do_pick(self, color):
        for btn in self._buttons:
            btn.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_buttons'):
            for btn in self._buttons:
                btn.unparent()
                btn.destroy()
            self._buttons = list()

class FileList(ButtonList):
    __gtype_name__ = 'FileList'
    __gproperties__ = {
        'directory' : ( \
            str, 'directory', 'Path to directory', '.', gobject.PARAM_READWRITE \
        ),
    }
    file_pattern = re.compile('.*')
    
    def __init__(self, directory, file_pattern=None):
        ButtonList.__init__(self)
        self._directory = directory
        if file_pattern is not None:
            if isinstance(file_pattern, (str, unicode)):
                file_pattern = re.compile(file_pattern)
            self.file_pattern = file_pattern
        self.populate()

    def do_get_property(self, pspec):
        if pspec.name == 'directory':
            return self._directory
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'directory':
            self._directory = os.path.abspath(os.path.expanduser(value))
            self.refresh()
    
    def populate(self):
        files = os.listdir(self._directory)
        for filename in files:
            if self.file_pattern.match(filename):
                self.add(filename)
    
    def refresh(self):
        self.clear()
        self.populate()


if __name__ == '__main__':
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)
    
    lst = ButtonList(spacing=16, font_name="Sans 18", button_height=48)#, multiselect=True)
    lst.button_height = 64
    lst.set_position(160, 96)
    lst.set_size(320, 240)
    lst.add('Hello World!')
    lst.add('Happy New Year!', 'Merry Christmas!')
    lst.add('Goodbye cruel world!')

    stage.add(lst)
    stage.show()

    clutter.main()
