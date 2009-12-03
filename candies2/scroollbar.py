#!/ur/bin/env python
# -*- coding: utf-8 -*-

''' 
Keyboard class
author : flavie
date : dec 3 2009
version : 0
'''

import sys
import operator
import gobject

class Scrollbar(clutter.Actor, clutter.Container):
    __gtype_name__ = 'Scrollbar'
    __gsignals__ = {'scroll_position' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_INT])}
    
    #keyboard initialisation
    def __init__(self):
        self.scrollbar_background=clutter.Rectangle()
        self.scroller=clutter.Rectangle()
        self.scroller.set_parent(self)
        self.scroller.set_reactive(True)
        self.scroller.connect('button-press-event', self.on_scroll_press)
        self.scroller.connect('button-release-event', self.on_scroll_release)
    
    def on_scroll_press(self, source, event):
        pass 
        
    def on_scroll_release(self, source, event):
        pass
        
    def do_allocate(self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
    
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

#main to test scrollbar
if __name__ == '__main__':

stage = clutter.Stage()
stage.connect('destroy',clutter.main_quit)

scrollbar = Scrollbar()
scrollbarr.set_size(10,460)
scrollbar.set_origin(10,10)

stage.show

clutter.main() 
