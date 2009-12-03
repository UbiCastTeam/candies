from candies2 import VideoPlayer, SeekBar
import clutter
import sys

stage = clutter.Stage()
stage.connect('destroy', clutter.main_quit)

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
seek2.connect('seek_request_lasy', player.on_seek_request)
player.connect('seek', seek2.on_seek)

stage.set_size(800, 600)
stage.add(player, seek, seek2)
stage.show()

clutter.main()
