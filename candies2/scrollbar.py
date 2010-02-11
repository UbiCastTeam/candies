#!/ur/bin/env python
# -*- coding: utf-8 -*-

''' 
Scrollbar and Clipper class
author : flavie
date : dec 3 2009
version : 0
'''

import os
import sys
import operator
import gobject
import clutter

class Scrollbar(clutter.Actor, clutter.Container):
    '''
    Scrollbar class :
        variables :
            .scrollbar_background : clutter.Rectangle or clutter.Texture if bar_image_path set
            .scroller : clutter.Rectangle or clutter.Texture if scroller_image_path set
            .scroller_position : float
            .border : float
            .thin_scroller : boolean
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
    
    def __init__(self, border=8.0, thin_scroller=True, bar_image_path=None, scroller_image_path=None,h=False,reallocate=False):
        clutter.Actor.__init__(self)
        self.border = border
        self.thin_scroller = thin_scroller
        self.reallocate=reallocate
        
        if bar_image_path != None and os.path.exists(bar_image_path):
            self.scrollbar_background = clutter.Texture()
            self.scrollbar_background.set_from_file(bar_image_path)
        else:
            self.scrollbar_background = clutter.Rectangle()
            self.scrollbar_background.set_color('LightBlue')
        self.scrollbar_background.set_parent(self)
        
        if scroller_image_path != None and os.path.exists(scroller_image_path):
            self.scroller = clutter.Texture()
            self.scroller.set_from_file(scroller_image_path)
        else:
            self.scroller = clutter.Rectangle()
            self.scroller.set_color('Gray')
        self.scroller.set_parent(self)
        self.scroller.set_reactive(True)
        self.scroller.connect('button-press-event', self.on_scroll_press)
        self.scroller.connect('button-release-event', self.on_scroll_release)
        self.scroller.connect('motion-event', self.on_scroll_move)
        self.scroller_position = 0
        self.height=0
        self.last_event_y = None
        self.last_event_x = None
        self.h=h
    
    def on_scroll_press(self, source, event):
        self.last_event_y = event.y
        self.last_event_x = event.x
        return True 
        
    def on_scroll_release(self, source, event):
        clutter.ungrab_pointer()
        self.last_event_y = None
        self.last_event_x = None
        
    def on_scroll_move(self, source, event):
        if self.h == False : 
            if self.last_event_y is None: return
            clutter.grab_pointer(self.scroller)
            self.last_event_y = event.y - self.get_transformed_position()[1] - self.border
            self.scroller_position = event.y - self.get_transformed_position()[1] - self.border
        else : 
            if self.last_event_x is None: return
            clutter.grab_pointer(self.scroller)
            self.last_event_x = event.x - self.get_transformed_position()[0] - self.border
            self.scroller_position = event.x - self.get_transformed_position()[0] - self.border
        self.queue_relayout()
        
        if self.reallocate : 
            box = clutter.ActorBox()
            box.x1 = self.get_allocation_box()[0]
            box.y1 = self.get_allocation_box()[1]
            box.x2 = self.get_allocation_box()[2]
            box.y2 = self.get_allocation_box()[3]
            flags = self.get_flags()
            self.do_allocate(box,0)
        
    def go_to_top(self):
        self.scroller_position = 0
        self.queue_relayout()
    
    def do_get_preferred_height(self, for_width):
        if self.h == False :
            return 200, 200
        else :
            return 80,80
    
    def do_get_preferred_width(self, for_height):
        if self.h == False :
            return 80, 80
        else :
            return 200,200
    
    def do_allocate(self, box, flags):
        if self.h == False : 
            box_width = box.x2 - box.x1
            self.height = box_height = box.y2 - box.y1
        else :
            box_width = box.y2 - box.y1
            self.height = box_height = box.x2 - box.x1
            
        scroller_width = box_width - 2*self.border
        self.scroller_height=scroller_height = scroller_width
        if self.thin_scroller:
            bar_width = box_width/4
        else:
            bar_width = box_width - 2*self.border
        bar_height = box_height - 2*self.border - scroller_height + bar_width
            
        bar_box = clutter.ActorBox()  
        if self.h == False :
            bar_box.x1 = box_width/2 - bar_width/2
            bar_box.y1 = box_height/2 - bar_height/2 
            bar_box.x2 = bar_box.x1 + bar_width
            bar_box.y2 = bar_box.y1 + bar_height
        else :
            bar_box.y1 = box_width/2 - bar_width/2
            bar_box.x1 = box_height/2 - bar_height/2 
            bar_box.y2 = bar_box.x1 + bar_width
            bar_box.x2 = bar_box.y1 + bar_height
        self.scrollbar_background.allocate(bar_box, flags)
            
        scroller_box = clutter.ActorBox()
        if self.h == False :
            scroller_box.x1 = self.border 
            scroller_box.x2 = scroller_box.x1 + scroller_width
        else :
            scroller_box.y1 = self.border 
            scroller_box.y2 = scroller_box.y1 + scroller_width
            
        self.scroller_position -= scroller_height/2
        if self.scroller_position >= box_height - 2*self.border - scroller_height:
            self.scroller_position = box_height - 2*self.border - scroller_height
        if self.scroller_position <= 0:
            self.scroller_position = 0
            scroll_position_percent = 0
        if self.h == False :
            scroller_box.y1 = self.border + self.scroller_position
            scroller_box.y2 = scroller_box.y1 + scroller_height  
        else :
            scroller_box.x1 = self.border + self.scroller_position
            scroller_box.x2 = scroller_box.x1 + scroller_height
        self.scroller.allocate(scroller_box,flags)
        scroll_position_percent = (self.scroller_position)/(box_height - 2*self.border - scroller_height)
        self.emit("scroll_position", scroll_position_percent)
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        children = (self.scrollbar_background, self.scroller)
        for child in children :
            func(child, data)
    
    def do_paint(self):
        children = (self.scrollbar_background, self.scroller)
        for child in children :
            child.paint()

    def do_pick(self, color):
        children = (self.scrollbar_background, self.scroller)
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
    
    def __init__(self, actor, expand=False):
        clutter.Actor.__init__(self)
        self.actor = actor
        self.actor.set_parent(self)
        self.clipper_position = 0
        self.expand = expand
        
    def callback_position(self, source, position):
        self.clipper_position = position
        self.queue_relayout()
        
    def do_allocate (self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
        
        if self.expand == True:
            position = self.clipper_position * (self.actor.get_preferred_size()[3] - box_height) 
            self.actor.set_anchor_point(0, int(position))
            self.actor.set_clip(0, int(position), box_width, box_height)
            objbox = clutter.ActorBox()
            objbox.x1 = 0
            objbox.y1 = 0
            objbox.x2 = box_width
            objbox.y2 = box_height
            self.actor.allocate(objbox, flags)
            clutter.Actor.do_allocate(self, box, flags)
        else:
            position = self.clipper_position * (self.actor.get_preferred_size()[3] - box_height) 
            self.actor.set_anchor_point(0, int(position))
            self.actor.set_clip(0, int(position), box_width, box_height)
            self.actor.allocate_preferred_size(flags)
            clutter.Actor.do_allocate(self, box, flags)
        
    def do_foreach(self, func, data=None):
        func(self.actor, data)
    
    def do_paint(self):
        self.actor.paint()

    def do_pick(self, color):
        self.actor.paint()


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
