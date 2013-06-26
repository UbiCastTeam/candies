#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import clutter
from text import TextContainer
from roundrect import RoundRectangle, OutlinedRoundRectangle
from clutter import cogl

class ClassicButton(TextContainer):
    __gtype_name__ = 'ClassicButton'
    
    def __init__(self, label=' ', margin=0, padding=6, texture=None, rounded=True, crypted=False):
        TextContainer.__init__(self, label, margin=margin, padding=padding, texture=texture, rounded=rounded, crypted=crypted)
        self.set_reactive(True)
    
    def set_lock(self, lock):
        self.set_reactive(not lock)
        self.set_opacity(128 if lock else 255)

class ImageButton(ClassicButton):
    __gtype_name__ = 'ImageButton'

    def __init__(self, label=' ', image_src=None, margin=0, padding=10, spacing=10, texture=None, has_text=True, expand=False):
        ClassicButton.__init__(self, label, margin=margin, padding=padding, texture=texture)

        self.spacing = spacing
        self._has_text = has_text
        self._expand = expand
        
        self.image = clutter.Texture()
        if image_src:
            self.image.set_from_file(image_src)
        self.image.set_parent(self)
        
        self.set_font_name('16')
        self.set_font_color('#000000ff')
        self.set_inner_color('#aaaaaaff')
        self.set_border_color('#888888ff')
    
    def set_image_src(self, image_src):
        self.image.set_from_file(image_src)
    
    def do_allocate(self, box, flags):
        btn_width = box.x2 - box.x1
        btn_height = box.y2 - box.y1
        inner_width = btn_width - 2*self._padding.x
        inner_height = btn_height - 2*self._padding.y
        
        # allocate background
        self._allocate_rect(0, 0, btn_width, btn_height, flags)
        
        # allocate image
        if self._has_text:
            label_height = ClassicButton.do_get_preferred_height(self, for_width=inner_width)[1]
            remaining_height = btn_height - label_height - self.spacing
        else:
            label_height = 0
            remaining_height = inner_height
        image_preferred_size = self.image.get_preferred_size()
        if image_preferred_size[3] > 0:
            image_ratio = float(image_preferred_size[2]) / float(image_preferred_size[3])
            if self._expand:
                image_height = remaining_height
                image_width = round(float(image_height) * float(image_ratio))
                if image_width > inner_width:
                    image_width = inner_width
                    image_height = round(float(image_width) / float(image_ratio))
            else:
                image_height = image_preferred_size[3]
                if remaining_height < image_height:
                    image_height = remaining_height
                image_width = round(float(image_height) * float(image_ratio))
                if image_width > inner_width:
                    image_width = inner_width
                    image_height = round(float(image_width) / float(image_ratio))
        else:
            image_width = 0
            image_height = 0
        x_padding = round((inner_width - image_width) / 2.0)
        y_padding = round((remaining_height - image_height) / 2.0)
        
        image_box = clutter.ActorBox()
        image_box.x1 = self._padding.x + x_padding
        image_box.y1 = self._padding.y + y_padding
        image_box.x2 = image_box.x1 + image_width
        image_box.y2 = image_box.y1 + image_height
        self.image.allocate(image_box, flags)
        
        # allocate label
        if self._has_text:
            base_y = image_height + self.spacing
            label_height = btn_height - base_y
            self._allocate_label(0, base_y, btn_width, label_height, flags)
        
        clutter.Actor.do_allocate(self, box, flags)

    def do_set_property(self, pspec, value):
        return ClassicButton.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        return ClassicButton.do_get_property(self, pspec)

    def do_paint(self):
        self.rect.paint()
        self.image.paint()
        if self._has_text:
            self.label.paint()

    def do_foreach(self, func, data=None):
        ClassicButton.do_foreach(self, func, data)
        func(self.image, data)
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'image'):
            if self.image:
                self.image.unparent()
                self.image.destroy()
        try:
            ClassicButton.do_destroy(self)
        except:
            pass

gobject.type_register(ImageButton)

if __name__ == '__main__':
    from flowbox import FlowBox
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)
    #toto = cogl.Material()
    texture_path = '/home/aviolo/sources/easycast/unstable/easycast/images/buttons/copy.png'
    texture = clutter.cogl.texture_new_from_file(texture_path, clutter.cogl.TEXTURE_NO_SLICING, clutter.cogl.PIXEL_FORMAT_ANY)
    #toto.set_layer(0, texture)
    #stage.add(toto)
    t = ClassicButton('test efopkzekfopzf opfzeopfkz opfzegjzeh guzehiug ezhgiozeghizeogh eziogzeoighze oigzeiogzeig opg jzeopgjzepogzzeogjze zeigergre ergerg', texture = texture, rounded = True)
    t.set_size(640, 480)
    stage.add(t)
    '''
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
    
    b = ClassicButton('E', texture=texture)
    b.set_inner_color('Pink')
    b.set_size(170, 170)
    b.set_position(425, 210)
    stage.add(b)
    
    stage.add(box0)
    '''
    test_memory_usage = False
    if test_memory_usage:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
        from pprint import pprint
        
        max_count = 5000
        
        #texture_path = '/home/sdiemer/sources/candies/main/candies2/effect_light.png'
        texture = clutter.cogl.texture_new_from_file(texture_path, clutter.cogl.TEXTURE_NO_SLICING, clutter.cogl.PIXEL_FORMAT_ANY)
        texture = None
        
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
