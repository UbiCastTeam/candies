#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clutter
import common

class Aligner(clutter.Actor, clutter.Container):
    __gtype_name__ = 'Aligner'
    
    ALIGNMENT = ('top_left', 'top', 'top_right', 'left', 'center', 'right', 'bottom_left', 'bottom', 'bottom_right')

    def __init__(self, align='center', margin=0, padding=0, expand=False, keep_ratio=True, pick_enabled=True):
        clutter.Actor.__init__(self)
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
        prefered_width = 2*self._margin.x - 2*self._padding.x
        
        if self.element:
            element_width, element_height = self.element.get_preferred_size()[2:]
            if self.expand and self.keep_ratio and element_height != 0 and for_height != -1:
                inner_height = for_height - 2*self._margin.y - 2*self._padding.y
                ratio = float(element_width) / float(element_height)
                element_height = inner_height
                element_width = element_height * ratio
            else:
                if element_height != 0 and for_height != -1:
                    inner_height = for_height - 2*self._margin.y - 2*self._padding.y
                    ratio = float(element_width) / float(element_height)
                    if element_height > inner_height:
                        element_height = inner_height
                        element_width = element_height * ratio
                else:
                    if for_height != -1:
                        inner_height = for_height - 2*self._margin.y - 2*self._padding.y
                        if element_height > inner_height:
                            element_height = inner_height
            prefered_width += element_width
        
        return prefered_width, prefered_width
    
    def do_get_preferred_height(self, for_width):
        prefered_height = 2*self._margin.y - 2*self._padding.y
        
        if self.element:
            element_width, element_height = self.element.get_preferred_size()[2:]
            if self.expand and self.keep_ratio and element_height != 0 and for_width != -1:
                inner_width = for_width - 2*self._margin.x - 2*self._padding.x
                ratio = float(element_width) / float(element_height)
                element_width = inner_width
                element_height = element_width / ratio
            else:
                if element_height != 0 and for_width != -1:
                    inner_width = for_width - 2*self._margin.x - 2*self._padding.x
                    ratio = float(element_width) / float(element_height)
                    if element_width > inner_width:
                        element_width = inner_width
                        element_height = element_width / ratio
                else:
                    if for_width != -1:
                        inner_width = for_width - 2*self._margin.x - 2*self._padding.x
                        if element_width > inner_width:
                            element_width = inner_width
            prefered_height += element_height
        
        return prefered_height, prefered_height
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        inner_width = width - 2*self._margin.x - 2*self._padding.x
        inner_height = height - 2*self._margin.y - 2*self._padding.y
        
        # allocate background
        if self.background:
            bgbox = clutter.ActorBox()
            bgbox.x1 = self._margin.x
            bgbox.y1 = self._margin.y
            bgbox.x2 = width - self._margin.x
            bgbox.y2 = height - self._margin.y
            self.background.allocate(bgbox, flags)
        
        if self.element:
            # get element size
            element_width, element_height = self.element.get_preferred_size()[2:]
            if self.expand:
                if self.keep_ratio and element_height != 0:
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
                if element_height != 0:
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
            elebox = clutter.ActorBox()
            elebox.x1 = int(self._padding.x + self._margin.x + base_x)
            elebox.y1 = int(self._padding.y + self._margin.y + base_y)
            elebox.x2 = int(elebox.x1 + element_width)
            elebox.y2 = int(elebox.y1 + element_height)
            #print elebox.x1, elebox.y1, elebox.x2, elebox.y2, '--------', width, height
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
    
    def on_click(source, event):
        color_a = '#880000ff'
        color_b = '#ff0000ff'
        bg = source.background
        current_color = bg.get_color()
        if str(current_color) == color_a:
            bg.set_color(color_b)
        else:
            bg.set_color(color_a)
    
    bg = clutter.Rectangle()
    bg.set_color('#ff0000ff')
    
    ele = clutter.Rectangle()
    ele.set_color('#00ff00ff')
    ele.set_size(50, 100)
    
    aligner = Aligner(align='right', expand=False, keep_ratio=False, pick_enabled=False)
    aligner.set_background(bg)
    aligner.set_element(ele)
    aligner.set_position(100, 100)
    aligner.set_size(400, 400)
    aligner.set_reactive(True)
    aligner.connect('button-press-event', on_click)
    stage.add(aligner)
    
    stage.show()
    clutter.main()


