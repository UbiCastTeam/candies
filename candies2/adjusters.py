#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
import gobject
import clutter
from buttons import ClassicButton
from box import Box

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
    
    # skin
    button_size = 50
    label_font_size = '16'
    label_font_color = '#000000ff'
    button_font_size = '20'
    button_font_color = '#000000ff'
    button_inner_color = '#ffffff55'
    button_highlight_color = '#ffffffbb'
    button_border_color = '#ffffff66'
    button_inactive_color = '#00000044'

    def __init__(self, min, max, default, increment=1, text=None, factor=None, spacing=5, padding=0, texture=None):
        Box.__init__(self, horizontal=True, spacing=spacing, padding=padding)

        self.min = min
        self.max = max
        self.value = default
        self.increment = increment
        if factor is None:
            factor = 1
        self.factor = factor
        
        minus = ClassicButton("-", texture=texture)
        minus.set_font_name(self.button_font_size)
        minus.set_font_color(self.button_font_color)
        minus.set_inner_color(self.button_inner_color)
        minus.set_border_color(self.button_border_color)
        minus.set_size(self.button_size, self.button_size)
        minus.connect("button-release-event", self.dec)

        self.value_btn = ClassicButton('', texture=texture)
        self.value_btn.set_font_name(self.button_font_size)
        self.value_btn.set_font_color(self.button_font_color)
        self.value_btn.set_inner_color(self.button_inner_color)
        self.value_btn.set_border_color(self.button_border_color)
        self.value_btn.set_width(2*self.button_size) #minimum size

        self.update_rounded_value()
        # set default value

        plus = ClassicButton("+", texture=texture)
        plus.set_font_name(self.button_font_size)
        plus.set_font_color(self.button_font_color)
        plus.set_inner_color(self.button_inner_color)
        plus.set_border_color(self.button_border_color)
        plus.connect("button-release-event", self.inc)
        plus.set_size(self.button_size, self.button_size)

        if text is not None:
            label = ClassicButton(str(text), padding=0)
            label.set_font_name(self.label_font_size)
            label.set_font_color(self.label_font_color)
            label.set_inner_color('#00000000')
            label.set_border_color('#00000000')
            self.add({'name': 'text', 'center': True, 'object': label, 'resizable': 0.7})

        self.add(
            {'name': 'minus', 'center': True, 'object': minus},
            {'name': 'value','expand': True, 'resizable': 0.3, 'object': self.value_btn},
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

        value_to_display = self.get_safe_value(value_to_display)
        self.value_btn.props.text = str(value_to_display)

    def get_safe_value(self, value):
        if value > self.max*self.factor:
            value = int(self.max*self.factor)
        elif value < self.min*self.factor:
            value = int(self.min*self.factor)
        return value


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

