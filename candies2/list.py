#!/usr/bin/env python
# -*- coding: utf-8 -*

import gobject
import clutter
import common
from container import BaseContainer


class LightList(BaseContainer):
    '''
    LightList is a light weight list to optimize long list with scrollbars
    All elements in this list will have the same height
    '''
    __gtype_name__ = 'LightList'
    
    def __init__(self, element_height=50, padding=0, spacing=0):
        BaseContainer.__init__(self, allow_add=True, allow_remove=True)
        self.element_height = element_height
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)
    
    def get_children(self):
        return self._children
    
    def insert(self, index, actor):
        if actor in self._children:
            raise Exception('Actor %s is already a children of %s' % (child, self))
        actor.set_parent(self)
        self._children.insert(index, actor)
        self.queue_relayout()
    
    def do_get_preferred_width(self, for_height):
        preferred_width = 2*self._padding.x
        if self._children:
            if for_height == -1:
                h = for_height - 2*self._padding.y
            else:
                h = for_height
            preferred_width += self._children[0].get_preferred_width(for_height=h)[1]
        return preferred_width, preferred_width
    
    def do_get_preferred_height(self, for_width):
        preferred_height = 2*self._padding.y
        if self._children:
            preferred_height += len(self._children) * (self.element_height + self._spacing.y) - self._spacing.y
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        y = self._padding.y
        for child in self._children:
            child_box = clutter.ActorBox()
            child_box.x1 = self._padding.x
            child_box.y1 = y
            child_box.x2 = width - self._padding.x
            child_box.y2 = y + self.element_height
            child.allocate(child_box, flags)
            y += self.element_height + self._spacing.y
        clutter.Actor.do_allocate(self, box, flags)
    
    def set_clip(self, x_offset, y_offset, width, height):
        displayed_y1 = y_offset
        displayed_y2 = y_offset + height
        y = self._padding.y
        for child in self._children:
            y1 = y
            y2 = y + self.element_height
            if y1 < displayed_y2 and y2 > displayed_y1:
                child.show()
            else:
                child.hide()
            y = y2 + self._spacing.y
    
    def remove_clip(self):
        for child in self._children:
            child.show()

if __name__ == '__main__':
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)
    stage.set_color('#000000ff')
    
    color = 0
    elements = list()
    for i in range(5):
        r = clutter.Rectangle()
        color += 30
        r.set_color((color, color, color))
        elements.apppend(r)
    
    lst = LightList()
    lst.add(*elements)
    lst.set_position(50, 50)
    lst.set_width(600)

    stage.add(lst)
    stage.show()

    clutter.main()


