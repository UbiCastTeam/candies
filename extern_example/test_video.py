#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
from gi.repository import Clutter
from gi.repository import ClutterGst
from gi.repository import Gst


def on_size_change(texture, width, height):
    stage = texture.get_stage()
    if stage is None:
        return
    stage.set_size(width, height)
    texture.set_position(0, 0)
    texture.set_size(width, height)


def on_error(bus, msg):
    print('on_error():', msg.parse_error())


def on_destroy(*args):
    Clutter.main_quit()


def __init__(uri):
    stage = Clutter.Stage()
    stage.connect('destroy', on_destroy)
    texture = Clutter.Texture()
    if texture is None:
        return 2
    texture.connect('size-change', on_size_change)
    pipeline = Gst.ElementFactory.make('playbin', None)
    if pipeline is None:
        return 3
    bus = pipeline.get_bus()
    bus.connect('message::error', on_error)
    pipeline.set_property('uri', uri)
    sink = Gst.ElementFactory.make('autocluttersink', None)
    if sink is None:
        return 4
    sink.set_property('texture', texture)
    pipeline.set_property('video-sink', sink)
    pipeline.set_state(Gst.State.PLAYING)
    stage.add_actor(texture)
    stage.show_all()
    Clutter.main()
    pipeline.set_state(Gst.State.NULL)
    del pipeline
    return 0


def main(argv):
    if ClutterGst.init(argv)[0] != 1:  # Clutter.INIT_SUCCESS:
        return 1
    return __init__(*argv[1:])

if __name__ == '__main__':
    exit(main(argv))
