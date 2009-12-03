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
import clutter
from roundrect import RoundRectangle

class Scrollbar(clutter.Actor, clutter.Container):
    __gtype_name__ = 'Scrollbar'
    __gsignals__ = {'scroll_position' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_INT])}
    
    #keyboard initialisation
    def __init__(self):
        clutter.Actor.__init__(self)
        self.scrollbar_background=clutter.Rectangle()
        self.scrollbar_background.set_parent(self)
        self.scrollbar_background.set_color('LightBlue')
      
        self.scroller=clutter.Rectangle()
        self.scroller.set_color('Gray')
        self.scroller.set_parent(self)
        self.scroller.set_reactive(True)
        self.scroller.connect('button-press-event', self.on_scroll_press)
        self.scroller.connect('button-release-event', self.on_scroll_release)
        self.scroller.connect('motion-event', self.on_scroll_move)
        self.scroller_position = 0
    
        self.last_event_y = None
    
    def on_scroll_press(self, source, event):
        self.last_event_y = event.y
        return True 
        
    def on_scroll_release(self, source, event):
        clutter.ungrab_pointer()
        self.last_event_y = None
        
    def on_scroll_move(self, source, event):
        if self.last_event_y is None: return
        clutter.grab_pointer(self.scroller)
        self.last_event_y = event.y
        self.scroller_position = event.y
        print event.y
        self.queue_relayout()
        
    def do_allocate(self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
        margin = box_width/8
        
        scroller_width = box_width - 2*margin        
        bar_width = box_width/4
        bar_height = box_height - 2*margin - scroller_width      
        
        bar_box = clutter.ActorBox()  
        bar_box.x1 = box_width/2
        bar_box.y1 = margin + scroller_width/2 
        bar_box.x2 = bar_box.x1 + bar_width
        bar_box.y2 = bar_box.y1 + bar_height
        self.scrollbar_background.allocate(bar_box, flags)
        
        scroller_box=clutter.ActorBox()
        scroller_box.x1 = margin
        scroller_box.x2 = scroller_box.x1 + box_width
        if self.scroller_position >= box_height-scroller_width -margin:
            self.scroller_position = box_height-scroller_width -margin
        scroller_box.y1 = self.scroller_position 
        scroller_box.y2 = scroller_box.y1 + box_width
        self.scroller.allocate(scroller_box,flags)
                
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        children = (self.scrollbar_background,self.scroller)
        for child in children :
            func(child, data)
    
    def do_paint(self):
        children = (self.scrollbar_background,self.scroller)
        for child in children :
            child.paint()

    def do_pick(self, color):
        children = (self.scrollbar_background,self.scroller)
        for child in children :
            child.paint()

#main to test scrollbar
if __name__ == '__main__':

    stage = clutter.Stage()
    stage.connect('destroy',clutter.main_quit)

    scrollbar = Scrollbar()
    scrollbar.set_size(40,480)
    stage.add(scrollbar)

    stage.show()

    clutter.main() 
