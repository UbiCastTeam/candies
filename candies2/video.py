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
logger = logging.getLogger("candies2.videoplayer")

class VideoPlayer(VideoTexture):
    """
    Simple VideoPlayer

    This class wraps the clutter base VideoTexture object, itself
    wrapping the gstreamer playbin element.

    It can be called with an optional uri (either http:// or file://),
    or media initialization can be called later.

    Available properties are:
        "buffer-percent"           gint                  : Read
        "duration"                 gint                  : Read
        "playing"                  gboolean              : Read / Write
        "position"                 gint                  : Read / Write
        "uri"                      gchar*                : Read / Write

    Available signals are:
        Position_update:
                        new_position    gfloat          : current_time
                        get_progress    gfloat          : pourcent of video
                        get_duration    gfloat          : total time of video
    """
    __gsignals__ = {'position_update' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT, gobject.TYPE_FLOAT, gobject.TYPE_FLOAT])}

    def __init__(self, uri=None, progress_callback=None, end_callback=None, got_duration_callback=None):
        VideoTexture.__init__(self)
        self._last_progress = None
        self._seeking_timeout_id = None
        self._next_seek_value = None
        
        self.uri = uri
        self.got_duration_callback = got_duration_callback
        self.end_callback = end_callback
        self.set_position(100, 50)
        if uri is not None:
            self.set_uri(uri)

        self._init_gst_bus()

        self.connect("notify::progress", self.on_progress)
        self.connect("notify::duration", self.on_duration)

    def _init_gst_bus(self):
        try:
            playbin = self.get_pipeline()
        except:
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
                self.stop()

    def on_duration(self, source, duration):
        duration = source.get_duration()
        if duration > 0 and self.got_duration_callback is not None:
            self.got_duration_callback(duration)

    def set_filename(self, path=None):
        if self.get_playing():
            self.stop()
        self._last_progress = None
        self._next_seek_value = None
        if path is not None:
            self.uri = "file://" + path
            self.set_uri(self.uri)
        else:
            self.uri = None
        # play stop to fix first paint
        self.play()
        self.stop()

    def seek_at_percent(self, percent):
        self._next_seek_value = percent
        if self._seeking_timeout_id is None:
            self._seeking_timeout_id = gobject.timeout_add(100, self._execute_seek_request)
    
    def _execute_seek_request(self):
        gobject.source_remove(self._seeking_timeout_id)
        percent = self._next_seek_value
        self._next_seek_value = None
        self.set_progress(percent)
        self.emit_position_update(percent)
        if self._next_seek_value is not None:
            self._seeking_timeout_id = gobject.timeout_add(100, self._execute_seek_request)
        else:
            self._seeking_timeout_id = None

    def emit_position_update(self, progress):
        if progress != self._last_progress:
            self._last_progress = progress
            self.emit('position_update', progress * self.get_duration(), progress, self.get_duration())

    def on_seek_relative(self, arg):
        new_position = self.get_progress() * self.get_duration()
        if arg > 0:
            if new_position + arg < self.get_duration():
                new_position = new_position + arg
                self.set_progress(new_position / self.get_duration())
            else:
                self.set_progress(1)
        else:
            if new_position + arg > 0:
                new_position = new_position + arg
                self.set_progress(new_position / self.get_duration())
            else:
                self.set_progress(0)

    def on_progress(self, source, progress):
        if self.get_progress() > 0:
            self.emit_position_update(self.get_progress())

    def play(self):
        logger.info("Playing file %s", self.uri)
        self.set_playing(True)

    def pause(self):
        logger.info("Pausing playback for file %s", self.uri)
        self.set_playing(False)

    def stop(self):
        logger.info("Stopping playback for file %s", self.uri)
        self.set_playing(False)
        self.rewind()
    
    def toggle_playing(self):
        if self.get_playing():
            self.pause()
        else:
            self.play()

    def rewind(self):
        logger.debug("Rewinding")
        self.set_progress(0)
        self.emit_position_update(0)

