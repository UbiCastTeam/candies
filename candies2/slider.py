#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Clutter
from container import BaseContainer
from buttons import ImageButton
from list import LightList
import common
import math


class Slider(BaseContainer):

    def __init__(self, elements_per_page=3, margin=0, spacing=10, horizontal=True, keep_ratio=False, h_align='center', v_align='middle', pick_enabled=True):
        BaseContainer.__init__(
            self, allow_add=False, allow_remove=False, pick_enabled=pick_enabled)
        self._margin = common.Margin(margin)
        self._spacing = common.Spacing(spacing)
        self._padding = common.Padding(0)
        self._keep_ratio = keep_ratio
        self._h_align = h_align
        self._v_align = v_align
        self._horizontal = horizontal
        self._buttons_width = 64
        self._buttons_flash_fct = None
        self._elements_per_page = elements_per_page
        self._elements_count = 0
        self._elements_preferred_size = (250, 250)
        self._elements_size = self._elements_preferred_size

        self._width = 0
        self._height = 0
        self._list_width = 0
        self._list_height = 0
        self._list_box = Clutter.ActorBox()

        self._previous = ImageButton(has_text=False)
        self._previous.connect('button-press-event', self._on_previous_press)

        self._next = ImageButton(has_text=False)
        self._next.connect('button-press-event', self._on_next_press)

        if self._horizontal:
            self._list = LightList(
                horizontal=horizontal, padding=(spacing, 0), spacing=spacing)
        else:
            self._list = LightList(
                horizontal=horizontal, padding=(0, spacing), spacing=spacing)

        self._group = Clutter.Group()
        self._group.add(self._list)

        self._add(self._group)
        self._add(self._previous)
        self._add(self._next)

        self._current_position = (0, 0)
        self._move_to = (0, 0)
        self._min_index = 0
        self._max_index = 0
        self._timeline_completed = True

        self._timeline = Clutter.Timeline(250)
        self._timeline.set_loop(False)
        self._timeline.connect('completed', self._on_timeline_completed)
        self._alpha = Clutter.Alpha(self._timeline, Clutter.LINEAR)
        self._path = Clutter.Path('M 0 0 L 0 0')
        self._behaviour = Clutter.BehaviourPath(self._alpha, self._path)

        # key bindings
        self.pool = Clutter.BindingPool(
            '%s_%s' % (self.__gtype_name__, id(self)))
        self.pool.install_action(
            'move-left', Clutter.keysyms.Left, None, self._keyboard_previous_page)
        self.pool.install_action(
            'move-up', Clutter.keysyms.Up, None, self._keyboard_previous_page)
        self.pool.install_action(
            'move-right', Clutter.keysyms.Right, None, self._keyboard_next_page)
        self.pool.install_action(
            'move-down', Clutter.keysyms.Down, None, self._keyboard_next_page)

        self.pool.install_action(
            'beginning', Clutter.keysyms.Left, Clutter.SHIFT_MASK, self._keyboard_beginning)
        self.pool.install_action(
            'beginning', Clutter.keysyms.Up, Clutter.SHIFT_MASK, self._keyboard_beginning)
        self.pool.install_action(
            'beginning', Clutter.keysyms.Home, None, self._keyboard_beginning)
        self.pool.install_action(
            'end', Clutter.keysyms.Right, Clutter.SHIFT_MASK, self._keyboard_end)
        self.pool.install_action(
            'end', Clutter.keysyms.Down, Clutter.SHIFT_MASK, self._keyboard_end)
        self.pool.install_action(
            'end', Clutter.keysyms.End, None, self._keyboard_end)

        self.pool.install_action(
            'previous-page', Clutter.keysyms.Page_Up, None, self._keyboard_previous_page)
        self.pool.install_action(
            'next-page', Clutter.keysyms.Page_Down, None, self._keyboard_next_page)
        self.connect('key-press-event', self._on_key_press_event)

    def _on_key_press_event(self, source, event):
        self.pool.activate(event.keyval, event.modifier_state, source)

    def _keyboard_previous(self, group, action_name, keyval, modifiers):
        self.previous()

    def _keyboard_next(self, group, action_name, keyval, modifiers):
        self.next()

    def _keyboard_beginning(self, group, action_name, keyval, modifiers):
        self.go_to_beginning()

    def _keyboard_end(self, group, action_name, keyval, modifiers):
        self.go_to_end()

    def _keyboard_previous_page(self, group, action_name, keyval, modifiers):
        self.go_to_previous_page()

    def _keyboard_next_page(self, group, action_name, keyval, modifiers):
        self.go_to_next_page()

    def set_elements_preferred_size(self, width, height):
        self._elements_preferred_size = (width, height)

    def previous(self, nb=1):
        # print '_on_previous_press'
        if nb > self._min_index:
            nb = self._min_index
        if self._min_index > 0:
            self._min_index -= nb
            self._max_index -= nb
            if self._horizontal:
                self._move_to = (self._move_to[0] + nb * (
                    self._elements_size[0] + self._spacing.x), 0)
            else:
                self._move_to = (0, self._move_to[1] + nb * (
                    self._elements_size[1] + self._spacing.y))
            self._request_move()
            if self._buttons_flash_fct:
                self._buttons_flash_fct(self._previous)

            self._next.set_opacity(255)
            if self._min_index == 0:
                self._previous.set_opacity(127)
            else:
                self._previous.set_opacity(255)

    def next(self, nb=1):
        # print '_on_next_press'
        if nb > self._elements_count - self._max_index:
            nb = self._elements_count - self._max_index
        if self._max_index < self._elements_count:
            self._min_index += nb
            self._max_index += nb
            if self._horizontal:
                self._move_to = (self._move_to[0] - nb * (
                    self._elements_size[0] + self._spacing.x), 0)
            else:
                self._move_to = (0, self._move_to[1] - nb * (
                    self._elements_size[1] + self._spacing.y))
            self._request_move()
            if self._buttons_flash_fct:
                self._buttons_flash_fct(self._next)

            self._previous.set_opacity(255)
            if self._max_index == self._elements_count:
                self._next.set_opacity(127)
            else:
                self._next.set_opacity(255)

    def go_to_previous_page(self):
        if self._min_index - self._elements_per_page <= 0:
            self.go_to_beginning()
        else:
            self.previous(self._elements_per_page)

    def go_to_next_page(self):
        if self._max_index + self._elements_per_page >= self._elements_count:
            self.go_to_end()
        else:
            self.next(self._elements_per_page)

    def go_to_beginning(self):
        self._min_index = 0
        self._max_index = self._elements_per_page
        self._move_to = (0, 0)
        self._request_move()
        if self._buttons_flash_fct:
            self._buttons_flash_fct(self._previous)

        self._previous.set_opacity(127)
        self._next.set_opacity(255)

    def go_to_end(self):
        if self._elements_per_page < self._elements_count:
            self._min_index = self._elements_count - self._elements_per_page
            self._max_index = self._elements_count
            if self._horizontal:
                self._move_to = ((self._elements_per_page - self._elements_count) * (
                    self._elements_size[0] + self._spacing.x), 0)
            else:
                self._move_to = (0, (self._elements_per_page - self._elements_count) * (
                    self._elements_size[1] + self._spacing.y))
            self._request_move()
            if self._buttons_flash_fct:
                self._buttons_flash_fct(self._next)

            self._previous.set_opacity(255)
            self._next.set_opacity(127)

    def _on_previous_press(self, source, event):
        self.go_to_previous_page()

    def _on_next_press(self, source, event):
        self.go_to_next_page()

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
                self._list.set_clip(-self._current_position[
                                    0], -self._current_position[1], self._list_width, self._list_height)
            else:
                self._list.set_clip(-self._current_position[
                                    0], -self._current_position[1], self._list_width, self._list_height)

    def _execute_move(self):
        self._timeline_completed = False

        start = self._list.get_position()
        end = self._move_to

        # clip the list to get more fps
        if self._horizontal:
            diff = end[0] - start[0]
            if diff > 0:
                self._list.set_clip(
                    -end[0], -end[1], diff + self._list_width, self._list_height)
            else:
                self._list.set_clip(
                    -start[0], -start[1], -diff + self._list_width, self._list_height)
        else:
            diff = end[1] - start[1]
            if diff > 0:
                self._list.set_clip(
                    -end[0], -end[1], self._list_width, diff + self._list_height)
            else:
                self._list.set_clip(
                    -start[0], -start[1], self._list_width, -diff + self._list_height)

        self._path = Clutter.Path(
            'M %s %s L %s %s' % (start[0], start[1], end[0], end[1]))
        self._behaviour = Clutter.BehaviourPath(self._alpha, self._path)
        self._behaviour.apply(self._list)

        self._timeline.rewind()
        self._timeline.start()

    def add(self, *children):
        self._list.add(*children)
        self._elements_count = len(self._list.get_children())

    def remove(self, *children):
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

    def complete_relayout(self):
        self._width = 0
        self.queue_relayout()

    def do_get_preferred_width(self, for_height):
        preferred_width = 2 * self._margin.x
        elements_size = self._elements_preferred_size
        if for_height == -1:
            if not self._horizontal:
                preferred_width += elements_size[0]
            else:
                preferred_width += 2 * self._buttons_width + \
                    self._spacing.x + 3 * (elements_size[0] + self._spacing.x)
        else:
            if not self._horizontal:
                if self._keep_ratio:
                    inner_height = for_height - 2 * self._margin.y - \
                        2 * self._buttons_width - self._spacing.y
                    elements_height = float(
                        inner_height - self._elements_per_page * self._spacing.y) / self._elements_per_page
                    ratio = elements_height / elements_size[1]
                    elements_width = elements_size[0] * ratio
                    preferred_width += math.ceil(elements_width)
                else:
                    preferred_width += elements_size[0]
            else:
                # width for 3 items
                preferred_width += 2 * self._buttons_width + \
                    self._spacing.x + 3 * (elements_size[0] + self._spacing.x)
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        preferred_height = 2 * self._margin.y
        elements_size = self._elements_preferred_size
        if for_width == -1:
            if self._horizontal:
                preferred_height += elements_size[1]
            else:
                preferred_height += 2 * self._buttons_width + \
                    self._spacing.y + 3 * (elements_size[1] + self._spacing.y)
        else:
            if self._horizontal:
                if self._keep_ratio:
                    inner_width = for_width - 2 * self._margin.x - \
                        2 * self._buttons_width - self._spacing.x
                    elements_width = float(
                        inner_width - self._elements_per_page * self._spacing.x) / self._elements_per_page
                    ratio = elements_width / elements_size[0]
                    elements_height = elements_size[1] * ratio
                    preferred_height += math.ceil(elements_height)
                else:
                    preferred_height += elements_size[1]
            else:
                # height for 3 items
                preferred_height += 2 * self._buttons_width + \
                    self._spacing.y + 3 * (elements_size[1] + self._spacing.y)
        return preferred_height, preferred_height

    def _refresh_allocation_params(self):
        elements_size = self._elements_preferred_size
        if self._keep_ratio:
            if self._horizontal:
                inner_width = self._width - 2 * self._margin.x - \
                    2 * self._buttons_width - self._spacing.x
                inner_height = self._height - 2 * self._margin.y
                elements_width = float(
                    inner_width - self._elements_per_page * self._spacing.x) / self._elements_per_page
                ratio = elements_width / elements_size[0]
                elements_height = elements_size[1] * ratio
                if elements_height > inner_height:
                    elements_height = inner_height
                    ratio = elements_height / elements_size[1]
                    elements_width = elements_size[0] * ratio
            else:
                inner_width = self._width - 2 * self._margin.x
                inner_height = self._height - 2 * self._margin.y - \
                    2 * self._buttons_width - self._spacing.y
                elements_height = float(
                    inner_height - self._elements_per_page * self._spacing.y) / self._elements_per_page
                ratio = elements_height / elements_size[1]
                elements_width = elements_size[0] * ratio
                if elements_width > inner_width:
                    elements_width = inner_width
                    ratio = elements_width / elements_size[0]
                    elements_height = elements_size[1] * ratio
        else:
            if self._horizontal:
                inner_width = self._width - 2 * self._margin.x - \
                    2 * self._buttons_width - self._spacing.x
                inner_height = self._height - 2 * self._margin.y
                elements_width = float(
                    inner_width - self._elements_per_page * self._spacing.x) / self._elements_per_page
                elements_height = inner_height
            else:
                inner_width = self._width - 2 * self._margin.x
                inner_height = self._height - 2 * self._margin.y - \
                    2 * self._buttons_width - self._spacing.y
                elements_height = float(
                    inner_height - self._elements_per_page * self._spacing.y) / self._elements_per_page
                elements_width = inner_width
        elements_width = int(elements_width)
        elements_height = int(elements_height)

        # get list size
        content_width = elements_width
        content_height = elements_height
        list_width = elements_width
        list_height = elements_height
        if self._horizontal:
            if self._elements_per_page > self._elements_count:
                list_width = self._elements_count * \
                    (elements_width + self._spacing.x) + self._spacing.x
            else:
                list_width = self._elements_per_page * \
                    (elements_width + self._spacing.x) + self._spacing.x
            content_width = 2 * self._buttons_width + list_width
        else:
            if self._elements_per_page > self._elements_count:
                list_height = self._elements_count * \
                    (elements_height + self._spacing.y) + self._spacing.y
            else:
                list_height = self._elements_per_page * \
                    (elements_height + self._spacing.y) + self._spacing.y
            content_height = 2 * self._buttons_width + list_height
        self._list_width = list_width
        self._list_height = list_height

        # adapt padding for alignment
        if self._h_align == 'center':
            self._padding.left = self._padding.right = int(
                float(self._width - 2 * self._margin.x - content_width) / 2.0)
        elif self._h_align == 'left':
            self._padding.left = 0
            self._padding.right = self._width - \
                2 * self._margin.x - content_width
        else:
            self._padding.left = self._width - \
                2 * self._margin.x - content_width
            self._padding.right = 0
        if self._v_align == 'middle':
            self._padding.top = self._padding.bottom = int(
                float(self._height - 2 * self._margin.y - content_height) / 2.0)
        elif self._v_align == 'top':
            self._padding.top = 0
            self._padding.bottom = self._height - \
                2 * self._margin.y - content_height
        else:
            self._padding.top = self._height - \
                2 * self._margin.y - content_height
            self._padding.bottom = 0

        if self._elements_per_page >= self._elements_count:
            self._hide_buttons(True)
        else:
            self._hide_buttons(False)

        # save params
        self._elements_size = (elements_width, elements_height)
        if self._horizontal:
            self._list.element_size = elements_width
            self._list.set_height(elements_height)
        else:
            self._list.element_size = elements_height
            self._list.set_width(elements_width)
        # print self, elements_width, elements_height, padding_x, padding_y

        # check displayed elements
        if self._min_index == 0 and self._max_index == 0 or self._elements_count <= self._elements_per_page:
            self._min_index = 0
            self._max_index = self._elements_per_page
            self._previous.set_opacity(127)
            if self._max_index >= self._elements_count:
                self._next.set_opacity(127)
            if self._horizontal:
                self._list.set_clip(-self._current_position[
                                    0], -self._current_position[1], self._list_width, self._list_height)
            else:
                self._list.set_clip(-self._current_position[
                                    0], -self._current_position[1], self._list_width, self._list_height)

    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1

        if width != self._width or height != self._height:
            self._width = width
            self._height = height
            self._refresh_allocation_params()

        # allocate buttons
        previous_box = Clutter.ActorBox()
        next_box = Clutter.ActorBox()
        if self._horizontal:
            # previous
            previous_box.x1 = self._margin.x + self._padding.left
            previous_box.y1 = self._margin.y + self._padding.top
            previous_box.x2 = previous_box.x1 + self._buttons_width
            previous_box.y2 = height - self._margin.y - self._padding.bottom
            # next
            next_box.x1 = width - self._margin.x - \
                self._padding.right - self._buttons_width
            next_box.y1 = previous_box.y1
            next_box.x2 = next_box.x1 + self._buttons_width
            next_box.y2 = previous_box.y2
        else:
            # previous
            previous_box.x1 = self._margin.x + self._padding.left
            previous_box.y1 = self._margin.y + self._padding.top
            previous_box.x2 = width - self._margin.x - self._padding.right
            previous_box.y2 = previous_box.y1 + self._buttons_width
            # next
            next_box.x1 = previous_box.x1
            next_box.y1 = height - self._margin.y - \
                self._padding.bottom - self._buttons_width
            next_box.x2 = previous_box.x2
            next_box.y2 = next_box.y1 + self._buttons_width
        self._previous.allocate(previous_box, flags)
        self._next.allocate(next_box, flags)

        list_box = Clutter.ActorBox()
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
        self._list_box = list_box

        Clutter.Actor.do_allocate(self, box, flags)

    def do_paint(self):
        # Draw a rectangle to cut animation
        Clutter.cogl.path_rectangle(
            self._list_box.x1, self._list_box.y1, self._list_box.x2, self._list_box.y2)
        Clutter.cogl.path_close()
        # Start the clip
        Clutter.cogl.clip_push_from_path()

        self._group.paint()

        # Finish the clip
        Clutter.cogl.clip_pop()

        self._previous.paint()
        self._next.paint()


if __name__ == '__main__':
    # stage
    stage = Clutter.Stage()
    stage_width = 1000
    stage_height = 600
    stage.set_size(stage_width, stage_height)
    stage.set_color('#000000ff')
    stage.connect('destroy', Clutter.main_quit)

    bg = Clutter.Rectangle()
    bg.set_color('#444444ff')
    bg.set_size(700, 500)
    bg.set_position(150, 50)
    stage.add(bg)

    bg = Clutter.Rectangle()
    bg.set_color('#666666ff')
    bg.set_size(660, 460)
    bg.set_position(170, 70)
    stage.add(bg)

    # horizontal
    """
    test_slider = Slider(elements_per_page=3, keep_ratio=False, horizontal=True, margin=40, spacing=10)
    test_slider.set_elements_preferred_size(150, 150)
    test_slider.set_buttons_width(64)
    test_slider.set_width(700)
    test_slider.set_height(300)
    test_slider.set_position(150, 50)
    stage.add(test_slider)
    test_slider.set_focused(True)
    """

    # vertical
    test_slider = Slider(
        elements_per_page=3, keep_ratio=False, horizontal=False, margin=40, spacing=10)
    test_slider.set_elements_preferred_size(150, 150)
    test_slider.set_buttons_width(64)
    test_slider.set_width(700)
    test_slider.set_height(500)
    test_slider.set_position(150, 50)
    stage.add(test_slider)
    test_slider.set_focused(True)

    from text import TextContainer

    def add_element(source, event):
        print 'adding a new element to slider'
        rect = TextContainer(
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit.')
        rect.set_border_color('#558844ff')
        rect.set_inner_color("#ffffffff")
        rect.set_radius(10)
        rect.set_border_width(5)
        test_slider.add(rect)
        test_slider.complete_relayout()

    btn = TextContainer('add element')
    btn.set_reactive(True)
    btn.connect('button-press-event', add_element)
    stage.add(btn)

    for i in range(20):
        rect = TextContainer(
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec viverra adipiscing posuere. Proin fringilla nisl non dui consectetur aliquet. Integer et elit sem, faucibus fringilla urna. Suspendisse vel ipsum nunc, sed malesuada urna. Nunc bibendum imperdiet tellus vitae tempus. Vivamus sodales feugiat cursus. Maecenas accumsan est ac lorem consequat sed aliquam justo sollicitudin. Vivamus congue dignissim ligula, a malesuada enim sagittis et. Nam fringilla nisl quis nisi ultrices tincidunt. Cras ut magna eu nunc adipiscing rhoncus. Donec at leo vel magna congue auctor id ut eros. Praesent sodales fringilla lacus quis congue. Quisque a nunc urna. Donec euismod sagittis bibendum.')
        rect.set_line_wrap(True)
        if i % 3 == 0:
            color = (10 * i, 255 - 10 * i, 10 * i, 255)
        elif i % 2 == 0:
            color = (10 * i, 10 * i, 255 - 10 * i, 255)
        else:
            color = (255 - 10 * i, 10 * i, 10 * i, 255)
        rect.set_border_color(color)
        rect.set_inner_color("#ffffffff")
        rect.set_radius(10)
        rect.set_border_width(5)
        rect.set_reactive(True)
        rect.name = 'rect %s' % i

        def on_press(source, event):
            print 'press', source.name
        rect.connect('button-press-event', on_press)
        test_slider.add(rect)

    stage.show()
    Clutter.main()
