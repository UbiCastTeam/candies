#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gobject
import clutter
import common
from container import BaseContainer
from buttons import ClassicButton
from autoscroll import AutoScrollPanel
from list import LightList
from aligner import Aligner
from slider import Slider
from dropdown import OptionLine


class FileEntry(BaseContainer):
    '''
    An actor to represet a file
    '''
    __gtype_name__ = 'FileEntry'

    def __init__(self, name='', icon_src='', text='', extension='', is_dir=False, padding=10, spacing=10):
        BaseContainer.__init__(self, allow_add=False, allow_remove=False, pick_enabled=False)
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)
        self.name = name
        self.selected = False
        self._icon_src = icon_src
        self._text = text
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
        self._label.set_ellipsize(2) # let 2 words after "..."
        self._label.set_line_alignment(3) # align text to left
        self._label.set_text(text)
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
            h = for_height - 2*self._padding.y
        else:
            h = for_height
        preferred_width = 2*self._padding.x + self._icon.get_preferred_width(h)[1] + self._label.get_preferred_width(h)[1]
        return preferred_width, preferred_width
    
    def do_get_preferred_height(self, for_width):
        if for_width != -1:
            w = for_width - 2*self._padding.x - self._spacing.x - self.icon_size
        else:
            w = for_width
        preferred_height = 2*self._padding.y + max(self.label.get_preferred_height(w), self.icon_size)
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        
        inner_width = width - 2*self._padding.x
        inner_height = height - 2*self._padding.y
        
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
        inner_width = width - 2*self._padding.x
        inner_height = height - 2*self._padding.y
        
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


class FileChooser(BaseContainer):
    '''
    A pannel to select file
    '''
    __gtype_name__ = 'FileChooser'
    
    def __init__(self, base_dir='/', callback=None, padding=0, spacing=0, styles=None, icons=None):
        BaseContainer.__init__(self, allow_add=False, allow_remove=False)
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)
        self._base_dir = base_dir
        self.callback = callback
        
        if not styles:
            self.styles = dict(
                file_bg = '#333333ff',
                file_bg2 = '#444444ff',
                selected_bg = '#228822ff',
                selected_bg2 = '#228822ff',
                bg_color = '#222222ff',
                button_font_name = '14',
                button_font_color = '#ffffffff',
                button_inner_color = '#444444ff',
                button_border_color = '#333333ff',
                element_size = 50,
                preview_width = 500,
                top_bar_height = 64,
                bottom_bar_height = 64,
                button_texture = None,
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
        self.paths = list() # list of tuples with path and current selection index
        
        # actors
        self._bg = clutter.Rectangle()
        self._bg.set_color(self.styles['bg_color'])
        self._add(self._bg)
        
        self._slider = Slider(elements_per_page=4, keep_ratio=False, horizontal=True, margin=10, h_align='left')
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
        self._add(self._slider)
        
        self._files_list = LightList(element_size=self.styles['element_size'])
        self._files_pannel = AutoScrollPanel(self._files_list)
        self._add(self._files_pannel)
        
        self._preview = PreviewDisplayer(padding=self.components_padding)
        self._preview.hide()
        self._add(self._preview)
        
        self._cancel = OptionLine('cancel', 'Cancel', icon_path=self.icons.get('cancel_btn'), padding=(10, 0))
        self._cancel.set_reactive(True)
        self._cancel.connect('button-release-event', self._on_cancel)
        self._cancel.set_font_name(self.styles['button_font_name'])
        self._cancel.set_font_color(self.styles['button_font_color'])
        self._cancel.set_inner_color(self.styles['button_inner_color'])
        self._cancel.set_border_color(self.styles['button_border_color'])
        self._cancel.set_texture(self.styles['button_texture'])
        self._add(self._cancel)
        
        self._validate = OptionLine('validate', 'Validate', icon_path=self.icons.get('validate_btn'), padding=(10, 0))
        self._validate.set_reactive(True)
        self._validate.connect('button-release-event', self._on_validate)
        self._validate.set_font_name(self.styles['button_font_name'])
        self._validate.set_font_color(self.styles['button_font_color'])
        self._validate.set_inner_color(self.styles['button_inner_color'])
        self._validate.set_border_color(self.styles['button_border_color'])
        self._validate.set_texture(self.styles['button_texture'])
        self._add(self._validate)
        
        self.open_dir(base_dir)
        
        # key bindings
        self.pool = clutter.BindingPool('%s_%s' %(self.__gtype_name__, id(self)))
        self.pool.install_action('move-down', clutter.keysyms.Down, None, self.select_next)
        self.pool.install_action('move-up', clutter.keysyms.Up, None, self.select_previous)
        self.pool.install_action('parent', clutter.keysyms.BackSpace, None, self.parent_dir)
        self.pool.install_action('select', clutter.keysyms.Return, None, self._on_validate)
        self.pool.install_action('select', clutter.keysyms.KP_Enter, None, self._on_validate)
        self.pool.install_action('escape', clutter.keysyms.Escape, None, self._on_cancel)
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
        if self.callback:
            self.callback(None)
    
    def get_actor(self, name):
        if name == 'background':
            return self._bg
        if name == 'pannel':
            return self._files_pannel
        if name == 'slider':
            return self._slider
        elif name == 'next_btn':
            return self._slider.get_next_button()
        elif name == 'previous_btn':
            return self._slider.get_previous_button()
        elif name == 'cancel_btn':
            return self._cancel
        elif name == 'validate_btn':
            return self._validate
    
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
        path = source.name
        is_dir = os.path.isdir(path)
        if not source.selected:
            if self._selected is not None:
                self._selected.set_selected(False)
            self._selected = source
            index = self._files_list.get_children().index(self._selected)
            self.paths[-1][1] = index
            source.set_selected(True)
            if not is_dir and source.extension in ('bmp', 'png', 'gif', 'tiff', 'jpg'):
                self._preview.set_from_file(path)
                self._preview.show()
            else:
                self._preview.hide()
        elif event is None:
            if is_dir:
                self.open_dir(path)
            else:
                if self.callback:
                    self.callback(path)
        if event is not None and is_dir:
            self.open_dir(path)
    
    def change_dir(self, dir_path, index=0):
        self._selected = None
        self._files_list.clear()
        self._current_dir = dir_path
        files = os.listdir(dir_path)
        files.sort()
        
        cycle = 'even'
        for name in files:
            file_path = os.path.join(dir_path, name)
            is_dir = os.path.isdir(file_path)
            extension = ''
            if not is_dir:
                splitted = name.split('.')
                extension = splitted[len(splitted) - 1]
                icon_src = self.icons.get(extension, self.icons['default'])
            else:
                icon_src = self.icons.get('folder', self.icons['default'])
            file_entry = FileEntry(name=file_path, icon_src=icon_src, text=name, extension=extension, is_dir=is_dir)
            file_entry.set_reactive(True)
            file_entry.connect('button-release-event', self.select_entry)
            if cycle != 'even':
                cycle = 'even'
                file_entry.set_bg_color(self.styles['file_bg'])
                file_entry.set_selected_bg_color(self.styles['selected_bg'])
            else:
                cycle = 'odd'
                file_entry.set_bg_color(self.styles['file_bg2'])
                file_entry.set_selected_bg_color(self.styles['selected_bg2'])
            self._files_list.add(file_entry)
        self._files_pannel.check_scrollbar()
        
        # select index
        try:
            to_select = self._files_list.get_children()[index]
        except IndexError:
            pass
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
            path, index, button = self.paths[-1]
            self.change_dir(path, index)
    
    def _on_button_click(self, source, event):
        if self._buttons_flash_fct:
            self._buttons_flash_fct(source)
        self._return_to_index(source.index)
    
    def open_dir(self, path):
        if self._current_dir == path:
            return
        button = ClassicButton(os.path.basename(path))
        button.index = len(self.paths) + 1
        button.connect('button-release-event', self._on_button_click)
        button.set_font_name(self.styles['button_font_name'])
        button.set_font_color(self.styles['button_font_color'])
        button.set_inner_color(self.styles['button_inner_color'])
        button.set_border_color(self.styles['button_border_color'])
        button.set_texture(self.styles['button_texture'])
        self.paths.append([path, 0, button])
        self._slider.add(button)
        self._slider.complete_relayout()
        self._slider.go_to_end()
        self.change_dir(path, 0)
    
    def parent_dir(self, *args):
        if len(self.paths) > 1:
            button = self.paths.pop()[2]
            self._slider.remove(button)
            self._slider.complete_relayout()
            if len(self.paths) > 4:
                self._slider.go_to_end()
            else:
                self._slider.go_to_beginning()
            path, index, button = self.paths[-1]
            self.change_dir(path, index)
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        
        inner_width = width - 2*self._padding.x
        inner_height = height - 2*self._padding.y
        
        bg_box = clutter.ActorBox(0, 0, width, height)
        
        slider_box = clutter.ActorBox()
        slider_box.x1 = self._padding.x
        slider_box.y1 = self._padding.y
        slider_box.x2 = self._padding.x + inner_width
        slider_box.y2 = self._padding.y + self.styles['top_bar_height']
        
        pannel_box = clutter.ActorBox()
        pannel_box.x1 = self._padding.x
        pannel_box.y1 = self._padding.y + self.styles['top_bar_height']
        pannel_box.x2 = width - self._padding.x - self.styles['preview_width'] - self._spacing.x
        pannel_box.y2 = height - self._padding.y - self.styles['bottom_bar_height']
        
        preview_box = clutter.ActorBox()
        preview_box.x1 = pannel_box.x2 + self._spacing.x
        preview_box.y1 = pannel_box.y1
        preview_box.x2 = width - self._padding.x
        preview_box.y2 = pannel_box.y2
        
        validate_box = clutter.ActorBox()
        validate_box.y1 = pannel_box.y2 + self.components_padding
        validate_box.y2 = height - self._padding.y - self.components_padding
        validate_width = self._validate.get_preferred_width(for_height=validate_box.y2 - validate_box.y1)[1]
        validate_box.x1 = width - self._spacing.x - self.components_padding - validate_width
        validate_box.x2 = validate_box.x1 + validate_width
        
        cancel_box = clutter.ActorBox()
        cancel_box.y1 = validate_box.y1
        cancel_box.y2 = validate_box.y2
        cancel_width = self._cancel.get_preferred_width(for_height=cancel_box.y2 - cancel_box.y1)[1]
        cancel_box.x1 = self._spacing.x + self.components_padding
        cancel_box.x2 = cancel_box.x1 + cancel_width
        
        self._bg.allocate(bg_box, flags)
        self._slider.allocate(slider_box, flags)
        self._files_pannel.allocate(pannel_box, flags)
        self._preview.allocate(preview_box, flags)
        self._validate.allocate(validate_box, flags)
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
    
    icons = dict(
        default = '/data/sdiemer/storage/images/iconset musthave/New.png',
        folder = '/data/sdiemer/storage/images/iconset musthave/Folder.png',
        bmp = '/data/sdiemer/storage/images/iconset musthave/Picture.png',
        tiff = '/data/sdiemer/storage/images/iconset musthave/Picture.png',
        gif = '/data/sdiemer/storage/images/iconset musthave/Picture.png',
        jpg = '/data/sdiemer/storage/images/iconset musthave/Picture.png',
        png = '/data/sdiemer/storage/images/iconset musthave/Picture.png',
        cancel_btn = '/data/sdiemer/storage/images/iconset musthave/Previous.png',
        validate_btn = '/data/sdiemer/storage/images/iconset musthave/Next.png',
    )
    fc = FileChooser(base_dir='/data', callback=cb, icons=icons)
    fc.set_size(1100, 600)
    fc.set_position(50, 50)
    stage.add(fc)
    fc.set_focused(True)
    
    stage.show()
    clutter.main()
    





