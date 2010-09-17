#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter

class BaseContainer(clutter.Actor, clutter.Container):
    """
    A container class wich implements all standard container functions.
    """
    __gtype_name__ = 'BaseContainer'
    
    def __init__(self):
        clutter.Actor.__init__(self)
        self._children = list()
    
    def _add(self, *children):
        for child in children:
            child.set_parent(self)
            self._children.append(child)
    
    def _remove(self, *children):
        for child in children:
            if child in self._children:
                self._children.remove(child)
                child.unparent
    
    def do_foreach(self, func, data=None):
        for child in self._children:
            func(child, data)
        
    def do_paint(self):
        for actor in self._children:
            actor.paint()
    
    def do_pick(self, color):
        for actor in self._children:
            actor.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_children'):
            for child in self._children:
                child.unparent()
                child.destroy()
            self._children = list()



