import gobject
import clutter
import os

class ProgressBar(clutter.Actor, clutter.Container):
    
    (_TRACK_LEFT, _TRACK_MIDDLE, _TRACK_RIGHT,
                  _PROGRESS_LEFT, _PROGRESS_MIDDLE, _PROGRESS_RIGHT) = range(6)
    __gtype_name__ = 'ProgressBar'
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

gobject.type_register(ProgressBar)