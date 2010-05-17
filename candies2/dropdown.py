import clutter
from roundrect import RoundRectangle

class OptionLine(clutter.Actor, clutter.Container):
    """
    A option line for select input.
    """
    __gtype_name__ = 'OptionLine'
    
    
    def __init__(self, name, hname, icon_height=32, icon_path=None, border=8, enable_background=True, font='14', font_color='Black', color='LightGray', border_color='Gray', light_texture=None, dark_texture=None):
        clutter.Actor.__init__(self)
        self.name = name
        self.hname = hname
        self.border = border
        
        self.font = font
        self.font_color = font_color
        self.default_color = color
        self.default_border_color = border_color
        
        # background
        self.background = RoundRectangle(light_texture=light_texture, dark_texture=dark_texture)
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
        self.label = clutter.Text()
        self.label.set_text(hname)
        self.label.set_color(self.font_color)
        self.label.set_font_name(self.font)
        self.label.set_parent(self)
    
    def set_hname(self, new_hname):
        self.label.set_text(new_hname)
        self.queue_relayout()
    
    def set_icon(self, new_icon_path=None):
        self.icon_path = new_icon_path
        if new_icon_path:
            self.icon.set_from_file(new_icon_path)
            self.icon.show()
        else:
            self.icon.hide()
    
    def show_background(self):
        if self.enable_background != True:
            self.enable_background = True
            self.background.show()
    
    def hide_background(self):
        if self.enable_background != False:
            self.enable_background = False
            self.background.hide()
    
    def do_remove(self, actor):
        if self.background == actor:
            actor.unparent()
            self.background = None
        if self.icon == actor:
            actor.unparent()
            self.icon = None
        if self.label == actor:
            actor.unparent()
            self.label = None
    
    def do_get_preferred_width(self, for_height):
        preferred_width = self.icon_height + 4*self.border + self.label.get_preferred_size()[2]
        return preferred_width, preferred_width
    
    def do_get_preferred_height(self, for_width):
        preferred_height = self.icon_height + 2*self.border
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        inner_height = main_height - 2*self.border
        
        # background
        background_box = clutter.ActorBox()
        background_box.x1 = 0
        background_box.y1 = 0
        background_box.x2 = main_width
        background_box.y2 = main_height
        self.background.allocate(background_box, flags)
        
        # icon
        icon_box = clutter.ActorBox()
        icon_box.x1 = self.border
        icon_box.y1 = self.border
        icon_box.x2 = self.border + inner_height
        icon_box.y2 = self.border + inner_height
        self.icon.allocate(icon_box, flags)
        
        # label
        label_width = self.label.get_preferred_size()[2]
        label_height = self.label.get_preferred_size()[3]
        label_h_padding = round((main_width - main_height - 2*self.border - label_width) / 2)
        label_v_padding = round((inner_height - label_height) / 2)
        label_box = clutter.ActorBox()
        label_box.x1 = main_height + self.border + label_h_padding
        label_box.y1 = self.border + label_v_padding
        label_box.x2 = main_width - self.border - label_h_padding
        label_box.y2 = main_height - self.border - label_v_padding
        self.label.allocate(label_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        childrens = [self.background, self.icon, self.label]
        for children in childrens:
            func(children, data)
    
    def do_destroy(self):
        try:
            self.background.destroy()
            self.icon.destroy()
            self.label.destroy()
        except:
            pass
    
    def do_paint(self):
        self.background.paint()
        self.icon.paint()
        self.label.paint()
    

class Select(clutter.Actor, clutter.Container):
    """
    A select input.
    """
    __gtype_name__ = 'Select'
    
    def __init__(self, border=8, on_change_callback=None, icon_height=48, open_icon_path=None, font='14', font_color='Black', color='LightGray', border_color='Gray', option_color='LightBlue', light_texture=None, dark_texture=None):
        clutter.Actor.__init__(self)
        self.border = border
        self.on_change_callback = on_change_callback
        self.icon_height = icon_height
        self.options = list()
        self.opened = False
        self.selected = None
        self.selected_icon = None
        self.open_icon = open_icon_path
        
        self.font = font
        self.font_color = font_color
        self.default_color = color
        self.default_border_color = border_color
        self.option_color = option_color
        self.light_texture = light_texture
        self.dark_texture = dark_texture
        
        self.background = RoundRectangle()
        self.background.set_color(self.default_color)
        self.background.set_border_color(self.default_border_color)
        self.background.set_border_width(3)
        self.background.props.radius = 10
        self.background.set_parent(self)
        
    
    def add_option(self, name, hname, icon_path=None):
        new_option = OptionLine(name, hname, border=self.border, icon_path=icon_path, icon_height=self.icon_height, enable_background=False, font=self.font, font_color=self.font_color, color=self.option_color, border_color='#00000000', light_texture=self.light_texture, dark_texture=self.dark_texture)
        new_option.set_parent(self)
        new_option.set_reactive(True)
        new_option.connect('button-press-event', self._on_click)
        self.options.append(new_option)
        if self.selected == None:
            self.selected = new_option
            self.selected.show_background()
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
            self.selected = source
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
                self.selected = option
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
        inner_width = main_width - 2*self.border
        inner_height = main_height - 2*self.border
        
        if self.opened:
            total_height = (self.icon_height + 2*self.border) * len(self.options)
            
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
                option_box.y1 = index*(self.icon_height + 2*self.border)
                option_box.x2 = main_width
                option_box.y2 = (index + 1)*(self.icon_height + 2*self.border)
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
    
    def do_destroy(self):
        self.background.destroy()
        for option in list(self.options):
            option.destroy()
        self.options = list()
    
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


if __name__ == '__main__':
    stage_width = 640
    stage_height = 480
    stage = clutter.Stage()
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', clutter.main_quit)
    
    test_line = OptionLine('test', 'displayed fezfzefezfzef', icon_height=32, border=8)
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



