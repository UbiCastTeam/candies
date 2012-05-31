#!/ur/bin/env python
# -*- coding: utf-8 -*-

import os
import gobject
import clutter
from container import BaseContainer

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
    __gsignals__ = {'scroll_position': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT])}
    
    def __init__(self, padding=8, position='center', bar_image_path=None, scroller_image_path=None, scroller_press_image_path=None, horizontal=False, reallocate=False, label=None, value=0, scale=None):
        clutter.Actor.__init__(self)
        self.padding = padding
        self.position = position
        self.reallocate = reallocate
        self.show_label = False
        self.scroller_position_percent = value
        self.height = 0
        self.last_event_y = None
        self.last_event_x = None
        self.h = horizontal
        self.flags = None
        self.box = None
        self.pointer_grabbed = False
        
        if bar_image_path != None and os.path.exists(bar_image_path):
            self.scrollbar_background = clutter.Texture()
            self.scrollbar_background.set_from_file(bar_image_path)
        else:
            self.scrollbar_background = clutter.Rectangle()
            self.scrollbar_background.set_color('LightBlue')
        self.scrollbar_background.set_parent(self)

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
        
        self.event_listener = clutter.Rectangle()
        self.event_listener.set_color('#00000000')
        self.event_listener.set_parent(self)
        self.event_listener.set_reactive(True)
        self.event_listener.connect('button-press-event', self.on_scroll_press)
        self.event_listener.connect('button-release-event', self.on_scroll_release)
        self.event_listener.connect('motion-event', self.on_scroll_move)
        self.event_listener.connect('scroll-event', self.on_mouse_scroll)
    
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
    
    def set_bar_image_path(self, path):
        if isinstance(self.scrollbar_background, clutter.Rectangle):
            self.scrollbar_background.unparent()
            self.scrollbar_background.destroy()
            self.scrollbar_background = clutter.Texture()
            self.scrollbar_background.set_parent(self)
        self.scrollbar_background.set_from_file(path)
    
    def set_scroller_image_path(self, path):
        if isinstance(self.scroller, clutter.Rectangle):
            self.scroller.unparent()
            self.scroller.destroy()
            self.scroller = clutter.Texture()
            self.scroller.set_parent(self)
        self.scroller.set_from_file(path)
    
    def on_mouse_scroll(self, source, event):
        current_pos = self.scroller_position_percent
        if event.direction == clutter.SCROLL_UP:
            if self.h:
                current_pos += 0.1
            else:
                current_pos -= 0.1
        else:
            if self.h:
                current_pos -= 0.1
            else:
                current_pos += 0.1
        self.set_scroller_progress_percent(current_pos)
    
    def on_scroll_press(self, source, event):
        clutter.grab_pointer(self.event_listener)
        self.pointer_grabbed = True
        self.last_event_y = event.y
        self.last_event_x = event.x
        self.set_progress_with_event(event)
        if self.scroller_press_image_path is not None:
            self.scroller.set_from_file(self.scroller_press_image_path)

    def on_scroll_release(self, source, event):
        clutter.ungrab_pointer()
        self.pointer_grabbed = False
        self.last_event_y = None
        self.last_event_x = None
        if self.scroller_press_image_path is not None and self.scroller_image_path is not None:
            self.scroller.set_from_file(self.scroller_image_path)

    def on_scroll_move(self, source, event):
        self.set_progress_with_event(event)
    
    def is_pointer_grabbed(self):
        return self.pointer_grabbed
    
    def set_progress_with_event(self, event):
        if self.h:
            if self.last_event_x is None: return
            self.last_event_x = event.x - self.get_transformed_position()[0] - self.padding - self.scroller_height/2
            position = self.last_event_x/(self.height - 2*self.padding - self.scroller_height)
            self.set_scroller_progress_percent(position)
        else:
            if self.last_event_y is None: return
            self.last_event_y = event.y - self.get_transformed_position()[1] - self.padding - self.scroller_height/2
            position = self.last_event_y/(self.height - 2*self.padding - self.scroller_height)
            self.set_scroller_progress_percent(position)

    def set_scroller_progress_percent(self, position):
        new_position = max(position, 0.0)
        new_position = min(new_position, 1.0)
        if new_position != self.scroller_position_percent:
            self.scroller_position_percent = new_position
            self.emit('scroll_position', self.scroller_position_percent)
            self.queue_relayout()
            if self.reallocate:
                self.do_allocate(self.box,self.flags)

    def get_scroller_position_percent(self):
        return self.scroller_position_percent

    def go_to_top(self):
        self.set_scroller_progress_percent(0)

    def go_to_bottom(self):
        self.set_scroller_progress_percent(1)

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
        
        listener_box = clutter.ActorBox(0, 0, box.x2 - box.x1, box.y2 - box.y1)
        self.event_listener.allocate(listener_box, flags)
        
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
        clutter.Actor.do_allocate(self, box, flags)

    def do_foreach(self, func, data=None):
        children = (self.scrollbar_background, self.scroller, self.event_listener)
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
        self.event_listener.paint()

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
        if hasattr(self, 'event_listener'):
            if self.event_listener is not None:
                self.event_listener.unparent()
                self.event_listener.destroy()
                self.event_listener = None
        if hasattr(self, 'scale_positions_list'):
            if self.scale_positions_list is not None:
                for child in self.scale_list:
                    if child is not None:
                        child.unparent()
                        child.destroy()
                        child = None
    
    def set_lock(self, lock):
        self.set_reactive(not lock)
        self.set_opacity(128 if lock else 255)


class Clipper(clutter.Actor, clutter.Container):
    '''
    Clipper class
        need clutter.Actor
        variables :
            .actor : clutter.Actor object to move
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
    
    def get_actor(self):
        return self.actor
    
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


class CoglClipper(BaseContainer):
    '''
    CoglClipper class
        This class is a test. It has the same behaviour than clipper class.
        This class will not be used because cogl is to slow for this case.
    '''
    __gtype_name__ = 'CoglClipper'
    
    def __init__(self, actor=None, expand=False):
        BaseContainer.__init__(self)
        self._width = 0
        self._height = 0
        self.clipper_position = 0
        self.expand = expand
        self.actor = actor
        if self.actor is not None:
            self.set_actor(actor)
    
    def set_actor(self, actor):
        if self.actor is not None:
            self.remove_actor()
        self.actor = actor
        self._add(actor)
    
    def remove_actor(self):
        if self.actor is not None:
            self._remove(self.actor)
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
        self._width = box.x2 - box.x1
        self._height = box.y2 - box.y1
        if self.actor:
            actor_width, actor_height = self.actor.get_preferred_size()[2:]
            position = 0 - int(self.clipper_position * (actor_height - self._height))
            if self.expand:
                objbox = clutter.ActorBox(0, position, self._width, position + actor_height)
            else:
                objbox = clutter.ActorBox(0, position, actor_width, position + actor_height)
            self.actor.allocate(objbox, flags)
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_paint(self):
        # Draw a rectangle to cut animation
        clutter.cogl.path_rectangle(0, 0, self._width, self._height)
        clutter.cogl.path_close()
        # Start the clip
        clutter.cogl.clip_push_from_path()
        
        if self.actor:
            self.actor.paint()

        # Finish the clip
        clutter.cogl.clip_pop()


#main to test scrollbar
if __name__ == '__main__':

    stage = clutter.Stage()
    stage.connect('destroy',clutter.main_quit)

    scrollbar = Scrollbar()
    scrollbar.set_size(40, 480)
    scrollbar.set_position(600, 0)
    stage.add(scrollbar)

    label = clutter.Text()
    label.set_text('test')
    
    image = clutter.Texture('test.jpg')
    
    clipper = Clipper(image)
    clipper.set_size(600, 480)
    clipper.set_position(0, 0)
    scrollbar.connect('scroll_position', clipper.callback_position)
    stage.add(clipper)
    
    stage.show()
    clutter.main()






