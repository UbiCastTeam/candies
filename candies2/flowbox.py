#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
from gi.repository import Clutter
from container import BaseContainer


class FlowBox(BaseContainer):

    """
    A Flow container.

    This is an horizontal Box container which can wraps on several lines.
    """
    __gtype_name__ = 'FlowBox'

    def __init__(self, orientation=0):
        BaseContainer.__init__(self)
        self._orientation = orientation

    def do_add(self, *children):
        for child in children:
            if child in self._children:
                raise Exception("Actor %s is already a children of %s" % (
                    child, self))
            self._add(child)
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
        # sys.stdout.write('do_get_preferred_width(%s)' %(for_height))
        min_width = 0
        natural_width = 0
        for child in self._children:
            if not child.props.visible:
                continue
            child_min_width, child_natural_width = child.get_preferred_width(
                for_height)
            min_width += child_min_width
            natural_width += child_natural_width
        # print ' ->', (min_width, natural_width)
        return (min_width, natural_width)

    def do_get_preferred_height(self, for_width):
        # sys.stdout.write('do_get_preferred_height(%s)' %(for_width))
        lines = self._map_lines(for_width)
        minimal_height = reduce(operator.add, (l['height'] for l in lines))
        # print ' ->', (minimal_height, minimal_height)
        return (minimal_height, minimal_height)

    def _map_lines(self, box_width):
        lines = list()
        line_dict = dict(actors=list(), width=0, height=0)
        for child in self._children:
            if not child.props.visible:
                continue
            w, h = child.get_preferred_size()[2:]
            if line_dict['width'] > 0 and line_dict['width'] + w > box_width:
                lines.append(line_dict)
                line_dict = dict(actors=list(), width=0, height=0)
            line_dict['height'] = max(h, line_dict['height'])
            line_dict['width'] += w
            line_dict['actors'].append(child)
        if line_dict['actors']:
            lines.append(line_dict)
            line_dict['height']
        return lines

    def do_allocate(self, box, flags):
        box_width, box_height = self.get_preferred_size()[2:]
        # print box_width, 'x', box_height

        lines = self._map_lines(box_width)
        minimal_height = reduce(operator.add, (l['height'] for l in lines))

        vspacing = 0
        nb_lines = len(lines)
        if nb_lines > 1:
            vspacing = (box_height - minimal_height) / float(nb_lines - 1)
        y = 0
        for line_dict in lines:
            hspacing = 0
            nb_actors = len(line_dict['actors'])
            if nb_actors > 1:
                hspacing = \
                    (box_width - line_dict['width']) / float(nb_actors - 1)
            x = 0
            for child in line_dict['actors']:
                w, h = child.get_preferred_size()[2:]
                child_box = Clutter.ActorBox()
                child_box.x1 = x
                child_box.y1 = y
                child_box.x2 = child_box.x1 + w
                child_box.y2 = child_box.y1 + h
                child.allocate(child_box, flags)
                x += w + hspacing
            y += line_dict['height'] + vspacing

        Clutter.Actor.do_allocate(self, box, flags)

if __name__ == '__main__':
    def create_box():
        import random
        box = FlowBox()
        for i in range(10):
            rect = Clutter.Rectangle()
            color = Clutter.color_from_string(
                random.randint(0, 255), random.randint(0, 255),
                random.randint(0, 255), 255
            )
            rect.set_color(color)
            rect.set_size(50, 50)
            box.add(rect)
        return box

    stage = Clutter.Stage()
    stage.connect('destroy', Clutter.main_quit)

    box1 = create_box()
    box1.set_width(640)
    box2 = create_box()
    box2.set_size(299, 115)
    box2.set_y(85)
    box3 = create_box()
    box3.set_size(199, 250)
    box3.set_y(225)
    stage.add(box1, box2, box3)

    stage.show()
    Clutter.main()
