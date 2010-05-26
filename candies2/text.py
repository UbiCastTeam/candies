#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gobject
import clutter
from roundrect import RoundRectangle

class StretchText(clutter.Text):
    """
    StretchText (clutter.Text)

    An enhanced Text actor which resize its font according to the available
    space.
    """
    __gtype_name__ = 'StretchText'
    minimal_fontsize = 5
    
    def do_get_preferred_width(self, for_height):
        fontface = self.get_font_name()
        fontface = fontface[:fontface.rindex(' ')]
        lbl = clutter.Text()
        text = self.get_text()
        lbl.set_text(text)
        lbl.set_font_name('%s %s' %(fontface, self.minimal_fontsize))
        min_width = lbl.get_preferred_width(-1)[0]
        if for_height > -1 and text.split():
            fontsize = self.get_preferred_fontsize(for_height=for_height)
            lbl.set_font_name('%s %s' %(fontface, fontsize))
            min, nat = lbl.get_preferred_width(-1)
        else:
            min, nat = clutter.Text.do_get_preferred_width(self, for_height)
        return max(min, min_width), nat
    
    def do_get_preferred_height(self, for_width):
        fontface = self.get_font_name()
        fontface = fontface[:fontface.rindex(' ')]
        lbl = clutter.Text()
        text = self.get_text()
        lbl.set_text(text)
        lbl.set_font_name('%s %s' %(fontface, self.minimal_fontsize))
        min_height = lbl.get_preferred_height(-1)[0]
        if for_width > -1 and text.split():
            fontsize = self.get_preferred_fontsize(for_width=for_width)
            lbl.set_font_name('%s %s' %(fontface, fontsize))
            min, nat_height = lbl.get_preferred_height(-1)
        else:
            min, nat_height = clutter.Text.do_get_preferred_height(self, for_width)
        return min_height, nat_height
    
    def get_preferred_fontsize(self, for_width=None, for_height=None):
        """ Compute the nearest fontsize according to the for_* statements.
        """
        # Build offscreen label
        lbl = clutter.Text()
        text = self.get_text()
        lbl.set_text(text)
        fontface = self.get_font_name()
        fontface = fontface[:fontface.rindex(' ')]
        fontsize = self.minimal_fontsize
        lbl.set_font_name('%s %s' %(fontface, fontsize))
        
        # Use default width when no for_* argument given or blank text
        if (for_width is None and for_height is None) or not text.strip():
            return fontsize
        
        # Look for the nearest fontsize according to the for_* statements
        while True:
            fontsize += 1
            lbl.set_font_name('Sans %s' %(fontsize))
            if (for_height is not None and lbl.get_height() > for_height) \
                    or (for_width is not None and lbl.get_width() > for_width):
                fontsize -= 1
                break
        return fontsize
        
        # Force minimal width if computed natural width is smaller
        nat_width = lbl.get_width()
        min_width = nat_width
        return min_width, nat_width
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        
        fontface = self.get_font_name()
        fontface = fontface[:fontface.rindex(' ')]
        fontsize = self.get_preferred_fontsize(width, height)
        self.set_font_name('%s %s' %(fontface, fontsize))
        
        clutter.Text.do_allocate(self, box, flags)


class TextContainer(clutter.Actor, clutter.Container):
    __gtype_name__ = 'TextContainer'
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
    
    def __init__(self, text, padding=6, light_texture=None, dark_texture=None, rounded=True):
        clutter.Actor.__init__(self)
        
        self.padding = padding
        self._text = text
        self._line_wrap = False
        self._multiline = False
        
        self.label = clutter.Text()
        self.label.set_parent(self)
        self.label.set_text(self._text)
        self.label.set_line_wrap(False)
        self.label.set_line_alignment(1)
        
        if rounded:
            self._rounded = True
            self.rect = RoundRectangle(light_texture=light_texture, dark_texture=dark_texture)
            self.rect.set_border_color(self.default_border_color)
            self.rect.set_border_width(3)
            self.rect.props.radius = 10
        else:
            self._rounded = False
            self.rect = clutter.Rectangle()
        self.rect.set_color(self.default_color)
        self.rect.set_parent(self)
    
    def set_text(self, text):
        self._text = text
        self.label.set_text(self._text)
        self.queue_relayout()
    
    def get_text(self):
        return self._text
    
    def set_radius(self, radius):
        if self._rounded:
            self.rect.set_radius(radius)
    
    def set_font_color(self, color):
        self.label.set_color(color)
    
    def set_font_name(self, font_name):
        self.label.set_font_name(font_name)
    
    def set_inner_color(self, color):
        if self.rect is not None:
            self.rect.set_color(color)
    
    def set_border_color(self, color):
        if self._rounded:
            self.rect.set_border_color(color)
    
    def set_border_width(self, width):
        if self._rounded:
            self.rect.set_border_width(width)
    
    def set_line_wrap(self, boolean):
        if boolean:
            self._line_wrap = True
            self.label.set_line_wrap(True)
        else:
            self._line_wrap = False
            self.label.set_line_wrap(False)
            
    def set_line_alignment(self, alignement):
        if alignement == 'center':
            self.label.set_line_alignment(1)
        elif alignement == 'right':
            self.label.set_line_alignment(2)
        elif alignement == 'left':
            self.label.set_line_alignment(3)
    
    def set_justify(self, boolean):
        if boolean:
            self.label.set_justify(True)
        else:
            self.label.set_justify(False)
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self.rect.props.color = value
        elif pspec.name == 'text':
            self._text = value
            self.label.set_text(self._text)
            self.queue_relayout()
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
        elif pspec.name == 'text':
            return self._text
        elif pspec.name == 'font-color':
            return self.label.props.color
        elif pspec.name == 'border-color':
            return self.rect.props.border_color
        elif pspec.name == 'border-width':
            return self.rect.props.border_width
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def do_get_preferred_width(self, for_height):
        min, nat = self.label.get_preferred_width(for_height)
        return min + 2*self.padding, nat + 2*self.padding
    
    def do_get_preferred_height(self, for_width):
        min, nat = self.label.get_preferred_height(for_width)
        return min + 2*self.padding, nat + 2*self.padding
    
    def _wrap_singleline_label(self, min, max, max_width):
        mid = (min + max) / 2
        if mid-6 < 0:
            self.label.set_text(self._text)
            return
        self.label.set_text('%s…%s' %(self._text[:mid-6], self._text[len(self._text)-6:]))
        if mid == min or self.label.get_preferred_size()[2] == max_width:
            return
        if self.label.get_preferred_size()[2] > max_width:
            self._wrap_singleline_label(min, mid, max_width)
        else:
            self._wrap_singleline_label(mid, max, max_width)
    
    def _wrap_multilines_label(self, min, max, max_width, max_height):
        mid = (min + max) / 2
        if mid-6 < 0:
            self.label.set_text(self._text)
            return
        self.label.set_text('%s…%s' %(self._text[:mid-6], self._text[len(self._text)-6:]))
        if mid == min or self.label.get_preferred_height(for_width = max_width)[1] == max_height:
            return
        if self.label.get_preferred_height(for_width = max_width)[1] > max_height:
            self._wrap_multilines_label(min, mid, max_width, max_height)
        else:
            self._wrap_multilines_label(mid, max, max_width, max_height)
    
    def do_allocate(self, box, flags):
        btn_width = box.x2 - box.x1
        btn_height = box.y2 - box.y1
        inner_width = btn_width - 2*self.padding
        inner_height = btn_height - 2*self.padding
        
        rect_box = clutter.ActorBox()
        rect_box.x1 = 0
        rect_box.y1 = 0
        rect_box.x2 = btn_width
        rect_box.y2 = btn_height
        self.rect.allocate(rect_box, flags)
        
        self.label.set_text(self._text)
        self._multiline = False
        if self._line_wrap:
            if self.label.get_preferred_height(for_width = inner_width)[1] > self.label.get_preferred_size()[3]:
                if inner_height > self.label.get_preferred_size()[3]:
                    self._multiline = True
        if self._multiline:
            if self.label.get_preferred_height(for_width = inner_width)[1] > inner_height:
                self._wrap_multilines_label(0, len(self._text), inner_width, inner_height)
            lbl_width = inner_width
            lbl_height = self.label.get_preferred_height(for_width = inner_width)[1]
        else:
            if self.label.get_preferred_size()[2] > inner_width:
                self._wrap_singleline_label(0, len(self._text), inner_width)
            lbl_width = self.label.get_preferred_size()[2]
            lbl_height = self.label.get_preferred_size()[3]
        lbl_box = clutter.ActorBox()
        lbl_box.x1 = round(self.padding + (inner_width - lbl_width) / 2)
        lbl_box.y1 = round(self.padding + (inner_height - lbl_height) / 2)
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
        if hasattr(self, 'rect'):
            if self.rect is not None:
                self.rect.unparent()
                self.rect.destroy()
                self.rect = None
        if hasattr(self, 'label'):
            if self.label is not None:
                self.label.unparent()
                self.label.destroy()
                self.label = None


if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(700, 700)
    stage.connect('destroy', clutter.main_quit)
    
    t = StretchText()
    t.set_text('Hello World')
    t.set_size(250, 150)
    t.set_position(400, 50)
    stage.add(t)

    t = StretchText()
    t.set_text('Hello World')
    t.set_size(150, 100)
    t.set_position(400, 250)
    stage.add(t)
    
    t = TextContainer('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec viverra adipiscing posuere. Proin fringilla nisl non dui consectetur aliquet. Integer et elit sem, faucibus fringilla urna. Suspendisse vel ipsum nunc, sed malesuada urna. Nunc bibendum imperdiet tellus vitae tempus. Vivamus sodales feugiat cursus. Maecenas accumsan est ac lorem consequat sed aliquam justo sollicitudin. Vivamus congue dignissim ligula, a malesuada enim sagittis et. Nam fringilla nisl quis nisi ultrices tincidunt. Cras ut magna eu nunc adipiscing rhoncus. Donec at leo vel magna congue auctor id ut eros. Praesent sodales fringilla lacus quis congue. Quisque a nunc urna. Donec euismod sagittis bibendum.', padding=20)
    t.set_size(300, 500)
    t.set_position(50, 50)
    t.set_line_wrap(True)
    #t.set_line_alignment('center')
    #t.set_justify(True)
    t.set_font_name('20')
    stage.add(t)

    stage.show()

    clutter.main()
