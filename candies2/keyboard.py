#!/ur/bin/env python
# -*- coding: utf-8 -*-

''' 
Keyboard class
author : flavie
date : nov 30 2009
version : 0
'''

import string
import gobject
import clutter
import common
from buttons import ClassicButton


# Key class: name, width, event default event=char width=1
class Key:
    def __init__(self, k, nb=1, evt='car', c_evt=None, no_c_evt=False):
        self.text = k
        self.width = nb
        self.event = evt
        if no_c_evt:
            self.clutter_event = None
        elif not c_evt:
            if k in string.letters:
                self.clutter_event = getattr(clutter.keysyms, k, None)
            elif k in string.digits:
                self.clutter_event = getattr(clutter.keysyms, '_%s' % k, None)
            else:
                self.clutter_event = None
        else:
            self.clutter_event = getattr(clutter.keysyms, c_evt, None)

class NoClKey(Key):
    def __init__(self, *args, **kwargs):
        Key.__init__(self, no_c_evt=True, *args, **kwargs)


# keyboard dictionnary
KEYBOARD_MAPS = {
    'fr_maj': (
        (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,c_evt='BackSpace')),
        (Key('A'), Key('Z'), Key('E'), Key('R'), Key('T'), Key('Y'), Key('U'), Key('I'), Key('O'), Key('P'), Key('\'',c_evt='quoteright')),
        (Key('Q'), Key('S'), Key('D'), Key('F'), Key('G'), Key('H'), Key('J'), Key('K'), Key('L'), Key('M')),
        (NoClKey('⇧',nb=2,evt='fr_min'), Key('W'), Key('X'), Key('C'), Key('V'), Key('B'), Key('N'), Key(',',c_evt='comma'), Key('.',c_evt='period'), NoClKey('⇧',nb=3,evt='fr_min')),
        (NoClKey('#+-',nb=2,evt='fr_caract'), Key(' ',nb=8,c_evt='space'))
    ),
    
    'en_maj': (
        (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,c_evt='BackSpace')),
        (Key('Q'), Key('W'), Key('E'), Key('R'), Key('T'), Key('Y'), Key('U'), Key('I'), Key('O'), Key('P'), Key('\'',c_evt='quoteright')),
        (Key('A'), Key('S'), Key('D'), Key('F'), Key('G'), Key('H'), Key('J'), Key('K'), Key('L'), Key(',',c_evt='comma')), 
        (NoClKey('⇧',nb=2,evt='en_min'), Key('Z'), Key('X'), Key('C'), Key('V'), Key('B'), Key('N'), Key('M'), Key('.',c_evt='period'), NoClKey('⇧',nb=3,evt='en_min')),
        (NoClKey('#+-',nb=2,evt='en_caract'), Key(' ',nb=8,c_evt='space'))
    ),
    
    'fr_min': (
         (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,c_evt='BackSpace')),
         (Key('a'), Key('z'), Key('e'), Key('r'), Key('t'), Key('y'), Key('u'), Key('i'), Key('o'), Key('p'), Key('\'',c_evt='quoteright')),
         (Key('q'), Key('s'), Key('d'), Key('f'), Key('g'), Key('h'), Key('j'), Key('k'), Key('l'), Key('m')),
         (NoClKey('⇧',nb=2,evt='fr_maj'), Key('w'), Key('x'), Key('c'), Key('v'), Key('b'), Key('n'), Key(',',c_evt='comma'), Key('.',c_evt='period'), NoClKey('⇧',nb=3,evt='fr_maj')),
         (Key('#+-',nb=2,evt='fr_caract'), Key(' ',nb=8,c_evt='space'))
     ),
    
    'en_min': (
        (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,c_evt='BackSpace')),
        (Key('q'), Key('w'), Key('e'), Key('r'), Key('t'), Key('y'), Key('u'), Key('i'), Key('o'), Key('p'), Key('\'',c_evt='quoteright')),
        (Key('a'), Key('s'), Key('d'), Key('f'), Key('g'), Key('h'), Key('j'), Key('k'), Key('l'), Key(',',c_evt='comma')), 
        (NoClKey('⇧',nb=2,evt='en_maj'), Key('z'), Key('x'), Key('c'), Key('v'), Key('b'), Key('n'), Key('m'), Key('.',c_evt='period'), NoClKey('⇧',nb=3,evt='en_maj')),
        (NoClKey('#+-',nb=2,evt='en_caract'), Key(' ',nb=8,c_evt='space'))
    ),
    
    'fr_caract': (
        (Key('\'',c_evt='quoteright'), Key('.',c_evt='period'), Key(',',c_evt='comma'), Key(';',c_evt='semicolon'), Key(':',c_evt='colon'), Key('/',c_evt='slash'), Key('?',c_evt='question'), Key('!',c_evt='exclam'), Key('%',c_evt='percent'),),
        (Key('*',c_evt='asterisk'), Key('+',c_evt='plus'), Key('-',c_evt='minus'), Key('=',c_evt='equal'), Key('#',c_evt='numbersign'), Key('~',c_evt='asciitilde'), Key('@',c_evt='at'), Key('\\',c_evt='backslash'), Key('_',c_evt='underscore')),
        (Key('`',c_evt='quoteleft'), Key('|',c_evt='bar'), Key('(',c_evt='parenleft'), Key(')',c_evt='parenright'), Key('"',c_evt='quotedbl'), Key('&',c_evt='ampersand'), Key('[',c_evt='bracketleft'), Key(']',c_evt='bracketright')),
        (NoClKey('ABC',nb=2,evt='fr_maj'), Key('<',c_evt='less'), Key('$',c_evt='dollar'), Key('>',c_evt='greater'), Key('←',nb=2,c_evt='BackSpace')),
        (NoClKey('abc',nb=2,evt='fr_min'), Key(' ',nb=8,c_evt='space'))
    ),
    
    'en_caract': (
        (Key('\'',c_evt='quoteright'), Key('.',c_evt='period'), Key(',',c_evt='comma'), Key(';',c_evt='semicolon'), Key(':',c_evt='colon'), Key('/',c_evt='slash'), Key('?',c_evt='question'), Key('!',c_evt='exclam'), Key('%',c_evt='percent'), ),
        (Key('*',c_evt='asterisk'), Key('+',c_evt='plus'), Key('-',c_evt='minus'), Key('=',c_evt='equal'), Key('#',c_evt='numbersign'), Key('~',c_evt='asciitilde'), Key('@',c_evt='at'), Key('\\',c_evt='backslash'), Key('_',c_evt='underscore')),
        (Key('`',c_evt='quoteleft'), Key('|',c_evt='bar'), Key('(',c_evt='parenleft'), Key(')',c_evt='parenright'), Key('"',c_evt='quotedbl'), Key('&',c_evt='ampersand'), Key('[',c_evt='bracketleft'), Key(']',c_evt='bracketright')),
        (NoClKey('ABC',nb=2,evt='en_maj'), Key('<',c_evt='less'), Key('$',c_evt='dollar'), Key('>',c_evt='greater'), Key('←',nb=2,c_evt='BackSpace')),
        (NoClKey('abc',nb=2,evt='en_min'), Key(' ',nb=8,c_evt='space'))
    ),
            
    'int': (
        (Key('1'), Key('2'), Key('3')), 
        (Key('4'), Key('5'), Key('6')), 
        (Key('7'), Key('8'), Key('9')),
        (Key('0',nb=2), Key('←',c_evt='BackSpace'))
    ), 

    'float': (
        (Key('1'), Key('2'), Key('3')), 
        (Key('4'), Key('5'), Key('6')), 
        (Key('7'), Key('8'), Key('9')),
        (Key('.',c_evt='period'), Key('0'), Key('←',c_evt='BackSpace'))
    ),

    'ip': (
        (Key('1'), Key('2'), Key('3')), 
        (Key('4'), Key('5'), Key('6')), 
        (Key('7'), Key('8'), Key('9')),
        (Key('.',c_evt='period'), Key('0'), Key('←',c_evt='BackSpace'))
    ),
    
    'hexa': (
        (Key('1'), Key('2'), Key('3'), Key('A'), Key('B')), 
        (Key('4'), Key('5'), Key('6'), Key('C'), Key('D')), 
        (Key('7'), Key('8'), Key('9'), Key('E'), Key('F')),
        (Key('-',c_evt='minus'), None,     Key('0'), None,     Key('←',c_evt='BackSpace'))
    )
}


class ButtonLine():
    def __init__(self):
        self.buttons = list()
        self.width = 0
        self.padding_x = 0
        self.padding_y = 0
    
    def add(self, button, width):
        self.buttons.append(button)
        self.width += width

'''
Keyboard Class
    .map_name = name of dictionnary used
    .button_map = dictionnary used
    .width_line = width of each line 
    
    .load_profile = change keyboard dictionnary
    .clear_keyboard = delete keyboard map
    .on_button_press = function wich describe action on button press
    .do_allocate = place each buttons in the container
'''
class Keyboard(clutter.Actor, clutter.Container):
    __gtype_name__ = 'Keyboard'
    __gsignals__ = {'keyboard' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_STRING])}
    
    #keyboard init
    def __init__(self, map_name='', spacing=15):
        clutter.Actor.__init__(self)
        self._spacing = common.Spacing(spacing)
        
        self.default_btn_size = 64
        self.font_name = 'Sans 18'
        self.font_color = '#000000ff'
        self.inner_color = '#ffffff44'
        self.border_color = '#ffffff44'
        self.highlight_color = '#ffffff88'
        self.button_texture = None
        
        self._text_actor = None
        
        self._width = 0
        self._height = 0
        self._button_size = 0
        self._padding_y = 0
        self._colums_count = 0
        
        self._lines = list()
        self._map_name = ''
        self._keyboard_map = None
        if map_name:
            self.load_profile(map_name)
    
    def get_map_name(self):
        return self._map_name
    
    #keyboard load profile ; load dictionnary, create buttons and calcul max line width 
    def load_profile(self, map_name):
        print 'Load profile:', map_name
        if map_name == self._map_name:
            return
        if self._keyboard_map:
            self.clear_keyboard()
        self._map_name = map_name
        self._keyboard_map = KEYBOARD_MAPS[map_name]
        
        self._lines = list()
        lines_width = list()
        for keys_line in self._keyboard_map:
            line = ButtonLine()
            for key in keys_line:
                if key is None:
                    # create spacer
                    spacer = ClassicButton('')
                    spacer.set_parent(self)
                    spacer.kb_width = 1
                    spacer.hide()
                    line.add(spacer, 1)
                    continue
                # create button
                button = ClassicButton(key.text, texture=self.button_texture)
                if self.font_name:
                    button.label.set_font_name(self.font_name)
                button.set_font_color(self.font_color)
                button.set_inner_color(self.inner_color)
                button.set_border_color(self.border_color)
                button.set_parent(self)
                button.connect('button-press-event', self._on_button_press)
                # save key param in button object
                button.kb_text = key.text
                button.kb_width = key.width
                button.kb_evt = key.event
                button.kb_c_evt = key.clutter_event
                # add button to line
                line.add(button, key.width)
            self._lines.append(line)
            lines_width.append(line.width)
        self._colums_count = max(lines_width)
        
        if self._width > 0 and self._height > 0:
            self._refresh_allocation_params()
    
    def to_min(self):
        if self._map_name.endswith('_maj'):
            self.load_profile('%s_min' % (self._map_name[:-4]))

    def to_maj(self):
        if self._map_name.endswith('_min'):
            self.load_profile('%s_maj' % (self._map_name[:-4]))
    
    # clear keyboard : delete buttons
    def clear_keyboard(self):
        for line in self._lines:
            for button in line.buttons:
                button.unparent()
                button.destroy()
        self._lines = list()
        self._map_name = None
        self._keyboard_map = None
    
    def connect_clutter_text(self, text_actor):
        self._text_actor = text_actor
    
    def _emit_key_press(self, keyval):
        if self._text_actor:
            event = clutter.Event(clutter.KEY_PRESS)
            event.keyval = keyval
            self._text_actor.emit('key-press-event', event)
        self.emit('keyboard', keyval)
    
    # on button press emit message
    def _on_button_press(self, source, event):
        # flash button
        source.set_inner_color(self.highlight_color)
        gobject.timeout_add(200, source.set_inner_color, self.inner_color)
        # execute button action
        if source.kb_evt == 'car':
            if source.kb_c_evt:
                self._emit_key_press(source.kb_c_evt)
        elif source.kb_evt == 'fr_min':
            self.load_profile('fr_min')
        elif source.kb_evt == 'fr_maj':
            self.load_profile('fr_maj')
        elif source.kb_evt == 'en_min':
            self.load_profile('en_min')
        elif source.kb_evt == 'en_maj':
            self.load_profile('en_maj')
        elif source.kb_evt == 'en_caract':
            self.load_profile('en_caract')
        elif source.kb_evt == 'fr_caract':
            self.load_profile('fr_caract')
        elif source.kb_evt == 'num':
            self.load_profile('int')
        #elif source.kb_evt == 'del':
            #self.emit('keyboard','del')
    
    def do_get_preferred_width(self, for_height):
        #TODO
        preferred_width = 0
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        #TODO
        preferred_height = 0
        return preferred_height, preferred_height
    
    def _refresh_allocation_params(self):
        if self._colums_count > 0:
            button_width = int(float(self._width - self._colums_count * self._spacing.x + self._spacing.x) / self._colums_count)
            button_height = int(float(self._height - len(self._lines) * self._spacing.y + self._spacing.y) / len(self._lines))
            self._button_size = min(button_width, button_height)
            
            self._padding_y = int(float(self._height - len(self._lines) * (self._button_size + self._spacing.y) + self._spacing.y) / 2.0)
            
            for line in self._lines:
                line.padding_x = int(float(self._width - line.width * (self._button_size + self._spacing.x) + self._spacing.x) / 2.0)
                line.padding_y = self._padding_y + self._lines.index(line) * (self._button_size + self._spacing.y)
    
    # button mapping : calcul each buttons width and place them
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        
        if width != self._width or height != self._height:
            self._width = width
            self._height = height
            self._refresh_allocation_params()
        
        for line in self._lines:
            x = line.padding_x
            y = line.padding_y
            for button in line.buttons:
                btn_box = clutter.ActorBox()
                btn_box.x1 = x
                btn_box.y1 = y
                if button.kb_width < 1:
                    btn_box.x2 = x + self._button_size
                else:
                    btn_box.x2 = x + button.kb_width * (self._button_size + self._spacing.x) - self._spacing.x
                btn_box.y2 = y + self._button_size
                button.allocate(btn_box, flags)
                x = btn_box.x2 + self._spacing.x
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for line in self._lines:
            for button in line.buttons:
                func(button, data)
    
    def do_paint(self):
        for line in self._lines:
            for button in line.buttons:
                button.paint()
    
    def do_pick(self, color):
        self.do_paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'lines'):
            for line in self._lines:
                for button in line.buttons:
                    button.unparent()
                    button.destroy()
            self._lines = list()


'''
main to test keyboard functionalities
contain a text , keyboard, and other entries
'''
if __name__ == '__main__':
    from flowbox import FlowBox

    #create window
    stage = clutter.Stage()
    stage.set_size(1000, 600)
    stage.connect('destroy', clutter.main_quit)
    stage.set_color('#000000ff')
    
    #create text wich will show keyboard entries results
    text = clutter.Text()
    stage.set_key_focus(text)
    text.set_color('#ffffffff')
    text.set_selection_color('#8888ffff')
    text.set_font_name('22')
    text.set_size(900, 40)
    text.set_position(50, 5)
    text.set_cursor_visible(True)
    text.set_editable(True)
    text.set_selectable(True)
    text.set_reactive(True)
    text.grab_key_focus()
    stage.add(text)
    
    kb_bg = clutter.Rectangle()
    kb_bg.set_color('#ffffff22')
    kb_bg.set_size(1000, 500)
    kb_bg.set_position(0, 50)
    stage.add(kb_bg)
    
    #create keyboard in fr
    keyboard = Keyboard('fr_maj', spacing=10)
    keyboard.set_size(1000, 500)
    keyboard.set_position(0, 50)
    stage.add(keyboard)
    
    #create other entries
    box = FlowBox()
    box.set_size(900, 50)
    box.set_position(50, 550)
    lan = ClassicButton('language')
    lan.set_size(150, 50)
    box.add(lan)
    
    left = ClassicButton('←')
    left.set_size(75, 50)
    box.add(left)
    
    right = ClassicButton('→')
    right.set_size(75, 50)
    box.add(right)
    
    num = ClassicButton('num')
    num.set_size(150, 50)
    box.add(num)
    stage.add(box)
    
    stage.show()
   
    #function lang_callback : action when language is changed 
    def lang_callback(button, event, keyboard):
        map_name = keyboard.get_map_name()
        if map_name =='fr_maj':
            keyboard.load_profile('en_maj')
        elif map_name =='fr_min':
            keyboard.load_profile('en_min')
        elif map_name =='en_maj':
            keyboard.load_profile('fr_maj')
        elif map_name =='en_min':
            keyboard.load_profile('fr_min')
        elif map_name =='fr_caract':
            keyboard.load_profile('en_caract')
        elif map_name =='en_caract':
            keyboard.load_profile('fr_caract')

    #function keyboard_callback : action keyboard is used
    def on_text_change(actor):
        CAPITAL_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        print 'Text changed:', actor.get_text()
        new_text = actor.get_text()
        if len(new_text) == 0 or new_text.endswith('.'):
            keyboard.to_maj()
        else:
            second_last_char = '_'
            if len(new_text) > 1:
                second_last_char = new_text[-2]
            last_char = new_text[-1]
            if last_char in CAPITAL_LETTERS and second_last_char not in CAPITAL_LETTERS:
                keyboard.to_min()
    
    # function num_callback used when numeric keyboard is called
    def num_callback(button,event,keyboard):
        map_name = keyboard.get_map_name()
        if map_name == 'int':
            keyboard.load_profile('fr_maj')
        else :
            keyboard.load_profile('int')
            
    # function left_callback when left button is used
    def left_callback(button,event,text):
        cursor_pos=text.get_cursor_position()
        if cursor_pos == -1:
          cursor_pos = len(text.get_text())
        cursor_res = cursor_pos - 1
        text.set_selection(cursor_res, cursor_res)
      
    # function right_callback when right button is used
    def right_callback(button,event,text):
        cursor_pos = text.get_cursor_position()
        cursor_res = cursor_pos+1
        text.set_selection(cursor_res, cursor_res)
    
    #connect signals
    left.connect('button-press-event',left_callback,text)
    right.connect('button-press-event',right_callback,text)
    num.connect('button-press-event',num_callback,keyboard)   
    lan.connect('button-press-event',lang_callback,keyboard)
    
    
    def on_key_press_event(source, event):
        print 'Key pressed:', event.keyval
    
    text.connect('key-press-event', on_key_press_event)
    text.connect('text-changed', on_text_change)
    
    keyboard.connect_clutter_text(text)
    
    clutter.main()
