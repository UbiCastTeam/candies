import sys
import gobject
import clutter

from clutter import cogl

class OutlinedRoundRectangle(clutter.Actor):
    __gtype_name__ = 'OutlinedRoundRectangle'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'radius': (
            gobject.TYPE_FLOAT, 'Radius', 'Radius of the round angles',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
    }
    
    def __init__(self):
        clutter.Actor.__init__(self)
        self._color = clutter.color_from_string('Black')
        self._radius = 0.0
    
    def set_color(self, color):
        self._color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_radius(self, radius):
        self._radius = radius
        self.queue_redraw()
    
    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self.set_color(value)
        elif pspec.name == 'radius':
            self.set_radius(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self._color
        elif pspec.name == 'radius':
            return self._radius
        else:
            raise TypeError('Unknown property ' + pspec.name)
    
    def __paint_rectangle(self, width, height, color):
        cogl.path_round_rectangle(0, 0, width, height, self._radius, 1)
        cogl.path_close()
        cogl.set_source_color(color)
        cogl.path_stroke()
    
    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()

        paint_color = self._color
        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha
        
        self.__paint_rectangle(x2 - x1, y2 - y1, paint_color)

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return

        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__paint_rectangle(x2 - x1, y2 - y1, pick_color)


class RoundRectangle(OutlinedRoundRectangle):
    """
    RoundRectangle (clutter.Actor)

    A simple actor drawing a rectangle with round angles using the clutter.cogl
    primitives.
    """
    __gtype_name__ = 'RoundRectangle'
    __gproperties__ = {
        'border_color': (
            str, 'border color', 'Border color', None, gobject.PARAM_READWRITE
        ),
        'border_width' : (
            gobject.TYPE_FLOAT, 'border width', 'Border width',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
    }

    def __init__(self, light_path=None, dark_path=None):
        OutlinedRoundRectangle.__init__(self)
        self._border_color = clutter.color_from_string('Black')
        self._border_width = 0.0
        self._light_path = light_path
        self._dark_path = dark_path

    def set_border_color(self, color):
        self._border_color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_border_width(self, width):
        self._border_width = width
        self.queue_redraw()

    def do_set_property(self, pspec, value):
        if pspec.name == 'border-color':
            self.set_border_color(value)
        elif pspec.name == 'border-width':
            self.set_border_width(value)
        else:
            OutlinedRoundRectangle.do_set_property(self, pspec, value)
            return

    def do_get_property(self, pspec):
        if pspec.name == 'border-color':
            return self._border_color
        elif pspec.name == 'border-width':
            return self._border_width
        else:
            return OutlinedRoundRectangle.do_get_property(self, pspec)

    def __paint_rectangle(self, width, height, color, border_color=None):
        if border_color is not None and self._border_width > 0.0:
            cogl.path_round_rectangle(0, 0, width, height, self._radius, 1)
            cogl.path_close()
            cogl.set_source_color(border_color)
            cogl.path_fill()
            
            w = self._border_width
            cogl.path_round_rectangle(w, w, width - w, height - w, self._radius - w, 1)
            cogl.path_close()
            cogl.set_source_color(color)
            cogl.path_fill()
            
            # light texture
            if self._light_path:
                cogl.path_round_rectangle(w, w, width - w, height - w, self._radius - w, 1)
                cogl.path_close()
                cogl.set_source_texture(cogl.texture_new_from_file(self._light_path))
                cogl.path_fill()
            # dark texture
            if self._dark_path:
                cogl.path_round_rectangle(w, w, width - w, height - w, self._radius - w, 1)
                cogl.path_close()
                cogl.set_source_texture(cogl.texture_new_from_file(self._dark_path))
                cogl.path_fill()
        else:
            cogl.path_round_rectangle(0, 0, width, height, self._radius, 1)
            cogl.path_close()
            cogl.set_source_color(color)
            cogl.path_fill()
    
    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()

        paint_color = self._color
        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha
        
        border_color = self._border_color
        real_alpha = self.get_paint_opacity() * border_color.alpha / 255
        border_color.alpha = real_alpha

        self.__paint_rectangle(x2 - x1, y2 - y1, paint_color, border_color)


if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    rect = OutlinedRoundRectangle()
    rect.set_radius(25)
    rect.set_color('#ff0000ff')
    rect.set_size(160, 120)
    rect.set_anchor_point(80, 60)
    rect.set_position(160, 240)
    stage.add(rect)
    
    rect = RoundRectangle()
    rect.set_radius(25)
    rect.set_color('#0000ffff')
    rect.set_border_width(5)
    rect.set_size(160, 120)
    rect.set_anchor_point(80, 60)
    rect.set_position(480, 240)
    stage.add(rect)

    stage.show()

    clutter.main()
