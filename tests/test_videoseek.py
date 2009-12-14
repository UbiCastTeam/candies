from candies2 import VideoPlayer, SeekBar, ClassicButton
import clutter
import sys

import logging, sys

logging.basicConfig(
    level=getattr(logging, "DEBUG"),
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    stream=sys.stderr
)

def show_time(player, current_time, progression, duration, time_label):
    hour = duration // 3600
    min = (duration % 3600) // 60
    sec = duration % 60
    duration = "%02d:%02d:%02d" %(hour, min, sec)
    hour = current_time // 3600
    min = (current_time % 3600) // 60
    sec = current_time % 60
    current_time = "%02d:%02d:%02d" %(hour, min, sec)
    time_label.set_position(200, 470)
    time_label.set_text(str(current_time) + '/' + str(duration))

stage = clutter.Stage()
stage.connect('destroy', clutter.main_quit)

def on_button_seek(button, event, player):
    player.on_seek_relative(5)
    return True

def on_button_press(player, event):
    if event.button == 1:
        player.toggle_playing()
    else:
        is_playing = player.get_playing()
        player.set_filename(player.get_uri())
        if is_playing:
            player.play()


player = VideoPlayer()
try:
    player.set_filename(sys.argv[1])
except IndexError, e:
    print "Please provide a video file as argument\nExample: python test_videoseek.py test.ogg"
    sys.exit()

player.set_reactive(True)
player.connect('button_press_event', on_button_press)
player.set_size(320, 240)

seek = SeekBar()
#player.end_callback = seek.finish

seek.set_background_color('DarkGreen')
seek.set_cursor_color('Black')
seek.set_size(300, 50)
seek.set_position(200, 500)
seek.set_reactive(True)
seek.connect('seek_request_realtime', player.on_seek_request)
player.connect('position_update', seek.update_position)


seek2 = SeekBar()
seek2.set_background_color('DarkGreen')
seek2.set_cursor_color('Black')
seek2.set_size(630, 50)
seek2.set_position(5, 555)
seek2.set_reactive(True)
seek2.connect('seek_request_lazy', player.on_seek_request)
player.connect('position_update', seek2.update_position)

b = ClassicButton('seek +5s', stretch=True)
b.set_size(100, 50)
b.set_position(50, 350)
b.set_reactive(True)
b.connect('button_press_event', on_button_seek, player)

time_label = clutter.Text()
player.connect('position_update', show_time, time_label)

stage.set_size(800, 600)
stage.add(player, seek, seek2, b, time_label)
stage.show()

#import gobject
#gobject.timeout_add(10000, player.set_filename, "/home/anthony/src/candies/mine/test2.ogg")

clutter.main()
