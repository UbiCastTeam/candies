#!/usr/bin/env python
from gi.repository import GObject
from gi.repository import Clutter
import cairo
import math
from candies2.utils import get_clutter_color, get_rgba_color


class RoundRectangle(Clutter.Actor):
    '''a horizontal item inside a row'''

    def __init__(self):
        super(RoundRectangle, self).__init__()
        self.canvas = Clutter.Canvas()
        self.set_content(self.canvas)
        self.canvas.connect('draw', self.draw)
        self.line_width = 5
        self.border_radius = 50
        self.fill_color = get_rgba_color('red')
        self.stroke_color = get_rgba_color('blue')

        self.connect('notify::allocation', self.on_allocation)

    def on_allocation(self, *kwargs):
        GObject.idle_add(self.idle_resize)

    def idle_resize(self):
        self.canvas.set_size(*self.get_size())

    def draw(self, canvas, ctx, width, height):
        radius = self.border_radius
        if width <= radius * 2 or height <= radius * 2:
            radius = min((width, height)) / 2

        # clear the previous frame
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()

        ctx.set_operator(cairo.OPERATOR_OVER)
        x = self.line_width
        y = self.line_width
        w = width - self.line_width * 2
        h = height - self.line_width * 2
        ctx.new_sub_path()
        ctx.arc(x + w - radius, y + h - radius, radius, 0, math.pi / 2)
        ctx.arc(x + radius, y + h - radius, radius, math.pi / 2, math.pi)
        ctx.arc(x + radius, y + radius, radius, math.pi, math.pi * 3 / 2)
        ctx.arc(x + w - radius, y + radius, radius, math.pi * 3 / 2, math.pi * 2)
        ctx.close_path()

        ctx.set_source_rgba(*self.fill_color)
        ctx.fill_preserve()  # fill but keep the rectangle
        ctx.set_line_width(self.line_width)
        ctx.set_source_rgba(*self.stroke_color)
        ctx.stroke()


if __name__ == '__main__':
    def stage_key(element, event):
        if event.keyval == Clutter.Escape:
            clutter_quit()

    def clutter_quit(*args):
        Clutter.main_quit()

    Clutter.init()
    stage = Clutter.Stage()
    stage.set_size(800, 500)
    stage.set_title('Clutter - Cairo content')
    stage.set_background_color(get_clutter_color('white'))
    stage.set_user_resizable(True)

    # quit when the window gets closed
    stage.connect('destroy', clutter_quit)

    # close window on escape
    stage.connect('key-press-event', stage_key)

    cairo_actor = RoundRectangle()
    stage.add_child(cairo_actor)

    # bind the size of cairo_actor to the size of the stage
    cairo_actor.add_constraint(Clutter.BindConstraint.new(stage, Clutter.BindCoordinate.SIZE, 0.0))

    stage.show()
    Clutter.main()
