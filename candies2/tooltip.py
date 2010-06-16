#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import clutter
from clicking import LongClick
from text import TextContainer

class ToolTipManager(clutter.Actor, clutter.Container):
    __gtype_name__ = 'ToolTipManager'
    
    def __init__(self, content_actor=None, tooltip_actor=None, h_direction='middle', v_direction='top', clickable=True, long_click=True, tooltip_duration=0, animation_duration=500):
        clutter.Actor.__init__(self)
        
        self.h_direction = h_direction
        self.v_direction = v_direction
        self.long_click = long_click
        self.clickable = clickable
        
        # if tooltip_duration == 0: infinite lifetime for tooltips
        self.tooltip_duration = tooltip_duration
        self.animation_duration = animation_duration
        self.build_animations()
        
        self.content_actor = None
        self.content_connection = None
        self.tooltip_actor = None
        self.tooltip_connection = None
        self.tooltip_displayed = False
        if content_actor:
            self.set_content(content_actor)
        if tooltip_actor:
            self.set_tooltip(tooltip_actor)
    
    def build_animations(self):
        self.tooltip_show_timeline = clutter.Timeline(self.animation_duration)
        alpha = clutter.Alpha(self.tooltip_show_timeline, clutter.EASE_IN_EXPO)
        self.tooltip_show_animation = clutter.BehaviourOpacity(0, 255, alpha=alpha)
        
        self.tooltip_hide_timeline = clutter.Timeline(self.animation_duration)
        alpha = clutter.Alpha(self.tooltip_hide_timeline, clutter.EASE_IN_EXPO)
        self.tooltip_hide_animation = clutter.BehaviourOpacity(255, 0, alpha=alpha)
    
    def set_content(self, content_actor):
        if self.content_actor:
            self.content_actor.unparent()
            self._disconnect_content()
        self.content_actor = content_actor
        self.content_actor.set_parent(self)
        self._connect_content()
    
    def set_tooltip(self, tooltip_actor):
        if self.tooltip_actor:
            self.tooltip_actor.unparent()
            self._disconnect_tooltip()
        self.tooltip_actor = tooltip_actor
        self.tooltip_displayed = False
        self.tooltip_actor.hide()
        self.tooltip_actor.set_parent(self)
        self._connect_tooltip()
    
    def _connect_content(self):
        if self.content_actor and self.clickable:
            self.content_actor.set_reactive(True)
            if self.long_click:
                LongClick(self.content_actor)
                self.content_connection = self.content_actor.connect('long-press-event', self._on_content_press)
            else:
                self.content_connection = self.content_actor.connect('button-press-event', self._on_content_press)
    
    def _disconnect_content(self):
        if self.content_actor and self.content_connection is not None:
            self.content_actor.set_reactive(False)
            self.content_actor.disconnect(self.content_connection)
            self.content_connection = None
    
    def _on_content_press(self, source=None, event=None):
        self.toggle_tooltip_display()
        return True
    
    def _connect_tooltip(self):
        if self.tooltip_actor:
            self.tooltip_actor.set_reactive(True)
            self.tooltip_connection = self.tooltip_actor.connect('button-press-event', self._on_tooltip_press)
            self.tooltip_show_animation.apply(self.tooltip_actor)
            self.tooltip_hide_animation.apply(self.tooltip_actor)
    
    def _disconnect_tooltip(self):
        if self.content_actor and self.tooltip_connection is not None:
            self.tooltip_actor.set_reactive(False)
            self.tooltip_actor.disconnect(self.tooltip_connection)
            self.tooltip_connection = None
            self.tooltip_show_animation.remove_all()
            self.tooltip_hide_animation.remove_all()
    
    def _on_tooltip_press(self, source=None, event=None):
        self.toggle_tooltip_display()
        return True
    
    def toggle_tooltip_display(self):
        if self.tooltip_displayed:
            self.display_tooltip(False)
        else:
            self.display_tooltip(True)
        return False
    
    def display_tooltip(self, boolean):
        if boolean:
            self._show_tooltip()
        else:
            self._hide_tooltip()
    
    def _show_tooltip(self):
        if self.tooltip_actor and not self.tooltip_displayed:
            self.tooltip_displayed = True
            self.tooltip_actor.set_opacity(0)
            self.tooltip_actor.show()
            self.tooltip_show_timeline.start()
            if self.tooltip_duration > 0:
                gobject.timeout_add(self.tooltip_duration, self._hide_tooltip)
        return False
    
    def _hide_tooltip(self):
        if self.tooltip_actor and self.tooltip_displayed:
            self.tooltip_hide_timeline.start()
            gobject.timeout_add(self.animation_duration, self._hide_tooltip_finish)
        return False
    
    def _hide_tooltip_finish(self):
        if self.tooltip_actor:
            self.tooltip_displayed = False
            self.tooltip_actor.hide()
        return False
    
    def do_get_preferred_width(self, for_height):
        if self.content_actor:
            min, nat = self.content_actor.get_preferred_width(for_height)
        else:
            min = nat = 0
        return min, nat
    
    def do_get_preferred_height(self, for_width):
        if self.content_actor:
            min, nat = self.content_actor.get_preferred_height(for_width)
        else:
            min = nat = 0
        return min, nat
    
    def do_allocate(self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
        
        if self.content_actor:
            content_box = clutter.ActorBox()
            content_box.x1 = 0
            content_box.y1 = 0
            content_box.x2 = box_width
            content_box.y2 = box_height
            self.content_actor.allocate(content_box, flags)
        
            if self.tooltip_actor:
                preferred_size = self.tooltip_actor.get_preferred_size()
                tooltip_width = preferred_size[2]
                tooltip_height = preferred_size[3]
                
                if self.h_direction == 'left':
                    x_pos = box_width - tooltip_width
                elif self.h_direction == 'right':
                    x_pos = 0
                else:
                    x_pos = int(float(box_width - tooltip_width) / 2.0)
                
                if self.v_direction == 'top':
                    y_pos = 0 - tooltip_height
                else:
                    y_pos = box_height
                
                tooltip_box = clutter.ActorBox()
                tooltip_box.x1 = x_pos
                tooltip_box.y1 = y_pos
                tooltip_box.x2 = x_pos + tooltip_width
                tooltip_box.y2 = y_pos + tooltip_height
                self.tooltip_actor.allocate(tooltip_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        if self.content_actor:
            func(self.content_actor, data)
        if self.tooltip_actor:
            func(self.tooltip_actor, data)
        
    def do_paint(self):
        if self.content_actor:
            self.content_actor.paint()
        if self.tooltip_actor:
            self.tooltip_actor.paint()
    
    def do_pick(self, color):
        if self.content_actor:
            self.content_actor.paint()
        if self.tooltip_actor:
            self.tooltip_actor.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'content_actor'):
            if self.content_actor:
                self.content_actor.unparent()
                self.content_actor.destroy()
                self.content_actor = None
        if hasattr(self, 'tooltip_actor'):
            if self.tooltip_actor:
                self.tooltip_actor.unparent()
                self.tooltip_actor.destroy()
                self.tooltip_actor = None

if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(1280, 800)
    stage.set_color('#000000ff')
    stage.connect('destroy', clutter.main_quit)
    
    rect = clutter.Rectangle()
    rect.set_size(100, 100)
    rect.set_color('#0000ffff')
    
    rect2 = clutter.Rectangle()
    rect2.set_size(480, 60)
    rect2.set_position(200, 200)
    rect2.set_color('#00ff00ff')
    
    test = ToolTipManager(rect, rect2, tooltip_duration=0, animation_duration=500)
    test.set_content(rect)
    test.h_direction = 'left'
    test.v_direction = 'top'
    gobject.timeout_add(1000, test.display_tooltip, True)
    test.set_size(200, 100)
    test.set_position(400, 200)
    stage.add(test)
    
    stage.show()
    clutter.main()
