#!/usr/bin/env python
# -*- coding: utf-8 -*

class Margin():
    def __init__(self, value, xy_only=False):
        self._attr_name = 'margin'
        if isinstance(value, int):
            self.left = value
            self.right = value
            self.top = value
            self.bottom = value
        elif isinstance(value, tuple):
            if len(value) == 2:
                self.left = value[0]
                self.right = value[0]
                self.top = value[1]
                self.bottom = value[1]
            elif xy_only:
                raise ValueError('Invalid value for %s, %s must be a tuple with 2 values' %(self._attr_name, self._attr_name, len(value)))
            elif len(value) == 4:
                self.top = value[0]
                self.right = value[1]
                self.bottom = value[2]
                self.left = value[3]
            else:
                raise ValueError('Invalid value for %s, %s must be a tuple with 2 or 4 values' %(self._attr_name, self._attr_name, len(value)))
        else:
            raise ValueError('Invalid value for %s, %s must be a int or a tuple' %(self._attr_name, self._attr_name, len(value)))
        
        if self.left == self.right:
            self.x = self.left
        else:
            self.x = int((self.left + self.right) / 2)
        
        if self.top == self.bottom:
            self.y = self.top
        else:
            self.y = int((self.top + self.bottom) / 2)

class Padding(Margin):
    def __init__(self, value, xy_only=False):
        Margin.__init__(self, value, xy_only=xy_only)
        self._attr_name = 'padding'

class Spacing(Margin):
    def __init__(self, value, xy_only=True):
        Margin.__init__(self, value, xy_only=xy_only)
        self._attr_name = 'spacing'


