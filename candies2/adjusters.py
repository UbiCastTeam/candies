#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
import gobject
import clutter
from roundrect import RoundRectangle
from buttons import ClassicButton
from box import Box
from text import StretchText

class NumberAdjuster(Box):
    __gtype_name__ = 'NumberAdjuster'
    __gproperties__ = {
        'increment' : (
            gobject.TYPE_FLOAT, 'increment', 'Increment amount when adjusting the value',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
    }
    __gsignals__ = {'value_updated' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT]),
    }

    def __init__(self, min, max, default, increment=1, text=None, factor=None):
        Box.__init__(self, horizontal=True, spacing=5, border=5)

        self.min = min
        self.max = max
        self.value = default
        self.increment = increment
        if factor is None:
            factor = 1
        self.factor = factor
        
        # skin
        self.button_size = 50
        self.label_font_size = '16'
        self.button_font_size = '20'
        self.button_font_color = '#000000ff'
        self.button_inner_color = '#ffffff44'
        self.button_highlight_color = '#ffffff88'
        self.button_border_color = '#ffffff44'
        self.button_inactive_color = '#00000044'

        minus = ClassicButton("-")
        minus.label.set_font_name(self.button_font_size)
        minus.label.set_color(self.button_font_color)
        minus.rect.set_color(self.button_inner_color)
        minus.rect.set_border_color(self.button_border_color)
        minus.set_size(self.button_size, self.button_size)
        minus.connect("button-release-event", self.dec)

        self.value_btn = ClassicButton('')
        self.value_btn.label.set_font_name(self.button_font_size)
        self.value_btn.label.set_color(self.button_font_color)
        self.value_btn.rect.set_color(self.button_inner_color)
        self.value_btn.rect.set_border_color(self.button_border_color)
        self.value_btn.set_width(2*self.button_size) #minimum size

        self.update_rounded_value()
        # set default value

        plus = ClassicButton("+")
        plus.label.set_font_name(self.button_font_size)
        plus.label.set_color(self.button_font_color)
        plus.rect.set_color(self.button_inner_color)
        plus.rect.set_border_color(self.button_border_color)
        plus.connect("button-release-event", self.inc)
        plus.set_size(self.button_size, self.button_size)

        if text is not None:
            label = ClassicButton(str(text), stretch=False, border=0.0)
            label.label.set_font_name(self.label_font_size)
            label.label.set_color(self.button_font_color)
            label.rect.set_color('#00000000')
            label.rect.set_border_color('#00000000')
            self.add({'name': 'text', 'center': True, 'object': label, 'resizable': 0.6})

        self.add(
            {'name': 'minus', 'center': True, 'object': minus},
            {'name': 'value','expand': True, 'resizable': 0.4, 'object': self.value_btn},
            {'name': 'plus', 'center': True, 'object': plus})

    def inc(self, button, event):
        button.rect.set_color(self.button_highlight_color)
        if self.value + self.increment <= self.max:
            self.value += self.increment
            self.update()
        elif self.value != self.max:
            self.value = self.max
            self.update()
        gobject.timeout_add(200, button.rect.set_color, self.button_inner_color)

    def dec(self, button, event):
        button.rect.set_color(self.button_highlight_color)
        if self.value - self.increment >= self.min:
            self.value -= self.increment
            self.update()
        elif self.value != self.min:
            self.value = self.min
            self.update()
        gobject.timeout_add(200, button.rect.set_color, self.button_inner_color)

    def update(self):
        self.update_rounded_value()
        self.emit('value_updated', self.value)

    def do_set_property(self, pspec, value):
        if pspec.name == 'text':
            self.rect.props.color = value
        elif pspec.name == 'increment':
            self.increment = value
        else:
            raise TypeError('Unknown property ' + pspec.name)
        #self.queue_redraw()

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self.rect.props.color
        elif pspec.name == 'text':
            return self.text
        elif pspec.name == 'font-color':
            return self.label.props.color
        elif pspec.name == 'border-color':
            return self.rect.props.border_color
        elif pspec.name == 'border-width':
            return self.rect.props.border_width
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def update_rounded_value(self):
        value_to_display = float(self.value * self.factor)
        if isinstance(self.increment, int):
            value_to_display = int(round(value_to_display, 0))
        elif isinstance(self.increment, float):
            number_decimals = len(str(self.increment).split(".")[1])
            value_to_display = round(value_to_display, number_decimals)
        self.value_btn.props.text = str(value_to_display)


if __name__ == '__main__':

    stage_width = 640
    stage_height = 480
    stage = clutter.Stage()
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', clutter.main_quit)


    def update_callback(source, value):
        print "Test value has been updated", value

    test = NumberAdjuster(0, 10, 5, increment=0.1, text="Test value")
    test.connect("value-updated", update_callback)
    stage.add(test)
    
    r = clutter.Rectangle()
    r.set_color('#8888ffff')
    test.set_background(r)


    test = NumberAdjuster(1000, 10000, 5000, increment=1000, factor=0.001)
    test.set_width(600)
    stage.add(test)
    test.set_position(0, 200)
    
    r = clutter.Rectangle()
    r.set_color('#8888ffff')
    test.set_background(r)

    t = clutter.Text()

    stage.show()
    clutter.main()

