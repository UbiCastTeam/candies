#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Video player: cluttergst.VideoTexture wrapper

Copyright 2008, Florent Thiery, UbiCast
"""
from __future__ import division
from cluttergst import VideoTexture
import gobject
from seekbar import SeekBar

class VideoPlayer(VideoTexture):
    __gsignals__ = {'seek' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT, gobject.TYPE_FLOAT, gobject.TYPE_FLOAT])}
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

    Some gobject code lets some time for some properties to
    get updated, such as duration (would be 0 otherwise).

    TODOs:
    * handle remote sources
    * handle volume
    """

    def __init__(self, uri=None, preview_proportion=0.5,
                 progress_callback=None, end_callback=None, is_live=False, got_duration_callback=None):
        VideoTexture.__init__(self)

        self.uri = uri
        self.is_live = is_live
        self.duration_attempt = 0
        self.got_duration_callback=got_duration_callback

        if uri is not None:
            self.set_uri(uri)
            if not is_live:
                self._get_safe_duration()

        self.preview_proportion = preview_proportion
        self.is_ready = False
        self.was_playing_before_seek = False
        self.end_callback = end_callback
        self.connect("eos", self.on_eos)
        self.connect("error", self.on_error)
        self.connect("notify::progress", self.on_progress)
        self.connect("notify::duration", self.on_duration)

    def on_duration(self, source, duration):
        duration = source.get_duration()
        if duration > 0:
            if self.got_duration_callback is not None:
                self.got_duration_callback(duration)
                self.is_ready = True
                self.is_live = False

    def on_eos(self, source):
        #logger.info("EOS: Stream playback ended after %ss, media location: %s",
        #            self.get_duration(), self.uri)
        if self.end_callback is not None:
            self.end_callback()
        else:
            self.rewind()

    def on_error(self, source, gerror):
        # FIXME: how to get the error contents ?
        #logger.error("Unkown playback error, media location: %s", self.uri)
        pass

    def set_filename(self, path):
        if self.get_playing():
            self.stop()
        if self.uri is None:
            self.duration_attempt = 0
            self.is_live = False
            self.uri = "file://" + path
            self.set_uri(self.uri)
            self.play()
            self.stop()
        else:
            self.change_filename(path)

    def change_filename(self, path):
        self.is_ready = False
        self.duration_attempt = 0
        self.is_live = False
        if self.get_playing():
            self.stop()
        self.set_uri("file://" + path)

    def on_seek_request(self, source, arg):
        self.set_progress(arg)

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
        gobject.timeout_add(1000, self.emit_seek)
        return True

    def play(self):
        #logger.info("Playing file %s", self.uri)
        self.set_playing(True)
        self.was_playing_before_seek = True

    def on_progress(self, source, position):
        new_position = self.get_progress() * self.get_duration()
        if new_position > 0:
            self.emit('seek', new_position, source.get_progress(), source.get_duration())

    def stop(self):
        #logger.info("Stopping playback for file %s", self.uri)
        self.set_playing(False)
        self.was_playing_before_seek = False

    def toggle_playing(self):
        if self.get_playing():
            self.stop()
        elif not self.get_playing():
            self.play()

    def rewind(self):
        #logger.info("Rewinding")
        self.set_playing(False)
        self.was_playing_before_seek = False
        self.set_progress(0)
