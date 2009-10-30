# -*- coding: utf-8 -*-
import gobject
import clutter
from roundrect import RoundRectangle

class ClassicButton(clutter.Actor, clutter.Container):
    
    __gtype_name__ = 'ClassicButton'
    def __init__(self, label):
        clutter.Actor.__init__(self)
        self.text = label
        
        self.label = clutter.Text()
        self.label.set_parent(self)
        
        self.rect = RoundRectangle()
        self.rect.set_color('LightGray')
        self.rect.set_border_color('Gray')
        self.rect.set_border_width(3)
        self.rect.props.radius = 10
        self.rect.set_parent(self)
    
    def do_get_preferred_size(self):
        t = clutter.Text()
        t.set_font_name(self.label.get_font_name())
        t.set_text('…')
        min = t.get_preferred_size()[:2]
        t.set_text(self.text)
        nat = t.get_preferred_size()[2:]
        return min[0] + 10, min[1] + 10, nat[0] + 5, nat[1] * 2
    
    def do_get_preferred_width(self, for_height):
        preferred = self.do_get_preferred_size()
        return preferred[0], preferred[2]
    
    def do_get_preferred_height(self, for_width):
        min, nat = self.label.get_preferred_height(for_width)
        return min, nat * 2
    
    def _wrap_label(self, min, max, width):
        mid = (min + max) / 2
        self.label.set_text(self.text[:mid] + '…')
        if mid == min or self.label.get_preferred_size()[2] == width:
            return
        if self.label.get_preferred_size()[2] > width:
            self._wrap_label(min, mid, width)
        else:
            self._wrap_label(mid, max, width)
    
    def do_allocate(self, box, flags):
        btn_width, btn_height = self.get_preferred_size()[2:]
        #print btn_width, 'x', btn_height
        
        cbox = clutter.ActorBox()
        cbox.x1 = 0
        cbox.y1 = 0
        cbox.x2 = btn_width
        cbox.y2 = btn_height
        self.rect.allocate(cbox, flags)
        
        self.label.set_text(self.text)
        if self.label.get_preferred_size()[2] > btn_width - 5:
            self._wrap_label(0, len(self.text), btn_width - 5)
        lbl_width, lbl_height = self.label.get_preferred_size()[2:]
        cbox = clutter.ActorBox()
        cbox.x1 = (btn_width - lbl_width) / 2
        cbox.y1 = (btn_height - lbl_height) / 2
        cbox.x2 = box.x1 + lbl_width
        cbox.y2 = box.y1 + lbl_height
        self.label.allocate(cbox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        func(self.rect, data)
        func(self.label, data)
    
    def do_paint(self):
        self.rect.paint()
        self.label.paint()

if __name__ == '__main__':
    from flowbox import FlowBox
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)
    
    # Main flowbox
    box0 = FlowBox()
    box0.set_size(640, 480)
    
    # Invisible rectangle for top margin
    r = clutter.Rectangle()
    r.set_size(640, 1)
    box0.add(r)
    
    # Button at natural size
    b = ClassicButton('Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt.')
    b.set_size(*b.get_preferred_size()[2:])
    box0.add(b)
    
    # Button larger than natural size
    b = ClassicButton('Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt.')
    b.set_size(630, 50)
    box0.add(b)
    
    # Intermediate flowbox to force line wrapping
    box1 = FlowBox()
    box1.set_size(640, 50)
    box0.add(box1)
    
    # Button fitter than natural size
    b = ClassicButton('Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.')
    b.set_size(420, 50)
    box1.add(b)
    
    # Button more fitter than natural size
    b = ClassicButton('Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.')
    b.set_size(210, 50)
    box0.add(b)
    
    # Intermediate flowbox to force line wrapping
    box2 = FlowBox()
    box2.set_size(640, 50)
    box0.add(box2)
    
    # Button at minimal size (just suspension marks)
    b = ClassicButton('Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt.')
    b.set_size(*b.get_preferred_size()[:2])
    box2.add(b)
    
    # Invisible rectangle for bottom margin
    r = clutter.Rectangle()
    r.set_size(640, 1)
    box0.add(r)
    
    stage.add(box0)
    stage.show()

    clutter.main()