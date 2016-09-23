#!/usr/bin/env python
# -*- coding: utf-8 -*


class Margin(object):
    ATTR_NAME = 'margin'

    def __init__(self, value, xy_only=False):
        object.__init__(self)
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
                raise ValueError('Invalid value for %s, %s must be a tuple with 2 values' %
                                 (self.ATTR_NAME, self.ATTR_NAME))
            elif len(value) == 4:
                self.top = value[0]
                self.right = value[1]
                self.bottom = value[2]
                self.left = value[3]
            else:
                raise ValueError('Invalid value for %s, %s must be a tuple with 2 or 4 values' %
                                 (self.ATTR_NAME, self.ATTR_NAME))
        else:
            raise ValueError('Invalid value for %s, %s must be a int or a tuple' %
                             (self.ATTR_NAME, self.ATTR_NAME))

        if self.left == self.right:
            self.x = self.left
        else:
            self.x = int((self.left + self.right) / 2)

        if self.top == self.bottom:
            self.y = self.top
        else:
            self.y = int((self.top + self.bottom) / 2)


class Padding(Margin):
    ATTR_NAME = 'padding'

    def __init__(self, value, xy_only=False):
        Margin.__init__(self, value, xy_only=xy_only)


class Spacing(Margin):
    ATTR_NAME = 'spacing'

    def __init__(self, value, xy_only=True):
        Margin.__init__(self, value, xy_only=xy_only)
