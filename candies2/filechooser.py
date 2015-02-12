#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import clutter
import common
import gobject
import magic
import unicodedata

from aligner import Aligner
from autoscroll import AutoScrollPanel
from box import HBox
from box import VBox
from buttons import ClassicButton
from container import BaseContainer
from dropdown import OptionLine, Select
from list import LightList
from multilayer import MultiLayerContainer
from slider import Slider
from video import VideoPlayer


class FileEntry(BaseContainer):
    '''
    An actor to represent a file
    '''
    __gtype_name__ = 'FileEntry'

    def __init__(self, name='', icon_src='', text='', extension='', is_dir=False, padding=10, spacing=10):
        BaseContainer.__init__(self, allow_add=False, allow_remove=False, pick_enabled=False)
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)
        self.name = name
        self.selected = False
        self._icon_src = icon_src
        # TODO gérer les caractere latin et utf8
        # self.text = encode_string(text)
        self.text = text
        self.extension = extension
        self._is_dir = is_dir
        self.icon_size = 32
        self._bg_color = '#ffffff44'
        self._selected_bg_color = '#ffff8844'

        # actors
        self._bg = clutter.Rectangle()
        self._bg.set_color(self._bg_color)
        self._add(self._bg)

        self._icon = clutter.Texture()
        if self._icon_src:
            self._icon.set_from_file(self._icon_src)
        self._add(self._icon)

        self._label = clutter.Text()
        self._label.set_color('#ffffffff')
        self._label.set_font_name('14')
        self._label.set_line_wrap(False)
        self._label.set_ellipsize(2)  # let 2 words after "..."
        self._label.set_line_alignment(3)  # align text to left
        self._label.set_text(str(self.text))
        self._add(self._label)

    def set_selected(self, boolean):
        if boolean:
            self.selected = True
            self._bg.set_color(self._selected_bg_color)
        else:
            self.selected = False
            self._bg.set_color(self._bg_color)

    def set_bg_color(self, bg_color):
        self._bg_color = bg_color
        if not self.selected:
            self._bg.set_color(bg_color)

    def set_selected_bg_color(self, selected_bg_color):
        self._selected_bg_color = selected_bg_color
        if self.selected:
            self._bg.set_color(selected_bg_color)

    def do_get_preferred_width(self, for_height):
        if for_height != -1:
            h = for_height - 2 * self._padding.y
        else:
            h = for_height
        preferred_width = 2 * self._padding.x + self._icon.get_preferred_width(h)[1] + self._label.get_preferred_width(h)[1]
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        if for_width != -1:
            w = for_width - 2 * self._padding.x - self._spacing.x - self.icon_size
        else:
            w = for_width
        preferred_height = 2 * self._padding.y + max(self.label.get_preferred_height(w), self.icon_size)
        return preferred_height, preferred_height

    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1

        inner_width = width - 2 * self._padding.x
        inner_height = height - 2 * self._padding.y

        bg_box = clutter.ActorBox(0, 0, width, height)

        if self.icon_size == inner_height:
            icon_base_y = self._padding.y
        else:
            icon_base_y = self._padding.y + int((inner_height - self.icon_size) / 2.0)

        icon_box = clutter.ActorBox()
        icon_box.x1 = self._padding.x
        icon_box.y1 = icon_base_y
        icon_box.x2 = self._padding.x + self.icon_size
        icon_box.y2 = icon_base_y + self.icon_size

        label_width = inner_width - self.icon_size - self._spacing.x
        label_height = self._label.get_preferred_height(for_width=label_width)[1]
        label_base_y = self._padding.y + int((inner_height - label_height) / 2.0)

        label_box = clutter.ActorBox()
        label_box.x1 = self._padding.x + self.icon_size + self._spacing.x
        label_box.y1 = label_base_y
        label_box.x2 = width - self._padding.x
        label_box.y2 = label_base_y + label_height

        self._bg.allocate(bg_box, flags)
        self._icon.allocate(icon_box, flags)
        self._label.allocate(label_box, flags)

        clutter.Actor.do_allocate(self, box, flags)


class PreviewDisplayer(BaseContainer):
    __gtype_name__ = 'PreviewDisplayer'

    def __init__(self, padding=10):
        BaseContainer.__init__(self, allow_add=False, allow_remove=False, pick_enabled=False)
        self._padding = common.Padding(padding)

        self._image = clutter.Texture()
        self._add(self._image)

    def set_from_file(self, image_src):
        self._image.set_from_file(image_src)

    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        inner_width = width - 2 * self._padding.x
        inner_height = height - 2 * self._padding.y

        image_width, image_height = self._image.get_preferred_size()[2:]
        if image_height > 0 and (image_width > inner_width or image_height > inner_height):
            image_ratio = float(image_width) / float(image_height)
            image_width = inner_width
            image_height = round(float(image_width) / float(image_ratio))
            if image_height > inner_height:
                image_height = inner_height
                image_width = round(float(image_height) * float(image_ratio))
        x_padding = round((inner_width - image_width) / 2.0)
        y_padding = round((inner_height - image_height) / 2.0)

        image_box = clutter.ActorBox()
        image_box.x1 = self._padding.x + x_padding
        image_box.y1 = self._padding.y + y_padding
        image_box.x2 = image_box.x1 + image_width
        image_box.y2 = image_box.y1 + image_height
        self._image.allocate(image_box, flags)

        clutter.Actor.do_allocate(self, box, flags)


class TypeFilter(object):

    def __init__(self, name, extensions, label=None):
        object.__init__(self)
        self.name = name
        self.extensions = extensions
        if label:
            self.label = label
        else:
            self.label = name

    def full_label(self):
        if self.extensions:
            extension_list = ", ".join(["*.%s" % ext for ext in self.extensions])
        else:
            extension_list = "*.*"
        return "%s (%s)" % (self.label, extension_list)

    def file_matchs(self, filename):
        if not self.extensions:
            return True
        extension = os.path.splitext(filename)[1][1:]
        return extension.lower() in self.extensions


class FileChooser(BaseContainer):
    '''
    A panel to select file
    '''
    __gtype_name__ = 'FileChooser'

    BASE_TYPE_FILTERS = {
        "images": TypeFilter("images", ("png", "bmp", "jpg", "jpeg", "tiff"), "Images"),
        "all": TypeFilter("all", None, "All")
    }

    def __init__(self, base_dir='/', start_dir=None, allow_hidden_files=False, display_hidden_files_at_start=False, directories_first=True, case_sensitive_sort=False, type_filters=None, callback=None, delete_button=False, custom_widget=None, custom_image=None, padding=0, spacing=0, styles=None, icons=None):
        BaseContainer.__init__(self, allow_add=False, allow_remove=False)
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)
        self._base_dir = base_dir
        self.path = None
        # start_dir must be a subdirectory of base_dir
        # startswith is not enough because /home/toto1 is not a subdir of /home/toto
        if start_dir and os.path.dirname(start_dir).startswith(base_dir):
            self._start_dir = start_dir
        else:
            self._start_dir = self._base_dir
        self.custom_widget = custom_widget
        self.custom_image = custom_image
        self._allow_hidden_files = allow_hidden_files
        self._display_hidden_files = display_hidden_files_at_start
        self._delete_file_button = None
        if not self._allow_hidden_files:
            self._display_hidden_files = False
        self._directories_first = directories_first
        self._case_sensitive_sort = case_sensitive_sort

        if type_filters:
            self._type_filters = list()
            for type_filter in type_filters:
                if type_filter in self.BASE_TYPE_FILTERS:
                    self._type_filters.append(self.BASE_TYPE_FILTERS[type_filter])
                else:
                    self._type_filters.append(type_filter)
        else:
            self._type_filters = [self.BASE_TYPE_FILTERS["all"]]
        self._type_filters_dict = dict()
        for type_filter in self._type_filters:
            self._type_filters_dict[type_filter.name] = type_filter

        self.callback = callback

        if not styles:
            self.styles = dict(
                file_bg='#333333ff',
                file_bg2='#444444ff',
                selected_bg='#228822ff',
                selected_bg2='#228822ff',
                bg_color='#222222ff',
                panel_bg_color='#00000044',
                button_font_name='14',
                button_font_color='#ffffffff',
                button_font_color_selected='#ffffffff',
                button_inner_color='#444444ff',
                button_inner_color_selected='#444444ff',
                button_border_color='#333333ff',
                element_size=50,
                preview_width=500,
                top_bar_height=64,
                bottom_bar_height=64,
                button_texture=None,
                icon_height=32,
            )
        else:
            self.styles = styles
        if not icons:
            self.icons = dict()
        else:
            self.icons = icons

        self._buttons_flash_fct = None
        self._selected = None
        self._current_dir = None
        self.components_padding = 10
        self.paths = list()  # list of tuples with path and current selection name

        # actors
        self._bg = clutter.Rectangle()
        self._bg.set_color(self.styles['bg_color'])
        self._add(self._bg)

        self._panel_bg = clutter.Rectangle()
        self._panel_bg.set_color(self.styles['panel_bg_color'])
        self._add(self._panel_bg)

        self.top_container = HBox(spacing=8, padding=12)
        self._slider = Slider(elements_per_page=4, keep_ratio=False, horizontal=True, margin=0, h_align='left')
        self.top_container.add_element(self._slider, "slider", expand=True, resizable=1.0)
        button = self._slider.get_next_button()
        button.set_font_name(self.styles['button_font_name'])
        button.set_font_color(self.styles['button_font_color'])
        button.set_inner_color(self.styles['button_inner_color'])
        button.set_border_color(self.styles['button_border_color'])
        button.set_texture(self.styles['button_texture'])
        button = self._slider.get_previous_button()
        button.set_font_name(self.styles['button_font_name'])
        button.set_font_color(self.styles['button_font_color'])
        button.set_inner_color(self.styles['button_inner_color'])
        button.set_border_color(self.styles['button_border_color'])
        button.set_texture(self.styles['button_texture'])
        self._add(self.top_container)
        self._files_list = LightList(element_size=self.styles['element_size'])
        self._files_panel = AutoScrollPanel(self._files_list)
        self._add(self._files_panel)

        self.right_container = VBox(spacing=8, padding=8)
        self.preview_block = MultiLayerContainer()
        self._video_container = MultiLayerContainer()
        self._aligner = Aligner(expand=True, keep_ratio=True)
        self._preview = PreviewDisplayer(padding=self.components_padding)

        self._video_player = VideoPlayer()
        self._video_player.connect('button-release-event', self._on_click)
        self.playbutton = Aligner(keep_ratio=True)
        self._texture = None
        if self.custom_image:
            # TODO check path
            self._texture = clutter.Texture()
            self._texture.set_from_file(self.custom_image)
            self._texture.set_opacity(255)
            self.playbutton.set_element(self._texture)
            self.playbutton.set_reactive(True)
        self.right_container.add_element(self.preview_block, "preview", expand=True, resizable=0.9, center=True)

        self._add(self.right_container)

        self._cancel = OptionLine('cancel', 'Cancel', icon_path=self.icons.get('cancel_btn'), icon_height=self.styles['icon_height'], padding=(10, 0))
        self._cancel.set_reactive(True)
        self._cancel.connect('button-release-event', self._on_cancel)
        self._cancel.set_font_name(self.styles['button_font_name'])
        self._cancel.set_font_color(self.styles['button_font_color'])
        self._cancel.set_inner_color(self.styles['button_inner_color'])
        self._cancel.set_border_color(self.styles['button_border_color'])
        self._cancel.set_texture(self.styles['button_texture'])
        self._add(self._cancel)

        self._validate = OptionLine('validate', 'Validate', icon_path=self.icons.get('validate_btn'), icon_height=self.styles['icon_height'], padding=(10, 0))
        self._validate.set_reactive(True)
        self._validate.connect('button-release-event', self._on_validate)
        self._validate.set_font_name(self.styles['button_font_name'])
        self._validate.set_font_color(self.styles['button_font_color'])
        self._validate.set_inner_color(self.styles['button_inner_color'])
        self._validate.set_border_color(self.styles['button_border_color'])
        self._validate.set_texture(self.styles['button_texture'])
        self._add(self._validate)

        self._type_filter_select = Select(
            padding=(10, 0),
            on_change_callback=self._on_change_type_filter,
            icon_height=self.styles['icon_height'],
            open_icon_path=self.icons.get('file_type_icon'),
            font=self.styles['button_font_name'],
            font_color=self.styles['button_font_color'],
            selected_font_color=self.styles['button_font_color_selected'],
            color=self.styles['button_inner_color'],
            border_color=self.styles['button_border_color'],
            option_color=self.styles['button_inner_color_selected'],
            texture=self.styles['button_texture'],
            user_data=None
        )

        for type_filter in self._type_filters:
            self._type_filter_select.add_option(type_filter.name, type_filter.full_label())
        if len(self._type_filters) < 2:
            self._type_filter_select.set_lock(True)
        self._add(self._type_filter_select)
        directory = self._base_dir
        while directory != self._start_dir:
            if directory == os.sep:
                label = directory
                button = ClassicButton(directory)
            else:
                label = os.path.basename(directory)
            button = ClassicButton(label)
            button.index = len(self.paths) + 1
            button.connect('button-release-event', self._on_button_click)
            button.set_font_name(self.styles['button_font_name'])
            button.set_font_color(self.styles['button_font_color'])
            button.set_inner_color(self.styles['button_inner_color'])
            button.set_border_color(self.styles['button_border_color'])
            button.set_texture(self.styles['button_texture'])
            self.paths.append([directory, None, button])
            self._slider.add(button)
            rest = self._start_dir[len(directory):].strip(os.sep)
            directory = os.path.join(directory, rest.split(os.sep)[0])
        self.open_dir(self._start_dir)

        # key bindings
        self.pool = clutter.BindingPool('%s_%s' % (self.__gtype_name__, id(self)))
        self.pool.install_action('move-down', clutter.keysyms.Down, None, self.select_next)
        self.pool.install_action('move-up', clutter.keysyms.Up, None, self.select_previous)
        self.pool.install_action('parent', clutter.keysyms.BackSpace, None, self.parent_dir)
        self.pool.install_action('select', clutter.keysyms.Return, None, self._on_validate)
        self.pool.install_action('select', clutter.keysyms.KP_Enter, None, self._on_validate)
        self.pool.install_action('escape', clutter.keysyms.Escape, None, self._on_cancel)
        self.pool.install_action('display_hidden_files', clutter.keysyms.h, clutter.CONTROL_MASK, self._on_display_hidden_files)
        self.pool.install_action('refresh', clutter.keysyms.F5, None, self._on_refresh)
        self.connect('key-press-event', self._on_key_press_event)

    def _on_key_press_event(self, source, event):
        self.pool.activate(event.keyval, event.modifier_state, source)

    def _on_validate(self, *args):
        if self._buttons_flash_fct:
            self._buttons_flash_fct(self._validate)
        if self._selected is not None:
            self.select_entry(self._selected)

    def _on_cancel(self, *args):
        if self._buttons_flash_fct:
            self._buttons_flash_fct(self._cancel)
        self.path = None
        if self.callback:
            self.callback(self.path)

    def _on_display_hidden_files(self, group, action_name, keyval, modifiers):
        if self._allow_hidden_files:
            self._display_hidden_files = not self._display_hidden_files
            self.refresh()

    def _on_refresh(self, group, action_name, keyval, modifiers):
        self.refresh()

    def _on_change_type_filter(self, type_filter):
        self.refresh()

    def set_delete_button(self, activate_delete_button=False):
        self.right_container.remove_element("delete_file_button")
        if activate_delete_button:
            # delete button
            self._delete_file_button = ClassicButton('Delete')
            self._delete_file_button.connect('button-release-event', self._on_delete_file_pressed)
            self._delete_file_button.set_font_name(self.styles['button_font_name'])
            self._delete_file_button.set_font_color(self.styles['button_font_color'])
            self._delete_file_button.set_inner_color(self.styles['button_inner_color'])
            self._delete_file_button.set_border_color(self.styles['button_border_color'])
            self._delete_file_button.set_texture(self.styles['button_texture'])
            self.right_container.add_element(self._delete_file_button, "delete_file_button", expand=True, resizable=0.1)

    def set_custom_widget(self, custom_widget=None):
        self.remove_custom_widget()
        if custom_widget:
            self.custom_widget = custom_widget
            self.top_container.add_element(self.custom_widget, "custom_widget", expand=False)
        else:
            self.custom_widget = None

    def remove_custom_widget(self):
        self.top_container.remove_element("custom_widget")

    def set_custom_image(self, custom_image=None):
        self.playbutton.remove_element()
        if custom_image:
            self._texture = clutter.Texture()
            self._texture.set_from_file(custom_image)
            self._texture.set_opacity(255)
            self.playbutton.set_element(self._texture)
            self.playbutton.set_reactive(True)

    def set_base_dir(self, base_dir, selected=None):
        self._base_dir = base_dir

        for path in self.paths:
            self._slider.remove(path[2])

        self._selected = None
        self._files_list.clear()
        self._current_dir = None
        self.paths = list()

        self.open_dir(base_dir, selected)

    def set_start_dir(self, start_dir, selected=None):
        # start_dir must be a subdirectory of base_dir
        # startswith is not enough because /home/toto1 is not a subdir of /home/toto
        if start_dir and os.path.dirname(start_dir).startswith(self._base_dir):
            self._start_dir = start_dir
        else:
            self._start_dir = self._base_dir

        for path in self.paths:
            self._slider.remove(path[2])

        self._selected = None
        self._files_list.clear()
        self._current_dir = None
        self.paths = list()
        directory = self._base_dir
        while directory != self._start_dir:
            if directory == os.sep:
                label = directory
                button = ClassicButton(directory)
            else:
                label = os.path.basename(directory)
            button = ClassicButton(label)
            button.index = len(self.paths) + 1
            button.connect('button-release-event', self._on_button_click)
            button.set_font_name(self.styles['button_font_name'])
            button.set_font_color(self.styles['button_font_color'])
            button.set_inner_color(self.styles['button_inner_color'])
            button.set_border_color(self.styles['button_border_color'])
            button.set_texture(self.styles['button_texture'])
            self.paths.append([directory, None, button])
            self._slider.add(button)
            rest = self._start_dir[len(directory):].strip(os.sep)
            directory = os.path.join(directory, rest.split(os.sep)[0])
        self.open_dir(self._start_dir, selected)

    def set_allow_hidden_files(self, allow_hidden_files):
        self._allow_hidden_files = allow_hidden_files
        if not self._allow_hidden_files:
            self._display_hidden_files = False
        self.refresh()

    def set_display_hidden_files(self, display_hidden_files):
        if self._allow_hidden_files and self._display_hidden_files != display_hidden_files:
            self.display_hidden_files = display_hidden_files
            self.refresh()

    def set_directories_first(self, directories_first):
        self._directories_first = directories_first
        self.refresh()

    def set_case_sensitive_sort(self, case_sensitive_sort):
        self._case_sensitive_sort = case_sensitive_sort
        self.refresh()

    def set_type_filters(self, type_filters):
        if type_filters:
            self._type_filters = list()
            for type_filter in type_filters:
                if type_filter in self.BASE_TYPE_FILTERS:
                    self._type_filters.append(self.BASE_TYPE_FILTERS[type_filter])
                else:
                    self._type_filters.append(type_filter)
        else:
            self._type_filters = [self.BASE_TYPE_FILTERS["all"]]
        self._type_filters_dict = dict()
        for type_filter in self._type_filters:
            self._type_filters_dict[type_filter.name] = type_filter

        selected = self._type_filter_select.get_selected().name
        self._type_filter_select.remove_all_options()
        for type_filter in self._type_filters:
            self._type_filter_select.add_option(type_filter.name, type_filter.full_label())
        if len(self._type_filters) < 2:
            self._type_filter_select.set_lock(True)
        if selected in self._type_filters_dict:
            self._type_filter_select.select_option(selected)

        self.refresh()

    def get_actor(self, name):
        if name == 'background':
            return self._bg
        if name == 'panel':
            return self._files_panel
        if name == 'slider':
            return self._slider
        elif name == 'next_btn':
            return self._slider.get_next_button()
        elif name == 'previous_btn':
            return self._slider.get_previous_button()
        elif name == 'delete_btn':
            return self._delete_file_button
        elif name == 'cancel_btn':
            return self._cancel
        elif name == 'validate_btn':
            return self._validate
        elif name == 'type_filter':
            return self._type_filter_select

    def set_buttons_flash_fct(self, fct):
        self._buttons_flash_fct = fct
        self._slider.set_buttons_flash_fct(fct)

    def select_next(self, *args):
        files_entries = self._files_list.get_children()
        if len(files_entries) == 0:
            return

        if self._selected is None:
            self.select_entry(files_entries[0])
        else:
            index = files_entries.index(self._selected) + 1
            try:
                file_entry = files_entries[index]
            except IndexError:
                pass
            else:
                self.select_entry(file_entry)

    def select_previous(self, *args):
        files_entries = self._files_list.get_children()
        if len(files_entries) == 0:
            return

        if self._selected is None:
            self.select_entry(files_entries[len(files_entries) - 1])
        else:
            index = files_entries.index(self._selected) - 1
            if index == -1:
                return
            try:
                file_entry = files_entries[index]
            except IndexError:
                pass
            else:
                self.select_entry(file_entry)

    def select_entry(self, source, event=None):
        self.path = source.name
        is_dir = os.path.isdir(self.path)
        if not source.selected:
            if self._selected is not None:
                self._selected.set_selected(False)
            self._selected = source
            self.paths[-1][1] = source.text
            source.set_selected(True)
            self._video_container.remove_all()
            self.preview_block.remove_all()
            try:
                mc = magic.open(magic.MAGIC_MIME_TYPE)
                mc.load()
                mime_type = mc.file(source.name)
                mc.close()
                file_type = mime_type.split('/')[0]
            except Exception:
                pass
            else:
                if file_type == 'image':
                    self._preview.set_from_file(self.path)
                    self._aligner.set_element(self._preview)
                    self.preview_block.add(self._aligner)
                    self.preview_block.show()
                elif file_type == 'video':
                    self.path = os.path.abspath(self.path)
                    self.reset_player()
                    self._video_player.set_file(self.path)
                    self._video_player.set_reactive(True)
                    self._video_player.set_audio_volume(0)
                    self._video_player.play()
                    gobject.timeout_add(40, self._video_player.pause)
                    self._aligner.set_element(self._video_player)
                    self._texture.show()
                    self._video_container.add(self._aligner)
                    self._video_container.add(self.playbutton)
                    self.preview_block.add(self._video_container)
                    self.preview_block.show()
                else:
                    self.preview_block.hide()
        elif event is None:
            if is_dir:
                self.open_dir(self.path)
            else:
                if self.callback:
                    self.callback(self.path)
        if event is not None and is_dir:
            self.open_dir(self.path)

    def _on_click(self, source=None, event=None):
        if self._video_player:
            if self._video_player.get_playing():
                self._video_player.pause()
                if self._texture:
                    self._texture.show()
            else:
                self._video_player.play()
                if self._texture:
                    self._texture.hide()

    def reset_player(self):
        if self.path is not None and self._video_player is not None:
            self._video_player.pause()
            self._video_player.reset_pipeline()
            self._video_player.set_uri('')

    def reinit(self):
        self._video_player.destroy()
        self._video_player = VideoPlayer()
        self._video_player.connect('button-release-event', self._on_click)

    def _files_comparator(self, file1, file2):
        abs_path1 = os.path.join(self._current_dir, file1)
        abs_path2 = os.path.join(self._current_dir, file2)
        is_dir1 = os.path.isdir(abs_path1)
        is_dir2 = os.path.isdir(abs_path2)
        if self._directories_first:
            if is_dir1 and not is_dir2:
                return -1
            if is_dir2 and not is_dir1:
                return 1
        if not self._case_sensitive_sort:
            file1 = file1.lower()
            try:
                file1 = unicode(file1.encode("latin1", "ignore"), "utf8")
            except Exception:
                try:
                    file1 = unicode(file1, "utf8")
                except Exception:
                    pass
            try:
                file1 = unicodedata.normalize("NFKD", file1).encode("utf8", "ignore")
            except Exception:
                pass
            file2 = file2.lower()
            try:
                file2 = unicode(file2.encode("latin1", "ignore"), "utf8")
            except Exception:
                try:
                    file2 = unicode(file2, "utf8")
                except Exception:
                    pass
            try:
                file2 = unicodedata.normalize("NFKD", file2).encode("utf8", "ignore")
            except Exception:
                pass
        return cmp(file1, file2)

    def change_dir(self, dir_path, selected=None):
        self._selected = None
        self._files_list.clear()
        self._current_dir = dir_path
        files = os.listdir(dir_path)

        # filter by type
        current_type_filter = self._type_filters_dict[self._type_filter_select.get_selected().name]
        tmp = list()
        for file_ in files:
            file_path = os.path.join(dir_path, file_)
            if os.path.isdir(file_path) or current_type_filter.file_matchs(file_):
                tmp.append(file_)
        files = tmp

        # hide dot files if required
        if not self._display_hidden_files:
            files = [f for f in files if not f.startswith('.')]

        files.sort(cmp=self._files_comparator)

        cycle = 'even'
        index = 0
        if len(files) > 0:
            self.right_container.show()
        else:
            self.right_container.hide()
        for name in files:
            file_path = os.path.join(dir_path, name)
            is_dir = os.path.isdir(file_path)
            extension = ''
            if is_dir:
                icon_src = self.icons.get('folder', self.icons['default'])
            else:
                extension = os.path.splitext(name)[1][1:]
                icon_src = self.icons.get(extension, self.icons['default'])
            file_entry = FileEntry(name=file_path, icon_src=icon_src, text=name, extension=extension, is_dir=is_dir)
            file_entry.set_reactive(True)
            file_entry.connect('button-release-event', self.select_entry)
            if cycle == 'even':
                cycle = 'odd'
                file_entry.set_bg_color(self.styles['file_bg2'])
                file_entry.set_selected_bg_color(self.styles['selected_bg2'])
            else:
                cycle = 'even'
                file_entry.set_bg_color(self.styles['file_bg'])
                file_entry.set_selected_bg_color(self.styles['selected_bg'])
            self._files_list.add(file_entry)
            if name == selected:
                index = files.index(name)
        self._files_panel.check_scrollbar()

        # select index
        try:
            to_select = self._files_list.get_children()[index]
        except IndexError:
            self.preview_block.hide()
        else:
            self.select_entry(to_select)

    def _return_to_index(self, index):
        current_index = len(self.paths)
        diff = current_index - index
        if diff > 0:
            for i in range(diff):
                button = self.paths.pop()[2]
                self._slider.remove(button)
            self._slider.complete_relayout()
            if len(self.paths) > 4:
                self._slider.go_to_end()
            else:
                self._slider.go_to_beginning()
            path, selected, button = self.paths[-1]
            self.change_dir(path, selected)

    def _on_button_click(self, source, event):
        if self._buttons_flash_fct:
            self._buttons_flash_fct(source)
        self._return_to_index(source.index)

    def set_hidden_path(self, hidden_path):
        self._set_buttons_opacity(0 if hidden_path else 255)

    def _set_buttons_opacity(self, opacity=0):
        for element in self.paths:
            try:
                button = element[2]
                button.set_opacity(opacity)
            except Exception:
                pass

    def open_dir(self, path, selected=None):
        if self._current_dir != path:
            button = ClassicButton(os.path.basename(path))
            button.index = len(self.paths) + 1
            button.connect('button-release-event', self._on_button_click)
            button.set_font_name(self.styles['button_font_name'])
            button.set_font_color(self.styles['button_font_color'])
            button.set_inner_color(self.styles['button_inner_color'])
            button.set_border_color(self.styles['button_border_color'])
            button.set_texture(self.styles['button_texture'])
            self.paths.append([path, selected, button])
            self._slider.add(button)
            self._slider.complete_relayout()
            if len(self.paths) > 4:
                self._slider.go_to_end()
            else:
                self._slider.go_to_beginning()
        self.change_dir(path, selected)

    def parent_dir(self, *args):
        if len(self.paths) > 1:
            button = self.paths.pop()[2]
            self._slider.remove(button)
            self._slider.complete_relayout()
            if len(self.paths) > 4:
                self._slider.go_to_end()
            else:
                self._slider.go_to_beginning()
            path, selected, button = self.paths[-1]
            self.change_dir(path, selected)

    def _on_delete_file_pressed(self, source, event):
        try:
            os.remove(self.path)
        except Exception:
            pass
        self.path = None
        self.refresh()

    def refresh(self):
        selected = None
        if self.paths:
            selected = self.paths[-1][1]
        self.open_dir(self._current_dir, selected)

    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1

        inner_width = width - 2 * self._padding.x

        bg_box = clutter.ActorBox(0, 0, width, height)

        top_container_box = clutter.ActorBox()
        top_container_box.x1 = self._padding.x
        top_container_box.y1 = self._padding.y
        top_container_box.x2 = self._padding.x + inner_width
        top_container_box.y2 = self._padding.y + self.styles['top_bar_height']

        panel_bg_box = clutter.ActorBox()
        panel_bg_box.x1 = self._padding.x
        panel_bg_box.y1 = top_container_box.y2
        panel_bg_box.x2 = width - self._padding.x
        panel_bg_box.y2 = height - self._padding.y - self.styles['bottom_bar_height']

        panel_box = clutter.ActorBox()
        panel_box.x1 = panel_bg_box.x1
        panel_box.y1 = panel_bg_box.y1
        panel_box.x2 = width - self._padding.x - self.styles['preview_width'] - self._spacing.x
        panel_box.y2 = panel_bg_box.y2

        right_box = clutter.ActorBox()
        right_box.x1 = panel_box.x2 + self._spacing.x
        right_box.y1 = panel_bg_box.y1
        right_box.x2 = panel_bg_box.x2
        right_box.y2 = panel_bg_box.y2

        type_filter_box = clutter.ActorBox()
        type_filter_box.y1 = panel_bg_box.y2 + self.components_padding
        type_filter_box.y2 = height - self._padding.y - self.components_padding
        type_filter_width = self._type_filter_select.get_preferred_width(for_height=type_filter_box.y2 - type_filter_box.y1)[1]
        type_filter_box.x1 = width - self._spacing.x - self.components_padding - type_filter_width
        type_filter_box.x2 = type_filter_box.x1 + type_filter_width

        cancel_box = clutter.ActorBox()
        cancel_box.y1 = type_filter_box.y1
        cancel_box.y2 = type_filter_box.y2
        cancel_width = self._cancel.get_preferred_width(for_height=cancel_box.y2 - cancel_box.y1)[1]
        cancel_box.x1 = self._spacing.x + self.components_padding
        cancel_box.x2 = cancel_box.x1 + cancel_width

        validate_box = clutter.ActorBox()
        validate_box.y1 = type_filter_box.y1
        validate_box.y2 = type_filter_box.y2
        validate_width = self._validate.get_preferred_width(for_height=validate_box.y2 - validate_box.y1)[1]
        validate_box.x1 = (type_filter_box.x1 + cancel_box.x2 - validate_width) / 2
        validate_box.x2 = validate_box.x1 + validate_width

        self._bg.allocate(bg_box, flags)
        self.top_container.allocate(top_container_box, flags)
        self._panel_bg.allocate(panel_bg_box, flags)
        self._files_panel.allocate(panel_box, flags)
        self.right_container.allocate(right_box, flags)
        self._validate.allocate(validate_box, flags)
        self._type_filter_select.allocate(type_filter_box, flags)
        self._cancel.allocate(cancel_box, flags)

        clutter.Actor.do_allocate(self, box, flags)


if __name__ == '__main__':
    # stage
    stage = clutter.Stage()
    stage_width = 1200
    stage_height = 700
    stage.set_size(stage_width, stage_height)
    stage.set_color('#000000ff')
    stage.connect('destroy', clutter.main_quit)

    def cb(result):
        print result
        # clutter.main_quit()

    icons = dict(
        default='/data/sdiemer/storage/images/iconset musthave/New.png',
        folder='/data/sdiemer/storage/images/iconset musthave/Folder.png',
        bmp='/data/sdiemer/storage/images/iconset musthave/Picture.png',
        tiff='/data/sdiemer/storage/images/iconset musthave/Picture.png',
        gif='/data/sdiemer/storage/images/iconset musthave/Picture.png',
        jpg='/data/sdiemer/storage/images/iconset musthave/Picture.png',
        png='/data/sdiemer/storage/images/iconset musthave/Picture.png',
        cancel_btn='/data/sdiemer/storage/images/iconset musthave/Previous.png',
        validate_btn='/data/sdiemer/storage/images/iconset musthave/Next.png',
    )

    """
    icons = dict(
        default='/home/sde-melo/bzr/easycast/images/files_icons/default.png',
        folder='/home/sde-melo/bzr/easycast/images/files_icons/folder.png',
        bmp='/home/sde-melo/bzr/easycast/images/files_icons/img.png',
        tiff='/home/sde-melo/bzr/easycast/images/files_icons/img.png',
        gif='/home/sde-melo/bzr/easycast/images/files_icons/img.png',
        jpg='/home/sde-melo/bzr/easycast/images/files_icons/img.png',
        png='/home/sde-melo/bzr/easycast/images/files_icons/img.png',
        cancel_btn='/home/sde-melo/bzr/easycast/images/buttons/cancel.png',
        validate_btn='/home/sde-melo/bzr/easycast/images/buttons/right.png'
    )
    """

    type_filters = (
        "images",
        TypeFilter("text", ("txt",), "Text files"),
        "all"
    )

    fc = FileChooser(base_dir='/data', start_dir='/data/sdiemer', allow_hidden_files=True, directories_first=True, case_sensitive_sort=False, type_filters=type_filters, callback=cb, icons=icons)
    # fc = FileChooser(base_dir='/home/sde-melo', start_dir='/home/sde-melo/Images', allow_hidden_files=True, directories_first=True, case_sensitive_sort=False, type_filters=type_filters, callback=cb, icons=icons)
    fc.set_size(1100, 600)
    fc.set_position(50, 50)
    stage.add(fc)
    fc.set_focused(True)

    stage.show()
    clutter.main()
