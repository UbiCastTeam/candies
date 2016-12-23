#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Clutter
import common
from container import BaseContainer


class LightList(BaseContainer):

    '''
    LightList is a light weight list to optimize long list with scrollbars
    All elements in this list will have the same height
    '''

    def __init__(self, element_size=50, padding=0, spacing=0, horizontal=False):
        BaseContainer.__init__(self, allow_add=True, allow_remove=True)
        self.element_size = element_size
        self._horizontal = horizontal
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)

    def get_children(self):
        return self._children

    def add_actor_after(self, actor, after):
        if actor in self._children:
            raise Exception(
                'Actor %s is already a children of %s' % (actor, self))
        try:
            index = self._children.index(after)
        except ValueError:
            raise ValueError(
                'Actor %s is not a children of %s' % (after, self))
        actor.set_parent(self)
        self._children.insert(index, actor)
        self.queue_relayout()

    def insert(self, index, actor):
        if actor in self._children:
            raise Exception(
                'Actor %s is already a children of %s' % (actor, self))
        actor.set_parent(self)
        self._children.insert(index, actor)
        self.queue_relayout()

    def clear(self):
        for child in self._children:
            child.unparent()
            child.destroy()
        self._children = list()
        self.queue_relayout()

    def remove(self, child_or_index):
        if child_or_index in self._children:
            child = child_or_index
            index = self._children.index(child)
        elif child_or_index < len(self._children):
            index = child_or_index
            child = self._children[index]
        child.unparent()
        self._children.pop(index)
        self.queue_relayout()
        return child

    def remove_all(self):
        for child in self._children:
            child.unparent()
        self._children = list()
        self.queue_relayout()

    def index(self, child):
        return self._children.index(child)

    def do_get_preferred_width(self, for_height):
        preferred_width = 2 * self._padding.x
        if self._children:
            if self._horizontal:
                preferred_width += len(self._children) * (
                    self.element_size + self._spacing.x) - self._spacing.x
            else:
                if for_height == -1:
                    h = for_height - 2 * self._padding.y
                else:
                    h = for_height
                preferred_width += self._children[0].get_preferred_width(
                    for_height=h)[1]
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        preferred_height = 2 * self._padding.y
        if self._children:
            if self._horizontal:
                if for_width == -1:
                    w = for_width - 2 * self._padding.x
                else:
                    w = for_width
                preferred_height += self._children[0].get_preferred_height(
                    for_width=w)[1]
            else:
                preferred_height += len(self._children) * (
                    self.element_size + self._spacing.y) - self._spacing.y
        return preferred_height, preferred_height

    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        x = self._padding.x
        y = self._padding.y
        if self._horizontal:
            for child in self._children:
                child_box = Clutter.ActorBox()
                child_box.x1 = x
                child_box.y1 = y
                child_box.x2 = x + self.element_size
                child_box.y2 = height - self._padding.y
                x += self.element_size + self._spacing.x
                child.allocate(child_box, flags)
        else:
            for child in self._children:
                child_box = Clutter.ActorBox()
                child_box.x1 = x
                child_box.y1 = y
                child_box.x2 = width - self._padding.x
                child_box.y2 = y + self.element_size
                y += self.element_size + self._spacing.y
                child.allocate(child_box, flags)
        Clutter.Actor.do_allocate(self, box, flags)

    def set_clip(self, x_offset, y_offset, width, height):
        if self._horizontal:
            displayed_x1 = x_offset
            displayed_x2 = x_offset + width
            x = self._padding.x
            for child in self._children:
                x1 = x
                x2 = x + self.element_size
                if x1 < displayed_x2 and x2 > displayed_x1:
                    child.show()
                else:
                    child.hide()
                x = x2 + self._spacing.x
        else:
            displayed_y1 = y_offset
            displayed_y2 = y_offset + height
            y = self._padding.y
            for child in self._children:
                y1 = y
                y2 = y + self.element_size
                if y1 < displayed_y2 and y2 > displayed_y1:
                    child.show()
                else:
                    child.hide()
                y = y2 + self._spacing.y
        Clutter.Actor.set_clip(self, x_offset, y_offset, width, height)

    def remove_clip(self):
        for child in self._children:
            child.show()
        Clutter.Actor.remove_clip(self)

if __name__ == '__main__':
    stage = Clutter.Stage()
    stage.connect('destroy', Clutter.main_quit)
    stage.set_size(700, 700)
    stage.set_color('#000000ff')

    color = 0
    elements = list()
    for i in range(5):
        r = Clutter.Rectangle()
        color += 30
        r.set_color((color, color, color, 255))
        elements.append(r)

    lst = LightList(spacing=15, horizontal=True)
    lst.add(*elements)
    lst.set_position(50, 50)
    lst.set_height(600)

    stage.add(lst)
    stage.show()

    Clutter.main()
