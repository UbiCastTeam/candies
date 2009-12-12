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

    def __init__(self, min, max, default, increment=1, text=None):
        Box.__init__(self, horizontal=True, spacing=5, border=5)

        self.min = min
        self.max = max
        self.value = default
        self.increment = increment
        self.button_size = 50
        self.button_font_size = '20'
        self.label_font_size = '16'

        minus = ClassicButton("-")
        minus.label.set_font_name(self.button_font_size)
        minus.set_size(self.button_size, self.button_size)
        minus.connect("button-release-event", self.dec)

        self.value_btn = ClassicButton(str(default))
        self.value_btn.label.set_font_name(self.button_font_size)
        self.value_btn.set_width(2*self.button_size) #minimum size
        #value.connect("button-release-event", self.launch_vkb)

        plus = ClassicButton("+")
        plus.label.set_font_name(self.button_font_size)
        plus.connect("button-release-event", self.inc)
        plus.set_size(self.button_size, self.button_size)

        if text is not None:
            label = ClassicButton(str(text), stretch=False, border=0.0)
            label.label.set_font_name(self.label_font_size)
            label.rect.set_color('#00000000')
            label.rect.set_border_color('#00000000')
            self.add({'name': 'text', 'center': True, 'object': label})

        self.add(
            {'name': 'minus', 'object': minus},
            {'name': 'value','expand': True, 'resizable': 1.0, 'object': self.value_btn},
            {'name': 'plus', 'object': plus})

    def inc(self, *args):
        if self.value + self.increment <= self.max:
            self.value += self.increment
            self.update()

    def dec(self, *args):
        if self.value - self.increment >= self.min:
            self.value -= self.increment
            self.update()

    def update(self):
        self.value_btn.text = str(self.value)
        self.value_btn.set_property("text", self.value)
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


if __name__ == '__main__':

    stage_width = 640
    stage_height = 480
    stage = clutter.Stage()
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', clutter.main_quit)

    r = clutter.Rectangle()
    r.set_color('#ff0000ff')

    def update_callback(source, value):
        print "Test value has been updated", value

    test = NumberAdjuster(0, 10, 5, 1, "Test value")
    test.connect("value-updated", update_callback)
    stage.add(test)
    test.set_background(r)


    test = NumberAdjuster(0, 10, 5.0, 0.1)
    test.queue_relayout()
    stage.add(test)
    test.set_position(0, 200)

    t = clutter.Text()

    stage.show()
    clutter.main()

