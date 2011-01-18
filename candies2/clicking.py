#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter
import gobject

class SimpleClick(gobject.GObject):
    __gtype_name__ = 'SimpleClick'
    
    def __init__(self, actor):
        gobject.GObject.__init__(self)
        self.actor = actor
        if 'simple-click-event' not in gobject.signal_list_names(actor):
            gobject.signal_new('simple-click-event', actor, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        actor.connect('button-press-event', self.on_press)
        actor.connect('button-release-event', self.on_release)
        actor.connect('leave-event', self.on_leave)
        self._is_pressed = False

    def on_press(self, source, event):
        self._is_pressed = True
        return True

    def on_release(self, source, event):
        if self._is_pressed == True:
            self._is_pressed = False
            self.actor.emit('simple-click-event')
            return True
        return False
    
    def on_leave(self, source, event):
        if self._is_pressed == True:
            self._is_pressed = False
            return True
        return False

class LongClick(SimpleClick):
    __gtype_name__ = 'LongClick'
    default_long_delay = 2000
    
    def __init__(self, actor, long_delay=None, long_msg=None):
        SimpleClick.__init__(self, actor)
        if 'long-press-event' not in gobject.signal_list_names(actor):
            gobject.signal_new('long-press-event', actor, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        if 'long-click-event' not in gobject.signal_list_names(actor):
            gobject.signal_new('long-click-event', actor, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        if long_delay is None:
            long_delay = self.default_long_delay
        self.long_delay = long_delay
        #self.long_msg = long_msg
        self._is_long = False
        self._timeout_id = None

    def on_press(self, source, event):
        if self._timeout_id:
            gobject.source_remove(self._timeout_id)
        clutter.grab_pointer(self.actor)
        self._is_long = False
        self._is_pressed = True
        self._timeout_id = gobject.timeout_add(self.long_delay, self.on_long_press, source)
        #if self.long_msg is not None:
        #    self.launchEvent('info', 'Hold %s seconds to %s' %(self.long_delay_ms/1000, self.long_msg))
        return True
    
    def on_long_press(self, source):
        if self._is_pressed:
            self._is_long = True
            self.actor.emit('long-press-event')
        return False
    
    def on_release(self, source, event):
        if self._is_pressed == True:
            self._is_pressed = False
            if self._timeout_id:
                gobject.source_remove(self._timeout_id)
                self._timeout_id = None
            clutter.ungrab_pointer()
            if self._is_long:
                self.actor.emit('long-click-event')
            else:
                self.actor.emit('simple-click-event')
            return True
        return False

if __name__ == '__main__':
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)
    
    lbl = clutter.Text()
    
    rect = clutter.Rectangle()
    SimpleClick(rect)
    rect.set_color(clutter.color_from_string('Green'))
    rect.set_border_width(2)
    rect.set_border_color(clutter.color_from_string('DarkGreen'))
    rect.set_size(200, 75)
    rect.set_position(240, 75)
    rect.set_reactive(True)
    rect.connect('simple-click-event', lambda src: lbl.set_text('Clic on green!'))
    
    rect2 = clutter.Rectangle()
    LongClick(rect2)
    rect2.set_color(clutter.color_from_string('Yellow'))
    rect2.set_border_width(2)
    rect2.set_border_color(clutter.color_from_string('DarkGreen'))
    rect2.set_size(200, 75)
    rect2.set_position(240, 175)
    rect2.set_reactive(True)
    rect2.connect('simple-click-event', lambda src: lbl.set_text('Clic on yellow!'))
    rect2.connect('long-press-event', lambda src: lbl.set_text('Long pressing...'))
    rect2.connect('long-click-event', lambda src: lbl.set_text('Long clic on yellow!'))
    
    stage.add(lbl, rect, rect2)
    stage.show()

    clutter.main()
