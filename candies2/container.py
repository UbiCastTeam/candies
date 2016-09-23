#!/usr/bin/env python
# -*- coding: utf-8 -*

from gi.repository import Clutter


class BaseContainer(Clutter.Actor, Clutter.Container):

    """A container class wich implements all standard container functions."""

    __gtype_name__ = 'BaseContainer'

    def __init__(self, allow_add=False, allow_remove=False, pick_enabled=True):
        Clutter.Actor.__init__(self)
        self._children = list()
        self.__allow_add = allow_add
        self.__allow_remove = allow_remove
        self.__pick_enabled = pick_enabled

    def has_child(self, obj):
        return obj in self._children

    def do_add(self, *children):
        if self.__allow_add:
            for child in children:
                if child in self._children:
                    raise Exception(
                        'Actor %s is already a children of %s' % (child, self))
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
                    raise Exception(
                        'Actor %s is not a child of %s' % (child, self))
        else:
            raise Exception('removing actor to %s is not authorized' % self)

    def _add(self, child):
        if child not in self._children:
            child.set_parent(self)
            self._children.append(child)

    def _remove(self, child):
        if child in self._children:
            self._children.remove(child)
            child.unparent()

    def do_foreach(self, func, data=None):
        for child in self._children:
            func(child, data)

    def do_paint(self):
        for actor in self._children:
            actor.paint()

    def do_pick(self, color):
        if self.__pick_enabled:
            for actor in self._children:
                actor.paint()
        else:
            Clutter.Actor.do_pick(self, color)

    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_children'):
            for child in self._children:
                child.unparent()
                child.destroy()

    def set_focused(self, boolean):
        if boolean:
            stage = self.get_stage()
            if stage:
                if stage.get_key_focus() != self:
                    self._old_key_focus = stage.get_key_focus()
                stage.set_key_focus(self)
        else:
            stage = self.get_stage()
            if stage and hasattr(self, '_old_key_focus'):
                stage.set_key_focus(self._old_key_focus)

    def get_stage(self):
        obj = self
        if obj.get_parent():
            has_parent = True
            obj = obj.get_parent()
            while has_parent:
                if obj.get_parent():
                    has_parent = True
                    obj = obj.get_parent()
                else:
                    has_parent = False
        if isinstance(obj, Clutter.Stage):
            return obj
        else:
            return None
