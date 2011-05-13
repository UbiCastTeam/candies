#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter
from text import TextContainer
from container import BaseContainer


class CheckButton(clutter.Texture):
    __gtype_name__ = 'CheckButton'
    """
    A check button
    """
    
    def __init__(self, name='', not_checked_image_path=None, checked_image_path=None, checked=False, callback=None, user_data=None):
        clutter.Texture.__init__(self)
        self.name = name
        self.not_checked_image_path = not_checked_image_path
        self.checked_image_path = checked_image_path
        if checked:
            self.checked = True
            if self.checked_image_path:
                self.set_from_file(self.checked_image_path)
        else:
            self.checked = False
            if self.not_checked_image_path:
                self.set_from_file(self.not_checked_image_path)
        self.callback = callback
        self.user_data = user_data
        self.set_reactive(True)
        self.connect('button-release-event',self._on_press)
    
    def _on_press(self, source, event):
        self.toggle_check()
    
    def toggle_check(self):
        if self.checked:
            self.checked = False
            self.set_from_file(self.not_checked_image_path)
        else:
            self.checked = True
            self.set_from_file(self.checked_image_path)
        if self.callback is not None:
            if self.user_data is not None:
                self.callback(self.checked, self.user_data)
            else:
                self.callback(self.checked)
    
    def set_checked(self, boolean):
        if boolean != self.checked:
            self.toggle_check()
    
    def set_lock(self, lock):
        self.set_reactive(not lock)
        self.set_opacity(128 if lock else 255)
    
    def set_checked_image_path(self, path):
        self.checked_image_path = path
        self.refresh_image()
    
    def set_not_checked_image_path(self, path):
        self.not_checked_image_path = path
        self.refresh_image()
    
    def refresh_image(self):
        if self.checked:
            if self.checked_image_path:
                self.set_from_file(self.checked_image_path)
        else:
            if self.not_checked_image_path:
                self.set_from_file(self.not_checked_image_path)


class CheckBox(BaseContainer):
    __gtype_name__ = 'CheckBox'
    """
    A check button with a label
    """
    
    def __init__(self, label='Checkbox', checked=False, callback=None, spacing=16, size=64, image_placement='left', user_data=None):
        BaseContainer.__init__(self, pick_enabled=False)
        self._children = list()
        self.checked = checked
        self.callback = callback
        self.user_data = user_data
        self.spacing = spacing
        self._image_size = size
        self._image_placement = image_placement
        self._checked_image_path = None
        self._not_checked_image_path = None
        
        self._label = TextContainer(label, padding=0, rounded=False)
        self._label.set_inner_color('#00000000')
        
        self._image = clutter.Texture()
        
        self.set_reactive(True)
        self.connect('button-release-event',self._on_press)
        
        self._add(self._image)
        self._add(self._label)
    
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
            self.set_reactive(False)
            self.set_opacity(128)
        else:
            self.set_reactive(True)
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
        
        if self._image_size < height:
            checkbox_size = self._image_size
            image_base_y = int((height - checkbox_size) / 2.0)
        else:
            image_base_y = 0
        
        checkbox_box = clutter.ActorBox()
        checkbox_box.y1 = image_base_y
        checkbox_box.y2 = image_base_y + checkbox_size
        
        label_box = clutter.ActorBox()
        label_box.y1 = 0
        label_box.y2 = height
        
        if self._image_placement == 'left':
            checkbox_box.x1 = 0
            checkbox_box.x2 = checkbox_size
            label_box.x1 = checkbox_box.x2 + self.spacing
            label_box.x2 = width
        else:
            checkbox_box.x1 = width - checkbox_size
            checkbox_box.x2 = width
            label_box.x1 = 0
            label_box.x2 = checkbox_box.x1 - self.spacing
        
        self._image.allocate(checkbox_box, flags)
        self._label.allocate(label_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)

#main to test
if __name__ == '__main__':
    stage = clutter.Stage()
    stage.connect('destroy',clutter.main_quit)
    
    def callback(checked):
        print checked
    
    checkbox = CheckBox('Test', callback=callback)
    checkbox.set_reactive(True)
    checkbox.set_position(50, 50)
    stage.add(checkbox)

    stage.show()
    clutter.main()
