# -*- coding: utf-8 -*-
import sys
import os
import re
import gobject
import clutter
from buttons import ClassicButton

class ButtonList(clutter.Actor, clutter.Container):
    __gtype_name__ = 'ButtonList'
    __gproperties__ = {
        'font_name' : ( \
            str, 'font', 'Font name', None, gobject.PARAM_READWRITE \
        ),
    }
    __gsignals__ = {
        'select-event' : ( \
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () \
        ),
    }
    button_class = ClassicButton
    selected_color = 'LightYellow'
    selected_border_color = 'Yellow'
    
    def __init__(self, spacing=0.0, button_height=None, font_name=None, multiselect=False):
        clutter.Actor.__init__(self)
        self._buttons = list()
        self.spacing = spacing
        self.button_height = button_height
        self._font_name = font_name
        self.multiselect = multiselect
        self.selection = list()
        self.props.request_mode = clutter.REQUEST_WIDTH_FOR_HEIGHT
    
    def do_set_property (self, pspec, value):
        if pspec.name == 'font_name':
            self._font_name = value
            for btn in self._buttons:
                btn.label.set_font_name(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def do_get_property (self, pspec):
        if pspec.name == 'font_name':
            return self._font_name
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def add(self, *labels):
        for label in labels:
            button = self.button_class(label)
            if self._font_name is not None:
                button.label.set_font_name(self._font_name)
            button.set_parent(self)
            button.set_reactive(True)
            button.connect('button-press-event', self.on_button_press)
            self._buttons.append(button)
    
    def do_remove(self, *children):
        for child in children:
            if child in self._buttons:
                self._buttons.remove(child)
                child.unparent()
    
    def clear(self):
        for btn in self._buttons:
            btn.destroy()
        self._buttons = list()
        self.selection = list()
    
    def on_button_press(self, button, event):
        if self.multiselect:
            if button in self.selection:
                button.rect.set_color(button.default_color)
                button.rect.set_border_color(button.default_border_color)
                self.selection.remove(button)
            else:
                button.rect.set_color(self.selected_color)
                button.rect.set_border_color(self.selected_border_color)
                self.selection.append(button)
        else:
            for btn in self.selection:
                btn.rect.set_color(btn.default_color)
                btn.rect.set_border_color(btn.default_border_color)
            button.rect.set_color(self.selected_color)
            button.rect.set_border_color(self.selected_border_color)
            self.selection = [button,]
        self.emit('select-event')
        return True
    
    def _compute_preferred_size(self):
        min_w = min_h = nat_w = nat_h = 0.0
        for btn in self._buttons:
            s = btn.get_preferred_size()
            min_w = max(min_w, s[0])
            min_h += s[1]
            nat_w = max(nat_w, s[2])
            nat_h += s[3]
        nb_buttons = len(self._buttons)
        if self.button_height is not None:
            nat_h = self.button_height * nb_buttons 
            min_h = nat_h
        if nb_buttons > 1:
            total_spacing = (nb_buttons - 1) * self.spacing
            min_h += total_spacing
            nat_h += total_spacing
        return min_w, min_h, nat_w, nat_h
    
    def do_get_preferred_width(self, for_height):
        preferred = self._compute_preferred_size()
        return preferred[0], preferred[2]
    
    def do_get_preferred_height(self, for_width):
        preferred = self._compute_preferred_size()
        return preferred[1], preferred[3]
    
    def do_allocate(self, box, flags):
        list_width = box.x2 - box.x1
        list_height = box.y2 - box.y1
        
        y = 0.0
        for button in self._buttons:
            button.set_width(list_width)
            btnbox = clutter.ActorBox()
            btnbox.x1 = 0.0
            btnbox.y1 = y
            btnbox.x2 = list_width
            if self.button_height is None:
                y += button.get_preferred_height(list_width)[1]
            else:
                button.set_height(self.button_height)
                y += self.button_height
            btnbox.y2 = y
            button.allocate(btnbox, flags)
            y += self.spacing
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for btn in self._buttons:
            func(btn, data)
    
    def do_paint(self):
        for btn in self._buttons:
            btn.paint()
    
    def do_pick(self, color):
        for btn in self._buttons:
            btn.paint()

class FileList(ButtonList):
    __gtype_name__ = 'FileList'
    __gproperties__ = {
        'directory' : ( \
            str, 'directory', 'Path to directory', '.', gobject.PARAM_READWRITE \
        ),
    }
    file_pattern = re.compile('.*')
    
    def __init__(self, directory, file_pattern=None):
        ButtonList.__init__(self)
        self._directory = directory
        if file_pattern is not None:
            if isinstance(file_pattern, (str, unicode)):
                file_pattern = re.compile(file_pattern)
            self.file_pattern = file_pattern
        self.populate()

    def do_get_property(self, pspec):
        if pspec.name == 'directory':
            return self._directory
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'directory':
            self._directory = os.path.abspath(os.path.expanduser(value))
            self.refresh()
    
    def populate(self):
        files = os.listdir(self._directory)
        for filename in files:
            if self.file_pattern.match(filename):
                self.add(filename)
    
    def refresh(self):
        self.clear()
        self.populate()

class ContainerList(clutter.Actor, clutter.Container):
    __gtype_name__ = 'ContainerList'
    
    def __init__(self, horizontal=True, spacing=0.0, border=0.0):
        clutter.Actor.__init__(self)
        self.elements = list()
        self.spacing = spacing
        self.border = border
        if horizontal == True:
            self._horizontal = True
        else:
            self._horizontal = False
    
    def get_element(self, name):
        for element in self.elements:
            if element['name'] == name:
                return element
        return None
    
    def do_set_property (self, pspec, value):
        if pspec.name == 'elements':
            self.elements = value
        elif pspec.name == 'spacing':
            self.spacing = value
        elif pspec.name == 'border':
            self.border = value
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def do_get_property (self, pspec):
        if pspec.name == 'elements':
            return self.elements
        elif pspec.name == 'spacing':
            return self.spacing
        elif pspec.name == 'border':
            return self.border
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def add(self, *new_elements):
        resizable_count = 0
        for new_ele in new_elements:
            if 'name' not in new_ele or 'object' not in new_ele:
                raise KeyError('Element must contain name and object')
            self.elements.append(new_ele)
            self.get_element(new_ele['name'])['object'].set_parent(self)
            if 'resizable' in self.get_element(new_ele['name']):
                if self.get_element(new_ele['name'])['resizable']:
                    resizable_count += 1
        if resizable_count > 1:
            print 'WARNING: More than 1 block has been defined to be resizable in a line. Only the first resizable block will be used'
    
    def do_remove(self, *children):
        for child in children:
            if element in self.elements:
                element['object'].remove(child)
                child.unparent()
    
    def clear(self):
        for element in self.elements:
            element['object'].destroy()
        self.elements = list()
    
    def _compute_preferred_size(self):
        min_w = min_h = nat_w = nat_h = 0.0
        for element in self.elements:
            s = element['object'].get_preferred_size()
            if self._horizontal == True:
                min_w += s[0] + self.spacing
                min_h = max(min_h, s[1])
                nat_w += s[2] + self.spacing
                nat_h = max(nat_h, s[3])
            else:
                min_w = max(min_w, s[0])
                min_h += s[1] + self.spacing
                nat_w = max(nat_w, s[2])
                nat_h += s[3] + self.spacing
        # enlever la marge a la fin
        if self._horizontal == True:
            min_w -= self.spacing
            nat_w -= self.spacing
        else:
            min_h -= self.spacing
            nat_h -= self.spacing
        # ajouter le bord
        min_w += 2*self.border
        nat_w += 2*self.border
        min_h += 2*self.border
        nat_h += 2*self.border
        return min_w, min_h, nat_w, nat_h
    
    def do_get_preferred_width(self, for_height):
        preferred = self._compute_preferred_size()
        return preferred[0], preferred[2]
    
    def do_get_preferred_height(self, for_width):
        preferred = self._compute_preferred_size()
        return preferred[1], preferred[3]
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1 - 2*self.border
        main_height = box.y2 - box.y1 - 2*self.border
        
        x = 0.0
        y = 0.0
        resizable_count = 0
        #ajouter le bord
        x += self.border
        y += self.border
        for element in self.elements:
            obj_width = element['object'].get_width()
            obj_height = element['object'].get_height()
            if 'resizable' in element:
                #on ne prend en compte que 1 seul block resizable
                if resizable_count == 0 and element['resizable'] == True:
                    #calcul de la taille du block en fonction des autres
                    resizable_block_width = main_width
                    resizable_block_height = main_height
                    for ele in self.elements:
                        if ele != element:
                            resizable_block_width -= ele['object'].get_width()
                            resizable_block_height -= ele['object'].get_height()
                        resizable_block_width -= self.spacing
                        resizable_block_height -= self.spacing
                    #rajoute la taille d'un espace a la fin car il n'y a pas d'espace en bout de list 
                    resizable_block_width += self.spacing
                    resizable_block_height += self.spacing
                    if self._horizontal == True:
                        obj_width = resizable_block_width
                    else:
                        obj_height = resizable_block_height
            
            objbox = clutter.ActorBox()
            objbox.x1 = x
            objbox.y1 = y
            objbox.x2 = x + obj_width
            objbox.y2 = y + obj_height
            element['object'].allocate(objbox, flags)
            if self._horizontal == True:
                x += obj_width + self.spacing
            else:
                y += obj_height + self.spacing
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for element in self.elements:
            func(element['object'], data)
    
    def do_paint(self):
        for element in self.elements:
            element['object'].paint()
    
    def do_pick(self, color):
        for element in self.elements:
            element['object'].paint()


if __name__ == '__main__':
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)
    
    lst = ButtonList(spacing=16, font_name="Sans 18", button_height=48)#, multiselect=True)
    lst.button_height = 64
    lst.set_position(160, 96)
    lst.set_size(320, 240)
    lst.add('Hello World!')
    lst.add('Happy New Year!', 'Merry Christmas!')
    lst.add('Goodbye cruel world!')

    stage.add(lst)
    stage.show()

    clutter.main()
