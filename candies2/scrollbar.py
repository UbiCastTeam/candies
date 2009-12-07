#!/ur/bin/env python
# -*- coding: utf-8 -*-

''' 
Scrollbar and Clipper class
author : flavie
date : dec 3 2009
version : 0
'''

import sys
import operator
import gobject
import clutter


class Scrollbar(clutter.Actor, clutter.Container):
    '''
    Scrollbar class :
        variables :
            .scrollbar_background : clutter.Rectangle
            .scroller : clutter.Rectangle
            .scroller_position : float
        functions :
            .on_scroll_press : drag scroller
            .on_scroll_release : drop scroller
            .on_scroll_move : move scroller
            .do_allocate : draw scrollbar, scroller and emit the position of scroller
            .do_foreach
            .do_paint
            .do_pick
    '''
    __gtype_name__ = 'Scrollbar'
    __gsignals__ = {'scroll_position' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT])}
    
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
        self.last_event_y = event.y - self.get_transformed_position()[1]
        self.scroller_position = event.y - self.get_transformed_position()[1]
        self.queue_relayout()
        
    def do_allocate(self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
        margin = box_width/8
        
        scroller_width = box_width - 2*margin        
        bar_width = box_width/4
        bar_height = box_height - 2*margin - scroller_width      
        
      
        bar_box = clutter.ActorBox()  
        bar_box.x1 = box_width/2 -bar_width/2
        bar_box.y1 = margin + scroller_width/2 
        bar_box.x2 = bar_box.x1 + bar_width
        bar_box.y2 = bar_box.y1 + bar_height
        self.scrollbar_background.allocate(bar_box, flags)
        
        scroller_box=clutter.ActorBox()
        scroller_box.x1 = margin 
        scroller_box.x2 = scroller_box.x1 + scroller_width
        if self.scroller_position >= box_height-scroller_width :
            self.scroller_position = box_height-scroller_width  
        scroll_position_percent=(self.scroller_position)/(box_height-scroller_width)
        if self.scroller_position <= scroller_width/2 :
            self.scroller_position = scroller_width/2
            scroll_position_percent =0 
        scroller_box.y1 = self.scroller_position - scroller_width/2 + margin
        scroller_box.y2 = scroller_box.y1 + scroller_width  
        self.scroller.allocate(scroller_box,flags)
        
        self.emit("scroll_position",scroll_position_percent)
                
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


class Clipper (clutter.Actor, clutter.Container):
    '''
    Clipper class
        need clutter.Actor and gsignals
        variables :
            .actor : clutter.Actor object to move
            .clipper_position = float position of the clipper
        functions :
            .callback_position : need float which indicate how to move clipper
            .do_allocate : move clipper
            .do_foreach
            .do_paint
            .do_pick 
    '''
    __gtype_name__ = 'Clipper'
    
    def __init__(self,actor):
        clutter.Actor.__init__(self)
        self.actor = actor
        self.actor.set_parent(self)
        self.clipper_position = 0
        
    def callback_position(self,source,position):
        self.clipper_position=position
        self.queue_relayout()
        
    def do_allocate (self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
        
        position = self.clipper_position * (self.actor.get_preferred_size()[3]-box_height) 
        self.actor.set_anchor_point(0,position)
        self.actor.set_clip(0,position,box_width,box_height)
        self.actor.allocate_preferred_size(flags)
        clutter.Actor.do_allocate(self, box, flags)
        
    def do_foreach(self, func, data=None):
        children = (self.actor,)
        for child in children :
            func(child, data)
    
    def do_paint(self):
        children = (self.actor,)
        for child in children :
            child.paint()

    def do_pick(self, color):
        children = (self.actor,)
        for child in children :
            child.paint()


#main to test scrollbar
if __name__ == '__main__':

    stage = clutter.Stage()
    stage.connect('destroy',clutter.main_quit)

    scrollbar = Scrollbar()
    scrollbar.set_size(40,480)
    stage.add(scrollbar)

    image=clutter.Texture('grr.jpg')
    
    label = clutter.Text()
    auto_source = open('scrollbar.py')
    label.set_text(auto_source.read())
    auto_source.close()
    
    clipper = Clipper(image)
    clipper.set_size(600,400)
    clipper.set_position(100,40)
    scrollbar.connect('scroll_position',clipper.callback_position)
    stage.add(clipper)
    
    stage.show()

    clutter.main() 
