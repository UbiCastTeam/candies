#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
from gi.repository import GObject
from gi.repository import Clutter
from text import TextContainer
from buttons import ClassicButton
from box import Box


class NumberAdjuster(Box):
    __gtype_name__ = 'NumberAdjuster'
    __gproperties__ = {
        'increment': (
            GObject.TYPE_FLOAT, 'increment', 'Increment amount when adjusting the value',
            0.0, sys.maxint, 0.0, GObject.PARAM_READWRITE
        ),
    }
    __gsignals__ = {
        'value_updated': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_FLOAT]),
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
            self.factor = 1
        else:
            self.factor = factor

        self.minus = ClassicButton('-', texture=texture)
        self.minus.set_font_name(self.button_font_size)
        self.minus.set_font_color(self.button_font_color)
        self.minus.set_inner_color(self.button_inner_color)
        self.minus.set_border_color(self.button_border_color)
        self.minus.set_size(self.button_size, self.button_size)
        self.minus.connect('button-release-event', self.dec)

        self.value_btn = ClassicButton(texture=texture)
        self.value_btn.set_font_name(self.button_font_size)
        self.value_btn.set_font_color(self.button_font_color)
        self.value_btn.set_inner_color(self.button_inner_color)
        self.value_btn.set_border_color(self.button_border_color)
        self.value_btn.set_size(
            2 * self.button_size, self.button_size)  # minimum size

        self.update_rounded_value()
        # set default value

        self.plus = ClassicButton('+', texture=texture)
        self.plus.set_font_name(self.button_font_size)
        self.plus.set_font_color(self.button_font_color)
        self.plus.set_inner_color(self.button_inner_color)
        self.plus.set_border_color(self.button_border_color)
        self.plus.set_size(self.button_size, self.button_size)
        self.plus.connect('button-release-event', self.inc)

        self.label = None
        if text is not None:
            self.label = TextContainer(str(text), padding=0)
            self.label.set_font_name(self.label_font_size)
            self.label.set_font_color(self.label_font_color)
            self.label.set_inner_color('#00000000')
            self.label.set_border_color('#00000000')
            self.add_element(self.label, 'minus', expand=True, resizable=0.7)
            value_btn_size = 0.3
        else:
            value_btn_size = 1.0

        self.add_element(self.minus, 'minus', expand=True)
        self.add_element(
            self.value_btn, 'value', expand=True, resizable=value_btn_size)
        self.add_element(self.plus, 'plus', expand=True)

    def set_lock(self, status):
        self.set_all_reactive(not status)
        self.set_opacity(255 - status * 128)

    def set_all_reactive(self, status):
        self.plus.set_reactive(status)
        self.minus.set_reactive(status)
        self.value_btn.set_reactive(status)

    def set_value(self, value, silent=False):
        if value < self.min:
            value = self.min
        elif value > self.max:
            value = self.max
        self.value = value
        self.update(silent)

    def inc(self, button, event):
        button.set_inner_color(self.button_highlight_color)
        if self.value + self.increment <= self.max:
            self.value += self.increment
            self.update()
        elif self.value != self.max:
            self.value = self.max
            self.update()
        GObject.timeout_add(
            200, button.set_inner_color, self.button_inner_color)

    def dec(self, button, event):
        button.set_inner_color(self.button_highlight_color)
        if self.value - self.increment >= self.min:
            self.value -= self.increment
            self.update()
        elif self.value != self.min:
            self.value = self.min
            self.update()
        GObject.timeout_add(
            200, button.set_inner_color, self.button_inner_color)

    def update(self, silent=False):
        self.update_rounded_value()
        if not silent:
            self.emit('value_updated', self.value)

    def do_set_property(self, pspec, value):
        if pspec.name == 'text':
            self.rect.props.color = value
        elif pspec.name == 'increment':
            self.increment = value
        else:
            raise TypeError('Unknown property ' + pspec.name)

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
        if value > self.max * self.factor:
            value = int(round(self.max * self.factor))
        elif value < self.min * self.factor:
            value = int(round(self.min * self.factor))
        return value

    def set_min(self, min):
        self.min = min
        if self.value < self.min:
            self.value = self.min
            self.update()

    def set_max(self, max):
        self.max = max
        if self.value > self.max:
            self.value = self.max
            self.update()


if __name__ == '__main__':
    stage_width = 640
    stage_height = 480
    stage = Clutter.Stage()
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', Clutter.main_quit)

    def update_callback(source, value):
        print("Test value has been updated", value)

    test = NumberAdjuster(0, 10, 5, increment=0.1, text="Test value")
    test.connect("value-updated", update_callback)
    stage.add(test)

    r = Clutter.Rectangle()
    r.set_color('#8888ffff')
    test.set_background(r)

    test = NumberAdjuster(1000, 10000, 5000, increment=1000, factor=0.001)
    test.set_width(600)
    stage.add(test)
    test.set_position(0, 200)

    r = Clutter.Rectangle()
    r.set_color('#8888ffff')
    test.set_background(r)

    t = Clutter.Text()

    stage.show()
    Clutter.main()
