#!/usr/bin/env python
# -*- coding: utf-8 -*

import gi
gi.require_version('Clutter', '1.0')
from gi.repository import Clutter
from gi.repository import GObject


class SimpleClick(GObject.GObject):
    __gtype_name__ = 'SimpleClick'

    def __init__(self, actor):
        GObject.GObject.__init__(self)
        self.actor = actor
        # if 'simple-click-event' not in GObject.signal_list_names(actor):
        if GObject.signal_lookup('simple-click-event', actor) == 0:  # correction d'un warning d'enregistrement multiple
            try:
                GObject.signal_new(
                    'simple-click-event', actor, GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
            except:
                pass
        actor.connect('button-press-event', self.on_press)
        actor.connect('button-release-event', self.on_release)
        actor.connect('leave-event', self.on_leave)
        self._is_pressed = False

    def on_press(self, source, event):
        self._is_pressed = True

    def on_release(self, source, event):
        if self._is_pressed:
            self._is_pressed = False
            self.actor.emit('simple-click-event')

    def on_leave(self, source, event):
        if self._is_pressed:
            self._is_pressed = False


class LongClick(SimpleClick):
    __gtype_name__ = 'LongClick'
    default_long_delay = 2000

    def __init__(self, actor, long_delay=None, long_msg=None):
        SimpleClick.__init__(self, actor)
        # if 'long-press-event' not in GObject.signal_list_names(actor):
        if GObject.signal_lookup('long-press-event', actor) == 0:  # correction d'un warning d'enregistrement multiple
            try:
                GObject.signal_new(
                    'long-press-event', actor, GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
            except:
                pass
        # if 'long-click-event' not in GObject.signal_list_names(actor):
        if GObject.signal_lookup('long-click-event', actor) == 0:  # correction d'un warning d'enregistrement multiple
            try:
                GObject.signal_new(
                    'long-click-event', actor, GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
            except:
                pass
        if long_delay is None:
            long_delay = self.default_long_delay
        self.long_delay = long_delay
        # self.long_msg = long_msg
        self._is_long = False
        self._timeout_id = None

    def on_press(self, source, event):
        if self._timeout_id:
            GObject.source_remove(self._timeout_id)
        Clutter.grab_pointer(self.actor)
        self._is_long = False
        self._is_pressed = True
        self._timeout_id = GObject.timeout_add(
            self.long_delay, self.on_long_press, source)
        # if self.long_msg is not None:
        # self.launchEvent('info', 'Hold %s seconds to %s'
        # %(self.long_delay_ms/1000, self.long_msg))

    def on_long_press(self, source):
        if self._is_pressed:
            self._is_long = True
            self.actor.emit('long-press-event')

    def on_release(self, source, event):
        Clutter.ungrab_pointer()
        if self._is_pressed:
            self._is_pressed = False
            if self._timeout_id:
                GObject.source_remove(self._timeout_id)
                self._timeout_id = None
            if self._is_long:
                self.actor.emit('long-click-event')
            else:
                self.actor.emit('simple-click-event')

    def is_long(self):
        return self._is_long


def tester(stage):

    lbl = Clutter.Text()

    rect = Clutter.Rectangle()
    SimpleClick(rect)
    rect.set_color(Clutter.color_from_string('Green')[1])
    rect.set_border_width(2)
    rect.set_border_color(Clutter.color_from_string('DarkGreen')[1])
    rect.set_size(200, 75)
    rect.set_position(240, 75)
    rect.set_reactive(True)
    rect.connect('simple-click-event',
                 lambda src: lbl.set_text('Clic on green!'))

    rect2 = Clutter.Rectangle()
    LongClick(rect2)
    rect2.set_color(Clutter.color_from_string('Yellow')[1])
    rect2.set_border_width(2)
    rect2.set_border_color(Clutter.color_from_string('DarkGreen')[1])
    rect2.set_size(200, 75)
    rect2.set_position(240, 175)
    rect2.set_reactive(True)
    rect2.connect('simple-click-event',
                  lambda src: lbl.set_text('Clic on yellow!'))
    rect2.connect('long-press-event',
                  lambda src: lbl.set_text('Long pressing...'))
    rect2.connect('long-click-event', lambda src:
                  lbl.set_text('Long clic on yellow!'))

    stage.add_child(lbl)
    stage.add_child(rect)
    stage.add_child(rect2)
    stage.show()

    Clutter.main()

if __name__ == '__main__':
    from test import run_test
    run_test(tester)
