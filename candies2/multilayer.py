#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clutter
from container import BaseContainer
import common

class MultiLayerContainer(BaseContainer):
    __gtype_name__ = 'MultiLayerContainer'
    '''
    A container in wich all childs have the same space allocated
    '''
    def __init__(self, margin=0, pick_enabled=True):
        BaseContainer.__init__(self, allow_add=True, allow_remove=True, pick_enabled=pick_enabled)
        self._margin = common.Margin(margin)
    
    def add_actor_after(self, actor, after):
        if actor in self._children:
            raise Exception('Actor %s is already a children of %s' % (actor, self))
        try:
            index = self._children.index(after)
        except ValueError:
            raise ValueError('Actor %s is not a children of %s' %(after, self))
        actor.set_parent(self)
        self._children.insert(index, child)
        self.queue_relayout()
    
    def remove_all(self):
        for child in self._children:
            child.unparent()
        self._children = list()
        self.queue_relayout()
    
    def do_get_preferred_width(self, for_height):
        preferred_width = 2*self._margin.x
        for child in self._children:
            preferred_width = max(preferred_width, child.get_preferred_width(for_height=for_height)[1])
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        preferred_height = 2*self._margin.y
        for child in self._children:
            preferred_height = max(preferred_height, child.get_preferred_height(for_width=for_width)[1])
        return preferred_height, preferred_height
    
    def do_raise_child(self, child, sibling=None):
        if child not in self._children:
            raise Exception('Actor %s is not a child of %s' % (child, self))
        if sibling:
            if sibling not in self._children:
                raise Exception('Actor %s is not a child of %s' % (sibling, self))
            sibling_index = self._children.index(sibling)
            child_index = self._children.index(child)
            self._children[sibling_index] = child
            self._children[child_index] = sibling
        else:
            self._children.remove(child)
            self._children.append(child)
    
    def do_lower_child(self, child, sibling=None):
        if child not in self._children:
            raise Exception('Actor %s is not a child of %s' % (child, self))
        if sibling:
            if sibling not in self._children:
                raise Exception('Actor %s is not a child of %s' % (sibling, self))
            sibling_index = self._children.index(sibling)
            child_index = self._children.index(child)
            self._children[sibling_index] = child
            self._children[child_index] = sibling
        else:
            self._children.remove(child)
            self._children.insert(0, child)
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        for child in self._children:
            child_box = clutter.ActorBox()
            child_box.x1 = self._margin.x
            child_box.y1 = self._margin.y
            child_box.x2 = main_width - self._margin.x
            child_box.y2 = main_height - self._margin.y
            child.allocate(child_box, flags)
        clutter.Actor.do_allocate(self, box, flags)


if __name__ == '__main__':
    # stage
    stage = clutter.Stage()
    stage_width = 1200
    stage_height = 600
    stage.set_size(stage_width, stage_height)
    stage.set_color('#000000ff')
    stage.connect('destroy', clutter.main_quit)
    
    
    rect5 = clutter.Rectangle()
    rect5.set_size(250, 150)
    rect5.set_color('#ff0000ff')
    
    rect6 = clutter.Rectangle()
    rect6.set_size(5, 5)
    rect6.set_color('#00ff0088')
    
    rect_bg_2 = clutter.Rectangle()
    rect_bg_2.set_color('#ffffffff')
    
    test_layer = MultiLayerContainer()
    test_layer.add(rect5, rect6)
    test_layer.set_position(50, 50)
    stage.add(test_layer)
    
    stage.show()
    clutter.main()
    
