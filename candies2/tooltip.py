#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import GObject
from gi.repository import Clutter
from clicking import LongClick
from text import TextContainer


class ToolTipManager(Clutter.Actor, Clutter.Container):
    __gtype_name__ = 'ToolTipManager'

    def __init__(self, content_actor=None, tooltip_actor=None, h_direction='middle', v_direction='top', clickable=True, long_click=True, tooltip_duration=0, animation_duration=500, tooltip_x_padding=0, tooltip_y_padding=0):
        Clutter.Actor.__init__(self)

        self.h_direction = h_direction
        self.v_direction = v_direction
        self.long_click = long_click
        self.clickable = clickable

        # if tooltip_duration == 0: infinite lifetime for tooltips
        self.tooltip_duration = tooltip_duration
        self.animation_duration = animation_duration
        self.build_animations()
        self._hide_timeout_id = None
        self._animation_timeout_id = None

        self.content_actor = None
        self._content_connection = None
        self.tooltip_actor = None
        self._tooltip_connection = None
        self._tooltip_displayed = False
        self.tooltip_x_padding = tooltip_x_padding
        self.tooltip_y_padding = tooltip_y_padding
        self.tooltip_pointer = Clutter.Texture()
        self.tooltip_pointer.hide()
        self.tooltip_pointer.set_parent(self)
        self.tooltip_show_animation.apply(self.tooltip_pointer)
        self.tooltip_hide_animation.apply(self.tooltip_pointer)

        if content_actor:
            self.set_content(content_actor)
        if tooltip_actor:
            self.set_tooltip(tooltip_actor)

    def build_animations(self):
        self.tooltip_show_timeline = Clutter.Timeline(self.animation_duration)
        alpha = Clutter.Alpha(self.tooltip_show_timeline, Clutter.EASE_IN_EXPO)
        self.tooltip_show_animation = Clutter.BehaviourOpacity(
            0, 255, alpha=alpha)

        self.tooltip_hide_timeline = Clutter.Timeline(self.animation_duration)
        alpha = Clutter.Alpha(self.tooltip_hide_timeline, Clutter.EASE_IN_EXPO)
        self.tooltip_hide_animation = Clutter.BehaviourOpacity(
            255, 0, alpha=alpha)

    def set_pointer_texture(self, texture_src):
        self.tooltip_pointer.set_from_file(texture_src)

    def set_content(self, content_actor):
        if self.content_actor:
            self.content_actor.unparent()
            self._disconnect_content()
        self.content_actor = content_actor
        self.content_actor.set_parent(self)
        self._connect_content()

    def get_tooltip_displayed(self):
        return self._tooltip_displayed

    def set_tooltip(self, tooltip_actor):
        if self.tooltip_actor:
            self.tooltip_actor.unparent()
            self._disconnect_tooltip()
        self.tooltip_actor = tooltip_actor
        self._tooltip_displayed = False
        self.tooltip_actor.hide()
        self.tooltip_actor.set_parent(self)
        self._connect_tooltip()

    def set_clickable(self, boolean):
        if boolean and not self.clickable:
            self.clickable = True
            self._connect_content()
        elif not boolean and self.clickable:
            self.clickable = False
            self._disconnect_content()

    def _connect_content(self):
        if self.content_actor and self.clickable:
            self.content_actor.set_reactive(True)
            if self.long_click:
                LongClick(self.content_actor)
                self._content_connection = self.content_actor.connect(
                    'long-press-event', self._on_content_press)
            else:
                self._content_connection = self.content_actor.connect(
                    'button-press-event', self._on_content_press)

    def _disconnect_content(self):
        if self.content_actor and self._content_connection is not None:
            self.content_actor.set_reactive(False)
            self.content_actor.disconnect(self._content_connection)
            self._content_connection = None

    def _on_content_press(self, source=None, event=None):
        self.toggle_tooltip_display()
        return True

    def _connect_tooltip(self):
        if self.tooltip_actor:
            self.tooltip_actor.set_reactive(True)
            self._tooltip_connection = self.tooltip_actor.connect(
                'button-press-event', self._on_tooltip_press)
            self.tooltip_show_animation.apply(self.tooltip_actor)
            self.tooltip_hide_animation.apply(self.tooltip_actor)

    def _disconnect_tooltip(self):
        if self.content_actor and self._tooltip_connection is not None:
            self.tooltip_actor.set_reactive(False)
            self.tooltip_actor.disconnect(self._tooltip_connection)
            self._tooltip_connection = None
            self.tooltip_show_animation.remove_all()
            self.tooltip_hide_animation.remove_all()

    def _on_tooltip_press(self, source=None, event=None):
        self.toggle_tooltip_display()
        return True

    def toggle_tooltip_display(self):
        if self._tooltip_displayed:
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
        if self.tooltip_actor and not self._tooltip_displayed:
            self._tooltip_displayed = True
            self.tooltip_actor.set_opacity(0)
            self.tooltip_actor.show()
            self.tooltip_pointer.set_opacity(0)
            self.tooltip_pointer.show()
            self.tooltip_show_timeline.start()
            if self.tooltip_duration > 0:
                if self._hide_timeout_id is not None:
                    GObject.source_remove(self._hide_timeout_id)
                self._hide_timeout_id = GObject.timeout_add(
                    self.tooltip_duration, self._hide_tooltip)
        return False

    def _hide_tooltip(self):
        if self.tooltip_actor and self._tooltip_displayed:
            self.tooltip_hide_timeline.start()
            if self._animation_timeout_id is not None:
                GObject.source_remove(self._animation_timeout_id)
            self._animation_timeout_id = GObject.timeout_add(
                self.animation_duration, self._hide_tooltip_finish)
        return False

    def _hide_tooltip_finish(self):
        if self.tooltip_actor:
            self._tooltip_displayed = False
            self.tooltip_actor.hide()
            self.tooltip_pointer.hide()
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
            content_box = Clutter.ActorBox()
            content_box.x1 = 0
            content_box.y1 = 0
            content_box.x2 = box_width
            content_box.y2 = box_height
            self.content_actor.allocate(content_box, flags)

            if self.tooltip_actor:
                box_x, box_y = self.get_transformed_position()
                box_x = int(box_x)
                box_y = int(box_y)

                preferred_size = self.tooltip_actor.get_preferred_size()
                tooltip_width = preferred_size[2]
                tooltip_height = preferred_size[3]

                preferred_size = self.tooltip_pointer.get_preferred_size()
                pointer_width = preferred_size[2]
                pointer_height = preferred_size[3]

                if self.h_direction == 'left':
                    pointer_x_pos = int((box_width - pointer_width) / 2.0)
                    if pointer_width > 0:
                        tooltip_x_pos = int(
                            (box_width + pointer_width) / 2.0) - tooltip_width + self.tooltip_x_padding
                    else:
                        tooltip_x_pos = box_width - \
                            tooltip_width + self.tooltip_x_padding
                elif self.h_direction == 'right':
                    pointer_x_pos = int((box_width - pointer_width) / 2.0)
                    if pointer_width > 0:
                        tooltip_x_pos = pointer_x_pos - self.tooltip_x_padding
                    else:
                        tooltip_x_pos = 0 - self.tooltip_x_padding
                else:
                    pointer_x_pos = int((box_width - pointer_width) / 2.0)
                    tooltip_x_pos = int((box_width - tooltip_width) / 2.0)

                if self.v_direction == 'top':
                    pointer_y_pos = 0 - pointer_height
                    tooltip_y_pos = 0 - tooltip_height - \
                        pointer_height + self.tooltip_y_padding
                else:
                    pointer_y_pos = box_height
                    tooltip_y_pos = box_height + \
                        pointer_height - self.tooltip_y_padding

                # if the tooltip will go outside, change x_pos (10 is for
                # padding)
                if box_x + tooltip_x_pos < 10:
                    tooltip_x_pos = 0 - box_x + 10

                pointer_box = Clutter.ActorBox()
                pointer_box.x1 = pointer_x_pos
                pointer_box.y1 = pointer_y_pos
                pointer_box.x2 = pointer_x_pos + pointer_width
                pointer_box.y2 = pointer_y_pos + pointer_height
                self.tooltip_pointer.allocate(pointer_box, flags)

                tooltip_box = Clutter.ActorBox()
                tooltip_box.x1 = tooltip_x_pos
                tooltip_box.y1 = tooltip_y_pos
                tooltip_box.x2 = tooltip_x_pos + tooltip_width
                tooltip_box.y2 = tooltip_y_pos + tooltip_height
                self.tooltip_actor.allocate(tooltip_box, flags)

        Clutter.Actor.do_allocate(self, box, flags)

    def do_foreach(self, func, data=None):
        if self.tooltip_pointer:
            func(self.tooltip_pointer, data)
        if self.tooltip_actor:
            func(self.tooltip_actor, data)
        if self.content_actor:
            func(self.content_actor, data)

    def do_paint(self):
        if self.tooltip_pointer:
            self.tooltip_pointer.paint()
        if self.tooltip_actor:
            self.tooltip_actor.paint()
        if self.content_actor:
            self.content_actor.paint()

    def do_pick(self, color):
        if self.tooltip_pointer:
            self.tooltip_pointer.paint()
        if self.tooltip_actor:
            self.tooltip_actor.paint()
        if self.content_actor:
            self.content_actor.paint()

    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'content_actor'):
            if self.content_actor:
                self.content_actor.unparent()
                self.content_actor.destroy()
        if hasattr(self, 'tooltip_actor'):
            if self.tooltip_actor:
                self.tooltip_actor.unparent()
                self.tooltip_actor.destroy()
        if hasattr(self, 'tooltip_pointer'):
            if self.tooltip_pointer:
                self.tooltip_pointer.unparent()
                self.tooltip_pointer.destroy()

if __name__ == '__main__':
    stage = Clutter.Stage()
    stage.set_size(1280, 800)
    stage.set_color('#000000ff')
    stage.connect('destroy', Clutter.main_quit)

    rect = Clutter.Rectangle()
    rect.set_size(100, 100)
    rect.set_color('#0000ffff')

    rect2 = Clutter.Rectangle()
    rect2.set_size(800, 60)
    rect2.set_position(200, 200)
    rect2.set_color('#00ff00ff')

    test = ToolTipManager(
        rect, rect2, tooltip_duration=0, animation_duration=500)
    # test.set_content(rect)
    test.h_direction = 'left'
    test.v_direction = 'top'
    GObject.timeout_add(1000, test.display_tooltip, True)
    test.set_size(200, 100)
    test.set_position(400, 200)
    stage.add(test)

    stage.show()
    Clutter.main()
