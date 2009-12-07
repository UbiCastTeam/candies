import gobject
import clutter

class Box(clutter.Actor, clutter.Container):
    """
    A Box container.
    """
    __gtype_name__ = 'Box'
    
    def __init__(self, horizontal=True, spacing=0.0, border=0.0):
        clutter.Actor.__init__(self)
        self.elements = list()
        self.spacing = spacing
        self.border = border
        if horizontal == True:
            self._horizontal = True
        else:
            self._horizontal = False
    
    def get_element(self, name):
        for element in self.elements:
            if element['name'] == name:
                return element
        return None
    
    def do_set_property (self, pspec, value):
        if pspec.name == 'elements':
            self.elements = value
        elif pspec.name == 'spacing':
            self.spacing = value
        elif pspec.name == 'border':
            self.border = value
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def do_get_property (self, pspec):
        if pspec.name == 'elements':
            return self.elements
        elif pspec.name == 'spacing':
            return self.spacing
        elif pspec.name == 'border':
            return self.border
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def add(self, *new_elements):
        for new_ele in new_elements:
            if 'name' not in new_ele or 'object' not in new_ele:
                raise KeyError('Element must contain name and object')
            self.elements.append(new_ele)
            self.get_element(new_ele['name'])['object'].set_parent(self)
    
    def do_remove(self, *children):
        for child in children:
            if element in self.elements:
                element['object'].remove(child)
                child.unparent()
    
    def clear(self):
        for element in self.elements:
            element['object'].destroy()
        self.elements = list()
    
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
        # ajouter le bord
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
        main_width = box.x2 - box.x1 - 2*self.border
        main_height = box.y2 - box.y1 - 2*self.border
        
        #find number of resizable elements and size available for resizable elements
        resizable_count = 0
        resizable_elements = list()
        resizable_width = main_width
        resizable_height = main_height
        for element in self.elements:
            if 'resizable' in element and element['resizable'] != 0:
                resizable_count += 1
                resizable_elements.append(element)
            else:
                resizable_width -= element['object'].get_width()
                resizable_height -= element['object'].get_height()
            resizable_width -= self.spacing
            resizable_height -= self.spacing
        resizable_width += self.spacing
        resizable_height += self.spacing
        
        
        x = 0.0
        y = 0.0
        #ajouter le bord
        x += self.border
        y += self.border
        for element in self.elements:
            obj_width = element['object'].get_width()
            obj_height = element['object'].get_height()
            if element in resizable_elements:
                if element['resizable'] > 1:
                    element['resizable'] = 1
                elif element['resizable'] < 0:
                    element['resizable'] = 0
                if self._horizontal == True:
                    obj_width = element['resizable'] * resizable_width
                else:
                    obj_height = element['resizable'] * resizable_height
            
            objbox = clutter.ActorBox()
            objbox.x1 = x
            objbox.y1 = y
            objbox.x2 = x + obj_width
            objbox.y2 = y + obj_height
            element['object'].allocate(objbox, flags)
            if self._horizontal == True:
                x += obj_width + self.spacing
            else:
                y += obj_height + self.spacing
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for element in self.elements:
            func(element['object'], data)
    
    def do_paint(self):
        for element in self.elements:
            element['object'].paint()
    
    def do_pick(self, color):
        for element in self.elements:
            element['object'].paint()


if __name__ == '__main__':
    import buttons
    
    # stage
    stage_width = 640
    stage_height = 480
    stage = clutter.Stage()
    stage.set_size(stage_width, stage_height)
    stage.connect('destroy', clutter.main_quit)
    
    # background texture
    global_bg = clutter.Rectangle()
    global_bg.set_position(0, 0)
    global_bg.set_size(stage_width, stage_height)
    global_bg.set_color('#000000ff')
    stage.add(global_bg)
    
    
    rect_bg_width = 400
    rect_bg_height = 400
    rect_bg = clutter.Rectangle()
    rect_bg.set_size(rect_bg_width, rect_bg_height)
    rect_bg.set_color('#ffffffff')
    stage.add(rect_bg)
    
    
    rect1 = clutter.Rectangle()
    rect1.set_size(200, 100)
    rect1.set_color(clutter.color_from_string('Black'))
    
    rect2 = clutter.Rectangle()
    rect2.set_size(30, 30)
    rect2.set_color(clutter.color_from_string('Blue'))
    
    rect3 = clutter.Rectangle()
    rect3.set_size(20, 20)
    rect3.set_color(clutter.color_from_string('Yellow'))
    
    rect4 = clutter.Rectangle()
    rect4.set_size(10, 10)
    rect4.set_color(clutter.color_from_string('Red'))
    
    line = Box(horizontal=False, spacing=10.0, border=20.0)
    line.add({'name': 'rect1',
        'object': rect1},
        {'name': 'rect2',
        'resizable': 0.8,
        'object': rect2},
        {'name': 'rect3',
        'resizable': 0.2,
        'object': rect3},
        {'name': 'rect4',
        'object': rect4})
    line.set_size(rect_bg_width, rect_bg_height)
    stage.add(line)
    
    def on_click(btn_test, event):
        color_a = '#ff000088'
        color_b = '#ff0000ff'
        current_color = line.get_element('rect4')['object'].get_color()
        if str(current_color) == color_a:
            line.get_element('rect4')['object'].set_color(color_b)
        else:
            line.get_element('rect4')['object'].set_color(color_a)
    btn_test = buttons.ClassicButton('test')
    btn_test.set_position(0, 430)
    btn_test.set_size(50, 50)
    btn_test.set_reactive(True)
    btn_test.connect('button-press-event', on_click)
    stage.add(btn_test)
    
    stage.show()
    clutter.main()
    
    
