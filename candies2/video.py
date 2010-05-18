#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Video player: cluttergst.VideoTexture wrapper

Copyright 2008, Florent Thiery, UbiCast
"""
from __future__ import division
from cluttergst import VideoTexture
import gobject
import gst

import logging
logger = logging.getLogger("videoplayer")

class VideoPlayer(VideoTexture):
    """
    Simple VideoPlayer

    This class wraps the clutter base VideoTexture object, itself
    wrapping the gstreamer playbin element.

    It can be called with an optional uri (either http:// or file://),
    or media initialization can be called later.

    preview_proportion is an optional percentage parameter that, if
    the media is seekable, lets you specify the place used as preview
    position.

    Available properties are:
        "buffer-percent"           gint                  : Read
        "can-seek"                 gboolean              : Read
        "duration"                 gint                  : Read
        "playing"                  gboolean              : Read / Write
        "position"                 gint                  : Read / Write
        "uri"                      gchar*                : Read / Write
        "volume"                   gdouble               : Read / Write

    Available signals are:
        Position_update:
                        new_position    gfloat          : current_time
                        get_progress    gfloat          : pourcent of video
                        get_duration    gfloat          : total time of video
    TODOs:
    * handle volume
    """
    __gsignals__ = {'position_update' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT, gobject.TYPE_FLOAT, gobject.TYPE_FLOAT])}

    def __init__(self, uri=None, preview_proportion=0.5,
                 progress_callback=None, end_callback=None, is_seekable=False, got_duration_callback=None):
        VideoTexture.__init__(self)

        self.uri = uri
        self.is_seekable = is_seekable
        self.got_duration_callback = got_duration_callback
        self.end_callback = end_callback
        self.preview_proportion = preview_proportion
        self.set_position(100, 50)
        if uri is not None:
            self.set_uri(uri)

        self.was_playing_before_seek = False

        self._init_gst_bus()

        self.connect("notify::progress", self.on_progress)
        self.connect("notify::duration", self.on_duration)

    def _init_gst_bus(self):
        playbin = self.get_playbin()
        bus = playbin.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_gst_message)

    def _on_gst_message(self, bus, message):
        '''
        Callback function that is called every time when message occurs on
        Gstreamer messagebus.
        '''
        if message.type == gst.MESSAGE_ERROR:
            error, debug = message.parse_error()
            logger.error("Gstreamer playback error: %s" %str(error))
            logger.debug("Gstreamer playback debug: %s" %str(debug))
        elif message.type == gst.MESSAGE_EOS:
            logger.info("Media playback end")
            logger.debug("EOS")
            if self.end_callback is not None:
                logger.debug("Calling end callback")
                self.end_callback()
            else:
                self.rewind()
                self.stop()

    def on_duration(self, source, duration):
        duration = source.get_duration()
        if duration > 0:
            if self.got_duration_callback is not None:
                self.got_duration_callback(duration)
                self.is_seekable = False

    def set_filename(self, path):
        if self.get_playing():
            self.stop()
        if self.uri is None:
            self.is_seekable = False
            self.uri = "file://" + path
            self.set_uri(self.uri)
            self.play()
            self.stop()
        else:
            self.change_filename(path)

    def change_filename(self, path):
        self.is_seekable = False
        if self.get_playing():
            self.stop()
        self.set_uri("file://" + path)

    def on_seek_request(self, source, arg):
        self.set_progress(arg)

    def emit_position_update(self, new_position):
        self.emit('position_update', new_position, self.get_progress(), self.get_duration())

    def on_seek_relative(self, arg):
        new_position = self.get_progress() * self.get_duration()
        if arg > 0:
            if  new_position + arg < self.get_duration():
                new_position = new_position + arg
                self.set_progress(new_position / self.get_duration())
            else:
                self.set_progress(1)
        else:
            if  new_position + arg > 0:
                new_position = new_position + arg
                self.set_progress(new_position / self.get_duration())
            else:
                self.set_progress(0)
        gobject.timeout_add(1000, self.emit_position_update, new_position)
        return True

    def play(self):
        logger.info("Playing file %s", self.uri)
        self.set_playing(True)
        self.was_playing_before_seek = True

    def on_progress(self, source, position):
        new_position = self.get_progress() * self.get_duration()
        if new_position > 0:
            self.emit_position_update(new_position)

    def stop(self):
        logger.info("Stopping playback for file %s", self.uri)
        self.set_playing(False)
        self.was_playing_before_seek = False

    def toggle_playing(self):
        if self.get_playing():
            self.stop()
        elif not self.get_playing():
            self.play()

    def rewind(self):
        logger.debug("Rewinding")
        self.set_playing(False)
        self.was_playing_before_seek = False
        self.set_progress(0)
        self.emit_position_update(0)
