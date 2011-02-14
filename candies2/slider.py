#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clutter
from container import BaseContainer
from buttons import ImageButton
from list import LightList
import common
import math

class Slider(BaseContainer):
    __gtype_name__ = 'Slider'
    
    def __init__(self, margin=0, spacing=10, horizontal=True, expand=False, pick_enabled=True):
        BaseContainer.__init__(self, allow_add=False, allow_remove=False, pick_enabled=pick_enabled)
        self._margin = common.Margin(margin)
        self._spacing = common.Spacing(spacing)
        self._padding = common.Padding(0)
        self._expand = expand
        self._horizontal = horizontal
        self._buttons_width = 64
        self._buttons_flash_fct = None
        self._displayed_elements = 3
        self._elements_count = 0
        self._elements_preferred_size = (250, 250)
        self._elements_size = self._elements_preferred_size
        
        self._width = 0
        self._height = 0
        
        self._previous = ImageButton(has_text=False)
        self._previous.connect('button-press-event', self._on_previous_press)
        
        self._next = ImageButton(has_text=False)
        self._next.connect('button-press-event', self._on_next_press)
        
        if self._horizontal:
            self._list = LightList(horizontal=horizontal, padding=(spacing, 0), spacing=spacing)
        else:
            self._list = LightList(horizontal=horizontal, padding=(0, spacing), spacing=spacing)
        
        self._group = clutter.Group()
        self._group.add(self._list)
        
        self._add(self._group)
        self._add(self._previous)
        self._add(self._next)
        
        self._current_position = (0, 0)
        self._move_to = (0, 0)
        self._min_index = 0
        self._max_index = 0
        self._timeline_completed = True
        
        self._timeline = clutter.Timeline(250)
        self._timeline.set_loop(False)
        self._timeline.connect('completed', self._on_timeline_completed)
        self._alpha = clutter.Alpha(self._timeline, clutter.LINEAR)
        self._path = clutter.Path('M 0 0 L 0 0')
        self._behaviour = clutter.BehaviourPath(self._alpha, self._path)
    
    def set_elements_preferred_size(self, width, height):
        self._elements_preferred_size = (width, height)
    
    def _on_previous_press(self, source, event):
        #print '_on_previous_press'
        if self._min_index > 0:
            self._min_index -= 1
            self._max_index -= 1
            if self._horizontal:
                self._move_to = (self._move_to[0] + self._elements_size[0] + self._spacing.x, 0)
            else:
                self._move_to = (0, self._move_to[1] + self._elements_size[1] + self._spacing.y)
            self._request_move()
            if self._buttons_flash_fct:
                self._buttons_flash_fct(source)
            
            self._next.set_opacity(255)
            if self._min_index == 0:
                self._previous.set_opacity(127)
            else:
                self._previous.set_opacity(255)
    
    def _on_next_press(self, source, event):
        #print '_on_next_press'
        if self._max_index < self._elements_count:
            self._min_index += 1
            self._max_index += 1
            if self._horizontal:
                self._move_to = (self._move_to[0] - self._elements_size[0] - self._spacing.x, 0)
            else:
                self._move_to = (0, self._move_to[1] - self._elements_size[1] - self._spacing.y)
            self._request_move()
            if self._buttons_flash_fct:
                self._buttons_flash_fct(source)
            
            self._previous.set_opacity(255)
            if self._max_index == self._elements_count:
                self._next.set_opacity(127)
            else:
                self._next.set_opacity(255)
    
    def _request_move(self):
        if self._timeline_completed:
            self._execute_move()
        else:
            self._on_timeline_completed()
    
    def _on_timeline_completed(self, timeline=None):
        self._timeline.stop()
        self._behaviour.remove_all()
        self._timeline_completed = True
        self._current_position = self._list.get_position()
        if self._move_to != self._current_position:
            self._execute_move()
        else:
            if self._horizontal:
                self._list.set_clip(-self._current_position[0], -self._current_position[1], self._inner_width, self._inner_height)
            else:
                self._list.set_clip(-self._current_position[0], -self._current_position[1], self._inner_width, self._inner_height)
    
    def _execute_move(self):
        self._timeline_completed = False
        
        start = self._list.get_position()
        end = self._move_to
        
        # clip the list to get more fps
        if self._horizontal:
            diff = end[0] - start[0]
            if diff > 0:
                self._list.set_clip(-end[0], -end[1], diff + self._inner_width, self._inner_height)
            else:
                self._list.set_clip(-start[0], -start[1], -diff + self._inner_width, self._inner_height)
        else:
            diff = end[1] - start[1]
            if diff > 0:
                self._list.set_clip(-end[0], -end[1], self._inner_width, diff + self._inner_height)
            else:
                self._list.set_clip(-start[0], -start[1], self._inner_width, -diff + self._inner_height)
        
        self._path = clutter.Path('M %s %s L %s %s' %(start[0], start[1], end[0], end[1]))
        self._behaviour = clutter.BehaviourPath(self._alpha, self._path)
        self._behaviour.apply(self._list)
        
        self._timeline.rewind()
        self._timeline.start()
    
    def do_add(self, *children):
        self._list.add(*children)
        self._elements_count = len(self._list.get_children())
    
    def do_remove(self, *children):
        self._list.remove(*children)
        self._elements_count = len(self._list.get_children())
    
    def add_actor_after(self, actor, after):
        self._list.add_actor_after(actor, after)
        self._elements_count = len(self._list.get_children())
    
    def remove_all(self):
        self._list.remove_all()
        self._elements_count = len(self._list.get_children())
    
    def _hide_buttons(self, boolean):
        if boolean:
            self._previous.hide()
            self._next.hide()
        else:
            self._previous.show()
            self._next.show()
    
    def set_buttons_width(self, width):
        self._buttons_width = width
    
    def set_buttons_flash_fct(self, fct):
        self._buttons_flash_fct = fct
    
    def get_previous_button(self):
        return self._previous
    
    def get_next_button(self):
        return self._next
    
    def do_get_preferred_width(self, for_height):
        preferred_width = 2 * self._margin.x
        elements_size = self._elements_preferred_size
        if for_height == -1:
            if not self._horizontal:
                preferred_width += elements_size[0]
            else:
                preferred_width += 2 * self._buttons_width + self._spacing.x + 3 * (elements_size[0] + self._spacing.x)
        else:
            if not self._horizontal:
                if self._expand:
                    inner_height = for_height - 2 * self._margin.y - 2 * self._buttons_width - self._spacing.y
                    displayable_elements = int(inner_height / float(elements_size[1] + self._spacing.y))
                    elements_height = float(inner_height - displayable_elements * self._spacing.y) / displayable_elements
                    ratio = elements_height / elements_size[1]
                    elements_width = elements_size[0] * ratio
                    preferred_width += math.ceil(elements_width)
                else:
                    preferred_width += elements_size[0]
            else:
                # width for 3 items
                preferred_width += 2 * self._buttons_width + self._spacing.x + 3 * (elements_size[0] + self._spacing.x)
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        preferred_height = 2 * self._margin.y
        elements_size = self._elements_preferred_size
        if for_width == -1:
            if self._horizontal:
                preferred_height += elements_size[1]
            else:
                preferred_height += 2 * self._buttons_width + self._spacing.y + 3 * (elements_size[1] + self._spacing.y)
        else:
            if self._horizontal:
                if self._expand:
                    inner_width = for_width - 2 * self._margin.x - 2 * self._buttons_width - self._spacing.x
                    displayable_elements = int(inner_width / float(elements_size[0] + self._spacing.x))
                    elements_width = float(inner_width - displayable_elements * self._spacing.x) / displayable_elements
                    ratio = elements_width / elements_size[0]
                    elements_height = elements_size[1] * ratio
                    preferred_height += math.ceil(elements_height)
                else:
                    preferred_height += elements_size[1]
            else:
                # height for 3 items
                preferred_height += 2 * self._buttons_width + self._spacing.y + 3 * (elements_size[1] + self._spacing.y)
        return preferred_height, preferred_height
    
    def _refresh_allocation_params(self):
        if self._expand:
            elements_size = self._elements_preferred_size
            padding_x = self._margin.x
            padding_y = self._margin.y
            if self._horizontal:
                inner_width = self._width - 2 * self._margin.x - 2 * self._buttons_width - self._spacing.x
                inner_height = self._height - 2 * self._margin.y
                displayable_elements = int(inner_width / float(elements_size[0] + self._spacing.x))
                elements_width = float(inner_width - displayable_elements * self._spacing.x) / displayable_elements
                ratio = elements_width / elements_size[0]
                elements_height = elements_size[1] * ratio
                if elements_height > inner_height:
                    elements_height = inner_height
                    ratio = elements_height / elements_size[1]
                    elements_width = elements_size[0] * ratio
                    padding_x = int(float(inner_width - displayable_elements * (elements_width + self._spacing.x)) / 2)
                if displayable_elements > self._elements_count:
                    padding_x = int(float(inner_width - self._elements_count * (elements_width + self._spacing.x)) / 2)
                padding_y = int(float(self._height - elements_height) / 2)
            else:
                inner_width = self._width - 2 * self._margin.x
                inner_height = self._height - 2 * self._margin.y - 2 * self._buttons_width - self._spacing.y
                displayable_elements = int(inner_height / float(elements_size[1] + self._spacing.y))
                elements_height = float(inner_height - displayable_elements * self._spacing.y) / displayable_elements
                ratio = elements_height / elements_size[1]
                elements_width = elements_size[0] * ratio
                if elements_width > inner_width:
                    elements_width = inner_width
                    ratio = elements_width / elements_size[0]
                    elements_height = elements_size[1] * ratio
                    padding_y = int(float(inner_height - displayable_elements * (elements_height + self._spacing.y)) / 2)
                if displayable_elements > self._elements_count:
                    padding_y = int(float(inner_height - self._elements_count * (elements_height + self._spacing.y)) / 2)
                padding_x = int(float(self._width - elements_width) / 2)
            elements_size = (int(math.ceil(elements_width)), int(math.ceil(elements_height)))
        else:
            elements_size = self._elements_preferred_size
            if self._horizontal:
                inner_width = self._width - 2 * self._margin.x - 2 * self._buttons_width - self._spacing.x
                inner_height = self._height - 2 * self._margin.y
                displayable_elements = int(inner_width / float(elements_size[0] + self._spacing.x))
                if displayable_elements > self._elements_count:
                    padding_x = int(float(inner_width - self._elements_count * (elements_size[0] + self._spacing.x)) / 2)
                else:
                    padding_x = int(float(inner_width - displayable_elements * (elements_size[0] + self._spacing.x)) / 2)
                padding_y = int(float(self._height - elements_size[1]) / 2)
            else:
                inner_width = self._width - 2 * self._margin.x
                inner_height = self._height - 2 * self._margin.y - 2 * self._buttons_width - self._spacing.y
                displayable_elements = int(inner_height / float(elements_size[1] + self._spacing.y))
                padding_x = int(float(self._width - elements_size[0]) / 2)
                if displayable_elements > self._elements_count:
                    padding_y = int(float(inner_height - self._elements_count * (elements_size[1] + self._spacing.y)) / 2)
                else:
                    padding_y = int(float(inner_height - displayable_elements * (elements_size[1] + self._spacing.y)) / 2)
        if displayable_elements >= self._elements_count:
            self._hide_buttons(True)
        else:
            self._hide_buttons(False)
        # save params
        self._padding.x = padding_x
        self._padding.y = padding_y
        self._elements_size = elements_size
        self._displayed_elements = displayable_elements
        if self._horizontal:
            self._list.element_size = elements_size[0]
            self._list.set_height(elements_size[1])
        else:
            self._list.element_size = elements_size[1]
            self._list.set_width(elements_size[0])
        #print self, elements_size, padding_x, padding_y
            
        # check displayed elements
        if self._min_index == 0 and self._max_index == 0:
            self._min_index = 0
            self._max_index = self._displayed_elements
            self._previous.set_opacity(127)
            if self._max_index >= self._elements_count:
                self._next.set_opacity(127)
            if self._horizontal:
                self._list.set_clip(-self._current_position[0], -self._current_position[1], self._inner_width, self._inner_height)
            else:
                self._list.set_clip(-self._current_position[0], -self._current_position[1], self._inner_width, self._inner_height)
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        
        if width != self._width or height != self._height:
            self._width = width
            self._height = height
            if self._horizontal:
                self._inner_width = self._width - 2 * self._margin.x - 2 * self._padding.x - 2 * self._buttons_width
                self._inner_height = self._height - 2 * self._margin.y - 2 * self._padding.y
            else:
                self._inner_width = self._width - 2 * self._margin.x - 2 * self._padding.x
                self._inner_height = self._height - 2 * self._margin.y - 2 * self._padding.y - 2 * self._buttons_width
            self._refresh_allocation_params()
        
        # allocate buttons
        previous_box = clutter.ActorBox()
        next_box = clutter.ActorBox()
        if self._horizontal:
            # previous
            previous_box.x1 = self._padding.x
            previous_box.y1 = self._padding.y
            previous_box.x2 = self._padding.x + self._buttons_width
            previous_box.y2 = height - self._padding.y
            # next
            next_box.x1 = width - self._padding.x - self._buttons_width
            next_box.y1 = self._padding.y
            next_box.x2 = width - self._padding.x
            next_box.y2 = height - self._padding.y
        else:
            # previous
            previous_box.x1 = self._padding.x
            previous_box.y1 = self._padding.y
            previous_box.x2 = width - self._padding.x
            previous_box.y2 = self._padding.y + self._buttons_width
            # next
            next_box.x1 = self._padding.x
            next_box.y1 = height - self._padding.y - self._buttons_width
            next_box.x2 = width - self._padding.x
            next_box.y2 = height - self._padding.y
        self._previous.allocate(previous_box, flags)
        self._next.allocate(next_box, flags)
        
        list_box = clutter.ActorBox()
        if self._horizontal:
            list_box.x1 = previous_box.x2
            list_box.y1 = previous_box.y1
            list_box.x2 = next_box.x1
            list_box.y2 = next_box.y2
        else:
            list_box.x1 = previous_box.x1
            list_box.y1 = previous_box.y2
            list_box.x2 = next_box.x2
            list_box.y2 = next_box.y1
        self._group.allocate(list_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)

    def do_paint(self):
        # Draw a rectangle to cut animation
        if self._horizontal:
            clutter.cogl.path_rectangle(
                self._padding.x + self._buttons_width,
                self._padding.y,
                self._width - self._padding.x - self._buttons_width,
                self._height - self._padding.y
            )
        else:
            clutter.cogl.path_rectangle(
                self._padding.x,
                self._padding.y + self._buttons_width,
                self._width - self._padding.x,
                self._height - self._padding.y - self._buttons_width
            )
        clutter.cogl.path_close()
        # Start the clip
        clutter.cogl.clip_push_from_path()
        
        self._group.paint()

        # Finish the clip
        clutter.cogl.clip_pop()
        
        self._previous.paint()
        self._next.paint()


if __name__ == '__main__':
    # stage
    stage = clutter.Stage()
    stage_width = 1000
    stage_height = 600
    stage.set_size(stage_width, stage_height)
    stage.set_color('#000000ff')
    stage.connect('destroy', clutter.main_quit)
    
    bg = clutter.Rectangle()
    bg.set_color('#444444ff')
    bg.set_size(700, 500)
    bg.set_position(150, 50)
    stage.add(bg)
    
    bg = clutter.Rectangle()
    bg.set_color('#666666ff')
    bg.set_size(660, 460)
    bg.set_position(170, 70)
    stage.add(bg)
    
    test_slider = Slider(expand=True, horizontal=True, margin=20, spacing=10)
    test_slider.set_elements_preferred_size(150, 150)
    test_slider.set_buttons_width(64)
    test_slider.set_width(700)
    test_slider.set_height(300)
    test_slider.set_position(150, 50)
    stage.add(test_slider)
    
    from text import TextContainer
    
    for i in range(10):
        rect = TextContainer('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec viverra adipiscing posuere. Proin fringilla nisl non dui consectetur aliquet. Integer et elit sem, faucibus fringilla urna. Suspendisse vel ipsum nunc, sed malesuada urna. Nunc bibendum imperdiet tellus vitae tempus. Vivamus sodales feugiat cursus. Maecenas accumsan est ac lorem consequat sed aliquam justo sollicitudin. Vivamus congue dignissim ligula, a malesuada enim sagittis et. Nam fringilla nisl quis nisi ultrices tincidunt. Cras ut magna eu nunc adipiscing rhoncus. Donec at leo vel magna congue auctor id ut eros. Praesent sodales fringilla lacus quis congue. Quisque a nunc urna. Donec euismod sagittis bibendum.')
        rect.set_line_wrap(True)
        if i % 3 == 0:
            color = (10*i, 255 - 10*i, 10*i, 255)
        elif i % 2 == 0:
            color = (10*i, 10*i, 255 - 10*i, 255)
        else:
            color = (255 - 10*i, 10*i, 10*i, 255)
        rect.set_border_color(color)
        rect.set_inner_color("#ffffffff")
        rect.set_radius(10)
        rect.set_border_width(5)
        rect.set_reactive(True)
        rect.name = 'rect %s' %i
        def on_press(source, event):
            print 'press', source.name
        rect.connect('button-press-event', on_press)
        test_slider.add(rect)
    
    stage.show()
    clutter.main()
    
