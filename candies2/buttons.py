#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import clutter
from text import TextContainer
from roundrect import RoundRectangle, OutlinedRoundRectangle

class ClassicButton(TextContainer):
    __gtype_name__ = 'ClassicButton'
    
    def __init__(self, label, padding=6, texture=None, rounded=True):
        TextContainer.__init__(self, label, padding=padding, texture=texture, rounded=rounded)
        self.set_reactive(True)

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

    def __init__(self, label, image_location, padding=6, spacing=8, use_native_image_size=False, activable=False, texture=None):
        ClassicButton.__init__(self, label, padding=padding, texture=texture)

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
        inner_width = btn_width - 2*self.padding
        inner_height = btn_height - 2*self.padding
        
        # round rect
        rbox = clutter.ActorBox()
        rbox.x1 = 0
        rbox.y1 = 0
        rbox.x2 = btn_width
        rbox.y2 = btn_height
        self.rect.allocate(rbox, flags)
        
        # label
        self.label.set_text(self._text)
        if self.label.get_preferred_size()[2] > inner_width:
            self._wrap_singleline_label(0, len(self._text), inner_width)
        lbl_width = self.label.get_preferred_size()[2]
        lbl_height = self.label.get_preferred_size()[3]
        
        # image
        if self.use_native_image_size:
            image_width = self.image.get_preferred_size()[2]
            image_height = self.image.get_preferred_size()[3]
        else:
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
        lbox.x1 = round(self.padding + (inner_width - lbl_width)/2)
        lbox.y1 = round(self.padding + (inner_height - lbl_height - self.spacing - image_height)/2 + image_height + self.spacing)
        lbox.x2 = round(lbox.x1 + lbl_width)
        lbox.y2 = round(lbox.y1 + lbl_height)
        self.label.allocate(lbox, flags)
        
        ibox = clutter.ActorBox()
        ibox.x1 = round(self.padding + (inner_width - image_width)/2)
        ibox.y1 = round(self.padding + (inner_height - lbl_height - self.spacing - image_height)/2)
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
            ClassicButton.do_get_property(self, pspec)

    def do_paint(self):
        ClassicButton.do_paint(self)
        self.image.paint()

    def do_foreach(self, func, data=None):
        ClassicButton.do_foreach(self, func, data)
        func(self.image, data)
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'image'):
            if self.image is not None:
                self.image.unparent()
                self.image.destroy()
                self.image = None
        try:
            ClassicButton.do_destroy(self)
        except:
            pass

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
    
    # Testing buttons
    b = ClassicButton('A')
    b.set_size(15, 15)
    b.set_position(5, 450)
    stage.add(b)
    
    b = ClassicButton('B')
    b.set_size(25, 25)
    b.set_position(50, 425)
    stage.add(b)
    
    b = ClassicButton('C')
    b.set_font_color('Yellow')
    b.set_size(50, 50)
    b.set_position(125, 375)
    stage.add(b)
    
    b = ClassicButton('D')
    b.set_border_width(10)
    b.set_border_color('Green')
    b.set_size(100, 100)
    b.set_position(250, 325)
    stage.add(b)
    
    b = ClassicButton('E')
    b.set_color('Pink')
    b.set_size(170, 170)
    b.set_position(425, 210)
    stage.add(b)
    
    stage.add(box0)
    
    test_memory_usage = True
    if test_memory_usage:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
        from pprint import pprint
        
        max_count = 5000
        
        texture_path = '/home/sdiemer/sources/candies/main/candies2/effect_light.png'
        texture = clutter.cogl.texture_new_from_file(light_path)
        
        def create_test_object():
            t = ClassicButton('test efopkzekfopzf opfzeopfkz opfzegjzeh guzehiug ezhgiozeghizeogh eziogzeoighze oigzeiogzeig opg jzeopgjzepogzzeogjze zeigergre ergerg', texture = texture, rounded = True)
            return t
        def remove_test_object(obj, stage):
            obj.destroy()
            return False
        
        def test_memory(stage, counter, max_count):
            if counter < max_count or max_count == 0:
                counter += 1
                print counter
                tested_object = create_test_object()
                stage.add(tested_object)
                gobject.timeout_add(2, remove_tested_object, tested_object, stage, counter)
            return False
        
        def remove_tested_object(tested_object, stage, counter):
            remove_test_object(tested_object, stage)
            
            gc.collect()
            pprint(gc.garbage)
            
            gobject.timeout_add(2, test_memory, stage, counter, max_count)
            return False
        
        gobject.timeout_add(10, test_memory, stage, 0, max_count)
    
    stage.show()
    clutter.main()
