#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clutter
import common

class Aligner(clutter.Actor, clutter.Container):
    __gtype_name__ = 'Aligner'
    
    ALIGNMENT = ['top_left', 'top', 'top_right', 'left', 'center', 'right', 'bottom_left', 'bottom', 'bottom_right']

    def __init__(self, align='center', margin=0, padding=0, expand=False, keep_ratio=True, pick_enabled=True):
        clutter.Actor.__init__(self)
        if align in self.ALIGNMENT:
            self.align = align
        else:
            self.align = 'center'
        self._margin = common.Margin(margin)
        self._padding = common.Padding(padding)
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
        if self.element is not None:
            if self.expand:
                preferred_size = self.element.get_preferred_size()
                element_width = preferred_size[2]
                element_height = preferred_size[3]
                if self.keep_ratio and element_width != 0 and element_height != 0 and for_height != -1:
                    ratio = float(float(element_width) / float(element_height))
                    prefered_width = int(for_height * ratio)
                else:
                    prefered_width = element_width
            else:
                if for_height != -1:
                    h = for_height - 2*self._margin.y - 2*self._padding.y
                else:
                    h = for_height
                prefered_width = self.element.get_preferred_width(h)[1]
            prefered_width += 2*self._margin.x + 2*self._padding.x
            return prefered_width, prefered_width
        else:
            return 0, 0
    
    def do_get_preferred_height(self, for_width):
        if self.element is not None:
            if self.expand:
                preferred_size = self.element.get_preferred_size()
                element_width = preferred_size[2]
                element_height = preferred_size[3]
                if self.keep_ratio and element_width != 0 and element_height != 0 and for_width != -1:
                    ratio = float(float(element_height) / float(element_width))
                    prefered_height = int(for_width / ratio)
                else:
                    prefered_height = element_height
            else:
                if for_width != -1:
                    w = for_width - 2*self._margin.x - 2*self._padding.x
                else:
                    w = for_width
                prefered_height = self.element.get_preferred_height(w)[1]
            prefered_height += 2*self._margin.y + 2*self._padding.y
            return prefered_height, prefered_height
        else:
            return 0, 0
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        inner_width = main_width - 2*self._margin.x - 2*self._padding.x
        inner_height = main_height - 2*self._margin.y - 2*self._padding.y
        
        #box background
        if self.background:
            bgbox = clutter.ActorBox()
            bgbox.x1 = self._margin.x
            bgbox.y1 = self._margin.y
            bgbox.x2 = main_width - self._margin.x
            bgbox.y2 = main_height - self._margin.y
            self.background.allocate(bgbox, flags)
        
        if self.element:
            element_width, element_height = self.element.get_preferred_size()[2:]
            if self.expand:
                if self.keep_ratio and element_height != 0:
                    ratio = float(float(element_width) / float(element_height))
                    element_width = inner_width
                    element_height = int(element_width / ratio)
                    if element_width > inner_width:
                        element_width = inner_width
                        element_height = int(element_width / ratio)
                    if element_height > inner_height:
                        element_height = inner_height
                        element_width = int(element_height * ratio)
                    ele_x1 = int((inner_width - element_width)/2)
                    ele_y1 = int((inner_height - element_height)/2)
                    ele_x2 = inner_width - int((inner_width - element_width)/2)
                    ele_y2 = inner_height - int((inner_height - element_height)/2)
                else:
                    ele_x1 = 0
                    ele_y1 = 0
                    ele_x2 = inner_width
                    ele_y2 = inner_height
            else:
                if self.align == 'center':
                    ele_x1 = int((inner_width-element_width)/2)
                    ele_x2 = ele_x1 + element_width
                    ele_y1 = int((inner_height-element_height)/2)
                    ele_y2 = ele_y1 + element_height
                else:
                    if self.align == 'top_left' or self.align == 'left' or self.align == 'bottom_left':
                        ele_x1 = 0
                        ele_x2 = element_width
                    elif self.align == 'top_right' or self.align == 'right' or self.align == 'bottom_right':
                        ele_x1 = inner_width - element_width
                        ele_x2 = inner_width
                    else:
                        ele_x1 = int((inner_width-element_width)/2)
                        ele_x2 = ele_x1 + element_width
                    
                    if self.align.startswith('top'):
                        ele_y1 = 0
                        ele_y2 = element_height
                    elif self.align.startswith('bottom'):
                        ele_y1 = inner_height - element_height
                        ele_y2 = inner_height
                    else:
                        ele_y1 = int((inner_height-element_height)/2)
                        ele_y2 = ele_y1 + element_height
            base_x = self._padding.x + self._margin.x
            base_y = self._padding.y + self._margin.y
            elebox = clutter.ActorBox(base_x + ele_x1, base_y + ele_y1, base_x + ele_x2, base_y + ele_y2)
            #print elebox.x1, elebox.y1, elebox.x2, elebox.y2, '--------', main_width, main_height
            self.element.allocate(elebox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
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
            clutter.Actor.do_pick(self, color)
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'background'):
            if self.background is not None:
                self.background.unparent()
                self.background.destroy()
                self.background = None
        if hasattr(self, 'element'):
            if self.element is not None:
                self.element.unparent()
                self.element.destroy()
                self.element = None


if __name__ == '__main__':
    # stage
    stage = clutter.Stage()
    stage_width = 1200
    stage_height = 600
    stage.set_size(stage_width, stage_height)
    stage.set_color('#000000ff')
    stage.connect('destroy', clutter.main_quit)
    
    def on_click(btn_test, event):
        color_a = '#ff000088'
        color_b = '#ff0000ff'
        current_color = btn_rect.get_color()
        if str(current_color) == color_a:
            btn_rect.set_color(color_b)
        else:
            btn_rect.set_color(color_a)
    btn_test = Aligner(pick_enabled=False)
    btn_rect = clutter.Rectangle()
    btn_rect.set_color('#ff00ffff')
    btn_test.set_background(btn_rect)
    btn_test.set_position(80, 480)
    btn_test.set_size(50, 50)
    btn_test.set_reactive(True)
    btn_test.connect('button-press-event', on_click)
    stage.add(btn_test)
    
    stage.show()
    clutter.main()


