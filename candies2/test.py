#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from gi.repository import Clutter


def run_test(fct):

    def stage_key(element, event):
        if event.keyval == Clutter.Escape:
            clutter_quit()

    def clutter_quit(*args):
        Clutter.main_quit()

    Clutter.init()
    stage = Clutter.Stage()
    stage.set_size(800, 600)
    stage.set_background_color(Clutter.color_from_string('white')[1])
    stage.set_title('Clutter - Test %s' % fct.__name__)
    # quit when the window gets closed
    stage.connect('destroy', clutter_quit)
    # close window on escape
    stage.connect('key-press-event', stage_key)

    fct(stage)

    stage.show()
    try:
        Clutter.main()
    except KeyboardInterrupt:
        sys.exit(0)
