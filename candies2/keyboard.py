#!/ur/bin/env python
# -*- coding: utf-8 -*-

''' 
Keyboard class
author : flavie
date : nov 30 2009
version : 0
'''

import gobject
import clutter
from buttons import ClassicButton


# class Key : name , width , event default event = char width = 1
class Key:
    def __init__(self,k,nb=1,evt='car'):
        self.txt = k
        self.width = nb
        self.event = evt

# keyboard dictionnary

KEYBOARD_MAPS = {
    'fr_maj': (
        (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,evt='suppr')),
        (Key('A'), Key('Z'), Key('E'), Key('R'), Key('T'), Key('Y'), Key('U'), Key('I'), Key('O'), Key('P'), Key('\'')),
        (Key('Q'), Key('S'), Key('D'), Key('F'), Key('G'), Key('H'), Key('J'), Key('K'), Key('L'), Key('M')),
        (Key('⇧',nb=2,evt='fr_min'), Key('W'), Key('X'), Key('C'), Key('V'), Key('B'), Key('N'), Key(','), Key('.'), Key('⇧',nb=3,evt='fr_min')), 
        (Key('#+-,',nb=2,evt='caract_fr'), Key(' ',nb=8))
    ),
    
    'en_maj': (
        (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,evt='suppr')),
        (Key('Q'), Key('W'), Key('E'), Key('R'), Key('T'), Key('Y'), Key('U'), Key('I'), Key('O'), Key('P'), Key('\'')),
        (Key('A'), Key('S'), Key('D'), Key('F'), Key('G'), Key('H'), Key('J'), Key('K'), Key('L'), Key(',')), 
        (Key('⇧',nb=2,evt='en_min'), Key('Z'), Key('X'), Key('C'), Key('V'), Key('B'), Key('N'), Key('M'), Key('.'), Key('⇧',nb=3,evt='fr_min')),
        (Key('#+-,',nb=2,evt='caract_en'), Key(' ',nb=8))
    ),
    
    'fr_min': (
         (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,evt='suppr')),
         (Key('a'), Key('z'), Key('e'), Key('r'), Key('t'), Key('y'), Key('u'), Key('i'), Key('o'), Key('p'), Key('\'')),
         (Key('q'), Key('s'), Key('d'), Key('f'), Key('g'), Key('h'), Key('j'), Key('k'), Key('l'), Key('m')),
         (Key('⇧',nb=2,evt='fr_maj'), Key('w'), Key('x'), Key('c'), Key('v'), Key('b'), Key('n'), Key(','), Key('.'), Key('⇧',nb=3,evt='fr_min')),
         (Key('#+-,',nb=2,evt='caract_fr'), Key(' ',nb=8))
     ),
    
    'en_min': (
        (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,evt='suppr')),
        (Key('q'), Key('w'), Key('e'), Key('r'), Key('t'), Key('y'), Key('u'), Key('i'), Key('o'), Key('p'), Key('\'')),
        (Key('a'), Key('s'), Key('d'), Key('f'), Key('g'), Key('h'), Key('j'), Key('k'), Key('l'), Key(',')), 
        (Key('⇧',nb=2,evt='en_maj'), Key('z'), Key('x'), Key('c'), Key('v'), Key('b'), Key('n'), Key('m'), Key('.'), Key('⇧',nb=3,evt='fr_min')),
        (Key('#+-,',nb=2,evt='caract_en'), Key(' ',nb=8))
    ),
    
    'caract_fr': (
        (Key('\''), Key('.'), Key(','), Key(';'), Key(':'), Key('/'), Key('?'), Key('!'), Key('%'),),
        (Key('*'), Key('+'), Key('-'), Key('='), Key('#'), Key('~'), Key('@'), Key('\\'), Key('_')),
        (Key('`'), Key('|'), Key('('), Key(')'), Key('"'), Key('&'), Key('['), Key(']')),
        (Key('ABC',nb=2,evt='en_maj'), Key('<'), Key('$'), Key('>'), Key('←',nb=2,evt='suppr')),
        (Key('abc',nb=2,evt='fr_min'), Key(' ',nb=8))
    ),
    
    'caract_en': (
        (Key('\''), Key('.'), Key(','), Key(';'), Key(':'), Key('/'), Key('?'), Key('!'), Key('%'), ),
        (Key('*'), Key('+'), Key('-'), Key('='), Key('#'), Key('~'), Key('@'), Key('\\'), Key('_')),
        (Key('`'), Key('|'), Key('('), Key(')'), Key('"'), Key('&'), Key('['), Key(']')),
        (Key('ABC',nb=2,evt='en_maj'), Key('<'), Key('$'), Key('>'), Key('←',nb=2,evt='suppr')),
        (Key('abc',nb=2,evt='en_min'), Key(' ',nb=8))
    ),
            
    'int': (
        (Key('1'), Key('2'), Key('3')), 
        (Key('4'), Key('5'), Key('6')), 
        (Key('7'), Key('8'), Key('9')),
        (Key('0'), Key('←',evt='suppr'))
    ), 

    'float': (
        (Key('1'), Key('2'), Key('3')), 
        (Key('4'), Key('5'), Key('6')), 
        (Key('7'), Key('8'), Key('9')),
        (Key('.'), Key('0'), Key('←',evt='suppr'))
    ),

    'ip': (
        (Key('1'), Key('2'), Key('3')), 
        (Key('4'), Key('5'), Key('6')), 
        (Key('7'), Key('8'), Key('9')),
        (Key('.'), Key('0'), Key('←',evt='suppr'))
    ) 
}

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
    def __init__(self, map_name, font_name=None) : 
        clutter.Actor.__init__(self)
        
        self.default_btn_size = 64
        self.font_color = '#000000ff'
        self.inner_color = '#ffffff44'
        self.border_color = '#ffffff44'
        self.highlight_color = '#ffffff88'
        self.button_texture = None
        
        self.keyboard = None
        self.map_name = None
        self.key_font_name = font_name
        self.load_profile(map_name)
    
    #keyboard load profile ; load dictionnary, create buttons and calcul max line width 
    def load_profile(self, map_name):
        if self.keyboard is not None:
            self.clear_keyboard()
        self.map_name = map_name
        self.keyboard = KEYBOARD_MAPS[map_name]
        self.button_map = dict()
        
        self.width_line = list()
    
        for line in self.keyboard:
            one_line_width = 0
            for key in line:
                button = ClassicButton(key.txt, texture=self.button_texture)
                if self.key_font_name is not None:
                    button.label.set_font_name(self.key_font_name)
                button.set_font_color(self.font_color)
                button.set_inner_color(self.inner_color)
                button.set_border_color(self.border_color)
                button.set_parent(self)
                button.connect('button-press-event', self.on_button_press)
                self.button_map[key] = button
                one_line_width=one_line_width+key.width
            self.width_line.append(one_line_width)
    
        self.nb_col = max(self.width_line)
    
    # clear keyboard : delete buttons
    def clear_keyboard(self):
        for button in self.button_map.values():
            button.unparent()
            button.destroy()
        self.keyboard = None
        self.map_name = None
    
    # on button press emit message
    def on_button_press(self, source, event):
        source.set_inner_color(self.highlight_color)
        for key , button in self.button_map.items():
            if button == source :
                if key.event == 'fr_min':
                    self.load_profile("fr_min")
                elif key.event == 'fr_maj':
                    self.load_profile("fr_maj")
                elif key.event == 'en_min':
                    self.load_profile("en_min")
                elif key.event == 'en_maj':
                    self.load_profile("en_maj")
                elif key.event == 'caract_en':
                    self.load_profile("caract_en")
                elif key.event == 'caract_fr':
                    self.load_profile("caract_fr")
                elif key.event == 'num':
                    self.load_profile("int")
                elif key.event == 'car':
                    self.emit("keyboard", key.txt)
                elif key.event == 'enter':
                    self.emit("keyboard", 'enter')
                elif key.event == 'suppr':
                    self.emit("keyboard", 'suppr')
                #elif key.event == 'del':
                    #self.emit("keyboard",'del')
        gobject.timeout_add(200, source.set_inner_color, self.inner_color)
    
    def do_get_preferred_width(self, for_height):
        if for_height == -1:
            row_count = len(self.keyboard)
            col_count = self.nb_col
            margin = int(self.default_btn_size / 8.0)
            preferred_width = col_count * self.default_btn_size + margin
        else:
            row_count = len(self.keyboard)
            col_count = self.nb_col
            btn_size = float(for_height / row_count)
            margin = int(btn_size / 8.0)
            preferred_width = col_count * btn_size + margin
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        if for_width == -1:
            row_count = len(self.keyboard)
            col_count = self.nb_col
            margin = int(self.default_btn_size / 8.0)
            preferred_height = row_count * self.default_btn_size + margin
        else:
            row_count = len(self.keyboard)
            col_count = self.nb_col
            btn_size = float(for_width / col_count)
            margin = int(btn_size / 8.0)
            preferred_height = row_count * btn_size + margin
        return preferred_height, preferred_height
    
    # button mapping : calcul each buttons width and place them
    def do_allocate(self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
        
        nb_line = len(self.keyboard)
        taillemax = min(float(box_width / self.nb_col), float(box_height / nb_line))
        marge = int(taillemax / 8.0)
        origy = round((box_height - nb_line*taillemax + marge) / 2.0)
        
        for line_id, line in enumerate(self.keyboard):
            origx = round((box_width - self.width_line[line_id]*taillemax + marge) / 2.0)
            for key in line:
                button = self.button_map[key]
                btnbox = clutter.ActorBox()
                btnbox.x1 = origx
                btnbox.y1 = origy + taillemax*line_id
                btnbox.x2 = btnbox.x1 + taillemax*key.width-marge
                btnbox.y2 = btnbox.y1 + taillemax-marge
                origx += taillemax*key.width
                button.allocate(btnbox, flags)

        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for child in self.button_map.values():
            func(child, data)
        
    def do_paint(self):
        for actor in self.button_map.values():
            actor.paint()
    
    def do_pick(self, color):
        for actor in self.button_map.values():
            actor.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'button_map'):
            for button in self.button_map.values():
                button.unparent()
                button.destroy()
            self.button_map = dict()


'''
main to test keyboard functionalities
contain a text , keyboard, and other entries
'''
if __name__ == '__main__':
    from flowbox import FlowBox

#create window
    stage = clutter.Stage()
    stage.connect('destroy',clutter.main_quit)
    
#create text wich will show keyboard entries results
    text = clutter.Text()
    stage.set_key_focus(text)
    text.set_size(640,40)
    text.set_editable(True)
    text.set_cursor_visible(True)
    stage.add(text)
    
#create keyboard in fr
    keyboard = Keyboard('fr_maj')
    keyboard.set_size(640,360)
    keyboard.set_position(0,40)
    stage.add(keyboard)
    
#create other entries
    box = FlowBox()
    box.set_size(600,50)
    box.set_position(20,410)
    lan = ClassicButton("language",stretch=True)
    lan.set_size(150,50)
    lan.set_reactive(True)
    box.add(lan)
    
    left = ClassicButton('←',stretch=True)
    left.set_size(75,50)
    left.set_reactive(True)
    box.add(left)
    
    right = ClassicButton("→",stretch=True)
    right.set_size(75,50)
    right.set_reactive(True)
    box.add(right)
    
    num = ClassicButton("num",stretch=True)
    num.set_size(150,50)
    num.set_reactive(True)
    box.add(num)
    stage.add(box)
    
    stage.show()
   
#function lang_callback : action when language is changed 
    def lang_callback(button,event,keyboard) :
            if keyboard.map_name =='fr_maj':    
                keyboard.load_profile('en_maj')
            elif keyboard.map_name =='fr_min':
                keyboard.load_profile('en_min')
            elif keyboard.map_name =='en_maj':
                keyboard.load_profile('fr_maj')
            elif keyboard.map_name =='en_min':
                keyboard.load_profile('fr_min')
            elif keyboard.map_name =='caract_fr':
                keyboard.load_profile('caract_en')
            elif keyboard.map_name =='caract_en':
                keyboard.load_profile('caract_fr')

#function keyboard_callback : action keyboard is used
    def keyboard_callback(keyboard, key):
        #suppr button
        if key == 'suppr':
            text.delete_chars(1)
            text.set_selection(text.get_cursor_position(), text.get_cursor_position())
        #del button
        elif key == 'del':
            text.set_selection(text.get_cursor_position()+1, text.get_cursor_position()+1)
            text.delete_chars(1)
            text.set_selection(text.get_cursor_position(), text.get_cursor_position())
        # others entries
        else :
            older_entries=text.get_text()
            #maj or min mapping : when '. ' maj keyboard is mapped
            if len(older_entries)>=1 :
                last_char=older_entries[-1]
                if last_char == '.' and key == ' ':
                    if keyboard.map_name =='fr_min':
                        keyboard.load_profile('fr_maj')
                    elif keyboard.map_name =='en_min':
                        keyboard.load_profile('en_maj')
            # maj or min mapping : when '. ' is followed by maj mapping next char will be min
            if len(older_entries)>= 2 :
                last_2_char=older_entries[-2]+older_entries[-1]
                if last_2_char=='. ' :
                    if keyboard.map_name =='fr_maj':
                        keyboard.load_profile('fr_min')
                    elif keyboard.map_name =='en_maj':
                        keyboard.load_profile('en_min')
            # insert text
            text.insert_text(key, text.get_cursor_position())
        # maj or min mapping : when first char is maj the next is min
        text_length = len(text.get_text())
        if text_length == 1 : 
            if keyboard.map_name =='fr_maj':
                keyboard.load_profile('fr_min')
            elif keyboard.map_name =='en_maj':
                keyboard.load_profile('en_min')
        # first char is a maj
        if text_length == 0 : 
            if keyboard.map_name =='fr_min':
                keyboard.load_profile('fr_maj')
            elif keyboard.map_name =='en_min':
                keyboard.load_profile('en_maj')
                
    # function num_callback used when numeric keyboard is called
    def num_callback(button,event,keyboard):
        if  keyboard.map_name =='numeric':
            keyboard.load_profile('fr_maj')
        else :
            keyboard.load_profile('numeric')
            
    # function left_callback when left button is used
    def left_callback(button,event,text):
        cursor_pos=text.get_cursor_position()
        if cursor_pos == -1:
          cursor_pos = len(text.get_text())
        cursor_res = cursor_pos - 1
        text.set_selection(cursor_res, cursor_res)
      
    # function right_callback when right button is used
    def right_callback(button,event,text):
        cursor_pos=text.get_cursor_position()
        cursor_res =cursor_pos+1
        text.set_selection(cursor_res, cursor_res)
    
    #connect signals
    left.connect('button-press-event',left_callback,text)
    right.connect('button-press-event',right_callback,text)
    num.connect('button-press-event',num_callback,keyboard)   
    lan.connect('button-press-event',lang_callback,keyboard)
    #keyboard.connect("keyboard", keyboard_callback)
        
    clutter.main()
