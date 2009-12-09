import gobject
import clutter
import os
from clutter import cogl

'''
class Background(clutter.Actor):
    __gtype_name__ = 'Background'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
    }

    def __init__(self):
        clutter.Actor.__init__(self)
        self._color = clutter.color_from_string('Black')

    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self._color = clutter.color_from_string(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self._color
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def __paint_bar(self, width, height, color):

        cogl.set_source_color(color)
        radius = height / 2
        cogl.path_move_to(radius, height)
        cogl.path_arc(radius, radius, radius, radius, 90, 270)
        cogl.path_line_to(width - radius, radius - radius)
        cogl.path_arc(radius + (width - 2 * radius), radius, -radius, -radius, -270, -90)
        cogl.path_line_to(radius, height - radius + radius)
        cogl.path_close()
        cogl.path_fill()

    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()

        paint_color = self._color

        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha

        self.__paint_bar(x2 - x1, y2 - y1, paint_color)

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return
        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__paint_bar(x2 - x1, y2 - y1, pick_color)
'''
'''
class Cursor(clutter.Actor):
    __gtype_name__ = 'Cursor'
    __gproperties__ = {
        'color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
    }

    def __init__(self):
        clutter.Actor.__init__(self)
        self._color = clutter.color_from_string('White')

    def do_set_property(self, pspec, value):
        if pspec.name == 'color':
            self._color = clutter.color_from_string(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'color':
            return self._color
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_preferred_width(self, for_height):
        return (20, 20)

    def __paint_cursor(self, width, height, color):
        cogl.set_source_color(color)
        cogl.rectangle(0, 0, width, height)

    def do_paint(self):
        (x1, y1, x2, y2) = self.get_allocation_box()

        paint_color = self._color

        real_alpha = self.get_paint_opacity() * paint_color.alpha / 255
        paint_color.alpha = real_alpha

        self.__paint_cursor(x2 - x1, y2 - y1, paint_color)

    def do_pick(self, pick_color):
        if self.should_pick_paint() == False:
            return
        (x1, y1, x2, y2) = self.get_allocation_box()
        self.__paint_cursor(x2 - x1, y2 - y1, pick_color)
'''

class SeekBar(clutter.Actor, clutter.Container):
    '''
    SeekBar class :

    * Properties :
        - background :          clutter.Rectangle       background seekbar
        - cursor :              clutter.Rectangle       cursor
        - widthbar :            float                   width size of seekbar
        - cursor_width :        float                   width size of cursor
        - duration :            float                   total time of video
        - current_time :        float                   real time of video

    * Functions :
        - finish :              Update progression to set 1.

        - on_background_click : Update cursor where you click
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

    * Signal :
        - seek_request_realtime : progression   gfloat  during on_move in drag and drop.
        - seek_request_lazy : progression   gfloat  after drag and drop in on_release.
    '''
    __gsignals__ = {'seek_request_realtime' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT]), \
                        'seek_request_lazy' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT])}
    __gtype_name__ = 'SeekBar'
    __gproperties__ = {
        'cursor_color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'background_color' : (
            str, 'color', 'Color', None, gobject.PARAM_READWRITE
        ),
        'progression': (
            gobject.TYPE_FLOAT, 'Progression', 'Progression value',
            0.0, 1.0, 0.0, gobject.PARAM_READWRITE
        ),
    }
    def __init__(self, bar_image_path=None, cursor_image_path=None):
        clutter.Actor.__init__(self)
        self._progression = 0.0

        #self.background = Background()
        if bar_image_path != None and os.path.exists(bar_image_path):
            self.background = clutter.Texture()
            self.background.set_from_file(bar_image_path)
        else:
            self.background = clutter.Rectangle()
            self.background.set_color('LightBlue')
        self.background.set_reactive(True)
        self.background.connect('button-release-event', self.on_background_click)
        self.background.set_parent(self)

        #self.cursor = Cursor()
        if cursor_image_path != None and os.path.exists(cursor_image_path):
            self.cursor = clutter.Texture()
            self.cursor.set_from_file(cursor_image_path)
        else:
            self.cursor = clutter.Rectangle()
            self.cursor.set_color('Gray')
        self.cursor.set_reactive(True)
        self.cursor.connect('button-press-event', self.on_press)
        self.cursor.connect('button-release-event', self.on_release)
        self.cursor.connect('motion-event', self.on_move)
        self.cursor.set_parent(self)

        self.last_event_x = None
        self.widthbar = 0.0
        #self.radius = 0.0
        self.cursor_width = 0.0
        self.duration = 0.0
        self.current_time = 0.0

    def set_progression(self, value):
        self._progression = value
        self.queue_relayout()

    def finish(self):
        self.set_progression(1)

    def set_cursor_color(self, color):
        self.cursor.props.color = clutter.color_from_string(color)

    def set_background_color(self, color):
        self.background.props.color = clutter.color_from_string(color)

    def do_set_property(self, pspec, value):
        if pspec.name == 'progression':
            self.set_progression(value)
        elif pspec.name == 'cursor_color':
            self.set_cursor_color(value)
        elif pspec.name == 'background_color':
            self.set_background_color(value)
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def do_get_property(self, pspec):
        if pspec.name == 'progression':
            return self._progression
        elif pspec.name == 'cursor_color':
            return self.cursor.props.color
        elif pspec.name == 'background_color':
            return self.background.props.color
        else:
            raise TypeError('Unknown property ' + pspec.name)

    def on_background_click(self, source, event):
        x1, y1, x2, y2 = self.get_allocation_box()
        bar_width = x2 - x1
        self._progression = (event.x - self.cursor_width / 2 - self.get_transformed_position()[0]) / bar_width
        self.queue_relayout()
        self._progression = max(self._progression, 0.0)
        self._progression = min(self._progression, 1.0)
        self.emit('seek_request_realtime', self._progression)
        self.emit('seek_request_lazy', self._progression)
        return True

    def on_press(self, source, event):
        self.last_event_x = event.x
        return True

    def on_move(self, source, event):
        if self.last_event_x is None: return
        clutter.grab_pointer(self.cursor)
        x1, y1, x2, y2 = self.get_allocation_box()
        bar_width = x2 - x1
        self._progression = (event.x - self.get_transformed_position()[0]) / bar_width
        self._progression = max(self._progression, 0.0)
        self._progression = min(self._progression, 1.0)
        self.queue_relayout()
        self.last_event_x = event.x
        self.emit('seek_request_realtime', self._progression)

    def convert_date(self, duration):
        hour = duration // 3600
        min = (duration % 3600) // 60
        sec = duration % 60
        date = "%02d:%02d:%02d" %(hour, min, sec)
        return date

    def update_position(self, source, current_time, progression, duration):
        if self.last_event_x is None:
            self._progression = progression
            self.current_time = self.convert_date(current_time)
            self.duration = self.convert_date(duration)
            self.queue_relayout()

    def on_release(self, source, event):
        clutter.ungrab_pointer()
        self.last_event_x = None
        self.emit('seek_request_realtime', self._progression)
        self.emit('seek_request_lazy', self._progression)
    
    def do_get_preferred_height(self, for_width):
        return 40, 40
    
    def do_get_preferred_width(self, for_height):
        return 200, 200
    
    def do_allocate(self, box, flags):
        bar_width = box.x2 - box.x1
        bar_height = box.y2 - box.y1
        bg_box = clutter.ActorBox(0, 0, bar_width, bar_height)
        self.background.allocate(bg_box, flags)
        cursor_width = bar_height
        cursor_height = bar_height
        cursor_box = clutter.ActorBox()
        cursor_box.x1 = int(self._progression * (bar_width - cursor_width))
        cursor_box.y1 = 0
        cursor_box.x2 = int(cursor_box.x1 + cursor_width)
        cursor_box.y2 = cursor_height
        self.cursor.allocate(cursor_box, flags)
        clutter.Actor.do_allocate(self, box, flags)

    def do_foreach(self, func, data=None):
        children = (self.background, self.cursor)
        for child in children:
            func(child, data)

    def do_paint(self):
        children = (self.background, self.cursor)
        for child in children:
            child.paint()

    def do_pick(self, color):
        children = (self.background, self.cursor)
        for child in children:
            child.paint()
