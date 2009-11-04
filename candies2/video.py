#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Video player: cluttergst.VideoTexture wrapper

Copyright 2008, Florent Thiery, UbiCast
"""
from __future__ import division
from cluttergst import VideoTexture
import gobject

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
        self.progress_callback = progress_callback
        self.end_callback = end_callback

        self.connect("eos", self.on_eos)
        self.connect("error", self.on_error)

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
            self.uri = "file://"+path
            self.set_uri(self.uri)
            self._get_safe_duration()
        else:
            self.change_filename(path)

    def change_filename(self, path):
        self.is_ready = False
        self.duration_attempt = 0
        self.is_live = False
        if self.get_playing():
            self.stop()
        self.set_uri("file://"+path)
        self._get_safe_duration()

    def play(self):
        #logger.info("Playing file %s", self.uri)
        self.set_playing(True)
        self.was_playing_before_seek = True
        if not self.is_live:
            gobject.timeout_add(1000, self.update_position)

    def update_position(self):
        if self.get_playing() and not self.is_live:
            new_position = self.get_property("position")/self.get_duration()*100
            if self.progress_callback is not None:
                self.progress_callback(new_position)
            else:
                pass#logger.debug("Position update: %s", new_position)
        return True

    def stop(self):
        #logger.info("Stopping playback for file %s", self.uri)
        self.set_playing(False)
        self.was_playing_before_seek = False
    
    def seek_percent(self, percentage):
        # seek_percent(50) will set to 50% of the file
        if not self.is_live:
            #logger.info("Trying to seek to %s", percentage)
            if self.get_playing():
                self.set_playing(False)
                gobject.timeout_add(200, self.seek_percent, percentage)
            elif self.is_ready:
                new_position = percentage/100 * self.get_duration()
                self._set_media_position(new_position)
                if self.was_playing_before_seek:
                    self.play()
            else:
                self._get_safe_duration()
        else:
            pass#logger.info("Media is not seekable, discarding seeking request")

    def toggle_playing(self):
        if self.get_playing():
            self.stop()
        elif not self.get_playing():
            self.play()

    def rewind(self):
        #logger.info("Rewinding")
        self.set_playing(False)
        self.was_playing_before_seek = False
        self.set_property('position', 0)

    def _get_safe_duration(self):
        # FIXME: apparently get_can_seek doesn't work with provided test file !
        #if self.get_can_seek():
        #logger.debug("Trying to get real duration")
        if self.duration_attempt <= 4:
            duration = self.get_duration()
            if duration == 0:
                #logger.debug("Media hasn't been initialized yet, getting duration later")
                self.play()
                self.stop()
                self.duration_attempt += 1
                gobject.timeout_add(200, self._get_safe_duration)
            else:
                self.is_ready = True
                #logger.debug("Got real duration, we can now use percentages")
                if self.got_duration_callback is not None:
                    self.got_duration_callback(duration)
        else:
            self.is_live = True
            #logger.info("Media is not seekable, discarding preview procedure")

    def _set_media_position(self, position):
        self.set_property("position", position)
        #logger.debug("Setting media to %ss", position)

if __name__ == '__main__':
    import sys
    import clutter
    
    def on_button_press(player, event):
        if event.button == 1:
            player.toggle_playing()
        else:
            is_playing = player.get_playing()
            player.set_filename(player.get_uri())
            if is_playing:
                player.play()
    
    stage = clutter.Stage()
    stage.connect('destroy', clutter.main_quit)
    
    player = VideoPlayer()
    player.set_filename(sys.argv[1])
    player.set_reactive(True)
    player.connect('button_press_event', on_button_press)
    
    stage.add(player)
    stage.show()
    
    clutter.main()
