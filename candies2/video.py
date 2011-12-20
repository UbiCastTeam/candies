#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Video player: cluttergst.VideoTexture wrapper

Copyright 2008, Florent Thiery, UbiCast
'''
import gobject
import gst
import clutter
from cluttergst import VideoTexture

import logging
logger = logging.getLogger('candies2.videoplayer')

class VideoPlayer(VideoTexture):
    __gtype_name__ = 'VideoPlayer'
    '''
    VideoPlayer

    This class wraps the clutter base VideoTexture object, itself
    wrapping the gstreamer playbin element.

    It can be called with an optional uri (either http:// or file://),
    or media initialization can be called later.
    '''

    def __init__(self, uri=None, keep_ratio=True):
        VideoTexture.__init__(self)
        self._last_progress = None
        self._seeking_timeout_id = None
        self._next_seek_percent = None
        self._next_seek_time = None
        self._keep_ratio = keep_ratio
        self._state = 'IDLE' # state can be IDLE, PLAYING, PAUSED
        self._duration = 0
        self._width = 0
        self._height = 0
        
        self._uri = uri
        self._listeners = dict(
            on_complete = list(),
            on_state_change = list(),
            on_time_change = list(),
            on_seek = list(),
            on_duration = list()
        )
        if uri is not None:
            self.set_uri(uri)

        self._init_gst_bus()

        self.connect('notify::progress', self.on_progress)
        self.connect('notify::duration', self.on_duration)
    
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
            logger.error('Gstreamer playback error: %s' %str(error))
            logger.debug('Gstreamer playback debug: %s' %str(debug))
        elif message.type == gst.MESSAGE_EOS:
            logger.info('Media playback end')
            logger.debug('EOS')
            self.stop()
            for listener in self._listeners['on_complete']:
                listener()

    def on_duration(self, source, event=None):
        duration = source.get_duration()
        if duration > 0:
            self._duration = duration
            if self._next_seek_time:
                self.seek_to_time(self._next_seek_time)
            for listener in self._listeners['on_duration']:
                listener(duration)

    def set_file(self, path=None):
        self.stop()
        self._last_progress = None
        self._next_seek_percent = None
        if path is not None:
            self._uri = 'file://' + path
            self.set_uri(self._uri)
        else:
            self._uri = None
        # play stop to fix first paint
        self.set_playing(True)
        self.set_playing(False)
    
    def add_listener(self, event_name, function):
        if event_name in self._listeners.keys():
            if function not in self._listeners[event_name]:
                self._listeners[event_name].append(function)
            else:
                raise Exception('Function %s is already in listeners.' % function)
        else:
            raise Exception('Can not add function to listeners. %s is not a valid event name.' % event_name)
    
    def remove_listener(self, event_name, function):
        if event_name in self._listeners.keys():
            if function in self._listeners[event_name]:
                self._listeners[event_name].remove(function)
            else:
                raise Exception('Function %s is not in listeners.' % function)
        else:
            raise Exception('Can not remove function from listeners. %s is not a valid event name.' % event_name)
    
    def remove_all_listeners(self):
        for event_name in self._listeners.keys():
            self._listeners[event_name] = list()
    
    def _set_state(self, state):
        if state != self._state:
            self._state = state
            for listener in self._listeners['on_state_change']:
                listener(state)
    
    def seek_to_time(self, time):
        if not self._uri:
            return
        if self._duration > 0:
            percent = time / self._duration
            self._next_seek_time = None
            self.seek_to_percent(percent)
        else:
            self._next_seek_time = time
            self.play()
    
    def seek_to_percent(self, percent):
        if not self._uri:
            return
        self._next_seek_percent = percent
        self.emit_position_update(percent)
        for listener in self._listeners['on_seek']:
            listener(self._next_seek_percent)
        if self._seeking_timeout_id is None:
            self._seeking_timeout_id = gobject.timeout_add(100, self._execute_seek_request)
    
    def _execute_seek_request(self):
        gobject.source_remove(self._seeking_timeout_id)
        percent = self._next_seek_percent
        self._next_seek_percent = None
        self.set_progress(percent)
        self.emit_position_update(percent)
        self._seeking_timeout_id = None
    
    def emit_position_update(self, progress):
        if progress != self._last_progress:
            self._last_progress = progress
            #self.emit('position_update', progress * self.get_duration(), progress, self.get_duration())
            for listener in self._listeners['on_time_change']:
                listener(progress * self.get_duration(), progress, self._duration)
    
    def on_progress(self, source, progress):
        if self._seeking_timeout_id is None:
            if self.get_progress() > 0:
                self.emit_position_update(self.get_progress())

    def play(self):
        if not self._uri:
            return
        logger.debug('Playing file %s', self._uri)
        self.set_playing(True)
        self._set_state('PLAYING')

    def pause(self):
        if not self._uri:
            return
        logger.debug('Pausing playback for file %s', self._uri)
        self.set_playing(False)
        self._set_state('PAUSED')

    def stop(self):
        if not self._uri:
            return
        logger.debug('Stopping playback for file %s', self._uri)
        self.set_playing(False)
        self.rewind()
        self._set_state('IDLE')
    
    def toggle_playing(self):
        if not self._uri:
            return
        if self.get_playing():
            self.pause()
        else:
            self.play()

    def rewind(self):
        logger.debug('Rewinding')
        self.set_progress(0)
        self.emit_position_update(0)
    
    def refresh_video_texture(self):
        # Dirty fix for the texture color bug
        if not self.get_playing():
            current_volume = self.get_audio_volume()
            current_percent = self.get_progress()
            self.set_audio_volume(0)
            gobject.timeout_add(5, self.set_playing, True)
            gobject.timeout_add(15, self.set_playing, False)
            gobject.timeout_add(20, self.set_audio_volume, current_volume)
            gobject.timeout_add(20, self.seek_to_percent, current_percent)
    
    def get_ratio(self):
        preferred_width = VideoTexture.do_get_preferred_width(self, for_height=-1)[1]
        preferred_height = VideoTexture.do_get_preferred_height(self, for_width=-1)[1]
        if preferred_height > 0:
            return preferred_width / preferred_height
        else:
            return 0


if __name__ == '__main__':
    import clutter
    
    stage = clutter.Stage()
    stage.set_size(1000, 600)
    stage.set_color('#000000ff')
    stage.connect('destroy', clutter.main_quit)
    
    
    p = VideoPlayer()
    p.set_position(100, 50)
    p.set_size(600, 400)
    stage.add(p)
    
    def test(source, event, p):
        p.set_filename('/home/sdiemer/storage/www/videos/billyBrowsers.ogg')
        p.set_audio_volume(0.4)
        p.play()
        
        gobject.timeout_add(1000, p.set_file, '/home/sdiemer/storage/videos/recordings-folder-test-1/2011-07-27_16-10-58/original.mkv')
        gobject.timeout_add(1100, p.play)
        gobject.timeout_add(1300, p.set_audio_volume, 0.2)
        gobject.timeout_add(2300, p.set_audio_volume, 0.1)
        gobject.timeout_add(3300, p.set_audio_volume, 0.0)
        
        gobject.timeout_add(6000, p.set_file, '/home/sdiemer/storage/videos/recordings-folder-test-1/2011-07-27_16-10-58/original.mkv')
        gobject.timeout_add(6100, p.play)
        gobject.timeout_add(6300, p.set_audio_volume, 0.2)
        gobject.timeout_add(7300, p.set_audio_volume, 0.1)
        gobject.timeout_add(8300, p.set_audio_volume, 0.0)
        
    
    stage.connect('button-release-event', test, p)
    
    stage.show()
    clutter.main()


