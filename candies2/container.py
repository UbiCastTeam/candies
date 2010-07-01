#!/usr/bin/env python
# -*- coding: utf-8 -*

class ContainerAdapter:
    """
    An abstract container class to be subclass by common Candies containers.
    """
    def __init__(self):
        self._children = []

    def do_add(self, *children):
        for child in children:
            if child in self._children:
                raise Exception("Actor %s is already a children of %s" % (
                    child, self))
            self._children.append(child)
            child.set_parent(self)
            self.queue_relayout()
    
    def do_remove(self, *children):
        for child in children:
            if child in self._children:
                self._children.remove(child)
                child.unparent()
                self.queue_relayout()
            else:
                raise Exception("Actor %s is not a child of %s" % (
                    child, self))

    def do_get_preferred_width(self, for_height):
        raise NotImplementedError('do_get_preferred_width')

    def do_get_preferred_height(self, for_width):
        raise NotImplementedError('do_get_preferred_height')

    def do_allocate(self, box, flags):
        raise NotImplementedError('do_allocate')
    
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

