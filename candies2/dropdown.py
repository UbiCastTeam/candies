#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter
from roundrect import RoundRectangle
from text import TextContainer
from box import VBox
from autoscroll import AutoScrollPanel

class OptionLine(clutter.Actor, clutter.Container):
    """
    A option line for select input. Can be used alone to have a text with icon.
    """
    __gtype_name__ = 'OptionLine'
    
    def __init__(self, name, text, icon_height=32, icon_path=None, padding=8, spacing=8, enable_background=True, font='14', font_color='Black', color='LightGray', border_color='Gray', texture=None, rounded=True):
        clutter.Actor.__init__(self)
        self.name = name
        self.padding = padding
        self.spacing = spacing
        self._children = list()
        
        self.font = font
        self.font_color = font_color
        self.default_color = color
        self.default_border_color = border_color
        
        # background
        if rounded:
            self.background = RoundRectangle(texture=texture)
            self.background.set_color(self.default_color)
            self.background.set_border_color(self.default_border_color)
            self.background.set_border_width(3)
            self.background.set_radius(10)
        else:
            self.background = clutter.Rectangle()
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
        self.icon = clutter.Texture()
        if icon_path:
            self.icon.set_from_file(icon_path)
        else:
            self.icon.hide()
        self._add(self.icon)
        # label
        self.label = TextContainer(text, padding=0, rounded=False)
        self.label.set_font_color(self.font_color)
        self.label.set_font_name(self.font)
        self.label.set_inner_color('#00000000')
        self.label.set_border_color('#00000000')
        self._add(self.label)
    
    def _add(self, *children):
        for child in children:
            child.set_parent(self)
            self._children.append(child)
    
    def get_text(self):
        return self.label.get_text()
    
    def set_texture(self, texture):
        self.background.set_texture(texture)
    
    def set_line_wrap(self, boolean):
        self.label.set_line_wrap(boolean)
            
    def set_line_alignment(self, alignment):
        self.label.set_line_alignment(alignment)
    
    def set_justify(self, boolean):
        self.label.set_justify(boolean)
    
    def set_text(self, text):
        self.label.set_text(text)
        self.queue_relayout()
    
    def set_name(self, text):
        self.name = text
    
    def set_hname(self, text):
        self.label.set_text(text)
        self.queue_relayout()
        
    def set_icon(self, new_icon_path=None):
        self.icon_path = new_icon_path
        if new_icon_path:
            self.icon.set_from_file(new_icon_path)
            self.icon.show()
        else:
            self.icon.hide()
    
    def set_font_color(self, color):
        self.label.set_font_color(color)
    
    def set_font_name(self, font_name):
        self.label.set_font_name(font_name)
    
    def set_inner_color(self, color):
        self.background.set_color(color)
    
    def set_border_color(self, color):
        self.background.set_border_color(color)
    
    def set_radius(self, radius):
        self.background.set_radius(radius)
    
    def set_border_width(self, width):
        self.background.set_border_width(width)
    
    def set_icon_opacity(self, opacity):
        self.icon.set_opacity(opacity)
    
    def show_background(self):
        if self.enable_background != True:
            self.enable_background = True
            self.background.show()
    
    def hide_background(self):
        if self.enable_background != False:
            self.enable_background = False
            self.background.hide()
    
    def do_get_preferred_width(self, for_height):
        if for_height != -1:
            for_height -= 2*self.padding
        preferred_width = self.icon_height + 2*self.padding + self.spacing
        preferred_width += self.label.get_preferred_width(for_height)[1]
        return preferred_width, preferred_width
    
    def do_get_preferred_height(self, for_width):
        preferred_height = self.icon_height + 2*self.padding
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        
        # background
        background_box = clutter.ActorBox()
        background_box.x1 = 0
        background_box.y1 = 0
        background_box.x2 = main_width
        background_box.y2 = main_height
        self.background.allocate(background_box, flags)
        
        # icon
        icon_y_padding = int(float(main_height - self.icon_height)/2.0)
        icon_box = clutter.ActorBox()
        icon_box.x1 = self.padding
        icon_box.y1 = icon_y_padding
        icon_box.x2 = self.padding + self.icon_height
        icon_box.y2 = icon_box.y1 + self.icon_height
        self.icon.allocate(icon_box, flags)
        
        # label
        label_box = clutter.ActorBox()
        label_box.x1 = icon_box.x2 + self.spacing
        label_box.y1 = self.padding
        label_box.x2 = main_width - self.padding
        label_box.y2 = main_height - self.padding
        self.label.allocate(label_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for child in self._children:
            func(child, data)
    
    def do_paint(self):
        for actor in self._children:
            actor.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_children'):
            for child in self._children:
                child.unparent()
                child.destroy()
            self._children = list()
    

class Select(clutter.Actor, clutter.Container):
    """
    A select input.
    """
    __gtype_name__ = 'Select'
    
    def __init__(self, padding=8, spacing=8, on_change_callback=None, icon_height=48, open_icon_path=None, font='14', font_color='Black', selected_font_color='Blue', color='LightGray', border_color='Gray', option_color='LightBlue', texture=None, user_data=None):
        clutter.Actor.__init__(self)
        self.padding = padding
        self.spacing = spacing
        self.stage_padding = 10
        self.on_change_callback = on_change_callback
        self.user_data = user_data
        self.icon_height = icon_height
        self._stage_width, self._stage_height = 0, 0
        self._opened = False
        
        self._selected = None
        self.open_icon = open_icon_path
        self._background_box = None
        
        self.font = font
        self.font_color = font_color
        self.selected_font_color = selected_font_color
        self.default_color = color
        self.default_border_color = border_color
        self.option_color = option_color
        self.texture = texture
        
        # hidder is to catch click event on all stage when the select input is opened
        self._hidder = clutter.Rectangle()
        self._hidder.set_color('#00000000')
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
        self._list = VBox()
        # auto scroll panel
        self._auto_scroll = AutoScrollPanel(self._list)
        self._auto_scroll.hide()
        self._auto_scroll.set_parent(self)
        # selected option is displayed when the select input is closed
        self._selected_option = OptionLine('empty', '', padding=self.padding, spacing=self.spacing, icon_path=self.open_icon, icon_height=self.icon_height, enable_background=True, font=self.font, font_color=self.font_color, color=self.option_color, border_color='#00000000', texture=self.texture)
        self._selected_option.set_reactive(True)
        self._selected_option.connect('button-release-event', self._on_selected_click)
        self._selected_option.set_parent(self)

    def set_lock(self, status):
        self.set_disabled(status)
        self.set_opacity(255 - status*128)

    def set_disabled(self, boolean):
        if boolean:
            self._selected_option.set_reactive(False)
        else:
            self._selected_option.set_reactive(True)
    
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
        if isinstance(obj, clutter.Stage):
            return obj
        else:
            return None
    
    def get_selected(self):
        return self._selected
    
    def set_locked(self, lock):
        if lock:
            self._selected_option.set_reactive(False)
            self._selected_option.icon.hide()
        else:
            self._selected_option.set_reactive(True)
            self._selected_option.icon.show()
    
    def add_option(self, name, hname, icon_path=None):
        new_option = OptionLine(name, hname, padding=self.padding, spacing=self.spacing, icon_path=icon_path, icon_height=self.icon_height, enable_background=False, font=self.font, font_color=self.font_color, color=self.option_color, border_color='#00000000', texture=self.texture)
        new_option.set_reactive(True)
        new_option.connect('button-release-event', self._on_click)
        self._list.add_element(new_option, 'option_%s' %name, expand=True)
        self.check_scrollbar()
        
        if self._selected is None:
            self._selected = new_option
            self._selected.set_font_color(self.selected_font_color)
            self._selected.show_background()
            self._selected_option.set_name(name)
            self._selected_option.set_text(hname)
    
    def remove_option(self, name):
        if self._list.get_elements_count() == 1:
            self.remove_all_options()
        else:
            self._list.remove_element('option_%s' %name)
            self.check_scrollbar()
    
    def remove_all_options(self):
        self._list.remove_all_elements()
        self.check_scrollbar()
        self._selected = None
        self._selected_option.set_name('empty')
        self._selected_option.set_text('')
    
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
    
    def select_option(self, name, silent=True):
        element = self._list.get_by_name('option_%s' %name)
        if element is not None:
            option = element['object']
            self._select_option(option, silent=silent)
            self.queue_relayout()
    
    def _select_option(self, option, silent=True):
        if option != self._selected:
            if self._selected is not None:
                self._selected.hide_background()
                self._selected.set_font_color(self.font_color)
            
            self._selected = option
            self._selected.set_font_color(self.selected_font_color)
            self._selected.show_background()
            
            self._selected_option.set_name(option.name)
            self._selected_option.set_text(option.get_text())
            
            if self.on_change_callback is not None and not silent:
                if self.user_data is not None:
                    self.on_change_callback(self._selected, self.user_data)
                else:
                    self.on_change_callback(self._selected)
    
    def set_bar_image_path(self, path):
        self._auto_scroll.set_bar_image_path(path)
    
    def set_scroller_image_path(self, path):
        self._auto_scroll.set_scroller_image_path(path)
    
    def do_get_preferred_width(self, for_height):
        preferred = max(self._auto_scroll.get_preferred_width(for_height)[1], self._selected_option.get_preferred_width(for_height)[1])
        return preferred, preferred
    
    def do_get_preferred_height(self, for_width):
        preferred = self._selected_option.get_preferred_height(for_width)[1]
        return preferred, preferred
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        
        if self._opened:
            option_box = clutter.ActorBox(0, 0, main_width, main_height)
            self._selected_option.allocate(option_box, flags)
            
            box_x, box_y = self.get_transformed_position()
            box_x = int(box_x)
            box_y = int(box_y)
            
            if self._stage_height > 0 and self._stage_width > 0:
                hidder_box = clutter.ActorBox(-box_x, -box_y, self._stage_width-box_x, self._stage_height-box_y)
            else:
                hidder_box = clutter.ActorBox(self.padding, self.padding, self.padding, self.padding)
            self._hidder.allocate(hidder_box, flags)
            
            total_height = (self.icon_height + 2*self.padding) * len(self._list.get_elements())
            base_y = 0
            if self._stage_height > 0 and box_y + total_height > self._stage_height - self.stage_padding:
                if total_height > self._stage_height - 2*self.stage_padding:
                    total_height = self._stage_height - 2*self.stage_padding
                    base_y -= box_y - self.stage_padding
                    #TODO enable scrollbar
                else:
                    base_y -= box_y - (self._stage_height - self.stage_padding - total_height)
            self._background_box = clutter.ActorBox(0, base_y, main_width, base_y + total_height)
            self._background.allocate(self._background_box, flags)
            list_box = clutter.ActorBox(0, base_y, main_width, base_y + total_height)
            self._auto_scroll.allocate(list_box, flags)
        else:
            hidder_box = clutter.ActorBox(self.padding, self.padding, self.padding, self.padding)
            self._hidder.allocate(hidder_box, flags)
            self._background_box = clutter.ActorBox(0, 0, main_width, main_height)
            self._background.allocate(self._background_box, flags)
            option_box = clutter.ActorBox(0, 0, main_width, main_height)
            self._selected_option.allocate(option_box, flags)
            list_box = clutter.ActorBox(0, 0, main_width, main_height)
            self._auto_scroll.allocate(list_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
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
            clutter.cogl.path_round_rectangle(
                self._background_box.x1 + 3,
                self._background_box.y1 + 3,
                self._background_box.x2 - 3,
                self._background_box.y2 - 3,
                7,
                1
            )
            clutter.cogl.path_close()
            # Start the clip
            clutter.cogl.clip_push_from_path()
        
            self._auto_scroll.paint()
            
            # Finish the clip
            clutter.cogl.clip_pop()
        else:
            self._auto_scroll.paint()
    
    def do_pick(self, color):
        self.do_paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_hidder'):
            if self._hidder is not None:
                self._hidder.unparent()
                self._hidder.destroy()
                self._hidder = None
        if hasattr(self, '_background'):
            if self._background is not None:
                self._background.unparent()
                self._background.destroy()
                self._background = None
        if hasattr(self, '_selected_option'):
            if self._selected_option is not None:
                self._selected_option.unparent()
                self._selected_option.destroy()
                self._selected_option = None
        if hasattr(self, 'auto_scroll'):
            if self._auto_scroll is not None:
                self._auto_scroll.unparent()
                self._auto_scroll.destroy()
                self._auto_scroll = None
        self._selected = None
        self._list = None


if __name__ == '__main__':
    stage_width = 640
    stage_height = 480
    stage = clutter.Stage()
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', clutter.main_quit)
    
    test_line = OptionLine('test', 'displayed fezfzefezfzef', icon_height=32, padding=8)
    test_line.label.set_font_name('22')
    test_line.set_position(0, 0)
    stage.add(test_line)
    
    #test_select = Select(open_icon_path='/data/www/sdiemer/top.png')
    test_select = Select()
    test_select.set_position(0, 80)
    test_select.add_option('test1', 'displayed')
    test_select.add_option('test2', 'displayed regregreg')
    test_select.add_option('test3', 'displayed fezfzefezfzef')
    #test_select.set_size(400, 64)
    stage.add(test_select)
    
    """def on_click(btn, event):
        print 'click -----------'
        test_select.open_options()
    print 'selected : ', test_select.selected
    test_select.selected.set_reactive(True)
    test_select.selected.connect('button-press-event', on_click)"""
    
    stage.show()
    clutter.main()



