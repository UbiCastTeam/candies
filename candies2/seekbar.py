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

    def __init__(self, margin=0, padding=0, bar_image_path=None, bar_color='#000000ff', cursor_image_path=None, sequence_markers_image_paths=None, seek_function=None, sequence_colors=None):
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
        self._marker_width = 2
        # Sequences blocks
        self._sequences = list()
        self._sequence_markers = list()
        self._sequence_markers_image_paths = None
        if sequence_markers_image_paths:
            if isinstance(sequence_markers_image_paths, (list, tuple)) and len(sequence_markers_image_paths) == 2:
                self._sequence_markers_image_paths = tuple(sequence_markers_image_paths)
            else:
                raise ValueError("sequence_markers_image_paths argument must be a list or tuple containing 2 elements, not %s (type: %s)", sequence_markers_image_paths, type(sequence_markers_image_paths))
        self._sequence_blocks = list()
        if sequence_colors:
            self._sequence_colors = tuple(sequence_colors)
        else:
            self._sequence_colors = ('#00dd00ff', '#00ff00ff')
        self._sequence_color = self._sequence_colors[-1]
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
        if bar_image_path and os.path.isfile(bar_image_path):
            self.bar = clutter.Texture()
            self.bar.set_from_file(bar_image_path)
        else:
            self.bar = clutter.Rectangle()
            self.bar.set_color(bar_color)
        self.bar.set_parent(self)

        # limit
        self._limit = list()
        self._limit_blocks = list()
        self._limit_color = '#000000ff'

        # cursor
        if cursor_image_path and os.path.isfile(cursor_image_path):
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
            for l in limit:
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
        if self._last_event_x is None:
            return
        self._last_event_x = event.x - self.get_transformed_position()[0] - self._margin.x - self.cursor_width / 2
        position = self._last_event_x / (self._inner_width - self.cursor_width)
        self.set_progress(position)
        self.emit_seek_request()

    def set_progress(self, position):
        new_position = max(position, 0.0)
        new_position = min(new_position, 1.0)
        if len(self._limit) > 0:
            for i, limit in enumerate(self._limit):
                if self._limit[0] is not None:
                    if new_position < self._limit[0][0]:
                        new_position = max(new_position, self._limit[0][0])
                    if new_position > self._limit[-1][1]:
                        new_position = min(new_position, self._limit[-1][1])
                    if (i + 1) <= len(self._limit) - 1 and self._limit[i + 1][0] > new_position > limit[1]:
                        new_position = self._limit[i + 1][0]
        if new_position != self._progress:
            self._progress = new_position
            self.queue_relayout()

    def set_seek_function(self, seek_function):
        self.seek_function = seek_function

    def emit_seek_request(self):
        if self.seek_function is not None:
            self.seek_function(self._progress)

    def set_sequences(self, sequences):
        self._clear_sequences()
        self._sequences = list()
        for sequence in sequences:
            self._add_sequence(sequence)
        self.queue_relayout()

    def clear_sequences(self):
        self._clear_sequences()
        self.queue_relayout()

    def _clear_sequences(self):
        for sequence in self._sequence_blocks:
            sequence.unparent()
            sequence.destroy()
        for sequence_markers in self._sequence_markers:
            for sequence_marker in sequence_markers:
                if sequence_marker:
                    sequence_marker.unparent()
                    sequence_marker.destroy()
        self._sequence_blocks = list()
        self._sequence_markers = list()

    def add_sequence(self, sequence):
        self._add_sequence(sequence)
        self.queue_relayout()

    def _add_sequence(self, sequence):
        self._clear_sequences()
        self._sequences.append(sequence)
        self._sequences.sort(key=lambda s: s[1] if s[0] is None else s[0])

        self._sequence_color = self._sequence_colors[-1]
        for sequence in self._sequences:
            sequence_block = clutter.Rectangle()
            self._sequence_color = self._sequence_colors[(self._sequence_colors.index(self._sequence_color) + 1) % len(self._sequence_colors)]
            sequence_block.set_color(self._sequence_color)
            sequence_block.set_parent(self)
            self._sequence_blocks.append(sequence_block)
            if self._sequence_markers_image_paths:
                if sequence[0] is None:
                    start_marker = None
                else:
                    start_marker = clutter.Texture()
                    start_marker.set_from_file(self._sequence_markers_image_paths[0])
                    start_marker.set_parent(self)
                if sequence[1] is None:
                    stop_marker = None
                else:
                    stop_marker = clutter.Texture()
                    stop_marker.set_from_file(self._sequence_markers_image_paths[1])
                    stop_marker.set_parent(self)
                self._sequence_markers.append((start_marker, stop_marker))

    def update_position(self, current_time, position, duration):
        if self._last_event_x is None:
            self.set_progress(position)

    def seek_at_progression(self, new_progression):
        print '******** seek_at_progression method of SeekBar class is deprecated ********'
        self.set_progress(new_progression)
        self.emit_seek_request()

    def set_cursor_color(self, color):
        self.cursor.props.color = clutter.color_from_string(color)

    def set_bar_color(self, color):
        self.bar.props.color = clutter.color_from_string(color)

    def set_markers(self, new_markers):
        self.clear_markers()
        for marker in new_markers:
            position = marker.get('position', 0)
            position = min(position, 1.0)
            position = max(position, 0.0)
            self._markers_position.append(position)
            color = marker.get('color', '#ffffffaa')
            marker_obj = clutter.Rectangle()
            marker_obj.set_color(color)
            marker_obj.set_parent(self)
            self._markers.append(marker_obj)
        self.queue_relayout()

    def set_marker(self, marker):
        position = marker.get('position', 0)
        position = min(position, 1.0)
        position = max(position, 0.0)
        color = marker.get('color', '#ffffffaa')
        # look for existing marker at that time
        index = 0
        while index < len(self._markers_position):
            pos = self._markers_position[index]
            if pos > position or abs(pos - position) < 0.000001:
                break
            index += 1
        if self._markers_position and abs(pos - position) < 0.000001:
            # assume this is the same pos
            marker_obj = self._markers[index]
        else:
            # no marker at that position, create one
            marker_obj = clutter.Rectangle()
            marker_obj.set_color(color)
            marker_obj.set_parent(self)
            self._markers_position.insert(index, position)
            self._markers.insert(index, marker_obj)
        marker_obj.set_color(color)
        self.queue_relayout()

    def clear_markers(self):
        for marker in self._markers:
            marker.unparent()
            marker.destroy()
            marker = None
        self._markers = list()
        self._markers_position = list()

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
        for i, limit in enumerate(self._limit_blocks):
            limit_box = clutter.ActorBox()
            limit_box.x1 = int(bar_box.x1 + int(self._limit[i][0] * (bar_box.x2 - bar_box.x1)))
            limit_box.y1 = bar_box.y1
            limit_box.x2 = int(bar_box.x1 + int(self._limit[i][1] * (bar_box.x2 - bar_box.x1)))
            limit_box.y2 = bar_box.y2
            limit.allocate(limit_box, flags)

        # sequences
        for i, sequence in enumerate(self._sequence_blocks):
            if self._sequences[i][0] is not None and self._sequences[i][1] is not None:
                sequence_box = clutter.ActorBox()
                sequence_box.x1 = int(bar_box.x1 + int(self._sequences[i][0] * (bar_box.x2 - bar_box.x1)))
                sequence_box.y1 = bar_box.y1
                sequence_box.x2 = int(bar_box.x1 + int(self._sequences[i][1] * (bar_box.x2 - bar_box.x1)))
                sequence_box.y2 = bar_box.y2
                sequence.allocate(sequence_box, flags)

        # sequence markers
        trimming_marker_size = self._inner_height / 2
        bar_height = bar_box.y2 - bar_box.y1
        height_diff = trimming_marker_size - bar_height
        for i, sequence_markers in enumerate(self._sequence_markers):
            for j, trimming_point in enumerate(self._sequences[i]):
                if trimming_point is not None:
                    trimming_marker_box = clutter.ActorBox()
                    trimming_marker_box.x1 = int(bar_box.x1 + int(trimming_point * (bar_box.x2 - bar_box.x1)) - trimming_marker_size / 2)
                    trimming_marker_box.y1 = bar_box.y1 - height_diff / 2
                    trimming_marker_box.x2 = int(bar_box.x1 + int(trimming_point * (bar_box.x2 - bar_box.x1)) + trimming_marker_size / 2)
                    trimming_marker_box.y2 = bar_box.y2 + height_diff / 2
                    sequence_markers[j].allocate(trimming_marker_box, flags)

        # markers
        bar_width = bar_box.x2 - bar_box.x1
        for i, marker in enumerate(self._markers):
            marker_box = clutter.ActorBox()
            marker_box.x1 = int(bar_box.x1 - self._marker_width / 2 + bar_width * self._markers_position[i])
            marker_box.y1 = bar_box.y1
            marker_box.x2 = marker_box.x1 + self._marker_width
            marker_box.y2 = bar_box.y2
            marker.allocate(marker_box, flags)

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
        for sequence_markers in self._sequence_markers:
            for sequence_marker in sequence_markers:
                if sequence_marker:
                    children.append(sequence_marker)
        children.extend(self._markers)
        children.append(self.cursor)
        for child in children:
            func(child, data)

    def do_paint(self):
        children = [self.background, self.bar]
        children.extend(self._limit_blocks)
        children.extend(self._sequence_blocks)
        for sequence_markers in self._sequence_markers:
            for sequence_marker in sequence_markers:
                if sequence_marker:
                    children.append(sequence_marker)
        children.extend(self._markers)
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
        if hasattr(self, '_sequence_markers'):
            for sequence_markers in self._sequence_markers:
                for sequence_marker in sequence_markers:
                    if sequence_marker:
                        sequence_marker.unparent()
                        sequence_marker.destroy()
        if hasattr(self, '_markers'):
            for marker in self._markers:
                marker.unparent()
                marker.destroy()
