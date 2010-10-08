#!/ur/bin/env python
# -*- coding: utf-8 -*-

import clutter
from scrollbar import Scrollbar, Clipper
from box import HBox

# auto scroll panel
#------------------------------------------------------------------------------------------
class AutoScrollPanel(HBox):
    def __init__(self, actor=None, padding=0, spacing=0):
        HBox.__init__(self, spacing=spacing, padding=padding)
        self.connect('notify::visible', self.on_show_scrolled)
        self.contents_have_been_shown = False
        self._max_width = 0
        self._max_height = 0
        self._actor = actor
        if self._actor:
            self.add_element(self._actor, 'actor', expand=True, resizable=1.0)
        
        self._scrollbar = Scrollbar()
        self._clipper = Clipper(expand=True)
        self._scrollbar.connect('scroll_position', self._clipper.callback_position)

    def on_show_scrolled(self, panel, event):
        if not self.contents_have_been_shown:
            self.contents_have_been_shown = True
        else:
            self._actor.props.visible = self.props.visible

    def get_actor(self):
        return self._actor
    
    def set_actor(self, element):
        if self._actor is not None:
            self.remove_all_elements()
            self._actor.set_anchor_point(0, 0)
            self._actor.remove_clip()
            self._scrollbar.go_to_top()
        self._actor = element
        self.add_element(self._actor, 'actor', expand=True, resizable=1.0)
    
    def set_bar_image_path(self, path):
        self._scrollbar.set_bar_image_path(path)
    
    def set_scroller_image_path(self, path):
        self._scrollbar.set_scroller_image_path(path)
    
    def go_to_top(self):
        self._scrollbar.go_to_top()
    
    # Function to check and add a scrollbar if needed
    def check_scrollbar(self, relayout=True):
        #print '---------------------------', self._max_height
        if self._max_height > 0 and self._actor is not None:
            if self._max_width > 0:
                for_width = self._max_width
            else:
                for_width = -1
            preferred_height = self._actor.get_preferred_height(for_width=for_width)[1]
            #print '--------------------------- preferred_height', self._max_height, preferred_height
            if preferred_height > self._max_height:
                #print '--------------------------- add scrollbar'
                if self.get_by_name('scrollbar') is None:
                    #print '--------------------------- add scrollbar confirm'
                    self.remove_all_elements()
                    self._clipper.set_actor(self._actor)
                    self.add_element(self._clipper, 'clipper', expand=True, resizable=1.0)
                    self.add_element(self._scrollbar, 'scrollbar', expand=True)
            else:
                if self.get_by_name('actor') is None:
                    self.remove_all_elements()
                    self._clipper.remove_actor()
                    self._actor.set_anchor_point(0, 0)
                    self._actor.remove_clip()
                    self.go_to_top()
                    self.add_element(self._actor, 'actor', expand=True, resizable=1.0)
        if relayout:
            self.queue_relayout()
    
    def do_allocate(self, box, flags):
        new_width = box.x2 - box.x1
        new_height = box.y2 - box.y1
        #print '--------------------------- allocate', new_width, new_height
        if new_width != self._max_width or new_height != self._max_height:
            self._max_width = new_width
            self._max_height = new_height
            #print '--------------------------- max', self._max_width, self._max_height
            self.check_scrollbar(relayout=False)
        HBox.do_allocate(self, box, flags)

