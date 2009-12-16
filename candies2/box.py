import gobject
import clutter

class Box(clutter.Actor, clutter.Container):
    """
    A stacking box container.
    
    Works horizontally and vertically (see HBox and VBox for shortcut classes).
    
    The elements contained in a box are defined by a clutter actor (the
    children of the container), a name (str) and optional properties.
    
    Element properties can be :
    
        - resizable (float) : if set, defines the proportion an element take in
          the available place (value is between 0 and 1). It applies to width
          in horizontal box and to height in vertical one.
        
        - expand (bool) : if True, the element size is expanded on the whole
          box height (for horizontal boxes) and on the whole box width (for
          vertical ones).
        
        - keep_ratio (bool) : if True, the element resized because of the
          resizable or expand properties while keep its natural aspect ratio.
          (Please don't set it to True when resizable and expand are both set!)
        
        - center (bool) : if True, the element is centered (vertically for
          horizontal box and vice-versa).
    """
    __gtype_name__ = 'Box'
    
    def __init__(self, horizontal=True, spacing=0.0, border=0.0):
        clutter.Actor.__init__(self)
        self.elements = list()
        self.background = None
        self.spacing = spacing
        self.border = border
        if horizontal == True:
            self._horizontal = True
        else:
            self._horizontal = False
    
    def get_by_name(self, name):
        for element in self.elements:
            if element['name'] == name:
                return element
        return None
    
    def set_background(self, background):
        self.background = background
        background.set_parent(self)
    
    def remove_background(self):
        if self.background != None:
            self.background.unparent()
            self.background = None
    
    def add(self, *new_elements):
        for new_ele in new_elements:
            if 'name' not in new_ele or 'object' not in new_ele:
                raise KeyError('Element must contain name and object')
            self.elements.append(new_ele)
            new_ele['object'].set_parent(self)
    
    def add_element(self, obj, name, **properties):
        element = properties.copy()
        element['name'] = name
        element['object'] = obj
        self.add(element)
    
    def do_remove(self, actor):
        if self.background == actor:
            actor.unparent()
            self.background = None
        for element in self.elements:
            if element['object'] == actor:
                actor.unparent()
                self.elements.remove(element)
    
    def remove_element(self, name):
        element = self.get_by_name(name)
        if element:
            element['object'].unparent()
            self.elements.remove(element)
    
    def clear(self):
        for element in self.elements:
            element['object'].destroy()
        self.elements = list()
        self.background.destroy()
        self.background = None
    
    def _compute_preferred_size(self):
        min_w = min_h = nat_w = nat_h = 0.0
        for element in self.elements:
            s = element['object'].get_preferred_size()
            if self._horizontal == True:
                min_w += s[0] + self.spacing
                min_h = max(min_h, s[1])
                nat_w += s[2] + self.spacing
                nat_h = max(nat_h, s[3])
            else:
                min_w = max(min_w, s[0])
                min_h += s[1] + self.spacing
                nat_w = max(nat_w, s[2])
                nat_h += s[3] + self.spacing
        # enlever la marge a la fin
        if self._horizontal == True:
            min_w -= self.spacing
            nat_w -= self.spacing
        else:
            min_h -= self.spacing
            nat_h -= self.spacing
        # add border
        min_w += 2*self.border
        nat_w += 2*self.border
        min_h += 2*self.border
        nat_h += 2*self.border
        return min_w, min_h, nat_w, nat_h
    
    def do_get_preferred_width(self, for_height):
        preferred = self._compute_preferred_size()
        return preferred[0], preferred[2]
    
    def do_get_preferred_height(self, for_width):
        preferred = self._compute_preferred_size()
        return preferred[1], preferred[3]
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        inner_width = main_width - 2*self.border
        inner_height = main_height - 2*self.border
        
        #box background
        if self.background:
            bgbox = clutter.ActorBox()
            bgbox.x1 = 0
            bgbox.y1 = 0
            bgbox.x2 = main_width
            bgbox.y2 = main_height
            self.background.allocate(bgbox, flags)
        
        
        #find size available for resizable elements
        resizable_elements = list()
        resizable_width = inner_width
        resizable_height = inner_height
        for element in self.elements:
            if element.get('resizable', 0) != 0:
                if element['resizable'] > 1:
                    element['resizable'] = 1
                elif element['resizable'] < 0:
                    element['resizable'] = 0
                resizable_elements.append(element)
            else:
                resizable_width -= element['object'].get_preferred_size()[2]
                resizable_height -= element['object'].get_preferred_size()[3]
            resizable_width -= self.spacing
            resizable_height -= self.spacing
        resizable_width += self.spacing
        resizable_height += self.spacing
        
        #find resizable elements who will bypass box size
        for element in self.elements:
            if element.get('resizable', 0) != 0:
                original_width, original_height = element['object'].get_preferred_size()[2:]
                if self._horizontal is True:
                    if element.get('keep_ratio') is True and original_width != 0:
                        obj_width = element['resizable'] * resizable_width
                        ratio = float(obj_width/original_width)
                        obj_height = int(original_height*ratio)
                        if obj_height > inner_height:
                            # reduce resizable property
                            ratio = float(inner_height/original_height)
                            obj_width = int(original_width*ratio)
                            element['resizable'] = float(obj_width/resizable_width)
                else:
                    if element.get('keep_ratio') is True and original_height != 0:
                        obj_height = element['resizable'] * resizable_height
                        ratio = float(obj_height/original_height)
                        obj_width = int(original_width*ratio)
                        if obj_width > inner_width:
                            # reduce resizable property
                            ratio = float(inner_width/original_width)
                            obj_height = int(original_height*ratio)
                            element['resizable'] = float(obj_height/resizable_height)
        
        x = self.border
        y = self.border
        for element in self.elements:
            obj_width, obj_height = element['object'].get_preferred_size()[2:]
            if element.get('expand') is True:
                if self._horizontal is True:
                    original_height = obj_height
                    obj_height = inner_height
                    if element.get('keep_ratio') is True and original_height != 0:
                        ratio = float(obj_height/original_height)
                        obj_width = int(obj_width*ratio)
                else:
                    original_width = obj_width
                    obj_width = inner_width
                    if element.get('keep_ratio') is True and original_width != 0:
                        ratio = float(obj_width/original_width)
                        obj_height = int(obj_height*ratio)
            if element in resizable_elements:
                if self._horizontal is True:
                    original_width = obj_width
                    obj_width = element['resizable'] * resizable_width
                    if element.get('keep_ratio') is True and original_width != 0:
                        ratio = float(obj_width/original_width)
                        obj_height = int(obj_height*ratio)
                else:
                    original_height = obj_height
                    obj_height = element['resizable'] * resizable_height
                    if element.get('keep_ratio') is True and original_height != 0:
                        ratio = float(obj_height/original_height)
                        obj_width = int(obj_width*ratio)
            # Manage centering
            x_offset = 0
            y_offset = 0
            if element.get('center') is True:
                if self._horizontal is True:
                    y_offset = max(0, (inner_height - obj_height) / 2)
                else:
                    x_offset = max(0, (inner_width - obj_width) / 2)
            
            objbox = clutter.ActorBox()
            objbox.x1 = round(x + x_offset)
            objbox.y1 = round(y + y_offset)
            objbox.x2 = round(x + x_offset + obj_width)
            objbox.y2 = round(y + y_offset + obj_height)
            element['object'].allocate(objbox, flags)
            if self._horizontal is True:
                x += obj_width + self.spacing
            else:
                y += obj_height + self.spacing
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        if self.background:
            func(self.background, data)
        for element in self.elements:
            func(element['object'], data)
    
    def do_destroy(self):
        if self.background:
            self.background.destroy()
        for element in self.elements:
            element['object'].destroy()
    
    def do_paint(self):
        if self.background:
            self.background.paint()
        for element in self.elements:
            element['object'].paint()

class HBox(Box):
    
    def __init__(self, *args, **kw):
        Box.__init__(self, horizontal=True, *args, **kw)

class VBox(Box):
    
    def __init__(self, *args, **kw):
        Box.__init__(self, horizontal=False, *args, **kw)

class AlignedElement(clutter.Actor, clutter.Container):
    __gtype_name__ = 'AlignedElement'

    def __init__(self, align='center', border=0.0):
        clutter.Actor.__init__(self)
        if align == 'top_left':
            self.align = 'top_left'
        elif align == 'top':
            self.align = 'top'
        elif align == 'top_right':
            self.align = 'top_right'
        elif align == 'left':
            self.align = 'left'
        elif align == 'center':
            self.align = 'center'
        elif align == 'right':
            self.align = 'right'
        elif align == 'bottom_left':
            self.align = 'bottom_left'
        elif align == 'bottom':
            self.align = 'bottom'
        elif align == 'bottom_right':
            self.align = 'bottom_right'
        else:
            self.align = 'center'
        self.border = border
        self.element = None
        self.background = None
    
    def set_background(self, background):
        if self.background:
            self.background.unparent()
        self.background = background
        background.set_parent(self)
    
    def remove_background(self):
        if self.background:
            self.background.unparent()
            self.background = None
    
    def set_element(self, new_element):
        if self.element:
            self.element.unparent()
        self.element = new_element
        self.element.set_parent(self)
    
    def remove_element(self):
        if self.element:
            self.element.unparent()
            self.element = None
    
    def do_remove(self, actor):
        if self.background == actor:
            actor.unparent()
            self.background = None
        if self.element == actor:
            actor.unparent()
            self.elements = None
    
    def clear(self):
        if self.element:
            self.element.destroy()
            self.element = None
        if self.background:
            self.background.destroy()
            self.background = None
    
    def _compute_preferred_size(self):
        if self.element:
            return self.element.get_preferred_size()
        else:
            return 0, 0, 0, 0
    
    def do_get_preferred_width(self, for_height):
        preferred = self._compute_preferred_size()
        return preferred[0], preferred[2]
    
    def do_get_preferred_height(self, for_width):
        preferred = self._compute_preferred_size()
        return preferred[1], preferred[3]
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        inner_width = main_width - 2*self.border
        inner_height = main_height - 2*self.border
        
        #box background
        if self.background:
            bgbox = clutter.ActorBox()
            bgbox.x1 = 0
            bgbox.y1 = 0
            bgbox.x2 = main_width
            bgbox.y2 = main_height
            self.background.allocate(bgbox, flags)
        
        if self.element:
            element_width, element_height = self.element.get_preferred_size()[2:]
            ele_x1 = self.border
            ele_y1 = self.border
            ele_x2 = self.border
            ele_y2 = self.border
            if self.align == 'top_left' or self.align == 'left' or self.align == 'bottom_left':
                ele_x1 = self.border
                ele_x2 = self.border + element_width
            if self.align == 'top_right' or self.align == 'right' or self.align == 'bottom_right':
                ele_x1 = main_width - self.border - element_width
                ele_x2 = main_width - self.border
            if self.align == 'top_left' or self.align == 'top' or self.align == 'top_right':
                ele_y1 = self.border
                ele_y2 = self.border + element_height
            if self.align == 'bottom_left' or self.align == 'bottom' or self.align == 'bottom_right':
                ele_y1 = main_height - self.border - element_height
                ele_y2 = main_height - self.border
            if self.align == 'center':
                ele_x1 = self.border + int((inner_width-element_width)/2)
                ele_x2 = self.border + int((inner_width-element_width)/2) + element_width
                ele_y1 = self.border + int((inner_height-element_height)/2)
                ele_y2 = self.border + int((inner_height-element_height)/2) + element_height
            elebox = clutter.ActorBox()
            elebox.x1 = ele_x1
            elebox.y1 = ele_y1
            elebox.x2 = ele_x2
            elebox.y2 = ele_y2
            self.element.allocate(elebox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        if self.background:
            func(self.background, data)
        if self.element:
            func(self.element, data)
    
    def do_destroy(self):
        if self.background:
            self.background.destroy()
        if self.element:
            self.element.destroy()
    
    def do_paint(self):
        if self.background:
            self.background.paint()
        if self.element:
            self.element.paint()

if __name__ == '__main__':
    import buttons
    
    # stage
    stage_width = 1200
    stage_height = 600
    stage = clutter.Stage()
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', clutter.main_quit)
    
    # background texture
    global_bg = clutter.Rectangle()
    global_bg.set_position(0, 0)
    global_bg.set_size(stage_width, stage_height)
    global_bg.set_color('#000000ff')
    stage.add(global_bg)
    
    
    rect_bg = clutter.Rectangle()
    rect_bg.set_color('#ffffffff')
    
    
    rect1 = clutter.Rectangle()
    rect1.set_size(200, 100)
    rect1.set_color(clutter.color_from_string('Black'))
    
    rect2 = clutter.Rectangle()
    rect2.set_size(100, 30)
    rect2.set_color(clutter.color_from_string('Blue'))
    
    rect3 = clutter.Rectangle()
    rect3.set_size(20, 20)
    rect3.set_color(clutter.color_from_string('Yellow'))
    
    rect4 = clutter.Rectangle()
    rect4.set_size(10, 10)
    rect4.set_color(clutter.color_from_string('Red'))
    
    line = Box(horizontal=False, spacing=10.0, border=20.0)
    line.set_background(rect_bg)
    line.add({'name': 'rect1',
        'center': True,
        'object': rect1},
        {'name': 'rect2',
        'expand': True,
        'resizable': 0.8,
        'keep_ratio': True,
        'object': rect2},
        {'name': 'rect3',
        'resizable': 0.2,
        'object': rect3},
        {'name': 'rect4',
        'object': rect4})
    line.set_size(400, 400)
    line.set_position(30, 30)
    stage.add(line)
    
    def on_click(btn_test, event):
        print 'click'
        color_a = '#ff000088'
        color_b = '#ff0000ff'
        current_color = line.get_by_name('rect4')['object'].get_color()
        if str(current_color) == color_a:
            line.get_by_name('rect4')['object'].set_color(color_b)
        else:
            line.get_by_name('rect4')['object'].set_color(color_a)
    btn_test = AlignedElement()
    btn_rect = clutter.Rectangle()
    btn_rect.set_color('#ff00ffff')
    btn_test.set_background(btn_rect)
    btn_test.set_position(80, 480)
    btn_test.set_size(50, 50)
    btn_test.set_reactive(True)
    btn_test.connect('button-press-event', on_click)
    stage.add(btn_test)
    
    
    
    other_box = Box(horizontal=True, spacing=10.0, border=20.0)
    
    rect5 = clutter.Rectangle()
    rect5.set_size(250, 150)
    rect5.set_color(clutter.color_from_string('Black'))
    
    rect6 = clutter.Rectangle()
    rect6.set_size(5, 5)
    rect6.set_color(clutter.color_from_string('Blue'))
    
    rect_bg_2 = clutter.Rectangle()
    rect_bg_2.set_color('#ffffffff')
    
    other_box.set_background(rect_bg_2)
    other_box.add({'name': 'rect5',
        'expand': True,
        'object': rect5},
        {'name': 'rect6',
        #'expand': True,
        'resizable': 1.0,
        'keep_ratio': True,
        'object': rect6})
    other_box.set_size(400, 300)
    other_box.set_position(500, 30)
    stage.add(other_box)
    
    stage.show()
    clutter.main()
    
    
