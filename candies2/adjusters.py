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

        minus = ClassicButton("-", stretch=True)
        minus.set_size(minus.get_width(), minus.get_width())
        minus.connect("button-release-event", self.dec)

        self.value_btn = value_btn = ClassicButton(str(default), stretch=True)
        #value.connect("button-release-event", self.launch_vkb)

        plus = ClassicButton("+", stretch=True)
        plus.connect("button-release-event", self.inc)
        plus.set_size(plus.get_width(), plus.get_width())

        if text is not None:
            label = StretchText()
            label.set_text(text)
            label_width = label.get_preferred_width(minus.get_height())[1]
            label.set_width(label_width)
            self.add({'name': 'text', 'center': True, 'object': label})

        self.add(
            {'name': 'minus', 'expand': True, 'object': minus, 'keep_ratio': True},
            {'name': 'value','expand': True,'resizable': 0.7,'object': value_btn},
            {'name': 'plus', 'expand': True, 'object': plus, 'keep_ratio': True})

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

    def update_callback(source, value):
        print "Test value has been updated", value

    test = NumberAdjuster(0, 10, 5, 1, "Test value")
    test.connect("value-updated", update_callback)
    test.set_size(300, 50)
    stage.add(test)


    test = NumberAdjuster(0, 10, 5.0, 0.1)
    test.set_size(300, 50)
    test.queue_relayout()
    stage.add(test)
    test.set_position(0, 200)

    t = clutter.Text()

    stage.show()
    clutter.main()

