#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter

class BaseContainer(clutter.Actor, clutter.Container):
    '''
    A container class wich implements all standard container functions.
    '''
    __gtype_name__ = 'BaseContainer'
    
    def __init__(self, allow_add=False, allow_remove=False):
        clutter.Actor.__init__(self)
        self._children = list()
        self.__allow_add = allow_add
        self.__allow_remove = allow_remove
    
    def do_add(self, *children):
        if self.__allow_add:
            for child in children:
                if child in self._children:
                    raise Exception('Actor %s is already a children of %s' % (child, self))
                child.set_parent(self)
                self._children.append(child)
                self.queue_relayout()
        else:
            raise Exception('adding actor to %s is not authorized' % self)
    
    def do_remove(self, *children):
        if self.__allow_remove:
            for child in children:
                if child in self._children:
                    self._children.remove(child)
                    child.unparent()
                    self.queue_relayout()
                else:
                    raise Exception('Actor %s is not a child of %s' % (child, self))
        else:
            raise Exception('removing actor to %s is not authorized' % self)
    
    def _add(self, child):
        if child not in self._children:
            child.set_parent(self)
            self._children.append(child)
    
    def _remove(self, child):
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



