import clutter
import gobject

class SimpleClickActor(clutter.Actor):
    __gtype_name__ = 'SimpleClickActor'
    __gsignals__ = {
        'simple-click-event' : (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()
        ),
    }
    
    def __init__(self):
        clutter.Actor.__init__(self)
        self.connect('button-press-event', self.on_press)
        self.connect('button-release-event', self.on_release)
        self.connect('leave-event', self.on_leave)
        self._is_pressed = False

    def on_press(self, source, event):
        self._is_pressed = True
        clutter.grab_pointer(self)
        return True

    def on_release(self, source, event):
        if self._is_pressed == True:
            self._is_pressed = False
            clutter.ungrab_pointer()
            self.emit('simple-click-event')
            return True
        return False
    
    def on_leave(self, source, event):
        if self._is_pressed == True:
            self._is_pressed = False
            return True
        return False

class LongClickActor(SimpleClickActor):
    __gtype_name__ = 'LongClickActor'
    __gsignals__ = {
        'long-press-event' : (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()
        ),
        'long-click-event' : (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()
        ),
    }
    default_long_delay = 2000
    
    def __init__(self, long_delay=None, long_msg=None):
        SimpleClickActor.__init__(self)
        if long_delay is None:
            long_delay = self.default_long_delay
        self.long_delay = long_delay
        #self.long_msg = long_msg
        self._is_long = False

    def on_press(self, source, event):
        self._is_long = False
        SimpleClickActor.on_press(self, source, event)
        gobject.timeout_add(self.long_delay, self.on_long_press, source)
        #if self.long_msg is not None:
        #    self.launchEvent('info', 'Hold %s seconds to %s' %(self.long_delay_ms/1000, self.long_msg))
    
    def on_long_press(self, source): 
        if self._is_pressed:
            self._is_long = True
            self.emit('long-press-event')
        return False
    
    def on_release(self, source, event):
        if self._is_pressed == True:
            self._is_pressed = False
            clutter.ungrab_pointer()
            if self._is_long:
                self.emit('long-click_event')
            else:
                self.emit('simple-click-event')
            return True
        return False
