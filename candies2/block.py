#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import clutter
from clutter import cogl
from text import TextContainer

class TexturedBlock(clutter.Actor, clutter.Container):
    __gtype_name__ = 'TexturedBlock'
    
    def __init__(self, title=' ', title_actor=None, content_actor=None, padding=10, title_padding=None, spacing=10, textures_package=None):
        clutter.Actor.__init__(self)
        self.padding = padding
        self.spacing = spacing
        
        self._highlighted = False
        self._highlight_color = clutter.color_from_string('#ffffff44')
        
        self.title_actor = title_actor
        if title_actor:
            self.title_actor.set_parent(self)
        if title_padding:
            self.title_padding = title_padding
        else:
            self.title_padding = 0
        self.default_title_actor = TextContainer(title)
        self.default_title_actor.set_line_alignment(1)
        self.default_title_actor.set_line_wrap(False)
        self.default_title_actor.set_parent(self)
        self._title_alignement = 'center'
        self._title_height = 0
        
        self.content_actor = content_actor
        if self.content_actor:
            self.content_actor.set_parent(self)
        
        self.width = 0
        self.height = 0
        
        # textures
        #    background
        self._bg_textures_size = 40
        self._top_left = None
        self._top = None
        self._top_right = None
        self._middle_left = None
        self._middle = None
        self._middle_right = None
        self._bottom_left = None
        self._bottom = None
        self._bottom_right = None
        #    title
        self._title_textures_size = 20
        self._title_left = None
        self._title_middle = None
        self._title_right = None
        
        self._parse_textures_package(textures_package)
    
    def set_font_color(self, color):
        self.default_title_actor.set_font_color(color)
    
    def set_font_name(self, font_name):
        self.default_title_actor.set_font_name(font_name)
        
    def set_title_alignement(self, alignement):
        if alignement == 'center':
            self._title_alignement = 'center'
            self.default_title_actor.set_line_alignment('center')
        elif alignement == 'right':
            self._title_alignement = 'right'
            self.default_title_actor.set_line_alignment('right')
        elif alignement == 'left':
            self._title_alignement = 'left'
            self.default_title_actor.set_line_alignment('left')
    
    def set_title_inner_color(self, color):
        self.default_title_actor.set_inner_color(color)
    
    def set_title_border_color(self, color):
        self.default_title_actor.set_border_color(color)
    
    def set_title_radius(self, radius):
        self.default_title_actor.set_radius(radius)
    
    def set_title_wrap(self, boolean):
        if boolean:
            self.default_title_actor.set_line_wrap(True)
        else:
            self.default_title_actor.set_line_wrap(False)
    
    def set_highlighted(self, boolean):
        if boolean:
            self._highlighted = True
        else:
            self._highlighted = False
        self.queue_redraw()
        
    def set_highlight_color(self, color):
        self._highlight_color = clutter.color_from_string(color)
        if self._highlighted:
            self.queue_redraw()
    
    def set_textures(self, textures_package):
        self._parse_textures_package(textures_package)
        self.queue_redraw()
    
    def _parse_textures_package(self, package):
        if 'top_left' in package:
            self._top_left = package['top_left']
        if 'top' in package:
            self._top = package['top']
        if 'top_right' in package:
            self._top_right = package['top_right']
        if 'middle_left' in package:
            self._middle_left = package['middle_left']
        if 'middle' in package:
            self._middle = package['middle']
        if 'middle_right' in package:
            self._middle_right = package['middle_right']
        if 'bottom_left' in package:
            self._bottom_left = package['bottom_left']
        if 'bottom' in package:
            self._bottom = package['bottom']
        if 'bottom_right' in package:
            self._bottom_right = package['bottom_right']
        if 'title_left' in package:
            self._title_left = package['title_left']
        if 'title_middle' in package:
            self._title_middle = package['title_middle']
        if 'title_right' in package:
            self._title_right = package['title_right']
    
    def set_background_textures_size(self, size):
        self._bg_textures_size = size
        self.queue_redraw()
    
    def set_title_textures_size(self, size):
        self._title_texture_size = size
        self.queue_redraw()
    
    def remove_content(self):
        if self.content_actor:
            self.content_actor.unparent()
            self.content_actor = None
    
    def set_content(self, content):
        self.remove_content()
        self.content_actor = content
        if self.content_actor:
            self.content_actor.set_parent(self)
    
    def set_title(self, title):
        self.default_title_actor.set_text(title)
        self.queue_relayout()
    
    def get_title(self):
        return self.default_title_actor.get_text(title)
    
    def get_title_actor(self):
        if self.title_actor:
            return self.title_actor
        else:
            return self.default_title_actor
    
    def get_content_actor(self):
        return self.content_actor
    
    def do_get_preferred_width(self, for_height):
        if self.title_actor:
            max_width = max(self.title_actor.get_preferred_width(for_height)[1], self.content_actor.get_preferred_width(for_height)[1])
        else:
            max_width = max(self.default_title_actor.get_preferred_width(for_height)[1], self.content_actor.get_preferred_width(for_height)[1])
        preferred_width = 2*self.padding + max_width
        return preferred_width, preferred_width
    
    def do_get_preferred_height(self, for_width):
        preferred_height = 2*self.padding + self.spacing + self.content_actor.get_preferred_height(for_width)[1]
        if self.title_actor:
            preferred_height += self.title_actor.get_preferred_height(for_width)[1]
        else:
            preferred_height += self.default_title_actor.get_preferred_height(for_width)[1]
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        self.width = box.x2 - box.x1
        self.height = box.y2 - box.y1
        inner_width = self.width - 2*self.padding
        
        if self.title_actor:
            selected_title_actor = self.title_actor
        else:
            selected_title_actor = self.default_title_actor
        
        x1_padding = 0
        x2_padding = 0
        title_max_width = inner_width - 2*self.title_padding
        title_width = selected_title_actor.get_preferred_size()[2]
        if self.title_actor:
            if title_max_width > title_width:
                if self._title_alignement == 'center':
                    x1_padding = x2_padding = round(float(title_max_width - title_width) / 2.0)
                elif self._title_alignement == 'left':
                    x1_padding = 0
                    x2_padding = title_max_width - title_width
                elif self._title_alignement == 'right':
                    x1_padding = title_max_width - title_width
                    x2_padding = 0
        else:
            x1_padding = 0
            x2_padding = 0
        self._title_height = selected_title_actor.get_preferred_height(for_width=inner_width)[1]
        title_box = clutter.ActorBox()
        title_box.x1 = self.padding + self.title_padding + x1_padding
        title_box.y1 = self.padding + self.title_padding
        title_box.x2 = self.width - self.padding - self.title_padding - x2_padding
        title_box.y2 = self.padding + self.title_padding + self._title_height
        selected_title_actor.allocate(title_box, flags)
        
        if self.content_actor:
            content_box = clutter.ActorBox()
            content_box.x1 = self.padding
            content_box.y1 = self.padding + 2*self.title_padding + self._title_height + self.spacing
            content_box.x2 = self.width - self.padding
            content_box.y2 = self.height - self.padding
            self.content_actor.allocate(content_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        if self.title_actor:
            func(self.title_actor, data)
        if self.default_title_actor:
            func(self.default_title_actor, data)
        if self.content_actor:
            func(self.content_actor, data)
    
    def __paint_background(self):
        if self.width > 0 and self.height > 0:
            x1 = 0
            y1 = 0
            x2 = self._bg_textures_size
            y2 = self._bg_textures_size
            x3 = self.width - self._bg_textures_size
            y3 = self.height - self._bg_textures_size
            x4 = self.width
            y4 = self.height
            
            # top_left texture
            if self._top_left:
                cogl.path_rectangle(x1, y1, x2, y2)
                cogl.path_close()
                cogl.set_source_texture(self._top_left)
                cogl.path_fill()
            # top texture
            if self._top:
                cogl.path_rectangle(x2, y1, x3, y2)
                cogl.path_close()
                cogl.set_source_texture(self._top)
                cogl.path_fill()
            # top_right texture
            if self._top_right:
                cogl.path_rectangle(x3, y1, x4, y2)
                cogl.path_close()
                cogl.set_source_texture(self._top_right)
                cogl.path_fill()
            # middle_left texture
            if self._middle_left:
                cogl.path_rectangle(x1, y2, x2, y3)
                cogl.path_close()
                cogl.set_source_texture(self._middle_left)
                cogl.path_fill()
            # middle texture
            if self._middle:
                cogl.path_rectangle(x2, y2, x3, y3)
                cogl.path_close()
                cogl.set_source_texture(self._middle)
                cogl.path_fill()
            # middle_right texture
            if self._middle_right:
                cogl.path_rectangle(x3, y2, x4, y3)
                cogl.path_close()
                cogl.set_source_texture(self._middle_right)
                cogl.path_fill()
            # bottom_left texture
            if self._bottom_left:
                cogl.path_rectangle(x1, y3, x2, y4)
                cogl.path_close()
                cogl.set_source_texture(self._bottom_left)
                cogl.path_fill()
            # bottom texture
            if self._bottom:
                cogl.path_rectangle(x2, y3, x3, y4)
                cogl.path_close()
                cogl.set_source_texture(self._bottom)
                cogl.path_fill()
            # bottom_right texture
            if self._bottom_right:
                cogl.path_rectangle(x3, y3, x4, y4)
                cogl.path_close()
                cogl.set_source_texture(self._bottom_right)
                cogl.path_fill()
            
            title_x1 = self.padding
            title_x2 = self.padding + self._title_textures_size
            title_x3 = self.width - self.padding - self._title_textures_size
            title_x4 = self.width - self.padding
            title_y1 = self.padding
            title_y2 = self.padding + 2*self.title_padding + self._title_height
            # title_left texture
            if self._title_left:
                cogl.path_rectangle(title_x1, title_y1, title_x2, title_y2)
                cogl.path_close()
                cogl.set_source_texture(self._title_left)
                cogl.path_fill()
            # title texture
            if self._title_middle:
                cogl.path_rectangle(title_x2, title_y1, title_x3, title_y2)
                cogl.path_close()
                cogl.set_source_texture(self._title_middle)
                cogl.path_fill()
            # title_right texture
            if self._title_right:
                cogl.path_rectangle(title_x3, title_y1, title_x4, title_y2)
                cogl.path_close()
                cogl.set_source_texture(self._title_right)
                cogl.path_fill()
    
    def __paint_light(self):
        x1 = self.padding
        y1 = self.padding
        x2 = self.width - self.padding
        y2 = self.height - self.padding
        
        cogl.path_round_rectangle(x1, y1, x2, y2, 8, 1)
        cogl.path_close()
        cogl.set_source_color(self._highlight_color)
        cogl.path_fill()
    
    def do_paint(self):
        self.__paint_background()
        
        if self._highlighted:
            self.__paint_light()
        
        if self.title_actor:
            self.title_actor.paint()
        else:
            self.default_title_actor.paint()
        if self.content_actor:
            self.content_actor.paint()
    
    def do_pick(self, color):
        cogl.path_rectangle(0, 0, self.width, self.height)
        cogl.path_close()
        cogl.set_source_color(color)
        cogl.path_fill()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'title_actor'):
            if self.title_actor:
                self.title_actor.unparent()
                self.title_actor.destroy()
                self.title_actor = None
        if hasattr(self, 'default_title_actor'):
            if self.default_title_actor:
                self.default_title_actor.unparent()
                self.default_title_actor.destroy()
                self.default_title_actor = None
        if hasattr(self, 'content_actor'):
            if self.content_actor:
                self.content_actor.unparent()
                self.content_actor.destroy()
                self.content_actor = None


if __name__ == '__main__':
    # stage
    stage = clutter.Stage()
    stage_width = 1200
    stage_height = 600
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', clutter.main_quit)
    
    textures_path = '/home/sdiemer/Bureau/textures/'
    
    textures_package = {
        'top_left': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'top_left', '.png')),
        'top': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'top', '.png')),
        'top_right': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'top_right', '.png')),
        'middle_left': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'middle_left', '.png')),
        'middle': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'middle', '.png')),
        'middle_right': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'middle_right', '.png')),
        'bottom_left': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'bottom_left', '.png')),
        'bottom': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'bottom', '.png')),
        'bottom_right': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'bottom_right', '.png')),
        
        'title_left': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'title_left', '.png')),
        'title_middle': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'title_middle', '.png')),
        'title_right': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'title_right', '.png')),
    }
    
    content = clutter.Rectangle()
    content.set_color('#00000088')
    
    title = clutter.Rectangle()
    title.set_height(50)
    title.set_color('#ff000088')
    
    global_bg = TexturedBlock('Nouveau block', content_actor=content, textures_package=textures_package)
    #global_bg = TexturedBlock('Nouveau block', title_actor=title, content_actor=content, textures_package=textures_package)
    global_bg.set_position(50, 50)
    global_bg.set_size(800, 300)
    stage.add(global_bg)
    
    test_memory_usage = False
    if test_memory_usage:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
        from pprint import pprint
        
        max_count = 20000
        
        textures_package = {
            'top_left': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'top_left', '.png')),
            'top': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'top', '.png')),
            'top_right': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'top_right', '.png')),
            'middle_left': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'middle_left', '.png')),
            'middle': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'middle', '.png')),
            'middle_right': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'middle_right', '.png')),
            'bottom_left': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'bottom_left', '.png')),
            'bottom': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'bottom', '.png')),
            'bottom_right': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'bottom_right', '.png')),
            
            'title_left': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'title_left', '.png')),
            'title_middle': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'title_middle', '.png')),
            'title_right': cogl.texture_new_from_file('%s%s%s' %(textures_path, 'title_right', '.png')),
        }
        
        def create_test_object(textures_package):
            
            content = clutter.Rectangle()
            content.set_color('#00000088')
            
            t = TexturedBlock('Nouveau block', content=content, textures_package=textures_package)
            t.set_size(800, 300)
            return t
        def remove_test_object(obj, stage):
            obj.destroy()
            return False
        
        def test_memory(stage, counter, max_count, textures_package):
            if counter < max_count or max_count == 0:
                counter += 1
                print counter
                tested_object = create_test_object(textures_package)
                stage.add(tested_object)
                gobject.timeout_add(2, remove_tested_object, tested_object, stage, counter, textures_package)
            return False
        
        def remove_tested_object(tested_object, stage, counter, textures_package):
            remove_test_object(tested_object, stage)
            
            gc.collect()
            pprint(gc.garbage)
            
            gobject.timeout_add(2, test_memory, stage, counter, max_count, textures_package)
            return False
        
        gobject.timeout_add(10, test_memory, stage, 0, max_count, textures_package)

    
    stage.show()
    clutter.main()
    
    
