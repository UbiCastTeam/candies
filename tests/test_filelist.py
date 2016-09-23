#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lightweight file system browser.

python test_filelist.py /mnt/recordings
"""
from gi.repository import Clutter
import os
import sys
import gobject
from candies2 import FileList, ClassicButton, VideoPlayer
import re

image_pattern = re.compile(r'.+\.(jpe?g|png|gif|svg)$')
video_pattern = re.compile(r'.+\.(mpe?g?4|dv|ogg)$')

stage = Clutter.Stage()
stage.connect('destroy', Clutter.main_quit)

info = Clutter.Text()
info.set_color(Clutter.color_from_string('Black'))
info.set_position(245, 5)
info.set_width(640 - 250)
info.set_line_wrap(True)
info.hide()

texture = Clutter.Texture()
texture.set_x(245)
texture.hide()

def on_video_pressed(player, event):
    if event.button == 1:
        player.toggle_playing()
    else:
        is_playing = player.get_playing()
        player.set_filename(player.get_uri())
        if is_playing:
            player.play()

player = VideoPlayer()
player.set_x(245)
player.props.keep_aspect_ratio = True
player.set_width(640 - 250)
player.set_reactive(True)
player.connect('button-press-event', on_video_pressed)
player.hide()

def on_directory_changed(lst, event):
    stage.set_title(lst.props.directory)

def on_file_selected(lst):
    filename = lst.selection[0].label.get_text()
    path = os.path.join(lst.props.directory, filename)
    texture.hide()
    info.hide()
    player.hide()
    player.stop()
    if os.path.isdir(path):
        lst.props.directory = path
        return
    info_text = os.popen('file "%s"' %(path)).read()
    info.set_text(info_text[len(path) + 2:-1])
    info.show()
    if image_pattern.match(filename):
        texture.set_from_file(path)
        texture.set_y(info.get_height() + 10)
        texture.show()
    elif video_pattern.match(filename):
        player.set_filename(path)
        player.set_height(player.get_preferred_height(640 - 250)[1])
        player.set_y(info.get_height() + 10)
        player.show()

dir = os.getcwd()
if len(sys.argv) > 1:
    dir = sys.argv[1]
stage.set_title(dir)
lst = FileList(dir, '^[^.].*')
lst.connect('notify::directory', on_directory_changed)
lst.spacing = 4
lst.set_width(240)
lst.set_y(38)
lst.connect('select-event', on_file_selected)

def on_button_press(btn, event):
    texture.hide()
    info.hide()
    lst.props.directory = os.path.dirname(lst.props.directory)

btn = ClassicButton('Parent directory')
btn.set_y(4)
btn.set_size(*btn.get_preferred_size()[2:])
btn.set_width(btn.get_width() + 20)
btn.set_reactive(True)
btn.connect('button-press-event', on_button_press)

stage.add(lst, btn, texture, info, player)
stage.show()
Clutter.main()
