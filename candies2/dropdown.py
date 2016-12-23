#!/usr/bin/env python
# -*- coding: utf-8 -*
import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter
from gi.repository import Cogl
import common
from container import BaseContainer
from roundrect import RoundRectangle
from text import TextContainer
from box import VBox
from autoscroll import AutoScrollPanel


class OptionLine(BaseContainer):
    """
    A option line for select input. Can be used alone to have a text with icon.
    """

    INDENT_WIDTH = 24

    def __init__(self, name, text, icon_height=32, icon_path=None, padding=8,
                 spacing=8, enable_background=True, font='14', font_color='Black',
                 color='LightGray', border_color='Gray', texture=None,
                 rounded=True, crypted=False, indent_level=0):
        BaseContainer.__init__(self)
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)
        self.name = name

        self._locked = False
        self.font = font
        self.font_color = font_color
        self.default_color = color
        self.default_border_color = border_color
        self.rounded = rounded
        self.indent_level = indent_level

        # background
        if rounded:
            self.background = RoundRectangle(texture=texture)
            self.background.set_color(self.default_color)
            self.background.set_border_color(self.default_border_color)
            self.background.set_border_width(3)
            self.background.set_radius(10)
        else:
            self.background = Clutter.Rectangle()
            self.background.set_color(self.default_color)
        if enable_background:
            self.enable_background = True
        else:
            self.enable_background = False
            self.background.hide()
        self._add(self.background)
        # icon
        self.icon_height = icon_height
        self.icon_path = icon_path
        self._icon_allocate = True
        self.icon = Clutter.Texture()
        if icon_path:
            self.icon.set_from_file(icon_path)
        else:
            self.icon.hide()
        self._add(self.icon)
        # spacer (for indentation)
        self.spacer = Clutter.Rectangle()
        self.spacer.set_width(indent_level * self.INDENT_WIDTH)
        self.spacer.hide()
        self._add(self.spacer)
        # label
        self.label = TextContainer(
            unicode(text), padding=0, rounded=False, crypted=crypted)
        color = Clutter.color_from_string(self.font_color)[1]
        self.label.set_font_color(color)
        self.label.set_font_name(self.font)
        self.label.set_inner_color(Clutter.color_from_string('#00000000')[1])
        self.label.set_border_color(Clutter.color_from_string('#00000000')[1])
        self.label.set_line_wrap(False)  # to center text vertically
        self._add(self.label)

    def get_text(self):
        return self.label.get_text()

    def set_lock(self, lock):
        self.set_reactive(not lock)
        self.set_opacity(128 if lock else 255)
        self._locked = lock

    def get_lock(self):
        return self._locked

    def set_texture(self, texture):
        if self.rounded:
            self.background.set_texture(texture)

    def set_line_wrap(self, boolean):
        self.label.set_line_wrap(boolean)

    def set_line_alignment(self, alignment):
        self.label.set_line_alignment(alignment)

    def set_justify(self, boolean):
        self.label.set_justify(boolean)

    def set_text(self, text):
        self.label.set_text(str(text))

    def set_name(self, text):
        self.name = text

    def set_hname(self, text):
        self.label.set_text(str(text))

    def has_icon(self):
        return self.icon_path is not None

    def set_icon(self, new_icon_path=None):
        self.icon_path = new_icon_path
        if new_icon_path:
            self.icon.set_from_file(new_icon_path)
            self.icon.show()
        else:
            self.icon.hide()

    def set_font_color(self, color):
        self.label.set_font_color(Clutter.color_from_string(color)[1])

    def set_font_name(self, font_name):
        self.label.set_font_name(font_name)

    def set_inner_color(self, color):
        self.background.set_color(Clutter.color_from_string(color)[1])

    def set_border_color(self, color):
        self.background.set_border_color(Clutter.color_from_string(color)[1])

    def set_radius(self, radius):
        if self.rounded:
            self.background.set_radius(radius)

    def set_border_width(self, width):
        self.background.set_border_width(width)

    def set_icon_opacity(self, opacity):
        self.icon.set_opacity(opacity)

    def set_icon_allocate(self, boolean):
        if boolean and not self._icon_allocate:
            self._icon_allocate = True
            if self.has_icon():
                self.icon.show()
            self.queue_relayout()
        elif not boolean and self._icon_allocate:
            self._icon_allocate = False
            self.icon.hide()
            self.queue_relayout()

    def show_background(self):
        if not self.enable_background:
            self.enable_background = True
            self.background.show()

    def hide_background(self):
        if self.enable_background:
            self.enable_background = False
            self.background.hide()

    def do_get_preferred_width(self, for_height):
        if for_height != -1:
            for_height -= 2 * self._padding.y
        preferred_width = self.icon_height + \
            2 * self._padding.x + self._spacing.x
        preferred_width += self.spacer.get_preferred_width(for_height)[1]
        preferred_width += self.label.get_preferred_width(for_height)[1]
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        preferred_height = 0
        if for_width != -1:
            w = for_width - self.icon_height - \
                2 * self._padding.x - self._spacing.x
            preferred_height = self.label.get_preferred_height(w)[1]
        preferred_height = max(
            preferred_height, self.icon_height) + 2 * self._padding.y
        return preferred_height, preferred_height

    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1

        # background
        background_box = Clutter.ActorBox()
        background_box.x1 = 0
        background_box.y1 = 0
        background_box.x2 = main_width
        background_box.y2 = main_height
        self.background.allocate(background_box, flags)

        if self._icon_allocate:
            # icon
            icon_height = min(self.icon_height, main_height)
            icon_y_padding = int(float(main_height - icon_height) / 2.)
            icon_box = Clutter.ActorBox()
            icon_box.x1 = self._padding.x
            icon_box.y1 = icon_y_padding
            icon_box.x2 = self._padding.x + icon_height
            icon_box.y2 = icon_box.y1 + icon_height
            self.icon.allocate(icon_box, flags)

            # spacer
            spacer_width = self.indent_level * self.INDENT_WIDTH
            spacer_box = Clutter.ActorBox()
            spacer_box.x1 = icon_box.x2 + self._spacing.x
            spacer_box.y1 = self._padding.y
            spacer_box.x2 = spacer_box.x1 + spacer_width
            spacer_box.y2 = main_height - self._padding.y
            self.spacer.allocate(spacer_box, flags)
        else:
            # icon
            icon_box = Clutter.ActorBox(0, 0, 0, 0)
            self.icon.allocate(icon_box, flags)

            # spacer
            spacer_width = self.indent_level * self.INDENT_WIDTH
            spacer_box = Clutter.ActorBox()
            spacer_box.x1 = self._spacing.x
            spacer_box.y1 = self._padding.y
            spacer_box.x2 = spacer_box.x1 + spacer_width
            spacer_box.y2 = main_height - self._padding.y
            self.spacer.allocate(spacer_box, flags)

        # label
        label_box = Clutter.ActorBox()
        label_box.x1 = spacer_box.x2
        label_box.y1 = self._padding.y
        label_box.x2 = main_width - self._padding.x
        label_box.y2 = main_height - self._padding.y
        self.label.allocate(label_box, flags)

        Clutter.Actor.do_allocate(self, box, flags)

    def do_pick(self, color):
        Clutter.Actor.do_pick(self, color)


class Select(Clutter.Actor, Clutter.Container):
    """
    A select input.
    """

    def __init__(self, padding=8, spacing=8, on_change_callback=None,
                 icon_height=48, open_icon_path=None, font='14',
                 font_color='Black', selected_font_color='Blue',
                 color='LightGray', border_color='Gray',
                 option_color='LightBlue', texture=None, user_data=None,
                 direction="down", y_offsets=None, alignment="center"):
        Clutter.Actor.__init__(self)
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)
        self.stage_padding = 10
        self.on_change_callback = on_change_callback
        self.user_data = user_data
        self.direction = direction
        if y_offsets:
            if isinstance(y_offsets, (list, tuple)):
                if len(y_offsets) > 1:
                    self.y_offsets = tuple(y_offsets[:2])
                else:
                    self.y_offsets = (y_offsets[0], y_offsets[0])
            else:
                self.y_offsets = (y_offsets, y_offsets)
        else:
            self.y_offsets = (0, 0)
        self.alignment = alignment
        self.icon_height = icon_height
        self._stage_width, self._stage_height = 0, 0
        self._opened = False

        self._selected = None
        self._locked = False
        self.open_icon = open_icon_path
        self._background_box = None
        self._has_icons = False

        self.font = font
        self.font_color = font_color
        self.selected_font_color = selected_font_color
        self.default_color = color
        self.default_border_color = border_color
        self.option_color = option_color
        self.texture = texture

        # hidder is to catch click event on all stage when the select input is
        # opened
        self._hidder = Clutter.Rectangle()
        self._hidder.set_color(Clutter.color_from_string('#00000000')[1])
        self._hidder.connect('button-release-event', self._on_hidder_click)
        self._hidder.set_reactive(True)
        self._hidder.set_parent(self)
        # background
        self._background = RoundRectangle()
        self._background.set_color(self.default_color)
        self._background.set_border_color(self.default_border_color)
        self._background.set_border_width(3)
        self._background.set_radius(10)
        self._background.set_parent(self)
        # list of options displayed when the select input is opened
        self._list = VBox(padding=0, spacing=0)
        # auto scroll panel
        self._auto_scroll = AutoScrollPanel(self._list)
        self._auto_scroll.hide()
        self._auto_scroll.set_parent(self)
        # selected option is displayed when the select input is closed
        self._selected_option = OptionLine(
            'empty', '', padding=(self._padding.x, self._padding.y),
            spacing=self._spacing.x, icon_path=self.open_icon,
            icon_height=self.icon_height, enable_background=True,
            font=self.font, font_color=self.font_color,
            color=self.option_color, border_color='#00000000',
            texture=self.texture)
        self._selected_option.set_reactive(True)
        self._selected_option.connect(
            'button-release-event', self._on_selected_click)
        self._selected_option.set_parent(self)
        self._set_lock(True)

    def get_lock(self):
        return self._locked

    def _set_lock(self, status):
        if status:
            self._selected_option.set_reactive(False)
            self._selected_option.icon.hide()
        else:
            self._selected_option.set_reactive(True)
            self._selected_option.icon.show()
        self.set_opacity(127 if status else 255)

    def set_lock(self, status):
        self._set_lock(status)
        self._locked = status

    def get_stage(self):
        obj = self
        if obj.get_parent():
            has_parent = True
            obj = obj.get_parent()
            while has_parent:
                if obj.get_parent():
                    has_parent = True
                    obj = obj.get_parent()
                else:
                    has_parent = False
        if isinstance(obj, Clutter.Stage):
            return obj
        else:
            return None

    def get_selected(self):
        return self._selected

    def add_option(self, name, hname, icon_path=None, index=None, indent_level=0):
        new_option = OptionLine(
            name, hname, padding=(self._padding.x, self._padding.y), spacing=self._spacing.x,
            icon_path=icon_path, icon_height=self.icon_height,
            enable_background=False, font=self.font, font_color=self.font_color,
            color=self.option_color, border_color='#00000000', texture=self.texture, indent_level=indent_level)
        new_option.set_line_alignment(self.alignment)
        if icon_path is not None and not self._has_icons:
            self._has_icons = True
            for element in self._list.get_elements():
                element['object'].set_icon_allocate(True)
        new_option.set_icon_allocate(self._has_icons)
        new_option.set_reactive(True)
        new_option.connect('button-release-event', self._on_click)

        self._list.add_element(
            new_option, 'option_%s' % name, expand=True, index=index)
        self.check_scrollbar()

        if self._selected is None:
            self._selected = new_option
            self._selected.set_font_color(self.selected_font_color)
            self._selected.show_background()
            self._selected_option.set_name(name)
            self._selected_option.set_text(str(hname))
        if not self._locked:
            self._set_lock(False)

    def remove_option(self, name):
        if len(self._list.get_elements()) == 1:
            self.remove_all_options()
        else:
            option = self._list.remove_element('option_%s' % name)
            if self._selected == option:
                try:
                    self.select_option(self.get_option(0)[0])
                except TypeError:
                    self._selected = None
                    self._selected_option.set_name('empty')
                    self._selected_option.set_text('')
            self._has_icons = False
            for element in self._list.get_elements():
                if element['object'].has_icon:
                    self._has_icons = True
                    break
            for element in self._list.get_elements():
                element['object'].set_icon_allocate(self._has_icons)
            self.check_scrollbar()

    def remove_all_options(self):
        self._list.remove_all_elements()
        self._has_icons = False
        self.check_scrollbar()
        self._selected = None
        self._selected_option.set_name('empty')
        self._selected_option.set_text('')
        self._set_lock(True)

    def has_option(self, name):
        for element in self._list.get_elements():
            if element['name'] == "option_%s" % name:
                return True
        return False

    def get_options(self):
        return [(e["object"].name, e["object"].get_text()) for e in self._list.get_elements()]

    def get_option(self, index):
        try:
            option = self._list.get_elements()[index]["object"]
            return (option.name, option.get_text())
        except IndexError:
            return None

    def get_option_obj(self, index):
        try:
            option = self._list.get_elements()[index]["object"]
            return option
        except IndexError:
            return None

    def set_option_text(self, index, text):
        option = self.get_option_obj(index)
        if option:
            option.set_text(str(text))
            if option == self._selected:
                self._selected_option.set_text(str(text))

    def __len__(self):
        return len(self.get_options())

    def __nonzero__(self):
        return True

    def is_empty(self):
        return len(self) == 0

    def check_scrollbar(self):
        self._auto_scroll.check_scrollbar()

    def _on_click(self, source, event):
        if self._opened:
            if source == self._selected:
                self.close_options()
            else:
                self._select_option(source, silent=False)
                self.close_options()

    def _on_selected_click(self, source, event):
        self.open_options()

    def _on_hidder_click(self, source, event):
        self.close_options()

    def open_options(self):
        if not self._opened:
            self._opened = True
            stage = self.get_stage()
            if stage:
                self._stage_width, self._stage_height = stage.get_size()
            else:
                self._stage_width, self._stage_height = 0, 0
            self._selected_option.hide()
            self._auto_scroll.show()
            self.queue_relayout()

    def close_options(self):
        if self._opened:
            self._opened = False
            self._auto_scroll.hide()
            self._selected_option.show()
            self._auto_scroll.go_to_top()
            self.queue_relayout()

    def select_option(self, name, silent=True, force=False):
        element = self._list.get_by_name('option_%s' % name)
        if element is not None:
            option = element['object']
            self._select_option(option, silent=silent, force=force)
            self.queue_relayout()

    def _select_option(self, option, silent=True, force=False):
        if option != self._selected or force:
            if self._selected is not None:
                self._selected.hide_background()
                self._selected.set_font_color(self.font_color)

            self._selected = option
            self._selected.set_font_color(self.selected_font_color)
            self._selected.show_background()

            self._selected_option.set_name(option.name)
            self._selected_option.set_text(option.get_text())

            if self.on_change_callback is not None and (not silent or force):
                if self.user_data is not None:
                    self.on_change_callback(self._selected, self.user_data)
                else:
                    self.on_change_callback(self._selected)

    def set_bar_image_path(self, path):
        self._auto_scroll.set_bar_image_path(path)

    def set_scroller_image_path(self, path):
        self._auto_scroll.set_scroller_image_path(path)

    def do_get_preferred_width(self, for_height):
        preferred = max(self._selected_option.get_preferred_width(
            for_height)[1], self._list.get_preferred_width(for_height)[1])
        return preferred, preferred

    def do_get_preferred_height(self, for_width):
        preferred = self._selected_option.get_preferred_height(for_width)[1]
        return preferred, preferred

    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1

        if self._opened:
            option_box = Clutter.ActorBox(0, 0, main_width, main_height)
            self._selected_option.allocate(option_box, flags)

            box_x, box_y = self.get_transformed_position()
            box_x = int(box_x)
            box_y = int(box_y)

            if self._stage_height > 0 and self._stage_width > 0:
                hidder_box = Clutter.ActorBox(
                    -box_x, -box_y, self._stage_width - box_x, self._stage_height - box_y)
            else:
                hidder_box = Clutter.ActorBox(
                    self._padding.x, self._padding.y, self._padding.x, self._padding.y)
            self._hidder.allocate(hidder_box, flags)

            option_height = self.icon_height + 2 * self._padding.y
            total_height = option_height * len(self._list.get_elements())
            base_y = 0
            if self._stage_height > 0:
                if total_height > self._stage_height - 2 * self.stage_padding - self.y_offsets[0] - self.y_offsets[1]:
                    total_height = self._stage_height - 2 * \
                        self.stage_padding - self.y_offsets[0] - self.y_offsets[1]
                    base_y = -box_y + self.stage_padding + self.y_offsets[0]
                    if self.direction == "up":
                        base_y += total_height - main_height
                    # TODO enable scrollbar
                elif self.direction == "up":
                    if total_height > box_y + main_height - self.y_offsets[0]:
                        base_y = -box_y + total_height - main_height + \
                            self.y_offsets[0] + self.stage_padding
                elif box_y + total_height > self._stage_height - self.stage_padding - self.y_offsets[1]:
                    base_y = -box_y + self._stage_height - \
                        self.stage_padding - self.y_offsets[1] - total_height
            x1 = 0
            x2 = main_width
            if self.direction == "up":
                y1 = base_y - total_height + main_height
                y2 = base_y + main_height
            else:  # down, default
                y1 = base_y
                y2 = base_y + total_height
            self._background_box = Clutter.ActorBox(x1, y1, x2, y2)
            self._background.allocate(self._background_box, flags)
            list_box = Clutter.ActorBox(x1, y1, x2, y2)
            self._auto_scroll.allocate(list_box, flags)
        else:
            hidder_box = Clutter.ActorBox(
                self._padding.x, self._padding.y, self._padding.x, self._padding.y)
            self._hidder.allocate(hidder_box, flags)
            self._background_box = Clutter.ActorBox(
                0, 0, main_width, main_height)
            self._background.allocate(self._background_box, flags)
            option_box = Clutter.ActorBox(0, 0, main_width, main_height)
            self._selected_option.allocate(option_box, flags)
            list_box = Clutter.ActorBox(0, 0, main_width, main_height)
            self._auto_scroll.allocate(list_box, flags)

        Clutter.Actor.do_allocate(self, box, flags)

    def do_foreach(self, func, data=None):
        func(self._hidder, data)
        func(self._background, data)
        func(self._selected_option, data)
        func(self._auto_scroll, data)

    def do_paint(self):
        self._hidder.paint()
        self._background.paint()
        self._selected_option.paint()

        # Clip auto scroll panel
        if self._background_box is not None:
            # Draw a rectangle to cut scroller
            Cogl.path_round_rectangle(
                self._background_box.x1 + 3,
                self._background_box.y1 + 3,
                self._background_box.x2 - 3,
                self._background_box.y2 - 3,
                7,
                1
            )
            Clutter.cogl.path_close()
            # Start the clip
            Clutter.cogl.clip_push_from_path()

            self._auto_scroll.paint()

            # Finish the clip
            Clutter.cogl.clip_pop()
        else:
            self._auto_scroll.paint()

    def do_pick(self, color):
        self.do_paint()

    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_hidder'):
            if self._hidder:
                self._hidder.unparent()
                self._hidder.destroy()
        if hasattr(self, '_background'):
            if self._background:
                self._background.unparent()
                self._background.destroy()
        if hasattr(self, '_selected_option'):
            if self._selected_option:
                self._selected_option.unparent()
                self._selected_option.destroy()
        if hasattr(self, '_auto_scroll'):
            if self._auto_scroll:
                self._auto_scroll.unparent()
                self._auto_scroll.destroy()


def tester(stage):
    Clutter.init()
    stage_width = 640
    stage_height = 480
    stage = Clutter.Stage()
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', Clutter.main_quit)

    test_line = OptionLine(
        'test', 'displayed fezfzefezfzef', icon_height=32, padding=8)
    test_line.label.set_font_name('22')
    test_line.set_position(0, 0)
    stage.add_child(test_line)

    # test_select = Select(open_icon_path='/data/www/sdiemer/top.png')
    test_select = Select()
    test_select.set_position(0, 80)
    icon_path = None
    # icon_path = 'test.jpg'
    test_select.add_option('test1', 'displayed', icon_path=icon_path)
    test_select.add_option('test2', 'displayed regregreg', icon_path=icon_path)
    test_select.add_option(
        'test3', 'displayed fezfzefezfzef', icon_path=icon_path)
    # test_select.set_size(400, 64)
    stage.add_child(test_select)

    """def on_click(btn, event):
        print 'click -----------'
        test_select.open_options()
    print 'selected : ', test_select.selected
    test_select.selected.set_reactive(True)
    test_select.selected.connect('button-press-event', on_click)"""

    stage.show()
    Clutter.main()

if __name__ == '__main__':
    from test import run_test
    run_test(tester)
