#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter
import common


class Aligner(Clutter.Actor, Clutter.Container):

    ALIGNMENT = ('top_left', 'top', 'top_right', 'left',
                 'center', 'right', 'bottom_left', 'bottom', 'bottom_right')

    def __init__(self, align='center', margin=0, padding=0, expand=False, keep_ratio=True, pick_enabled=True):
        Clutter.Actor.__init__(self)
        self._margin = common.Margin(margin)
        self._padding = common.Padding(padding)
        if align in self.ALIGNMENT:
            self.align = align
        else:
            self.align = 'center'
        self.expand = expand
        self.keep_ratio = keep_ratio
        self.element = None
        self.background = None
        self.pick_enabled = pick_enabled

    def set_background(self, background):
        if self.background is not None:
            self.background.unparent()
        self.background = background
        background.set_parent(self)

    def remove_background(self):
        if self.background is not None:
            self.background.unparent()
            self.background = None

    def get_element(self):
        return self.element

    def set_element(self, new_element):
        if self.element is not None:
            self.element.unparent()
        self.element = new_element
        self.element.set_parent(self)

    def remove_element(self):
        if self.element is not None:
            self.element.unparent()
            self.element = None

    def do_remove(self, actor):
        if self.background == actor:
            actor.unparent()
            self.background = None
        if self.element == actor:
            actor.unparent()
            self.elements = None

    def clear(self):
        if self.element is not None:
            self.element.destroy()
            self.element = None
        if self.background is not None:
            self.background.destroy()
            self.background = None

    def do_get_preferred_width(self, for_height):
        preferred_width = 2 * self._margin.x + 2 * self._padding.x

        if self.element:
            if for_height != -1:
                h = for_height - 2 * self._margin.y - 2 * self._padding.y
            else:
                h = for_height

            element_width, element_height = self.element.get_preferred_size()[
                2:]
            if self.expand:
                if self.keep_ratio and element_width != 0 and element_height != 0 and h > 0:
                    ratio = float(element_width) / float(element_height)
                    preferred_width += int(h * ratio)
                else:
                    preferred_width += int(
                        self.element.get_preferred_width(h)[1])
            else:
                if element_width != 0 and element_height != 0 and h > 0 and element_height > h:
                    ratio = float(element_width) / float(element_height)
                    preferred_width += int(h * ratio)
                else:
                    preferred_width += int(
                        self.element.get_preferred_width(h)[1])

        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        preferred_height = 2 * self._margin.y + 2 * self._padding.y

        if self.element:
            if for_width != -1:
                w = for_width - 2 * self._margin.x - 2 * self._padding.x
            else:
                w = for_width

            element_width, element_height = self.element.get_preferred_size()[
                2:]
            if self.expand:
                if self.keep_ratio and element_width != 0 and element_height != 0 and w > 0:
                    ratio = float(element_width) / float(element_height)
                    preferred_height += int(w / ratio)
                else:
                    preferred_height += int(
                        self.element.get_preferred_height(w)[1])
            else:
                if element_width != 0 and element_height != 0 and w > 0 and element_height > w:
                    ratio = float(element_width) / float(element_height)
                    preferred_height += int(w / ratio)
                else:
                    preferred_height += int(
                        self.element.get_preferred_height(w)[1])

        return preferred_height, preferred_height

    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        inner_width = width - 2 * self._margin.x - 2 * self._padding.x
        inner_height = height - 2 * self._margin.y - 2 * self._padding.y

        # allocate background
        if self.background:
            bgbox = Clutter.ActorBox()
            bgbox.x1 = self._margin.x
            bgbox.y1 = self._margin.y
            bgbox.x2 = width - self._margin.x
            bgbox.y2 = height - self._margin.y
            self.background.allocate(bgbox, flags)

        if self.element:
            # get element size
            element_width, element_height = self.element.get_preferred_size()[
                2:]
            if self.expand:
                if self.keep_ratio and element_width != 0 and element_height != 0:
                    ratio = float(element_width) / float(element_height)
                    element_width = inner_width
                    element_height = element_width / ratio
                    if element_height > inner_height:
                        element_height = inner_height
                        element_width = element_height * ratio
                else:
                    element_width = inner_width
                    element_height = inner_height
            else:
                if self.keep_ratio and element_width != 0 and element_height != 0:
                    ratio = float(element_width) / float(element_height)
                    if element_width > inner_width:
                        element_width = inner_width
                        element_height = element_width / ratio
                    if element_height > inner_height:
                        element_height = inner_height
                        element_width = element_height * ratio
                else:
                    if element_width > inner_width:
                        element_width = inner_width
                    if element_height > inner_height:
                        element_height = inner_height

            # apply alignment
            if self.align == 'center':
                base_x = (inner_width - element_width) / 2.0
                base_y = (inner_height - element_height) / 2.0
            else:
                if self.align == 'top_left' or self.align == 'left' or self.align == 'bottom_left':
                    base_x = 0
                elif self.align == 'top_right' or self.align == 'right' or self.align == 'bottom_right':
                    base_x = inner_width - element_width
                else:
                    base_x = (inner_width - element_width) / 2.0

                if self.align.startswith('top'):
                    base_y = 0
                elif self.align.startswith('bottom'):
                    base_y = inner_height - element_height
                else:
                    base_y = (inner_height - element_height) / 2.0

            # allocate element
            elebox = Clutter.ActorBox()
            elebox.x1 = int(self._padding.x + self._margin.x + base_x)
            elebox.y1 = int(self._padding.y + self._margin.y + base_y)
            elebox.x2 = int(elebox.x1 + element_width)
            elebox.y2 = int(elebox.y1 + element_height)
            # print elebox.x1, elebox.y1, elebox.x2, elebox.y2, '--------',
            # width, height
            self.element.allocate(elebox, flags)

        Clutter.Actor.do_allocate(self, box, flags)

    def do_foreach(self, func, data=None):
        if self.background is not None:
            func(self.background, data)
        if self.element is not None:
            func(self.element, data)

    def do_paint(self):
        if self.background is not None:
            self.background.paint()
        if self.element is not None:
            self.element.paint()

    def do_pick(self, color):
        if self.pick_enabled:
            self.do_paint()
        else:
            Clutter.Actor.do_pick(self, color)

    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'background'):
            if self.background:
                self.background.unparent()
                self.background.destroy()
        if hasattr(self, 'element'):
            if self.element:
                self.element.unparent()
                self.element.destroy()


def tester(stage):
    stage_width = 1200
    stage_height = 600
    stage.set_size(stage_width, stage_height)
    stage.set_color(Clutter.color_from_string('#000000ff')[1])

    def on_click(source, event):
        color_a = '#880000ff'
        color_b = '#ff0000ff'
        bg = source.background
        current_color = bg.get_color()
        if str(current_color) == color_a:
            bg.set_color(Clutter.color_from_string(color_b)[1])
        else:
            bg.set_color(Clutter.color_from_string(color_a)[1])

    bg = Clutter.Rectangle()
    bg.set_color(Clutter.color_from_string('#ff0000ff')[1])

    ele = Clutter.Rectangle()
    ele.set_color(Clutter.color_from_string('#00ff00ff')[1])
    ele.set_size(50, 100)

    aligner = Aligner(align='center', expand=False,
                      keep_ratio=False, pick_enabled=False, padding=40)
    aligner.set_background(bg)
    aligner.set_element(ele)
    aligner.set_position(100, 100)
    # aligner.set_size(400, 400)
    aligner.set_reactive(True)
    aligner.connect('button-press-event', on_click)
    stage.add_child(aligner)

if __name__ == '__main__':
    from test import run_test
    run_test(tester)
