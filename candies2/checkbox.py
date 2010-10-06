#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter
from text import TextContainer
from container import BaseContainer

class CheckBox(BaseContainer):
    __gtype_name__ = 'CheckBox'
    
    def __init__(self, label='Checkbox', checked=False, callback=None, spacing=20, size=64, user_data=None):
        BaseContainer.__init__(self)
        self._children = list()
        self.checked = checked
        self.callback = callback
        self.user_data = user_data
        self.spacing = 16
        self._image_size = size
        self._checked_image_path = None
        self._not_checked_image_path = None
        
        self._label = TextContainer(label, padding=0, rounded=False)
        self._label.set_inner_color('#00000000')
        
        self._image = clutter.Texture()
        
        self._catcher = clutter.Rectangle()
        self._catcher.set_color('#00000000')
        self._catcher.connect('button-release-event',self._on_press)
        self._catcher.set_reactive(True)
        
        self._add(self._image)
        self._add(self._label)
        self._add(self._catcher)
    
    def set_text(self, text):
        self._label.set_text(text)
    
    def set_font_name(self, font_name):
        self._label.set_font_name(font_name)
    
    def set_font_color(self, font_color):
        self._label.set_font_color(font_color)
    
    def _on_press(self, source, event):
        self.toggle_check()
    
    def toggle_check(self):
        self.checked = not self.checked
        self.refresh_image()
        if self.callback is not None:
            if self.user_data is not None:
                self.callback(self.checked, self.user_data)
            else:
                self.callback(self.checked)

    def set_lock(self, status):
        if status:
            self._catcher.set_reactive(False)
            self.set_opacity(128)
        else:
            self._catcher.set_reactive(True)
            self.set_opacity(255)

    def set_checked(self, boolean):
        if boolean and not self.checked:
            self.toggle_check()
        elif not boolean and self.checked:
            self.toggle_check()
    
    def refresh_image(self):
        if self.checked:
            if self._checked_image_path:
                self._image.set_from_file(self._checked_image_path)
        else:
            if self._not_checked_image_path:
                self._image.set_from_file(self._not_checked_image_path)
    
    def set_checked_image_path(self, path):
        self._checked_image_path = path
        self.refresh_image()
    
    def set_not_checked_image_path(self, path):
        self._not_checked_image_path = path
        self.refresh_image()
    
    def do_get_preferred_width(self, for_height):
        preferred_width = self._image_size + self.spacing + self._label.get_preferred_width(for_height)[1]
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        preferred_height = max(self._image_size, self._label.get_preferred_height(for_width)[1])
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        
        checkbox_size = height
        base_y = 0
        if self._image_size < height:
            checkbox_size = self._image_size
            base_y = int((height - checkbox_size) / 2.0)
        checkbox_box = clutter.ActorBox()
        checkbox_box.x1 = 0
        checkbox_box.y1 = base_y
        checkbox_box.x2 = checkbox_size
        checkbox_box.y2 = base_y + checkbox_size
        self._image.allocate(checkbox_box, flags)
        
        label_box = clutter.ActorBox()
        label_box.x1 = checkbox_box.x2 + self.spacing
        label_box.y1 = 0
        label_box.x2 = width
        label_box.y2 = height
        self._label.allocate(label_box, flags)
        
        catcher_box = clutter.ActorBox(0, 0, width, height)
        self._catcher.allocate(catcher_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)


