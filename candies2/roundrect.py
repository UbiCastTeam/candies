import sys
import gobject
import clutter

from clutter import cogl

class RoundRectangle(clutter.Actor):
    """
    RoundRectangle (clutter.Actor)

    A simple actor drawing a rectangle with round angles using the clutter.cogl
    primitives.
    """
    __gtype_name__ = 'RoundRectangle'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'radius': (
            gobject.TYPE_FLOAT, 'Radius', 'Radius of the round angles',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
        'border_color': (
            str, 'border color', 'Border color', None, gobject.PARAM_READWRITE
        ),
        'border_width' : (
            gobject.TYPE_FLOAT, 'border width', 'Border width',
            0.0, sys.maxint, 0.0, gobject.PARAM_READWRITE
        ),
    }

    def __init__(self):
        clutter.Actor.__init__(self)
        self._color = clutter.color_from_string('Black')
        self._border_color = clutter.color_from_string('Black')
        self._border_width = 0.0
        self._radius = 0.0

    def set_color(self, color):
        self._color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_border_color(self, color):
        self._border_color = clutter.color_from_string(color)
        self.queue_redraw()
    
    def set_border_width(self, width):
        self._border_width = width
        self.queue_redraw()

    def set_radius(self, radius):
        self._radius = radius
        self.queue_redraw()

    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self._color = clutter.color_from_string(value)
        elif pspec.name == 'border-color':
            self._border_color = clutter.color_from_string(value)
        elif pspec.name == 'border-width':
            self._border_width = value
        elif pspec.name == 'radius':
            self._radius = value
        else:
            raise TypeError('Unknown property ' + pspec.name)
        self.queue_redraw()

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self._color
        elif pspec.name == 'border-color':
            return self._border_color
        elif pspec.name == 'border-width':
            return self._border_width
        elif pspec.name == 'radius':
            return self._radius
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def __paint_rectangle(self, width, height, color, border_color=None):
        cogl.path_round_rectangle(0, 0, width, height, self._radius, 1)
        cogl.path_close()
        
        if border_color is not None and self._border_width > 0.0:
            cogl.set_source_color(border_color)
            cogl.path_fill()
            
            w = self._border_width
            cogl.path_round_rectangle(
                                  w, w, width - w, height - w, self._radius - w, 1)
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

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return

        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__paint_rectangle(x2 - x1, y2 - y1, pick_color)

gobject.type_register(RoundRectangle)

if __name__ == '__main__':
    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    rect = RoundRectangle()
    rect.set_radius(25)
    rect.set_color('Blue')
    rect.set_border_width(5)
    rect.set_size(320, 240)
    rect.set_anchor_point(160, 120)
    rect.set_position(320, 240)
    stage.add(rect)

    stage.show()

    clutter.main()
