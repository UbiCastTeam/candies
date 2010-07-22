#!/ur/bin/env python
# -*- coding: utf-8 -*-

''' 
Scrollbar and Clipper class
author : flavie
date : dec 3 2009
version : 0
'''

import os
import gobject
import clutter

class Scrollbar(clutter.Actor, clutter.Container):
    '''
    Scrollbar class :
        variables :
            .scrollbar_background : clutter.Rectangle or clutter.Texture if bar_image_path set
            .scroller : clutter.Rectangle or clutter.Texture if scroller_image_path set
            .scroller_position : float
            .padding : float
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
    
    def __init__(self, padding=8, position = 'center', bar_image_path=None, scroller_image_path=None, scroller_press_image_path=None, horizontal=False, reallocate=False, label=None, value = 0, scale = None):
        clutter.Actor.__init__(self)
        self.padding = padding
        self.position = position
        self.reallocate=reallocate
        self.show_label=False

        if bar_image_path != None and os.path.exists(bar_image_path):
            self.scrollbar_background = clutter.Texture()
            self.scrollbar_background.set_from_file(bar_image_path)
        else:
            self.scrollbar_background = clutter.Rectangle()
            self.scrollbar_background.set_color('LightBlue')
        self.scrollbar_background.set_parent(self)
        self.scrollbar_background.set_reactive(True)
        self.scrollbar_background.connect('scroll-event', self.on_mouse_scroll)

        if label != None :
            self.label = clutter.Text()
            self.label.set_color('#FFFFFFFF')
            self.label.set_text(label)
            self.label.set_parent(self)
            self.show_label = True

        if scroller_image_path != None and os.path.exists(scroller_image_path):
            self.scroller = clutter.Texture()
            self.scroller.set_from_file(scroller_image_path)
            self.scroller_image_path = scroller_image_path
        else:
            self.scroller = clutter.Rectangle()
            self.scroller.set_color('Gray')
            self.scroller_image_path = None
        if scroller_press_image_path != None and os.path.exists(scroller_press_image_path):
            self.scroller_press_image_path = scroller_press_image_path
        else :
            self.scroller_press_image_path = None
        self.scroller.set_parent(self)
        self.scroller.set_reactive(True)
        self.scroller.connect('button-press-event', self.on_scroll_press)
        self.scroller.connect('button-release-event', self.on_scroll_release)
        self.scroller.connect('motion-event', self.on_scroll_move)
        self.scroller.connect('scroll-event', self.on_mouse_scroll)

        self.scroller_position_percent = value
        self.height = 0
        self.last_event_y = None
        self.last_event_x = None
        self.h = horizontal
        self.flags = None
        self.box = None
        self.scale_positions_list = None
        self.scale_list = None

        self.scale_positions_percent = scale
        if scale is not None :
            self.scale_list = list()
            for position in scale :
                rect = clutter.Rectangle()
                rect.set_color('#FFFFFF30')
                rect.set_parent(self)
                self.scale_list.append(rect)

    def on_mouse_scroll(self, source, event):
        current_pos = self.get_scroller_position_percent()
        if event.direction == clutter.SCROLL_UP:
            current_pos -= 0.1
        else:
            current_pos += 0.1
        current_pos = max(current_pos, 0.0)
        current_pos = min(current_pos, 1.0)
        if current_pos != self.get_scroller_position_percent():
            self.set_scroller_position_percent(current_pos)
    
    def on_scroll_press(self, source, event):
        self.last_event_y = event.y
        self.last_event_x = event.x
        if self.scroller_press_image_path is not None :
            self.scroller.set_from_file(self.scroller_press_image_path)
        return True

    def on_scroll_release(self, source, event):
        clutter.ungrab_pointer()
        self.last_event_y = None
        self.last_event_x = None
        if self.scroller_press_image_path is not None and self.scroller_image_path is not None:
            self.scroller.set_from_file( self.scroller_image_path)

    def on_scroll_move(self, source, event):
        if self.h:
            if self.last_event_x is None: return
            clutter.grab_pointer(self.scroller)
            self.last_event_x = event.x - self.get_transformed_position()[0] - self.padding - self.scroller_height/2
            self.scroller_position_percent = self.last_event_x/(self.height - 2*self.padding - self.scroller_height)
        else:
            if self.last_event_y is None: return
            clutter.grab_pointer(self.scroller)
            self.last_event_y = event.y - self.get_transformed_position()[1] - self.padding - self.scroller_height/2
            self.scroller_position_percent = self.last_event_y/(self.height - 2*self.padding - self.scroller_height)
        self.queue_relayout()

        if self.reallocate :
            self.do_allocate(self.box,self.flags)

    def set_scroller_position_percent(self, position):
        self.scroller_position_percent = position
        self.queue_relayout()

    def get_scroller_position_percent(self):
        value = self.scroller_position_percent
        return value

    def go_to_top(self):
        self.scroller_position_percent = 0
        self.queue_relayout()

    def do_get_preferred_height(self, for_width):
        if self.h:
            return 80, 80
        else:
            return 200, 200

    def do_get_preferred_width(self, for_height):
        if self.h:
            return 200,200
        else:
            return 80, 80

    def do_allocate(self, box, flags):
        self.box = box
        self.flags = flags
        if self.h:
            box_width = box.y2 - box.y1
            self.height = box_height = box.x2 - box.x1
        else:
            box_width = box.x2 - box.x1
            self.height = box_height = box.y2 - box.y1

        scroller_width = box_width - 2*self.padding
        self.scroller_height=scroller_height = scroller_width
        if not self.h and self.scrollbar_background.get_preferred_size()[2] > 0 and self.position == 'center':
            bar_width = self.scrollbar_background.get_preferred_size()[2]
        elif self.h and self.scrollbar_background.get_preferred_size()[3] > 0 and self.position == 'center':
            bar_width = self.scrollbar_background.get_preferred_size()[3]
        else :
            bar_width = box_width/4
        bar_height = box_height - 2*self.padding - scroller_height + bar_width

        bar_box = clutter.ActorBox()
        if self.h:
            if self.position == 'center' :
                bar_box.y1 = box_width/2 - bar_width/2
            elif self.position == 'top' :
                bar_box.y1 = box.y1 + self.padding
            else :
                bar_box.y1 = box_width - bar_width
            bar_box.x1 = box_height/2 - bar_height/2 
            bar_box.y2 = bar_box.y1 + bar_width
            bar_box.x2 = bar_box.x1 + bar_height
        else:
            if self.position == 'center' :
                bar_box.x1 = box_width/2 - bar_width/2
            elif self.position == 'top' :
                bar_box.x1 = box.x1 + self.padding
            else :
                bar_box.x1 = box_width - bar_width
            bar_box.y1 = box_height/2 - bar_height/2
            bar_box.x2 = bar_box.x1 + bar_width
            bar_box.y2 = bar_box.y1 + bar_height
        if not box_width == 0 and not box_height == 0:
            self.scrollbar_background.allocate(bar_box, flags)

        if self.scale_list is not None :
            for i, item in enumerate(self.scale_list) :
                scale_box = clutter.ActorBox()
                position = self.scale_positions_percent[i]*(self.height-2*self.padding-self.scroller_height)+self.scroller_height/2 + self.padding + 1
                scale_box.x1 = position
                scale_box.y1 = bar_box.y1
                scale_box.x2 = scale_box.x1 + 2
                scale_box.y2 = bar_box.y2
                item.allocate(scale_box, flags)

        if self.show_label :
            label_box = clutter.ActorBox()
            label_box.x1 = bar_box.x1 + bar_width/2
            label_box.x2 = bar_box.x2
            label_box.y1 = bar_box.y1
            label_box.y2 = label_box.y1 + 20
            self.label.allocate(label_box,flags)

        scroller_box = clutter.ActorBox()
        if self.h == False :
            scroller_box.x1 = self.padding
            scroller_box.x2 = scroller_box.x1 + scroller_width
        else :
            scroller_box.y1 = self.padding
            if self.position == 'top' :
                scroller_box.y1 += self.padding
            scroller_box.y2 = scroller_box.y1 + scroller_width
        scroller_position = self.scroller_position_percent * (box_height - 2*self.padding - scroller_height)
#        self.scroller_position -= scroller_height/2
        if scroller_position >= box_height - 2*self.padding - scroller_height:
            scroller_position = box_height - 2*self.padding - scroller_height
        if scroller_position <= 0:
            scroller_position = 0
            scroll_position_percent = 0
        if self.h == False :
            scroller_box.y1 = self.padding + scroller_position
            scroller_box.y2 = scroller_box.y1 + scroller_height
        else :
            scroller_box.x1 = self.padding + scroller_position
            scroller_box.x2 = scroller_box.x1 + scroller_height
        self.scroller.allocate(scroller_box,flags)
        self.scroller_position_percent = (scroller_position)/(box_height - 2*self.padding - scroller_height)
        self.emit("scroll_position", self.scroller_position_percent)
        clutter.Actor.do_allocate(self, box, flags)

    def do_foreach(self, func, data=None):
        children = (self.scrollbar_background, self.scroller)
        for child in children :
            func(child, data)
        if self.show_label:
            func(self.label,data)
        if self.scale_positions_percent is not None :
            for scale in self.scale_list :
                func(scale, data)

    def do_paint(self):
        self.scrollbar_background.paint()
        if self.scale_positions_percent is not None :
            for scale in self.scale_list :
                scale.paint()
        if self.show_label:
            self.label.paint()
        self.scroller.paint()

    def do_pick(self, color):
        self.scrollbar_background.paint()
        if self.show_label:
            self.label.paint()
        self.scroller.paint()
        if self.scale_positions_percent is not None :
            for scale in self.scale_list :
                scale.paint()

    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'scrollbar_background'):
            if self.scrollbar_background is not None:
                self.scrollbar_background.unparent()
                self.scrollbar_background.destroy()
                self.scrollbar_background = None
        if hasattr(self, 'label'):
            if self.label is not None:
                self.label.unparent()
                self.label.destroy()
                self.label = None
        if hasattr(self, 'scroller'):
            if self.scroller is not None:
                self.scroller.unparent()
                self.scroller.destroy()
                self.scroller = None
        if self.scale_positions_list is not None :
            for child in self.scale_list :
                if child is not None :
                    child.unparent()
                    child.destroy()
                    child = None

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
    
    def __init__(self, actor=None, expand=False):
        clutter.Actor.__init__(self)
        self.actor = actor
        if self.actor is not None:
            self.actor.set_parent(self)
        self.clipper_position = 0
        self.expand = expand
    
    def set_actor(self, actor):
        self.remove_actor()
        self.actor = actor
        self.actor.set_parent(self)
        self.queue_relayout()
    
    def remove_actor(self):
        if self.actor is not None:
            self.actor.unparent()
        self.actor = None
        
    def callback_position(self, source, position):
        self.clipper_position = position
        self.queue_relayout()
    
    def do_get_preferred_width(self, for_height):
        if self.actor is not None:
            preferred_width = self.actor.get_preferred_width(for_height)[1]
        else:
            preferred_width = 0
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        if self.actor is not None:
            preferred_height = self.actor.get_preferred_height(for_width)[1]
        else:
            preferred_height = 0
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
        
        if self.actor is not None:
            if self.expand == True:
                position = int(self.clipper_position * (self.actor.get_preferred_size()[3] - box_height))
                self.actor.set_anchor_point(0, position)
                self.actor.set_clip(0, position, box_width, box_height)
                objbox = clutter.ActorBox(0, 0, box_width, box_height)
                self.actor.allocate(objbox, flags)
            else:
                position = int(self.clipper_position * (self.actor.get_preferred_size()[3] - box_height))
                self.actor.set_anchor_point(0, position)
                self.actor.set_clip(0, position, box_width, box_height)
                self.actor.allocate_preferred_size(flags)
        
        clutter.Actor.do_allocate(self, box, flags)
        
    def do_foreach(self, func, data=None):
        if self.actor is not None:
            func(self.actor, data)
    
    def do_paint(self):
        if self.actor is not None:
            self.actor.paint()

    def do_pick(self, color):
        if self.actor is not None:
            self.actor.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'actor'):
            if self.actor is not None:
                self.actor.unparent()
                self.actor.destroy()
                self.actor = None


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
