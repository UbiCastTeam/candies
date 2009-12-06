# -*- coding: utf-8 -*-
import sys
import gobject
import clutter
from roundrect import RoundRectangle

class ClassicButton(clutter.Actor, clutter.Container):
    __gtype_name__ = 'ClassicButton'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'font_color' : (
            str, 'font color', 'Font color', None, gobject.PARAM_READWRITE
        ),
        'border_color': (
            str, 'border color', 'Border color', None, gobject.PARAM_READWRITE
        ),
        'border_width' : (
            gobject.TYPE_FLOAT, 'border width', 'Border width',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
    }
    default_color = 'LightGray'
    default_border_color = 'Gray'
    
    def __init__(self, label, stretch=False, border=6.0):
        clutter.Actor.__init__(self)
        self.text = label
        self.is_stretch = stretch
        self.border = border
        
        self.label = clutter.Text()
        self.label.set_parent(self)
        
        self.rect = RoundRectangle()
        self.rect.set_color(self.default_color)
        self.rect.set_border_color(self.default_border_color)
        self.rect.set_border_width(3)
        self.rect.props.radius = 10
        self.rect.set_parent(self)
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self.rect.props.color = value
        elif pspec.name == 'font-color':
            self.label.props.color = clutter.color_from_string(value)
        elif pspec.name == 'border-color':
            self.rect.props.border_color = value
        elif pspec.name == 'border-width':
            self.rect.props.border_width = value
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self.rect.props.color
        elif pspec.name == 'font-color':
            return self.label.props.color
        elif pspec.name == 'border-color':
            return self.rect.props.border_color
        elif pspec.name == 'border-width':
            return self.rect.props.border_width
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def do_get_preferred_width(self, for_height):
        t = clutter.Text()
        t.set_font_name(self.label.get_font_name())
        t.set_text('…')
        min = t.get_preferred_size()[0]
        t.set_text(self.text)
        nat = t.get_preferred_size()[2]
        return min + 2*self.border, nat + 2*self.border
    
    def do_get_preferred_height(self, for_width):
        min, nat = self.label.get_preferred_height(for_width)
        return min + 2*self.border, nat + 2*self.border
    
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
        btn_width = box.x2 - box.x1
        btn_height = box.y2 - box.y1
        inner_width = btn_width - 2*self.border
        inner_height = btn_height - 2*self.border
        #btn_width, btn_height = self.get_preferred_size()[2:]
        #print btn_width, 'x', btn_height
        
        cbox = clutter.ActorBox()
        cbox.x1 = 0
        cbox.y1 = 0
        cbox.x2 = btn_width
        cbox.y2 = btn_height
        self.rect.allocate(cbox, flags)
        
        self.label.set_text(self.text)
        if self.label.get_preferred_size()[2] > inner_width:
            self._wrap_label(0, len(self.text), inner_width)
        elif self.is_stretch:
            from text import StretchText
            lbl = StretchText()
            lbl.set_text(self.text)
            fontface = self.label.get_font_name()
            lbl.set_font_name(fontface)
            fontsize = lbl.get_preferred_fontsize(inner_width, inner_height)
            fontface = fontface[:fontface.rindex(' ')]
            self.label.set_font_name('%s %s' %(fontface, fontsize))
        lbl_width = self.label.get_preferred_size()[2]
        lbl_height = self.label.get_preferred_size()[3]
        cbox = clutter.ActorBox()
        cbox.x1 = int(self.border + (inner_width - lbl_width) / 2)
        cbox.y1 = int(self.border + (inner_height - lbl_height) / 2)
        cbox.x2 = int(cbox.x1 + lbl_width)
        cbox.y2 = int(cbox.y1 + lbl_height)
        self.label.allocate(cbox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        func(self.rect, data)
        func(self.label, data)
    
    def do_paint(self):
        self.rect.paint()
        self.label.paint()

gobject.type_register(ClassicButton)

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
    
    # Testing stretch buttons
    b = ClassicButton('A', stretch=True)
    b.set_size(15, 15)
    b.set_position(5, 450)
    stage.add(b)
    
    b = ClassicButton('B', stretch=True)
    b.set_size(25, 25)
    b.set_position(50, 425)
    stage.add(b)
    
    b = ClassicButton('C', stretch=True)
    b.props.font_color = 'Yellow'
    b.set_size(50, 50)
    b.set_position(125, 375)
    stage.add(b)
    
    b = ClassicButton('D', stretch=True)
    b.props.border_width = 10
    b.props.border_color = 'Green'
    b.set_size(100, 100)
    b.set_position(250, 325)
    stage.add(b)
    
    b = ClassicButton('E', stretch=True)
    b.props.color = 'Pink'
    b.set_size(200, 200)
    b.set_position(425, 275)
    stage.add(b)
    
    stage.add(box0)
    stage.show()

    clutter.main()
