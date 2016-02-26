#!/ur/bin/env python
# -*- coding: utf-8 -*-

import clutter
import common
import gobject
import os
import string
from buttons import ClassicButton


# Key class: name, width, event default event=char width=1
class Key(object):
    def __init__(self, k, nb=1, evt='car', c_evt=None, no_c_evt=False):
        object.__init__(self)
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
    'de_maj': (
        (Key('Ö',c_evt='Odiaeresis'), Key('Ä',c_evt='Adiaeresis'), Key('Ü',c_evt='Udiaeresis'), Key(u'^',c_evt='asciicircum'), Key(u'¨',c_evt='diaeresis'), Key(u'~',c_evt='asciitilde')),
        (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,c_evt='BackSpace')),
        (Key('Q'), Key('W'), Key('E'), Key('R'), Key('T'), Key('Z'), Key('U'), Key('I'), Key('O'), Key('P'), Key('\'',c_evt='quoteright')),
        (Key('A'), Key('S'), Key('D'), Key('F'), Key('G'), Key('H'), Key('J'), Key('K'), Key('L'), Key(',',c_evt='comma')),
        (NoClKey('⇧',nb=2,evt='de_min'), Key('Y'), Key('X'), Key('C'), Key('V'), Key('B'), Key('N'), Key('M'), Key('.',c_evt='period'), NoClKey('⇧',nb=3,evt='de_min')),
        (NoClKey('#+-',nb=2,evt='de_caract'), Key(' ',nb=8,c_evt='space'))
    ),

    'fr_maj': (
        (Key('À',c_evt='Agrave'), Key('Ç',c_evt='Ccedilla'), Key('É',c_evt='Eacute'), Key('È',c_evt='Egrave'), Key('Ù',c_evt='Ugrave'), Key(u'^',c_evt='asciicircum'), Key(u'¨',c_evt='diaeresis'), Key(u'~',c_evt='asciitilde'), Key('ß')),
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
    
    'de_min': (
        (Key('ö',c_evt='odiaeresis'), Key('ä',c_evt='adiaeresis'), Key('ü',c_evt='udiaeresis'), Key(u'^',c_evt='asciicircum'), Key(u'¨',c_evt='diaeresis'), Key(u'~',c_evt='asciitilde'), Key('ß')),
        (Key('1'), Key('2'), Key('3'), Key('4'), Key('5'), Key('6'), Key('7'), Key('8'), Key('9'), Key('0'), Key('←',nb=2,c_evt='BackSpace')),
        (Key('q'), Key('w'), Key('e'), Key('r'), Key('t'), Key('z'), Key('u'), Key('i'), Key('o'), Key('p'), Key('\'',c_evt='quoteright')),
        (Key('a'), Key('s'), Key('d'), Key('f'), Key('g'), Key('h'), Key('j'), Key('k'), Key('l'), Key(',',c_evt='comma')),
        (NoClKey('⇧',nb=2,evt='de_maj'), Key('y'), Key('x'), Key('c'), Key('v'), Key('b'), Key('n'), Key('m'), Key('.',c_evt='period'), NoClKey('⇧',nb=3,evt='de_maj')),
        (Key('#+-',nb=2,evt='de_caract'), Key(' ',nb=8,c_evt='space'))
     ),

    'fr_min': (
        (Key('à',c_evt='agrave'), Key('ç',c_evt='ccedilla'), Key('é',c_evt='eacute'), Key('è',c_evt='egrave'), Key('ù',c_evt='ugrave'), Key(u'^',c_evt='asciicircum'), Key(u'¨',c_evt='diaeresis'), Key(u'~',c_evt='asciitilde'), ),
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
    
    'de_caract': (
        (Key('\'',c_evt='quoteright'), Key('.',c_evt='period'), Key(',',c_evt='comma'), Key(';',c_evt='semicolon'), Key(':',c_evt='colon'), Key('/',c_evt='slash'), Key('?',c_evt='question'), Key('!',c_evt='exclam'), Key('%',c_evt='percent'),),
        (Key('*',c_evt='asterisk'), Key('+',c_evt='plus'), Key('-',c_evt='minus'), Key('=',c_evt='equal'), Key('#',c_evt='numbersign'), Key('~',c_evt='asciitilde'), Key('@',c_evt='at'), Key('\\',c_evt='backslash'), Key('_',c_evt='underscore')),
        (Key('`',c_evt='quoteleft'), Key('|',c_evt='bar'), Key('(',c_evt='parenleft'), Key(')',c_evt='parenright'), Key('"',c_evt='quotedbl'), Key('&',c_evt='ampersand'), Key('[',c_evt='bracketleft'), Key(']',c_evt='bracketright')),
        (NoClKey('ABC',nb=2,evt='de_maj'), Key('<',c_evt='less'), Key('$',c_evt='dollar'), Key('>',c_evt='greater'), Key('←',nb=2,c_evt='BackSpace')),
        (NoClKey('abc',nb=2,evt='de_min'), Key(' ',nb=8,c_evt='space'))
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
        (Key('-', c_evt='minus'), Key('←', nb=2, c_evt='BackSpace')),
        (Key('7'), Key('8'), Key('9')),
        (Key('4'), Key('5'), Key('6')),
        (Key('1'), Key('2'), Key('3')),
        (Key('0', nb=2), None)
    ),  

    'float': (
        (Key('-', c_evt='minus'), Key('←', nb=2, c_evt='BackSpace')),
        (Key('7'), Key('8'), Key('9')),
        (Key('4'), Key('5'), Key('6')),
        (Key('1'), Key('2'), Key('3')),
        (Key('0', nb=2), Key('.', c_evt='period'))
    ),

    'ip': (
        (Key('7'), Key('8'), Key('9')),
        (Key('4'), Key('5'), Key('6')),
        (Key('1'), Key('2'), Key('3')),
        (Key('0'), Key('.',c_evt='period'), Key('←', c_evt='BackSpace'))
    ),
    
    'hexa': (
        (Key('1'), Key('2'), Key('3'), Key('A'), Key('B')), 
        (Key('4'), Key('5'), Key('6'), Key('C'), Key('D')), 
        (Key('7'), Key('8'), Key('9'), Key('E'), Key('F')),
        (Key('-', c_evt='minus'), None, Key('0'), None, Key('←', c_evt='BackSpace'))
    )
}

# keys replacements to avoid some weird behaviour with keys pad
KEYBOARD_KEYS_REPLACEMENTS = {
    '_65430': 65460, # KP_Left      ->  KP_4
    '_65432': 65462, # KP_Right     ->  KP_6
    '_65431': 65464, # KP_Up        ->  KP_8
    '_65433': 65458, # KP_Down      ->  KP_2
    '_65436': 65457, # KP_End       ->  KP_1
    '_65437': 65461, # KP_Begin     ->  KP_5
    '_65429': 65463, # KP_Home      ->  KP_7
    '_65435': 65459, # KP_Page_Down ->  KP_3
    '_65434': 65465, # KP_Page_Up   ->  KP_9
    '_65438': 65456, # KP_Insert    ->  KP_0
    '_65439': 65454, # KP_Delete    ->  KP_Decimal
}

DEAD_KEYS = {
    96: "grave", # keyval: 65104
    180: "acute", # 65105
    94: "circumflex", # 65106
    126: "tilde", # 65107
    175: "macron", # 65108
    418: "breve", # 65109
    511: "abovedot", # 651010
    168: "diaeresis", # 65111
    #65112: "abovering", # 65112
    445: "doubleacute", # 65113
    439: "caron", # 65114
    184: "cedilla", # 65115
    434: "ogonek", # 65116
    #65117: "iota", # 65117
    1246: "voiced_sound", # 65118
    1247: "semivoiced_sound", # 65119
    #65120: "belowdot" # 65120
}

CODE_POINTS = dict()
for keysym in dir(clutter.keysyms):
    value = getattr(clutter.keysyms, keysym)
    try:
        CODE_POINTS[clutter.keysym_to_unicode(value)] = keysym
    except (TypeError, ValueError):
        pass


class ButtonLine(object):
    
    def __init__(self):
        object.__init__(self)
        self.buttons = list()
        self.width = 0
        self.padding_x = 0
        self.padding_y = 0
    
    def add(self, button, width):
        self.buttons.append(button)
        self.width += width

class Keyboard(clutter.Actor, clutter.Container):
    '''
    Keyboard Class
        .load_profile = load a keyboard mapping dictionnary
        .clear_keyboard = delete current keyboard mapping dictionnary
    '''
    __gtype_name__ = 'Keyboard'
    __gsignals__ = {'keyboard' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_STRING])}
    
    REPEAT_DELAY_MS = 400
    REPEAT_RATE_MS = 60
    
    def __init__(self, map_name='', spacing=15):
        clutter.Actor.__init__(self)
        self._spacing = common.Spacing(spacing)
        
        self.font_name = 'Sans 18'
        self.font_color = '#000000ff'
        self.inner_color = '#ffffff44'
        self.border_color = '#ffffff44'
        self.highlight_color = '#ffffff88'
        self.button_texture = None
        
        self._text_actor = None
        self._dead_key = None
        self._keyboard_delay_id = None
        self._keyboard_repeat_id = None
        
        self._width = 0
        self._height = 0
        self._button_size = 0
        self._padding_y = 0
        self._columns_count = 0
        
        self._lines = list()
        self._map_name = ''
        self._keyboard_map = None
        if map_name:
            self.load_profile(map_name)
        
        self._clipboards = dict(main="", secondary="")
        self._middle_click = False
        self._next_position = None
        self._next_selection_bound = None
        
        self.connect('key-press-event', self._on_key_press)
        self.connect('key-release-event', self._on_key_release)
    
    def _on_key_press(self, source, event):
        self._key_press_event(event)
    
    def _on_key_release(self, source, event):
        self._key_release_event(event)
    
    def _key_press_event(self, event):
        # for specific keys handling (num lock problem, dead keys, invalid keys mapping, copy/cut/paste)
        #print 'Char:', unichr(clutter.keysym_to_unicode(event.keyval))
        #print "CODE:", event.get_key_code()
        #print "SYMBOL:", event.get_key_symbol()
        #print "UNICODE:", event.get_key_unicode()
        #print "HK:", event.hardware_keycode
        #print "KEYVAL:", event.keyval
        #print "MODIFIER:", event.modifier_state, dir(event.modifier_state)
        #print "UV:", event.unicode_value
        emit_key = False
        # CONTROL_MASK: control, HYPER_MASK: ?, LOCK_MASK: caps lock, META_MASK: ?, MOD1_MASK: alt, MOD2_MASK: num lock, MOD3_MASK: ?, MOD4_MASK: windows, MOD5_MASK: alt gr
        # MODIFIER_MASK: ?, RELEASE_MASK: ?, SHIFT_MASK: shift, SUPER_MASK: ?
        # ASCII / unicode codes
        CTRL_C = 3  # copy
        CTRL_K = 11 # delete end
        CTRL_L = 12 # delete all
        CTRL_U = 21 # delete beginning
        CTRL_V = 22 # paste
        CTRL_W = 23 # delete previous word (bounded by white space character)
        CTRL_X = 24 # cut
        ctrl_keys = (CTRL_C, CTRL_K, CTRL_L, CTRL_U, CTRL_V, CTRL_W, CTRL_X)
        # hardware keycodes
        BACKSPACE = 22
        LEFT_ARROW = 113
        RIGHT_ARROW = 114
        arrow_keys = (LEFT_ARROW, RIGHT_ARROW)
        # Alt Backspace or Escape Backspace: delete previous word (bounded by a non-alphanumeric character))
        ignored_masks = clutter.HYPER_MASK | clutter.META_MASK | clutter.MOD1_MASK | clutter.MOD4_MASK | clutter.MOD5_MASK | clutter.SUPER_MASK
        if not ignored_masks & event.modifier_state and (event.unicode_value in ctrl_keys or (clutter.CONTROL_MASK & event.modifier_state and event.hardware_keycode in arrow_keys)):
            if event.unicode_value == CTRL_C:
                self.copy()
            elif event.unicode_value == CTRL_K:
                self.delete_end()
            elif event.unicode_value == CTRL_L:
                self.delete_all()
            elif event.unicode_value == CTRL_U:
                self.delete_beginning()
            elif event.unicode_value == CTRL_V:
                self.paste()
            elif event.unicode_value == CTRL_X:
                self.cut()
            elif event.unicode_value == CTRL_W:
                self.delete_previous_word(bound="whitespace")
            elif event.hardware_keycode == LEFT_ARROW:
                self.move_cursor_left(type_="word", select=bool(clutter.SHIFT_MASK & event.modifier_state))
            elif event.hardware_keycode == RIGHT_ARROW:
                self.move_cursor_right(type_="word", select=bool(clutter.SHIFT_MASK & event.modifier_state))
        elif clutter.MOD1_MASK & event.modifier_state and event.hardware_keycode == BACKSPACE:
            self.delete_previous_word(bound="alphanumeric")
        elif self._dead_key:
            if event.unicode_value:
                keysym = CODE_POINTS.get(event.unicode_value)
                new_key = getattr(clutter.keysyms, "%s%s" % (keysym, self._dead_key[2]), None)
                if event.unicode_value == clutter.keysyms.space:
                    event.keyval = self._dead_key[0]
                    event.unicode_value = self._dead_key[1]
                    emit_key = True
                elif new_key:
                    event.keyval = new_key
                    event.unicode_value = int(clutter.keysym_to_unicode(event.keyval))
                    emit_key = True
                # else: both keys ignored
                self._dead_key = None
        elif event.hardware_keycode in (LEFT_ARROW, RIGHT_ARROW): # arrow keys
            if event.hardware_keycode == LEFT_ARROW: # left arrow
                self.move_cursor_left(select=bool(clutter.SHIFT_MASK & event.modifier_state))
            else: # right arrow
                self.move_cursor_right(select=bool(clutter.SHIFT_MASK & event.modifier_state))
        else:
            if event.unicode_value in DEAD_KEYS:
                self._dead_key = event.keyval, event.unicode_value, DEAD_KEYS[event.unicode_value]
            else:
                emit_key = True
            if '_%s' % event.keyval in KEYBOARD_KEYS_REPLACEMENTS:
                event.keyval = KEYBOARD_KEYS_REPLACEMENTS['_%s' % event.keyval]
        if emit_key and self._text_actor:
            self._text_actor.emit('key-press-event', event)
    
    def _key_release_event(self, event):
        if self._text_actor:
            self._text_actor.emit('key-release-event', event)
    
    def get_map_name(self):
        return self._map_name
    
    #keyboard load profile: load a mapping dictionnary, create buttons and calcul max line width 
    def load_profile(self, map_name):
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
                button.connect('button-release-event', self._on_button_release)
                # save key param in button object
                button.kb_text = key.text
                button.kb_width = key.width
                button.kb_evt = key.event
                button.kb_c_evt = key.clutter_event
                # add button to line
                line.add(button, key.width)
            self._lines.append(line)
            lines_width.append(line.width)
        self._columns_count = max(lines_width)
        
        if self._width > 0 and self._height > 0:
            self._refresh_allocation_params()
    
    def to_min(self):
        if self._map_name.endswith('_maj'):
            self.load_profile('%s_min' % (self._map_name[:-4]))

    def to_maj(self):
        if self._map_name.endswith('_min'):
            self.load_profile('%s_maj' % (self._map_name[:-4]))
    
    # clear keyboard: delete current keyboard mapping dictionnary
    def clear_keyboard(self):
        for line in self._lines:
            for button in line.buttons:
                button.unparent()
                button.destroy()
        self._lines = list()
        self._map_name = None
        self._keyboard_map = None
    
    def select_all(self):
        self._text_actor.set_cursor_position(0)
        self._text_actor.set_selection_bound(-1)
    
    def connect_clutter_text(self, text_actor):
        self._text_actor = text_actor
        self._text_actor.connect("notify::position", self._on_text_actor_position_changed)
        self._text_actor.connect("notify::selection-bound", self._on_text_actor_selection_bound_changed)
        self._text_actor.connect("button-press-event", self._on_text_actor_press)
        self._text_actor.connect("button-release-event", self._on_text_actor_release)
    
    def _on_text_actor_position_changed(self, source, position):
        if self._middle_click:
            self._middle_click = False
            new_position = self._text_actor.get_cursor_position()
            if self._next_position == -1:
                min_bound = self._next_selection_bound
                max_bound = -1
            elif self._next_selection_bound == -1:
                min_bound = self._next_position
                max_bound = -1
            else:
                min_bound = min(self._next_position, self._next_selection_bound)
                max_bound = max(self._next_position, self._next_selection_bound)
            if self._next_position != -1 and self._next_selection_bound != -1 and self._next_position != self._next_selection_bound and min_bound <= new_position <= max_bound:
                self._next_position = self._next_selection_bound = max_bound
            elif self._next_position == -1 or (new_position != -1 and new_position <= self._next_position):
                if self._next_position != -1:
                    self._next_position += len(self._clipboards["secondary"])
                if self._next_selection_bound != -1:
                    self._next_selection_bound += len(self._clipboards["secondary"])
            self.paste(clipboard="secondary")
        else:
            self.copy(clipboard="secondary")
    
    def _on_text_actor_selection_bound_changed(self, source, selection_bound):
        if not self._middle_click:
            self.copy(clipboard="secondary")
    
    def _on_text_actor_press(self, source, event):
        self._middle_click = False
        self._next_position = None
        self._next_selection_bound = None
        if event.button == 2: # middle button
            self._middle_click = True
            self._next_position = self._text_actor.get_cursor_position()
            self._next_selection_bound = self._text_actor.get_selection_bound()
    
    def _on_text_actor_release(self, source, event):
        # copy selection to secondary clipboard
        stage = event.get_stage()
        if stage:
            stage.set_key_focus(self)
        elif event.button == 2 and self._next_position is not None: # middle button
            self._text_actor.set_cursor_position(self._next_position)
            self._text_actor.set_selection_bound(self._next_selection_bound)
            self._next_position = None
            self._next_selection_bound = None
    
    def _emit_key_press(self, keyval, unival=None):
        if self._text_actor:
            event = clutter.Event(clutter.KEY_PRESS)
            event.keyval = keyval
            event.unicode_value = unival or int(clutter.keysym_to_unicode(event.keyval))
            #self._text_actor.emit('key-press-event', event)
            if self._keyboard_delay_id:
                gobject.source_remove(self._keyboard_delay_id)
            if self._keyboard_repeat_id:
                gobject.source_remove(self._keyboard_repeat_id)
                self._keyboard_repeat_id = None
            self._keyboard_delay_id = gobject.timeout_add(self.REPEAT_DELAY_MS, self._key_delay, event)
            self._key_press_event(event)
        self.emit('keyboard', keyval)
    
    def _emit_key_release(self, keyval, unival=None):
        if self._keyboard_repeat_id:
            gobject.source_remove(self._keyboard_repeat_id)
            self._keyboard_repeat_id = None
        if self._keyboard_delay_id:
            gobject.source_remove(self._keyboard_delay_id)
            self._keyboard_delay_id = None
        if self._text_actor:
            event = clutter.Event(clutter.KEY_RELEASE)
            event.keyval = keyval
            event.unicode_value = unival or int(clutter.keysym_to_unicode(event.keyval))
            #self._text_actor.emit('key-release-event', event)
            self._key_release_event(event)
    
    def _key_delay(self, event):
        self._key_press_event(event)
        if self._keyboard_repeat_id:
            gobject.source_remove(self._keyboard_repeat_id)
        self._keyboard_repeat_id = gobject.timeout_add(self.REPEAT_RATE_MS, self._key_repeat, event)
        return False
    
    def _key_repeat(self, event):
        self._key_press_event(event)
        return True
    
    def _on_button_press(self, source, event):
        # highlight button
        source.set_inner_color(self.highlight_color)
        clutter.grab_pointer(source)
        # press button
        if source.kb_evt == 'car':
            if source.kb_c_evt:
                self._emit_key_press(source.kb_c_evt)
    
    def _on_button_release(self, source, event):
        clutter.ungrab_pointer()
        source.set_inner_color(self.inner_color)
        # release button
        if source.kb_evt == 'car':
            if source.kb_c_evt:
                self._emit_key_release(source.kb_c_evt)
        elif source.kb_evt == 'fr_min':
            self.load_profile('fr_min')
        elif source.kb_evt == 'fr_maj':
            self.load_profile('fr_maj')
        elif source.kb_evt == 'en_min':
            self.load_profile('en_min')
        elif source.kb_evt == 'en_maj':
            self.load_profile('en_maj')
        elif source.kb_evt == 'de_min':
            self.load_profile('de_min')
        elif source.kb_evt == 'de_maj':
            self.load_profile('de_maj')
        elif source.kb_evt == 'en_caract':
            self.load_profile('en_caract')
        elif source.kb_evt == 'fr_caract':
            self.load_profile('fr_caract')
        elif source.kb_evt == 'de_caract':
            self.load_profile('de_caract')
        elif source.kb_evt == 'num':
            self.load_profile('int')
    
    def is_text_crypted(self):
        try:
            return self._text_actor.is_crypted()
        except Exception:
            try:
                return self._text_actor.get_password_char() != u'\x00'
            except Exception:
                return False
    
    def copy(self, clipboard="main"):
        if not self.is_text_crypted():
            text = self._text_actor.get_selection()
            if text or clipboard != "main":
                self._set_to_clipboard(text, clipboard)
    
    def cut(self, clipboard="main"):
        if not self.is_text_crypted():
            self.copy(clipboard)
            self._text_actor.delete_selection()
    
    def paste(self, clipboard="main"):
        text = self._get_from_clipboard(clipboard)
        if text:
            self._text_actor.delete_selection()
            position = self._text_actor.get_cursor_position()
            current_text = self._text_actor.get_text()
            if position < 0 or position > len(current_text):
                position = -1
            self._text_actor.insert_text(text, position)
    
    def _get_from_clipboard(self, clipboard="main"):
        if not self._clipboards[clipboard]:
            # read from file if it exists
            if os.path.isfile("/tmp/clipboard.%s" % clipboard):
                clipboard_file = open("/tmp/clipboard.%s" % clipboard, "r")
                self._clipboards[clipboard] = clipboard_file.read()
                clipboard_file.close()
        return self._clipboards[clipboard]
    
    def _set_to_clipboard(self, text, clipboard="main"):
        self._clipboards[clipboard] = text
        clipboard_file = open("/tmp/clipboard.%s" % clipboard, "w")
        clipboard_file.write(self._clipboards[clipboard])
        clipboard_file.close()
    
    def _get_positions(self):
        cursor_pos = self._text_actor.get_cursor_position()
        selection_bound = self._text_actor.get_selection_bound()
        min_pos = cursor_pos
        max_pos = selection_bound
        if cursor_pos == -1:
            min_pos = selection_bound
            max_pos = cursor_pos
        elif selection_bound != -1:
            min_pos = min(cursor_pos, selection_bound)
            max_pos = max(cursor_pos, selection_bound)
        return cursor_pos, selection_bound, min_pos, max_pos
    
    def move_cursor_left(self, type_="char", select=False, *args, **kwargs):
        cursor_pos, selection_bound, min_pos, max_pos = self._get_positions()
        if type_ == "word":
            if select:
                selection_bound = self._get_previous_word_position(bound="alphanumeric")
            else:
                selection_bound = cursor_pos = self._get_previous_word_position(bound="alphanumeric")
        else: # char
            if select:
                if selection_bound == -1:
                    selection_bound = len(self._text_actor.get_text()) - 1
                elif selection_bound > 0:
                    selection_bound -= 1
            else:
                same = (cursor_pos == selection_bound)
                if min_pos == -1:
                    min_pos = len(self._text_actor.get_text())
                if same:
                    min_pos -= 1
                selection_bound = cursor_pos = max(0, min_pos)
        self._text_actor.set_cursor_position(cursor_pos)
        self._text_actor.set_selection_bound(selection_bound)
    
    def move_cursor_right(self, type_="char", select=False, *args, **kwargs):
        cursor_pos, selection_bound, min_pos, max_pos = self._get_positions()
        if type_ == "word":
            if select:
                selection_bound = self._get_next_word_position(bound="alphanumeric")
            else:
                selection_bound = cursor_pos = self._get_next_word_position(bound="alphanumeric")
        else: # char
            if select:
                if selection_bound == -1 or selection_bound >= len(self._text_actor.get_text()) - 1:
                    selection_bound = -1
                else:
                    selection_bound += 1
            else:
                same = (cursor_pos == selection_bound)
                if max_pos == -1 or max_pos >= len(self._text_actor.get_text()) - 1:
                    cursor_pos = -1
                else:
                    cursor_pos = max_pos
                    if same:
                        cursor_pos += 1
                selection_bound = cursor_pos
        self._text_actor.set_cursor_position(cursor_pos)
        self._text_actor.set_selection_bound(selection_bound)
    
    def delete_beginning(self):
        cursor_pos, selection_bound, min_pos, max_pos = self._get_positions()
        self._text_actor.delete_text(0, min_pos)
        self._text_actor.set_cursor_position(0)
        self._text_actor.set_selection_bound(max_pos - min_pos)
    
    def delete_end(self):
        cursor_pos, selection_bound, min_pos, max_pos = self._get_positions()
        self._text_actor.delete_text(cursor_pos, -1)
        self._text_actor.set_cursor_position(min_pos)
        self._text_actor.set_selection_bound(max_pos)
    
    def delete_all(self):
        self._text_actor.delete_text(0, -1)
        self._text_actor.set_cursor_position(0)
        self._text_actor.set_selection_bound(0)
    
    def _get_previous_word_position(self, bound="whitespace"):
        cursor_pos, selection_bound, min_pos, max_pos = self._get_positions()
        if selection_bound == 0:
            return 0
        if bound == "whitespace":
            def is_bound(text, i):
                return text[i].isspace() and not text[i+1].isspace()
        else: # non-alphanumeric
            def is_bound(text, i):
                return not text[i].isalnum() and text[i+1].isalnum()
        text = self._text_actor.get_text()
        if selection_bound == -1:
            i = len(text) - 2
        else:
            i = selection_bound - 2
        while i >= 0 and not is_bound(text, i):
            i -= 1
        return max(0, i + 1)
    
    def _get_next_word_position(self, bound="whitespace"):
        cursor_pos, selection_bound, min_pos, max_pos = self._get_positions()
        text = self._text_actor.get_text()
        if selection_bound in (-1, len(text)):
            return -1
        if bound == "whitespace":
            def is_bound(text, i):
                return not text[i-1].isspace() and text[i].isspace()
        else: # non-alphanumeric
            def is_bound(text, i):
                return text[i-1].isalnum() and not text[i].isalnum()
        i = selection_bound + 1
        while i < len(text) and not is_bound(text, i):
            i += 1
        return i
    
    def delete_previous_word(self, bound="whitespace"):
        cursor_pos, selection_bound, min_pos, max_pos = self._get_positions()
        previous_word_position = self._get_previous_word_position(bound)
        self._text_actor.delete_text(previous_word_position, min_pos)
        self._text_actor.set_cursor_position(previous_word_position)
        self._text_actor.set_selection_bound(previous_word_position + max_pos - min_pos)
    
    def do_get_preferred_width(self, for_height):
        #TODO
        preferred_width = 0
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        #TODO
        preferred_height = 0
        return preferred_height, preferred_height
    
    def _refresh_allocation_params(self):
        if self._columns_count > 0:
            button_width = int(float(self._width - self._columns_count * self._spacing.x + self._spacing.x) / self._columns_count)
            button_height = int(float(self._height - len(self._lines) * self._spacing.y + self._spacing.y) / len(self._lines))
            self._button_size = min(button_width, button_height)
            
            self._padding_y = int(float(self._height - len(self._lines) * (self._button_size + self._spacing.y) + self._spacing.y) / 2.0)
            
            for line in self._lines:
                line.padding_x = int(float(self._width - line.width * (self._button_size + self._spacing.x) + self._spacing.x) / 2.0)
                line.padding_y = self._padding_y + self._lines.index(line) * (self._button_size + self._spacing.y)
    
    # button mapping: calcul each buttons width and place them
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


if __name__ == '__main__':
    '''
    main to test keyboard functionalities
    contains a text, keyboard, and some buttons
    '''
    from flowbox import FlowBox

    # create window
    stage = clutter.Stage()
    stage.set_size(1000, 600)
    stage.connect('destroy', clutter.main_quit)
    stage.set_color('#000000ff')
    
    # create text wich will show keyboard entries results
    text = clutter.Text()
    text.set_color('#ffffffff')
    text.set_selection_color('#8888ffff')
    text.set_font_name('22')
    text.set_size(900, 40)
    text.set_position(50, 5)
    text.set_cursor_visible(True)
    text.set_editable(True)
    text.set_selectable(True)
    text.set_reactive(True)
    #text.set_reactive(False)
    stage.add(text)
    
    kb_bg = clutter.Rectangle()
    kb_bg.set_color('#ffffff22')
    kb_bg.set_size(1000, 500)
    kb_bg.set_position(0, 50)
    stage.add(kb_bg)
    
    # create keyboard in fr
    keyboard = Keyboard('fr_maj', spacing=10)
    keyboard.set_size(1000, 500)
    keyboard.set_position(0, 50)
    stage.add(keyboard)
    
    # create other entries
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
    
    keys_btn = ClassicButton('print clutter keys names')
    keys_btn.set_size(150, 50)
    box.add(keys_btn)
    
    stage.add(box)
    
    stage.show()
   
    # function lang_callback: action when language is changed 
    def lang_callback(button, event, keyboard):
        map_name = keyboard.get_map_name()
        if map_name == 'fr_maj':
            keyboard.load_profile('en_maj')
        elif map_name == 'fr_min':
            keyboard.load_profile('en_min')
        elif map_name == 'en_maj':
            keyboard.load_profile('fr_maj')
        elif map_name == 'en_min':
            keyboard.load_profile('fr_min')
        elif map_name == 'fr_caract':
            keyboard.load_profile('en_caract')
        elif map_name == 'en_caract':
            keyboard.load_profile('fr_caract')

    # function keyboard_callback: action keyboard is used
    def on_text_change(actor):
        CAPITAL_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        print 'Text changed:', actor.get_text()
        new_text = actor.get_text()
        if len(new_text) == 0:
            keyboard.to_maj()
        else:
            cursor_pos = actor.get_cursor_position()
            if cursor_pos >= len(new_text):
                cursor_pos = -1
            last_char = new_text[cursor_pos]
            if last_char in ('.', '!', '?'):
                keyboard.to_maj()
            else:
                second_last_char = '_'
                if cursor_pos >= 1 or len(new_text) > 1 and cursor_pos == -1:
                    second_last_char = new_text[cursor_pos - 1]
                if last_char in CAPITAL_LETTERS and second_last_char not in CAPITAL_LETTERS:
                    keyboard.to_min()
    
    # function num_callback used when numeric keyboard is called
    def num_callback(button, event, keyboard):
        map_name = keyboard.get_map_name()
        if map_name == 'int':
            keyboard.load_profile('fr_maj')
        else:
            keyboard.load_profile('int')
            
    # function left_callback when left button is used
    def left_callback(button, event, text):
        cursor_pos = text.get_cursor_position()
        if cursor_pos == -1:
            cursor_pos = len(text.get_text())
        cursor_pos -= 1
        text.set_selection(cursor_pos, cursor_pos)
      
    # function right_callback when right button is used
    def right_callback(button, event, text):
        cursor_pos = text.get_cursor_position()
        cursor_pos += 1
        text.set_selection(cursor_pos, cursor_pos)
    
    # function to get clutter keys names
    def print_clutter_key_map(button, event):
        for k in dir(clutter.keysyms):
            if hasattr(clutter.keysyms, k):
                attr = getattr(clutter.keysyms, k)
                if isinstance(attr, (int, long)):
                    print '%s\t%s\t%s' % (attr, k, unichr(clutter.keysym_to_unicode(attr)))

    # connect signals
    #left.connect('button-press-event', left_callback, text)
    left.connect('button-press-event', keyboard.move_cursor_left)
    #right.connect('button-press-event', right_callback, text)
    right.connect('button-press-event', keyboard.move_cursor_right)
    num.connect('button-press-event', num_callback, keyboard)
    lan.connect('button-press-event', lang_callback, keyboard)
    lan.connect('button-press-event', lang_callback, keyboard)
    keys_btn.connect('button-press-event', print_clutter_key_map)
    keyboard.connect_clutter_text(text)
    
    stage.set_key_focus(keyboard)
    
    clutter.main()

