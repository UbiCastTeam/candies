#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clutter

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

if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    t = StretchText()
    t.set_text('Hello World')
    t.set_size(640, 480)
    stage.add(t)

    t = StretchText()
    t.set_text('Hello World')
    t.set_size(320, 240)
    t.set_y(240)
    stage.add(t)

    t = StretchText()
    t.set_text('Hello World')
    t.set_size(160, 120)
    t.set_y(360)
    stage.add(t)

    t = StretchText()
    t.set_text('Hello World')
    t.set_size(80, 60)
    t.set_y(420)
    stage.add(t)

    stage.show()

    clutter.main()
