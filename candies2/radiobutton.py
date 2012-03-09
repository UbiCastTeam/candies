#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter
from checkbox import CheckButton, CheckBox


class RadioButton(CheckButton):
    __gtype_name__ = 'RadioButton'
    
    def __init__(self, name='', not_checked_image_path=None, checked_image_path=None, checked=False, callback=None, user_data=None):
        CheckButton.__init__(self, name=name, not_checked_image_path=not_checked_image_path, checked_image_path=checked_image_path, checked=checked, callback=callback, user_data=user_data)
        self._related_buttons = list()
    
    def set_related_buttons(self, buttons):
        # related buttons list must be a list of RadioButton
        self._related_buttons = list(buttons)
        if self in self._related_buttons:
            self._related_buttons.remove(self)
        checked_found = False
        for btn in self._related_buttons:
            if btn.checked:
                if checked_found:
                    btn.set_checked(False)
                else:
                    checked_found = True
    
    def _on_press(self, source, event):
        if not self.checked:
            self.set_selected()
    
    def set_selected(self):
        self.set_checked(True)
        for btn in self._related_buttons:
            btn.set_checked(False)


class RadioBox(CheckBox):
    __gtype_name__ = 'RadioBox'
    
    def __init__(self, label='RadioBox', checked=False, callback=None, spacing=20, size=64):
        CheckBox.__init__(self, label=label, checked=checked, callback=callback, spacing=spacing, size=size)
        self._related_buttons = list()
    
    def set_related_buttons(self, buttons):
        # related buttons list must be a list of RadioButton
        self._related_buttons = buttons
        checked_found = False
        for btn in self._related_buttons:
            if btn.checked:
                if not checked_found:
                    checked_found = True
                else:
                    btn.set_checked(False)
    
    def _on_press(self, source, event):
        if not self.checked:
            self.toggle_check()
            self.on_press()
            for btn in self._related_buttons:
                btn.set_checked(False)
    
    def set_selected(self, boolean):
        self.set_checked(boolean)
        for btn in self._related_buttons:
            btn.set_checked(False)

