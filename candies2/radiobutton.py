#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter
from checkbox import CheckBox

class RadioButton(CheckBox):
    __gtype_name__ = 'RadioButton'
    
    def __init__(self, label='RadioButton', checked=False, callback=None, spacing=20, size=64):
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
            for btn in self._related_buttons:
                btn.set_checked(False)
    
    def set_selected(self, boolean):
        self.set_checked(boolean)
    
    


