from candies2 import VideoPlayer, SeekBar, ClassicButton
import clutter
import sys

def show_time(self, current_time, progression, duration, time_label):
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
player.set_filename(sys.argv[1])
player.set_reactive(True)
player.connect('button_press_event', on_button_press)


seek = SeekBar()
player.end_callback = seek.finish

seek.set_background_color('DarkGreen')
seek.set_cursor_color('Black')
seek.set_size(630, 50)
seek.set_position(5, 500)
seek.set_reactive(True)
seek.connect('seek_request_realtime', player.on_seek_request)
player.connect('seek', seek.on_seek)


seek2 = SeekBar()
seek2.set_background_color('DarkGreen')
seek2.set_cursor_color('Black')
seek2.set_size(630, 50)
seek2.set_position(5, 555)
seek2.set_reactive(True)
seek2.connect('seek_request_lazy', player.on_seek_request)
player.connect('seek', seek2.on_seek)

b = ClassicButton('seek', stretch=True)
b.set_size(50, 50)
b.set_position(50, 350)
b.set_reactive(True)
b.connect('button_press_event', on_button_seek, player)

time_label = clutter.Text()
player.connect('seek', show_time, time_label)

stage.set_size(800, 600)
stage.add(player, seek, seek2, b, time_label)
stage.show()

clutter.main()
