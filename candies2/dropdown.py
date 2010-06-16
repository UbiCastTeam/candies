#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter
from roundrect import RoundRectangle
from text import TextContainer

class OptionLine(clutter.Actor, clutter.Container):
    """
    A option line for select input. Can be used alone to have a text with icon.
    """
    __gtype_name__ = 'OptionLine'
    
    def __init__(self, name, text, icon_height=32, icon_path=None, padding=8, spacing=8, enable_background=True, font='14', font_color='Black', color='LightGray', border_color='Gray', texture=None):
        clutter.Actor.__init__(self)
        self.name = name
        self.padding = padding
        self.spacing = spacing
        
        self.font = font
        self.font_color = font_color
        self.default_color = color
        self.default_border_color = border_color
        
        # background
        self.background = RoundRectangle(texture=texture)
        self.background.set_color(self.default_color)
        self.background.set_border_color(self.default_border_color)
        self.background.set_border_width(3)
        self.background.props.radius = 10
        self.background.set_parent(self)
        if enable_background:
            self.enable_background = True
        else:
            self.enable_background = False
            self.background.hide()
        # icon
        self.icon_height = icon_height
        self.icon_path = icon_path
        self.icon = clutter.Texture()
        if icon_path:
            self.icon.set_from_file(icon_path)
        else:
            self.icon.hide()
        self.icon.set_parent(self)
        # label
        self.label = TextContainer(text, padding=0)
        self.label.set_font_color(self.font_color)
        self.label.set_font_name(self.font)
        self.label.set_inner_color('#00000000')
        self.label.set_border_color('#00000000')
        self.label.set_parent(self)
    
    def set_line_wrap(self, boolean):
        self.label.set_line_wrap(boolean)
            
    def set_line_alignment(self, alignment):
        self.label.set_line_alignment(alignment)
    
    def set_justify(self, boolean):
        self.label.set_justify(boolean)
    
    def set_text(self, text):
        self.label.set_text(text)
        self.queue_relayout()
    
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
    
    def show_background(self):
        if self.enable_background != True:
            self.enable_background = True
            self.background.show()
    
    def hide_background(self):
        if self.enable_background != False:
            self.enable_background = False
            self.background.hide()
    
    def do_get_preferred_width(self, for_height):
        preferred_width = self.icon_height + 2*self.padding + self.spacing + self.label.get_preferred_width(for_height=for_height)[1]
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
        icon_box = clutter.ActorBox()
        icon_box.x1 = self.padding
        icon_box.y1 = self.padding
        icon_box.x2 = main_height - self.padding
        icon_box.y2 = main_height - self.padding
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
        childrens = [self.background, self.icon, self.label]
        for children in childrens:
            func(children, data)
    
    def do_paint(self):
        self.background.paint()
        self.icon.paint()
        self.label.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'background'):
            if self.background is not None:
                self.background.unparent()
                self.background.destroy()
                self.background = None
        if hasattr(self, 'icon'):
            if self.icon is not None:
                self.icon.unparent()
                self.icon.destroy()
                self.icon = None
        if hasattr(self, 'label'):
            if self.label is not None:
                self.label.unparent()
                self.label.destroy()
                self.label = None
    

class Select(clutter.Actor, clutter.Container):
    """
    A select input.
    """
    __gtype_name__ = 'Select'
    
    def __init__(self, padding=8, spacing=8, on_change_callback=None, icon_height=48, open_icon_path=None, font='14', font_color='Black', selected_font_color='Blue', color='LightGray', border_color='Gray', option_color='LightBlue', texture=None):
        clutter.Actor.__init__(self)
        self.padding = padding
        self.spacing = spacing
        self.on_change_callback = on_change_callback
        self.icon_height = icon_height
        self.options = list()
        self.opened = False
        self.selected = None
        self.selected_icon = None
        self.open_icon = open_icon_path
        
        self.font = font
        self.font_color = font_color
        self.selected_font_color = selected_font_color
        self.default_color = color
        self.default_border_color = border_color
        self.option_color = option_color
        self.texture = texture
        
        self.background = RoundRectangle()
        self.background.set_color(self.default_color)
        self.background.set_border_color(self.default_border_color)
        self.background.set_border_width(3)
        self.background.props.radius = 10
        self.background.set_parent(self)
        
    
    def add_option(self, name, hname, icon_path=None):
        new_option = OptionLine(name, hname, padding=self.padding, spacing=self.spacing, icon_path=icon_path, icon_height=self.icon_height, enable_background=False, font=self.font, font_color=self.font_color, color=self.option_color, border_color='#00000000', texture=self.texture)
        new_option.set_parent(self)
        new_option.set_reactive(True)
        new_option.connect('button-press-event', self._on_click)
        self.options.append(new_option)
        if self.selected == None:
            self.selected = new_option
            self.selected.show_background()
            self.selected.set_font_color(self.selected_font_color)
            self.selected_icon = self.selected.icon_path
            self.selected.set_icon(self.open_icon)
        else:
            new_option.hide()
    
    def remove_option(self, name):
        for option in list(self.options):
            if option.name == name:
                self.options.remove(option)
                option.unparent()
    
    def _on_click(self, source, event):
        if source == self.selected:
            if self.opened == True:
                self._close_options()
            else:
                self._open_options()
        elif self.opened == True:
            self.selected.set_font_color(self.font_color)
            self.selected = source
            self.selected.set_font_color(self.selected_font_color)
            self._close_options()
            if self.on_change_callback is not None:
                self.on_change_callback(source, event)
    
    def _open_options(self):
        self.opened = True
        self.selected.set_icon(self.selected_icon)
        self.selected.show_background()
        for option in self.options:
            option.show()
        self.queue_relayout()
    
    def _close_options(self):
        self.opened = False
        for option in self.options:
            if option != self.selected:
                option.hide()
                option.hide_background()
        self.selected.show_background()
        self.selected_icon = self.selected.icon_path
        self.selected.set_icon(self.open_icon)
        self.queue_relayout()
    
    def select_option(self, option_name, silent=True):
        for option in self.options:
            if option.name == option_name and option != self.selected:
                last_selection = self.selected
                self.selected.hide_background()
                self.selected.set_icon(self.selected_icon)
                self.selected.set_font_color(self.font_color)
                self.selected = option
                self.selected.set_font_color(self.selected_font_color)
                self.selected.show_background()
                if self.opened == True:
                    self.selected_icon = self.selected.icon_path
                else:
                    last_selection.hide()
                    self.selected.show()
                    self.selected_icon = self.selected.icon_path
                    self.selected.set_icon(self.open_icon)
                self.queue_relayout()
                if self.on_change_callback is not None and silent == False:
                    self.on_change_callback(self.selected, None)
                break
    
    def do_remove(self, actor):
        if self.background == actor:
            actor.unparent()
            self.background = None
        for option in list(self.options):
            if option == actor:
                self.options.remove(option)
                option.unparent()
    
    def do_get_preferred_width(self, for_height):
        preferred = 0
        for option in self.options:
            if preferred < option.get_preferred_width(for_height)[0]:
                preferred = option.get_preferred_width(for_height)[0]
        return preferred, preferred
    
    def do_get_preferred_height(self, for_width):
        preferred = 0
        for option in self.options:
            if preferred < option.get_preferred_height(for_width)[0]:
                preferred = option.get_preferred_height(for_width)[0]
        return preferred, preferred
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        
        if self.opened:
            total_height = (self.icon_height + 2*self.padding) * len(self.options)
            
            background_box = clutter.ActorBox()
            background_box.x1 = 0
            background_box.y1 = 0
            background_box.x2 = main_width
            background_box.y2 = total_height
            self.background.allocate(background_box, flags)
            index = 0
            for option in self.options:
                option_box = clutter.ActorBox()
                option_box.x1 = 0
                option_box.y1 = index*(self.icon_height + 2*self.padding)
                option_box.x2 = main_width
                option_box.y2 = (index + 1)*(self.icon_height + 2*self.padding)
                option.allocate(option_box, flags)
                index += 1
        else:
            background_box = clutter.ActorBox()
            background_box.x1 = 0
            background_box.y1 = 0
            background_box.x2 = main_width
            background_box.y2 = main_height
            self.background.allocate(background_box, flags)
            for option in self.options:
                option_box = clutter.ActorBox()
                option_box.x1 = 0
                option_box.y1 = 0
                option_box.x2 = main_width
                option_box.y2 = main_height
                option.allocate(option_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        func(self.background, data)
        for option in self.options:
            func(option, data)
    
    def do_paint(self):
        #last painted must be selected option
        self.background.paint()
        for option in self.options:
            if option != self.selected:
                option.paint()
        if self.selected:
            self.selected.paint()
    
    def do_pick(self, color):
        self.do_paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'options'):
            for option in list(self.options):
                option.unparent()
                option.destroy()
            self.options = list()
        if hasattr(self, 'background'):
            if self.background is not None:
                self.background.unparent()
                self.background.destroy()
                self.background = None


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



