#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import clutter
import os
import common

class SeekBar(clutter.Actor, clutter.Container):
    '''
    SeekBar class :

    * Properties :
        - bar :          clutter.Rectangle       bar seekbar
        - cursor :              clutter.Rectangle       cursor
        - cursor_width :        float                   width size of cursor
        - current_time :        float                   real time of video

    * Functions :
        - finish :              Update progression to set 1.

        - on_bar_click : Update cursor where you click
                                and send signal to video to update
                                progression of video.

        - on_press :            Moment or you click to do drag and drop.

        - on_move :             Moment where you have clicked, you move
                                your cursor, this update your cursor and
                                send signal to update the progression of video.

        - convert_date :        To convert float date in conventional date 00:00:00.

        - update_position :     To get progression of video, real time of video and total time

        - on_release :          For the drag and drop when you unclick
                                to finish the drag and drop, update cursor
                                and send a signal to update video progression.
        - do_allocate
        - do_foreach
        - do_paint
        - do_pick
    '''
    __gtype_name__ = 'SeekBar'
    __gproperties__ = {
        'cursor_color': (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'bar_color': (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'progression': (
            gobject.TYPE_FLOAT, 'Progression', 'Progression value',
            0.0, 1.0, 0.0, gobject.PARAM_READWRITE
        ),
    }
    def __init__(self, margin=0, padding=0, bar_image_path=None, bar_color='#000000ff', cursor_image_path=None, seek_function=None, sequence_color_1='#00dd00ff', sequence_color_2='#00ff00ff'):
        clutter.Actor.__init__(self)
        self._margin = common.Margin(margin)
        self._padding = common.Padding(padding)
        self._progress = 0.0
        self._last_event_x = None
        self.cursor_width = 0.0
        self.seek_function = seek_function
        # Time markers
        self._markers = list()
        self._markers_position = list()
        self._new_markers = list()
        self._new_markers_position = list()
        self._marker_width = 2
        # Sequences blocks
        self._trimming_points = list()
        self._sequence_blocks = list()
        self.sequence_color_1 = sequence_color_1
        self.sequence_color_2 = sequence_color_2
        self._sequence_color = self.sequence_color_2
        self._min = None
        self._max = None
        
        # background
        self.background = clutter.Rectangle()
        self.background.set_color('#00000000')
        self.background.connect('button-press-event', self._on_press)
        self.background.connect('button-release-event', self._on_release)
        self.background.connect('motion-event', self._on_move)
        self.background.connect('scroll-event', self._on_mouse_scroll)
        self.background.set_parent(self)
        self.background.set_reactive(True)
        
        # bar
        if bar_image_path != None and os.path.exists(bar_image_path):
            self.bar = clutter.Texture()
            self.bar.set_from_file(bar_image_path)
        else:
            self.bar = clutter.Rectangle()
            self.bar.set_color(bar_color)
        self.bar.set_parent(self)
        
        #limit
        self._limit = list()
        self._limit_blocks = list()
        self._limit_color = '#000000ff'
        
        # cursor
        if cursor_image_path != None and os.path.exists(cursor_image_path):
            self.cursor = clutter.Texture()
            self.cursor.set_from_file(cursor_image_path)
        else:
            self.cursor = clutter.Rectangle()
            self.cursor.set_color('Gray')
        self.cursor.set_parent(self)
    
    def set_reactive(self, value):
        self.background.set_reactive(value)

    def set_lock(self, lock):
        self.background.set_reactive(not lock)
        self.set_opacity(128 if lock else 255)

    def set_limit_progress(self, limit):
        
        for limit_block in list(self._limit_blocks):
            limit_block.unparent()
            limit_block.destroy()
        self._limit_blocks = list()
        
        if limit is not None:
            if isinstance(self.bar, clutter.Rectangle):
                self.bar.set_color('#00000070')
            for limit_index in range(len(limit)):
                block = clutter.Rectangle()
                block.set_color(self._limit_color)
                block.set_parent(self)
                self._limit_blocks.append(block)
            self._limit = limit
        else:
            if isinstance(self.bar, clutter.Rectangle):
                self.bar.set_color('#000000ff')
            self._limit = list()

    '''
    def set_min_progress(self, mini=None):
        self._limit = self._limit + (mini,)
        #self._min = mini
    
    def set_max_progress(self, maxi=None):
        self._limit = self._limit[:-1] + (self._limit[-1][0],maxi)
        #self._max = maxi
        '''

    def _on_press(self, source, event):
        clutter.grab_pointer(self.background)
        self._last_event_x = event.x
        self.set_progress_with_event(event)

    def _on_release(self, source, event):
        clutter.ungrab_pointer()
        self._last_event_x = None

    def _on_move(self, source, event):
        self.set_progress_with_event(event)
    
    def _on_mouse_scroll(self, source, event):
        current_pos = self._progress
        if event.direction == clutter.SCROLL_UP:
            current_pos += 0.1
        else:
            current_pos -= 0.1
        self.set_progress(current_pos)
        self.emit_seek_request()
    
    def set_progress_with_event(self, event):
        if self._last_event_x is None: return
        self._last_event_x = event.x - self.get_transformed_position()[0] - self._margin.x - self.cursor_width/2
        position = self._last_event_x/(self._inner_width - self.cursor_width)
        self.set_progress(position)
        self.emit_seek_request()

    def set_progress(self, position):
        new_position = max(position, 0.0)
        new_position = min(new_position, 1.0)
        if len(self._limit) > 0:
            for i in range(len(self._limit)):
                if self._limit[0] is not None:
                    if new_position < self._limit[0][0]:
                        new_position = max(new_position, self._limit[0][0])
                    if new_position > self._limit[-1][1]:
                        new_position = min(new_position, self._limit[-1][1])
                    if (i + 1) <= len(self._limit) - 1 and self._limit[i + 1][0] > new_position > self._limit[i][1]:
                        new_position = self._limit[i + 1][0]
        if new_position != self._progress:
            self._progress = new_position
            self.queue_relayout()

    def set_seek_function(self, seek_function):
        self.seek_function = seek_function

    def emit_seek_request(self):
        if self.seek_function is not None:
            self.seek_function(self._progress)

    def set_trimming_points(self, trimming_points):
        self._clear_trimming_points()
        for point in trimming_points:
            self._add_trimming_point(point)
        self.queue_relayout()

    def add_trimming_point(self, progression):
        self._add_trimming_point(progression)
        self.queue_relayout()

    def _add_trimming_point(self, progression):
        trimming_point = progression
        progression = min(progression, 1.0)
        progression = max(progression, 0.0)
        self.trimming_points.append(trimming_point)
        self.trimming_points.sort()

        for sequence_block in list(self._sequence_blocks):
            sequence_block.unparent()
            sequence_block.destroy()
        self._sequence_blocks = list()

        if len(self.trimming_points) > 1:
            used_trimming_points = list(self.trimming_points)
            if len(used_trimming_points) % 2 == 1:
                used_trimming_points = used_trimming_points[:-1]
            nb_sequences = int(len(used_trimming_points) / 2)
            self._sequence_color = self.sequence_color_2
            for sequence_index in range(nb_sequences):
                sequence = clutter.Rectangle()
                if self._sequence_color == self.sequence_color_2:
                    self._sequence_color = self.sequence_color_1
                else:
                    self._sequence_color = self.sequence_color_2
                sequence.set_color(self._sequence_color)
                sequence.set_parent(self)
                self._sequence_blocks.append(sequence)

    def clear_trimming_points(self):
        self._clear_trimming_points()
        self.queue_relayout()

    def _clear_trimming_points(self):
        for sequence_index in range(len(self._sequence_blocks)):
            sequence = self._sequence_blocks[sequence_index]
            sequence.unparent()
            sequence.destroy()
            sequence = None
        self.trimming_points = list()
        self._sequence_blocks = list()

    def update_position(self, current_time, position, duration):
        if self._last_event_x is None:
            self.set_progress(position)

    def update_markers_color(self, color, add_new_list=False):
        markers = self._new_markers if add_new_list else self._markers
        for marker in markers:
            marker.set_color(color)

    def seek_at_progression(self, new_progression):
        print '******** seek_at_progression method of SeekBar class is deprecated ********'
        self.set_progress(new_progression)
        self.emit_seek_request()

    def set_cursor_color(self, color):
        self.cursor.props.color = clutter.color_from_string(color)

    def set_bar_color(self, color):
        self.bar.props.color = clutter.color_from_string(color)

    def update_old_markers(self):
        self._markers = self._new_markers
        self._new_markers = list()
        self._markers_position = self._new_markers_position
        self._new_markers_position = list()

    def set_markers(self, new_markers, add_new_list=False):
        markers = self._new_markers if add_new_list else self._markers
        markers_position = self._new_markers_position if add_new_list else self._markers_position
        while markers:
            markers_position.pop()
            marker = markers.pop()
            marker.unparent()
            marker.destroy()
        for marker in new_markers:
            position = marker.get('position', 0)
            position = min(position, 1.0)
            position = max(position, 0.0)
            markers_position.append(position)
            color = marker.get('color', '#ffffffaa')
            marker_obj = clutter.Rectangle()
            marker_obj.set_color(color)
            marker_obj.set_parent(self)
            markers.append(marker_obj)
        self.queue_relayout()

    def set_marker(self, marker, add_new_list=False):
        markers = self._new_markers if add_new_list else self._markers
        markers_position = self._new_markers_position if add_new_list else self._markers_position
        position = marker.get('position', 0)
        position = min(position, 1.0)
        position = max(position, 0.0)
        color = marker.get('color', '#ffffffaa')
        # look for existing marker at that time
        index = 0
        while index < len(markers_position):
            pos = markers_position[index]
            if pos > position or abs(pos - position) < 0.000001:
                break
            index += 1
        if markers_position and abs(pos - position) < 0.000001:
            # assume this is the same pos
            marker_obj = markers[index]
        else:
            # no marker at that position, create one
            marker_obj = clutter.Rectangle()
            marker_obj.set_color(color)
            marker_obj.set_parent(self)
            markers_position.insert(index, position)
            markers.insert(index, marker_obj)
        marker_obj.set_color(color)
        self.queue_relayout()

    def delete_marker(self, marker, delete_new_list=False):
        markers = self._new_markers if delete_new_list else self._markers
        markers_position = self._new_markers_position if delete_new_list else self._markers_position
        position = marker.get('position', 0)
        position = min(position, 1.0)
        position = max(position, 0.0)
        index = 0
        while index < len(markers_position):
            pos = markers_position[index]
            if pos > position or abs(pos - position) < 0.000001:
                break
            index += 1
        if markers_position and abs(pos - position) < 0.000001:
            marker_obj = markers[index]
            marker_obj.unparent()
            marker_obj.destroy()
            marker_obj = None
        self.queue_relayout()

    def clear_markers(self, clear_new_list=False):
        markers = self._new_markers if clear_new_list else self._markers
        markers_position = self._new_markers_position if clear_new_list else self._markers_position
        while markers:
            markers_position.pop()
            marker = markers.pop()
            marker.unparent()
            marker.destroy()
            marker = None

    def do_set_property(self, pspec, value):
        if pspec.name == 'progression':
            self.set_progression(value)
        elif pspec.name == 'cursor_color':
            self.set_cursor_color(value)
        elif pspec.name == 'bar_color':
            self.set_bar_color(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'progression':
            return self._progress
        elif pspec.name == 'cursor_color':
            return self.cursor.props.color
        elif pspec.name == 'bar_color':
            return self.bar.props.color
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_preferred_height(self, for_width):
        return 40, 40

    def do_get_preferred_width(self, for_height):
        return 200, 200

    def do_allocate(self, box, flags):
        self._width = box.x2 - box.x1
        self._height = box.y2 - box.y1
        self._inner_width = self._width - 2 * self._margin.x
        self._inner_height = self._height - 2 * self._margin.y

        # background
        background_box = clutter.ActorBox(self._margin.x, self._margin.y, self._width - self._margin.x, self._height - self._margin.y)
        self.background.allocate(background_box, flags)

        # bar
        bar_box = clutter.ActorBox()
        bar_box.x1 = self._margin.x + self._padding.left
        bar_box.y1 = self._margin.y + self._padding.top
        bar_box.x2 = self._inner_width - self._margin.x - self._padding.right
        bar_box.y2 = self._height - self._margin.y - self._padding.bottom
        self.bar.allocate(bar_box, flags)

        # limits
        for limit_index in range(len(self._limit_blocks)):
            limit = self._limit_blocks[limit_index]
            limit_box = clutter.ActorBox()
            limit_box.x1 = int(bar_box.x1 + int(self._limit[limit_index][0] * (bar_box.x2 - bar_box.x1)))
            limit_box.y1 = bar_box.y1
            limit_box.x2 = int(bar_box.x1 + int(self._limit[limit_index][1] * (bar_box.x2 - bar_box.x1)))
            limit_box.y2 = bar_box.y2
            limit.allocate(limit_box, flags)

        # sequences
        for sequence_index in range(len(self._sequence_blocks)):
            sequence = self._sequence_blocks[sequence_index]
            sequence_box = clutter.ActorBox()
            sequence_box.x1 = int(bar_box.x1 + int(self.trimming_points[0 + 2 * sequence_index] * (bar_box.x2 - bar_box.x1)))
            sequence_box.y1 = bar_box.y1
            sequence_box.x2 = int(bar_box.x1 + int(self.trimming_points[1 + 2 * sequence_index] * (bar_box.x2 - bar_box.x1)))
            sequence_box.y2 = bar_box.y2
            sequence.allocate(sequence_box, flags)

        # markers
        bar_width = bar_box.x2 - bar_box.x1
        for i in range(len(self._markers)):
            marker_box = clutter.ActorBox()
            marker_box.x1 = int(bar_box.x1 - self._marker_width / 2 + bar_width * self._markers_position[i])
            marker_box.y1 = bar_box.y1
            marker_box.x2 = marker_box.x1 + self._marker_width
            marker_box.y2 = bar_box.y2
            self._markers[i].allocate(marker_box, flags)

        bar_width = bar_box.x2 - bar_box.x1
        for i in range(len(self._new_markers)):
            marker_box = clutter.ActorBox()
            marker_box.x1 = int(bar_box.x1 - self._marker_width / 2 + bar_width * self._new_markers_position[i])
            marker_box.y1 = bar_box.y1
            marker_box.x2 = marker_box.x1 + self._marker_width
            marker_box.y2 = bar_box.y2
            self._new_markers[i].allocate(marker_box, flags)

        # cursor
        cursor_width = self._inner_height
        cursor_height = self._inner_height
        self.cursor_width = cursor_width
        cursor_box = clutter.ActorBox()
        cursor_box.x1 = self._margin.x + int(self._progress * (self._inner_width - cursor_width))
        cursor_box.y1 = self._margin.y
        cursor_box.x2 = cursor_box.x1 + cursor_width
        cursor_box.y2 = cursor_box.y1 + cursor_height
        self.cursor.allocate(cursor_box, flags)
        clutter.Actor.do_allocate(self, box, flags)

    def do_foreach(self, func, data=None):
        children = [self.background, self.bar]
        children.extend(self._limit_blocks)
        children.extend(self._sequence_blocks)
        children.extend(self._markers)
        children.extend(self._new_markers)
        children.append(self.cursor)
        for child in children:
            func(child, data)

    def do_paint(self):
        children = [self.background, self.bar]
        children.extend(self._limit_blocks)
        children.extend(self._sequence_blocks)
        children.extend(self._markers)
        children.extend(self._new_markers)
        children.append(self.cursor)
        for child in children:
            child.paint()

    def do_pick(self, color):
        self.background.paint()

    def do_destroy(self):
        self.unparent()
        if hasattr(self, 'background'):
            if self.background:
                self.background.unparent()
                self.background.destroy()
        if hasattr(self, 'bar'):
            if self.bar:
                self.bar.unparent()
                self.bar.destroy()
        if hasattr(self, 'cursor'):
            if self.cursor:
                self.cursor.unparent()
                self.cursor.destroy()
        if hasattr(self, '_limit_blocks'):
            for limit_block in self._limit_blocks:
                limit_block.unparent()
                limit_block.destroy()
        if hasattr(self, '_sequence_blocks'):
            for sequence_block in self._sequence_blocks:
                sequence_block.unparent()
                sequence_block.destroy()
        if hasattr(self, '_markers'):
            for marker in self._markers:
                marker.unparent()
                marker.destroy()
            for marker in self._new_markers:
                marker.unparent()
                marker.destroy()

