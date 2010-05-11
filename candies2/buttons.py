#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gobject
import clutter
from roundrect import RoundRectangle, OutlinedRoundRectangle

class ClassicButton(clutter.Actor, clutter.Container):
    __gtype_name__ = 'ClassicButton'
    __gproperties__ = {
        'text' : (
            str, 'text', 'Text', None, gobject.PARAM_READWRITE
        ),
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
    
    def __init__(self, label, stretch=False, border=6.0, light_path=None, dark_path=None, round=True):
        clutter.Actor.__init__(self)

        self.set_reactive(True)

        self.text = label
        self.is_stretch = stretch
        self.border = border
        
        self.label = clutter.Text()
        self.label.set_parent(self)
        self.label.set_text(self.text)

        if round :
            self.rect = RoundRectangle(light_path=light_path, dark_path=dark_path)
            self.rect.set_border_color(self.default_border_color)
            self.rect.set_border_width(3)
            self.rect.props.radius = 10
        else :
            self.rect = clutter.Rectangle()
        self.rect.set_color(self.default_color)
        self.rect.set_parent(self)
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self.rect.props.color = value
        elif pspec.name == 'text':
            self.text = value
            self.queue_relayout()
        elif pspec.name == 'font-color':
            self.label.props.color = clutter.color_from_string(value)
        elif pspec.name == 'border-color':
            self.rect.props.border_color = value
        elif pspec.name == 'border-width':
            self.rect.props.border_width = value
        else:
            raise TypeError('Unknown property ' + pspec.name)
        self.queue_redraw()

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self.rect.props.color
        elif pspec.name == 'text':
            return self.text
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
        t.destroy()
        return min + 2*self.border, nat + 2*self.border
    
    def do_get_preferred_height(self, for_width):
        min, nat = self.label.get_preferred_height(for_width)
        return min + 2*self.border, nat + 2*self.border
    
    def _wrap_label(self, min, max, width):
        mid = (min + max) / 2
        if mid-6 < 0:
            self.label.set_text(self.text)
            return
        self.label.set_text('%s…%s' %(self.text[:mid-6], self.text[len(self.text)-6:]))
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
        
        rect_box = clutter.ActorBox()
        rect_box.x1 = 0
        rect_box.y1 = 0
        rect_box.x2 = btn_width
        rect_box.y2 = btn_height
        self.rect.allocate(rect_box, flags)
        
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
        lbl_box = clutter.ActorBox()
        lbl_box.x1 = round(self.border + (inner_width - lbl_width) / 2)
        lbl_box.y1 = round(self.border + (inner_height - lbl_height) / 2)
        lbl_box.x2 = round(lbl_box.x1 + lbl_width)
        lbl_box.y2 = round(lbl_box.y1 + lbl_height)
        self.label.allocate(lbl_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        func(self.rect, data)
        func(self.label, data)
    
    def do_paint(self):
        self.rect.paint()
        self.label.paint()
    
    def do_destroy(self):
        self.unparent()
        if self.rect is not None:
            self.rect.unparent()
            self.rect.destroy()
            self.rect = None
        if self.label is not None:
            self.label.unparent()
            self.label.destroy()
            self.label = None


class ItemButton(clutter.Actor, clutter.Container):
    __gtype_name__ = 'ItemButton'
    __gproperties__ = {
        'text' : (
            str, 'text', 'Text', None, gobject.PARAM_READWRITE
        ),
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'font_color' : (
            str, 'font color', 'Font color', None, gobject.PARAM_READWRITE
        ),
        'border_color': (
            str, 'border color', 'Border color', None, gobject.PARAM_READWRITE
        ),
        'active_color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'active': (
            bool, 'active', 'Is active status?', False, gobject.PARAM_READWRITE
        ),
    }
    default_color = 'LightGray'
    default_active_color = 'Yellow'
    default_border_color = 'Gray'
    
    def __init__(self, label, picture=None, border=6.0):
        clutter.Actor.__init__(self)

        self.set_reactive(True)

        self.text = label
        self.border_size = border
        self._is_active = False
        
        self.label = clutter.Text()
        self.label.set_parent(self)
        
        self.picture = None
        if picture is not None:
            self.picture = clutter.Texture(picture)
            self.picture.set_keep_aspect_ratio(True)
            self.picture.set_parent(self)
        
        self.border = OutlinedRoundRectangle()
        self.border.set_color(self.default_border_color)
        self.border.props.radius = 10
        self.border.set_parent(self)
        
        self.back = RoundRectangle()
        self.back.set_color(self.default_color)
        self.back.props.radius = 10
        self.back.set_parent(self)
    
    def toggle_status(self):
        self.props.active = not self.props.active
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self.default_color = value
            if not self._is_active:
                self.back.props.color = value
        elif pspec.name == 'active-color':
            self.default_active_color = value
            if self._is_active:
                self.back.props.color = value
        elif pspec.name == 'text':
            self.text = value
            self.queue_relayout()
        elif pspec.name == 'font-color':
            self.label.props.color = clutter.color_from_string(value)
        elif pspec.name == 'border-color':
            self.border.props.color = value
        elif pspec.name == 'active':
            self._is_active = value
            if value:
                self.back.props.color = self.default_active_color
            else:
                self.back.props.color = self.default_color
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self.default_color
        elif pspec.name == 'active-color':
            return self.default_active_color
        elif pspec.name == 'text':
            return self.text
        elif pspec.name == 'font-color':
            return self.label.props.color
        elif pspec.name == 'border-color':
            return self.rect.props.border_color
        elif pspec.name == 'active':
            return self._is_active
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def do_get_preferred_width(self, for_height):
        t = clutter.Text()
        t.set_font_name(self.label.get_font_name())
        t.set_text('…')
        min = t.get_preferred_size()[0]
        t.set_text(self.text)
        nat = t.get_preferred_size()[2]
        if self.picture is not None:
            pict_width = self.picture.get_preferred_width(-1)[1]
            nat = max(nat, pict_width)
        return min + 2*self.border_size, nat + 2*self.border_size
    
    def do_get_preferred_height(self, for_width):
        min, nat = self.label.get_preferred_height(for_width)
        if self.picture is not None:
            t = clutter.Text()
            t.set_font_name(self.label.get_font_name())
            t.set_text('…')
            min_width = t.get_preferred_size()[0]
            min += self.picture.get_preferred_height(min_width)[0]
            nat += self.picture.get_preferred_height(-1)[1]
        return min + 2*self.border_size, nat + 2*self.border_size
    
    
    def do_allocate(self, box, flags):
        btn_width = box.x2 - box.x1
        btn_height = box.y2 - box.y1
        inner_width = btn_width - 2*self.border_size
        inner_height = btn_height - 2*self.border_size
        
        bgbox = clutter.ActorBox()
        bgbox.x1 = 0
        bgbox.y1 = 0
        bgbox.x2 = btn_width
        bgbox.y2 = btn_height
        self.back.allocate(bgbox, flags)
        self.border.allocate(bgbox, flags)
        
        self.label.set_text(self.text)
        lbl_height = self.label.get_preferred_size()[3]
        lbl_width = self.label.get_preferred_size()[2]
        if self.label.get_preferred_size()[2] > inner_width:
            self.label.set_clip(0, 0, inner_width, lbl_height)
            lbl_width = inner_width
        lblbox = clutter.ActorBox()
        lblbox.x1 = round(self.border_size + (inner_width - lbl_width) / 2)
        lblbox.y1 = round(self.border_size)
        lblbox.x2 = round(lblbox.x1 + lbl_width)
        lblbox.y2 = round(lblbox.y1 + lbl_height)
        self.label.allocate(lblbox, flags)
        
        if self.picture is not None:
            pictbox = clutter.ActorBox()
            pict_width, pict_height = self.picture.get_preferred_size()[2:]
            remain_height = inner_height - lbl_height
            pict_top = lblbox.y2
            if pict_width > inner_width or pict_height > inner_height:
                pict_width = inner_width
                pict_height = self.picture.get_preferred_height(inner_width)[1]
                if pict_height > remain_height:
                    pict_width = \
                             self.picture.get_preferred_width(remain_height)[1]
                    pict_height = remain_height
            elif pict_height > remain_height:
                remain_height = inner_height
                pict_top = self.border_size
            
            pictbox.x1 = \
                       round(self.border_size + (inner_width - pict_width) / 2)
            pictbox.y1 = round(pict_top + (remain_height - pict_height) / 2)
            pictbox.x2 = round(pictbox.x1 + pict_width)
            pictbox.y2 = round(pictbox.y1 + pict_height)
            self.picture.allocate(pictbox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    @property
    def _children(self):
        children = [self.back, self.border]
        if self.picture is not None:
            children.append(self.picture)
        children.append(self.label)
        return children
    
    def do_foreach(self, func, data=None):
        for child in self._children:
            func(child, data)
    
    def do_paint(self):
        for child in self._children:
            child.paint()


class ImageButton(ClassicButton):
    __gtype_name__ = 'ImageButton'
    __gproperties__ = {
        'active' : (
            gobject.TYPE_BOOLEAN, 'active', 'Active', 0, gobject.PARAM_READWRITE
        ),
        'active_color' : (
            str, 'active color', 'Background color when active', None, gobject.PARAM_READWRITE
        ),
    }

    def __init__(self, label, image_location, stretch=False, border=6.0, spacing=8.0, use_native_image_size=False, activable=False, light_path=None, dark_path=None):
        ClassicButton.__init__(self, label, stretch, border, light_path=light_path, dark_path=dark_path)

        self.image = clutter.Texture(image_location)
        self.image.set_parent(self)
        self.image.set_keep_aspect_ratio(True)
        self.use_native_image_size = use_native_image_size
        self.spacing = spacing
        
        self.default_font_size = '16'
        self.default_font_color = '#000000ff'
        self.default_inner_color = '#aaaaaaff'
        self.default_highlight_color = '#ffffff88'
        self.default_border_color = '#888888ff'
        self.default_active_color = '#00000088'
        
        self.label.set_font_name(self.default_font_size)
        self.label.set_color(self.default_font_color)
        self.rect.set_color(self.default_inner_color)
        self.rect.set_border_color(self.default_border_color)
        
        self.last_color = self.rect.props.color

        self._activated = False
        if activable:
            self.connect("button-release-event", self.toggle_activate)

    def toggle_activate(self, source=None, event=None):
        if self._activated:
            self.set_active(False)
        else:
            self.set_active(True)

    def set_active(self, value):
        if value:
            self.last_color = self.rect.props.color
            self.rect.props.color = self.default_active_color
            self._activated = True
        else:
            self.rect.props.color = self.last_color
            self._activated = False

    def do_allocate(self, box, flags):
        btn_width = box.x2 - box.x1
        btn_height = box.y2 - box.y1
        inner_width = btn_width - 2*self.border
        inner_height = btn_height - 2*self.border
        
        # round rect
        rbox = clutter.ActorBox()
        rbox.x1 = 0
        rbox.y1 = 0
        rbox.x2 = btn_width
        rbox.y2 = btn_height
        self.rect.allocate(rbox, flags)
        
        # label
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
        
        # image
        if self.use_native_image_size:
            image_width = self.image.get_preferred_size()[2]
            image_height = self.image.get_preferred_size()[3]
        else:
            max_width = self.image.get_preferred_size()[2]
            max_height = self.image.get_preferred_size()[3]
            image_ratio = float(self.image.get_preferred_size()[2])/float(self.image.get_preferred_size()[3])
            
            image_height = inner_height - lbl_height - self.spacing
            if image_height > max_height:
                image_height = max_height
            if image_height > inner_height:
                image_height = inner_height
            image_width = image_height * image_ratio
            if image_width > inner_width:
                image_width = inner_width
                image_height = image_width/image_ratio
        
        lbox = clutter.ActorBox()
        lbox.x1 = round(self.border + (inner_width - lbl_width)/2)
        lbox.y1 = round(self.border + (inner_height - lbl_height - self.spacing - image_height)/2 + image_height + self.spacing)
        lbox.x2 = round(lbox.x1 + lbl_width)
        lbox.y2 = round(lbox.y1 + lbl_height)
        self.label.allocate(lbox, flags)
        
        ibox = clutter.ActorBox()
        ibox.x1 = round(self.border + (inner_width - image_width)/2)
        ibox.y1 = round(self.border + (inner_height - lbl_height - self.spacing - image_height)/2)
        ibox.x2 = round(ibox.x1 + image_width)
        ibox.y2 = round(ibox.y1 + image_height)
        self.image.allocate(ibox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)

    def do_set_property(self, pspec, value):
        if pspec.name == 'active':
            self.set_active(value)
        elif pspec.name == 'active-color':
            self.default_active_color = clutter.color_from_string(value)
        else:
            ClassicButton.do_set_property(self, pspec, value)
        self.queue_redraw()

    def do_get_property(self, pspec):
        if pspec.name == 'active':
            return self._activated
        elif pspec.name == 'active-color':
            return self.default_active_color
        else:
            ClassicButton.do_get_property(self, pspec, value)

    def do_paint(self):
        ClassicButton.do_paint(self)
        self.image.paint()

    def do_foreach(self, func, data=None):
        ClassicButton.do_foreach(self, func, data)
        func(self.image, data)

gobject.type_register(ImageButton)

if __name__ == '__main__':
    from flowbox import FlowBox
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)
    
    # Main flowbox
    box0 = FlowBox()
    box0.set_size(640, 640)
    
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
    b.set_size(170, 170)
    b.set_position(425, 210)
    stage.add(b)


    stage.add(box0)
    stage.show()

    clutter.main()
