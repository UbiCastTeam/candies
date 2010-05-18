import gobject
import clutter
import os

from clutter import cogl

class SimpleProgressBar(clutter.Actor):
    
    __gtype_name__ = 'SimpleProgressBar'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'progression': (
            gobject.TYPE_FLOAT, 'Progression', 'Progression value',
            0.0, 1.0, 0.0, gobject.PARAM_READWRITE
        ),
    }

    def __init__(self):
        clutter.Actor.__init__(self)
        self._color = clutter.color_from_string('Black')
        self._progression = 0.0
    
    def set_progression(self, value):
        self._progression = value
        self.notify("progression")
        self.queue_relayout()
    
    def set_color(self, color):
        self._color = clutter.color_from_string(color)
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'progression':
            self.set_progression(value)
        elif pspec.name == 'color':
            self._color = clutter.color_from_string(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def do_get_property(self, pspec):
        if pspec.name == 'progression':
            return self._progression
        elif pspec.name == 'color':
            return self._color
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def __paint_oval(self, width, height, radius):
        radius0 = height / 2
        
        cogl.path_move_to(radius0, height)
        cogl.path_arc(radius0, radius0, radius, radius, 90, 270)
        cogl.path_line_to(width - radius0, radius0 - radius)
        cogl.path_arc(width - radius0, radius0, -radius, -radius, -270, -90)
        cogl.path_line_to(radius0, height - radius0 + radius)
    
    def __paint_bar(self, width, height, color):
        cogl.set_source_color(color)
        
        radius0 = height / 2
        cogl.path_move_to(radius0, height)
        cogl.path_arc(radius0, radius0, radius0, radius0, 90, 270)
        cogl.path_line_to(radius0, 4)
        cogl.path_arc(radius0, radius0, radius0 - 4, radius0 - 4, -270, -90)
        cogl.path_close()
        cogl.path_fill()
        
        cogl.rectangle(radius0, 0, width - radius0, 4)
        cogl.rectangle(radius0, height - 4, width - radius0, height)
        
        cogl.path_move_to(width - radius0, 0)
        cogl.path_arc(width - radius0, radius0, -radius0, -radius0, -270, -90)
        cogl.path_line_to(width - radius0, height - 4)
        cogl.path_arc(width - radius0, radius0, 4 - radius0, 4 - radius0, 90, 270)
        cogl.path_close()
        cogl.path_fill()
        
        if self._progression:
            radius = radius0 - 10
            cogl.path_move_to(radius0, height)
            cogl.path_arc(radius0, radius0, radius, radius, 90, 270)
            cogl.path_line_to(width - radius0, radius0 - radius)
            cogl.path_arc(radius0 + (width - 2 * radius0) * self._progression, radius0, -radius, -radius, -270, -90)
            cogl.path_line_to(radius0, height - radius0 + radius)
            cogl.path_close()
            cogl.path_fill()

    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()

        paint_color = self._color.copy()

        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha

        self.__paint_bar(x2 - x1, y2 - y1, paint_color)

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return
        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__paint_bar(x2 - x1, y2 - y1, pick_color)

gobject.type_register(SimpleProgressBar)


class SkinnedProgressBar(clutter.Actor, clutter.Container):
    
    (_TRACK_LEFT, _TRACK_MIDDLE, _TRACK_RIGHT,
                  _PROGRESS_LEFT, _PROGRESS_MIDDLE, _PROGRESS_RIGHT) = range(6)
    __gtype_name__ = 'SkinnedProgressBar'
    __gproperties__ = {
            'progression': (gobject.TYPE_FLOAT, 'Progression', 'Progression value',
                0.0, 1.0, 0.0, gobject.PARAM_READWRITE),
    }
    def __init__(self, skin_path):
        clutter.Actor.__init__(self)
        self._textures = (
            clutter.Texture(os.path.join(skin_path, 'track_left.png')),
            clutter.Texture(os.path.join(skin_path, 'track_middle.png')),
            clutter.Texture(os.path.join(skin_path, 'track_right.png')),
            clutter.Texture(os.path.join(skin_path, 'progress_left.png')),
            clutter.Texture(os.path.join(skin_path, 'progress_middle.png')),
            clutter.Texture(os.path.join(skin_path, 'progress_right.png')),
        )
        self.natural_height = 0
        for texture in self._textures:
            texture.show()
            texture.set_parent(self)
            self.natural_height = \
                      max(self.natural_height, texture.get_preferred_size()[3])
        self._progression = 0.0
    
    def set_progression(self, value):
        self._progression = value
        self.notify("progression")
        self.queue_relayout()

    def get_progression(self):
        return self._progression

    def do_get_property(self, pspec):
        if pspec.name == 'progression':
            return self.get_progression()
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'progression':
            self.set_progression(value)
    
    def do_get_preferred_width(self, for_height):
        minimal_width = \
            self._textures[self._TRACK_LEFT].get_preferred_width(for_height)[1] +\
            self._textures[self._TRACK_RIGHT].get_preferred_width(for_height)[1] \
            + 1
        natural_width = 2 * (
            self._textures[self._TRACK_LEFT].get_preferred_width(for_height)[1] +
            self._textures[self._TRACK_RIGHT].get_preferred_width(for_height)[1]
        )
        #print minimal_width, natural_width
        return minimal_width, natural_width
    
    def do_get_preferred_height(self, for_width):
        return self.natural_height, self.natural_height
    
    def do_allocate(self, box, flags):
        box_width, box_height = self.get_preferred_size()[2:]
        #print box_width, 'x', box_height
        
        minimal_width = self.do_get_preferred_width(box_height)[0]
        #print 'minimal', minimal_width
        
        texture = self._textures[self._TRACK_LEFT]
        box_tl = clutter.ActorBox()
        box_tl.x1 = 0
        box_tl.y1 = 0
        if box_width > minimal_width:
            texture.props.keep_aspect_ratio = True
            box_tl.x2 = texture.get_preferred_width(box_height)[1]
        else:
            texture.props.keep_aspect_ratio = False
            box_tl.x2 = box_width / 2 - 1
        box_tl.y2 = box_height
        texture.allocate(box_tl, flags)
        
        texture = self._textures[self._TRACK_RIGHT]
        box_tr = clutter.ActorBox()
        if box_width > minimal_width:
            texture.props.keep_aspect_ratio = True
            box_tr.x1 = box_width - texture.get_preferred_width(box_height)[1]
        else:
            texture.props.keep_aspect_ratio = False
            box_tr.x1 = box_width / 2 + 1
        box_tr.y1 = 0
        box_tr.x2 = box_width
        box_tr.y2 = box_height
        texture.allocate(box_tr, flags)
        
        texture = self._textures[self._TRACK_MIDDLE]
        box_tm = clutter.ActorBox()
        box_tm.x1 = box_tl.x2
        box_tm.y1 = 0
        box_tm.x2 = box_tr.x1
        box_tm.y2 = box_height
        texture.allocate(box_tm, flags)
        
        texture = self._textures[self._PROGRESS_LEFT]
        texture.allocate(box_tl, flags)
        if self._progression == 0.0:
            texture.hide()
        else:
            texture.show()
        
        texture = self._textures[self._PROGRESS_RIGHT]
        texture.allocate(box_tr, flags)
        if self._progression == 1.0:
            texture.show()
        else:
            texture.hide()
        
        texture = self._textures[self._PROGRESS_MIDDLE]
        box_pm = clutter.ActorBox()
        box_pm.x1 = box_tl.x2
        box_pm.y1 = 0
        box_pm.x2 = box_pm.x1 + (box_tr.x1 - box_tl.x2) * self._progression
        box_pm.y2 = box_height
        texture.allocate(box_pm, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for child in self._textures:
            func(child, data)
    
    def do_paint(self):
        for texture in self._textures:
            texture.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_textures'):
            for texture in self._textures:
                texture.unparent()
                texture.destroy()
            self._textures = list()

if __name__ == '__main__':
    def update_label(bar, event, label):
        label.set_text('%d %%' %(bar.props.progression * 100))
    
    def progress(bar):
        bar.props.progression = min(round(bar.props.progression + 0.002, 3), 1.0)
        return bar.props.progression < 1.0
    
    def on_button_press(stage, event, bar):
        bar.props.progression = 0.0
        gobject.timeout_add(10, progress, bar)
    
    stage = clutter.Stage()
    stage.set_reactive(True)
    stage.connect('destroy', clutter.main_quit)
    
    label = clutter.Text()
    label.set_position(5, 5)
    label.set_text('Click to launch progression...')
    stage.add(label)
    
    bar = SimpleProgressBar()
    bar.set_color('Cyan')
    bar.set_size(630, 100)
    bar.set_position(5, 30)
    bar.connect('notify::progression', update_label, label)
    stage.add(bar)
    stage.connect('button-press-event', on_button_press, bar)

    stage.show()

    clutter.main()
